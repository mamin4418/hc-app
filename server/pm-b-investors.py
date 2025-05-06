# -*- coding: utf-8 -*-
"""
Investor Financials, updates etc.
Created on Mon Jan 20 08:59:13 2020

@author: ppare
"""
import sys, getopt, os, platform
from flask import  json
import flask
from locale import LC_ALL
from locale import setlocale
from logging import FileHandler
from logging import Formatter
import logging
import pm_mail, pm_conf, ref_data, pm_update
from pm_tenant import PMTenant
import pandas as pd
from datetime import datetime
from datetime import timedelta
from calendar import monthrange

from utils.pm_db import PMDB
import utils.pm_conf

db = PMDB

app = flask.Flask(__name__, static_url_path="/templates", static_folder="files")

appname="pm-b-investors"

    
def noticeEmail(app, core):
    core['h_logo']=app.config['LOGO_HTML']
    print(appname+".noticeEmail.0:", core)
    
    core['sender_email']='support@himalayaproperties.org'
    core['sender_address1']='support@himalayaproperties.org'
    core['sender_name']=core['company_name']
    
    core['receiver_email']='pgp6758@gmail.com'
    if ( 'email' in core and core['email'] != ''):
        core['receiver_email']=core['email']

    core['receiver_name']=core['first_name']+" "+core['last_name']
    core['message_format']='html'
    if ( 'subject' not in core ):
        core['subject']='IMPORTANT: Himalaya Properties - Payment Update'
    core['reference']= datetime.today().strftime('%Y%m%d%H%M%S')+"/"+str(core['tenancy_id'])+"/"+str(core['tenant_id'])+"/"+str(core['property_id'])
    
    with app.app_context():
        core['message']=flask.render_template(core['template_file'], data=core)

    if ( 'attachment' in core and core['attachment'] != ''):        
        pm_mail.sendMailWAttachment(app, core)    
    else:
        pm_mail.sendMail(app, core)

def paymentUpdates(app, db1, qj, tdate):
    print("paymentUpdates:",tdate, qj)
    today =  datetime.today()
    l_sd1 = '2020-01-01'
    
    O_t = PMTenant(qj['tenant_id'], qj, app.logger, db1)    
    data = O_t.getTInfo()
    
    O_t.updateFTS(db1, tdate, tdate)
    c = O_t.getSTATS()
    print("paymentUpdates.5:", c)
       
    if ( c.empty ):
        print("paymentUpdates: NO PAYMENT FOR THIS TENANT:", data['tenant_id'], data['first_name'], data['last_name'])
        return
    h1 = json.loads(c.to_json(orient='table', double_precision=2))['data']
    print(" format: length:",len(h1))
    i=0
    while i < len(h1):
        #print("history=>", i, "=>", range(len(h1)))
        x = h1[i]
        x['tdate']=x['tdate'].split('T')[0]
        if ( x['type'] != 'TX' ):
            #print("BAD: ", x)
            garbage = h1.pop(i)
        else:
            i +=1
        
    if ( i < 1 ):
        print("paymentUpdates: NO PAYMENT FOR THIS TENANT:", data['tenant_id'], data['first_name'], data['last_name'])
        return
    
    data['transactions']=h1
    
    if ( 'email' not in data or data['email'] == '' ):
        data['email']='pgp6758@gmail.com'

    # Company info
    c_pd = ref_data.get_company_info_pd(db1, app.logger)
    for ind in c_pd.index:
        if ( c_pd['label'][ind] == data['company']):
            data['company']=c_pd['name'][ind]
            data['company_address']=c_pd['m_address'][ind]
            data['company_address2']=c_pd['m_city'][ind]+"  "+c_pd['m_state'][ind]+" "+c_pd['m_zip'][ind]
    
    data['statement_date']=today.strftime('%d %b %Y')     
    
    data['company_name']=data['company']
    data['account'] = "TC."+str(data['tenancy_id'])+".P."+str(data['property_id'])+".T."+str(data['tenant_id'])
    data['amount_due']="{:.2f}".format(data['balance'])
    if ( data['balance'] > 0 ):
        data['amount_due'] += "    You have a credit balance"
    
    if ( 'template_file' not in data ):
        data['template_file']='HP Tenant Payment Update.html'
    data['subject']='HP Payment Update On your account'
    data['zelle_logo']=app.config['LOGO_ZELLE']
    data['venmo_logo']=app.config['LOGO_VENMO']
    data['cashapp_logo']=app.config['LOGO_CASHAPP']
    noticeEmail(app, data)


def updateFinancials(db, t_id, tdate):
    l_pd =  pd.DataFrame()
    l_sd = '2020-01-01'
    qj={}
    core={}
    core['last_payment']=0.0
    core['balance']=0.0
    core['last_payment_date']='1900-01-01'
    today =  datetime.today()
    
    days_in_month = lambda dt: monthrange(dt.year, dt.month)[1]
    dt = today.replace(day=1) + timedelta(days_in_month(today))
    next_month=dt.strftime('%Y-%m-%d') # always choose first of the month
    
    O_t = PMTenant(t_id, qj, app.logger, db)
    print("tenantTX info: ", t_id, next_month)
    
    ti = O_t.getTInfo()
    
    O_t.updateFTS(db, l_sd, tdate)
    l_pd = O_t.getSTATS()
    print(l_pd)
    for ind in l_pd.index:
        core['balance'] = l_pd.at[ind,'balance']
        if ( l_pd.at[ind,'credit'] > 0 ):
            core['last_payment']=l_pd.at[ind,'credit']
            core['last_payment_date'] = l_pd.at[ind,'tdate'].split('T')[0]
        
    if ( core['balance'] > 0 ):
        core['payament_due'] = 0.00
    else: 
        core['payament_due'] = abs(core['balance'])
            
    sqls = "UPDATE pm.Investors_financials SET balance="+str(core['balance'])+", last_payment="+str(core['last_payment'])
    sqls += ", last_payment_date='"+core['last_payment_date']+"', payment_due_date='"+next_month+"',payment_due="+str(core['payament_due'])
    sqls += " WHERE tenant_id="+ str(t_id)
    
    print("updateFinancials:[",t_id,"]:", sqls)
    db.update(sqls)
    print("updateFinancials:[",t_id,"]: DATA UPDATED")
    
    if ( 'tenancy_id' in ti and ti['tenancy_id'] != ''):
        sd = O_t.updateSD(db, None, None)
        
        if ( sd != ti['deposit_a']):
            sqls = "UPDATE pm.tenancy SET deposit_a = "+str(sd)+ " WHERE tenancy_id="+str(ti['tenancy_id'])
            print("updateFinancials:SD:[",t_id,"]:", sqls)
            db.update(sqls)
            print("updateFinancials:SD:[",t_id,"]: SD UPDATED")
    
def generateStatements(app, db1, qj, tdate):
    print("generateStatements:",tdate, qj)
    today =  datetime.today()
    l_sd1 = '2020-01-01'
  
    qj['output_file']="statements/stmt_"+str(qj['tenant_id'])+"_"+tdate+".pdf"
    
    c_pd = ref_data.get_my_categories_pd(db1, app.logger)
    
    if ( 'template_file' not in qj ):
        qj['template_file']='HP Tenant Statement.html'
    data={}
    l_format="pdf"
    
    dt = datetime.today()
    l_ed=tdate
    l_period=60
    
    if ('period' in qj):
        l_period=qj['period']
    
    dt = dt - timedelta(days=l_period)
    l_sd = dt.strftime('%Y-%m-%d')
    dt = dt.replace(day=1)
    
    if ('due_date' in qj):
        due_dt=qj['due_date']
    if ('format' in qj):
        l_format=qj['format']
    if ('start_date' in qj):
        l_sd=qj['start_date']
    if ('end_date' in qj):
        l_ed=qj['end_date']
        
    O_t = PMTenant(qj['tenant_id'], qj, app.logger, db1)    
    data = O_t.getTInfo()
    dt1 = dt.strptime(data['lease_start_date'].split('T')[0],'%Y-%m-%d') - timedelta(days=60)
    l_lsd = dt1.strftime('%Y-%m-%d')
    
    O_t.updateFTS(db1, l_sd1, l_ed)
    c = O_t.getSTATS()
    data['lease_start_date']=data['lease_start_date'].split('T')[0]
    data['lease_end_date']=data['lease_end_date'].split('T')[0]
    data['move_in_date']=data['move_in_date'].split('T')[0]
    print("Dates:", l_sd, l_sd1, " l_lsd=", l_lsd, c)
    if ( not c.empty ):
        h1 = json.loads(c.to_json(orient='table', double_precision=2))['data']
        print(" format: length:",len(h1))
        i=0
        while i < len(h1):
            #print("history=>", i, "=>", range(len(h1)))
            x = h1[i]
            x['tdate']=x['tdate'].split('T')[0]
            if ( x['tdate'] > l_sd):
                #print("GOOD: ", x)
                if ( x['credit'] > 0 ):
                    data['last_payment_date']=x['tdate']
                    data['last_payment']="{:.2f}".format(x['credit'])
                x['credit']="{:.2f}".format(x['credit'])
                x['debit']="{:.2f}".format(x['debit'])
                x['balance']="{:.2f}".format(x['balance'])
                x['category_l']=c_pd.at[x['category_id'],'name']
                if ( '-' in x['balance'] ):
                    data['amount_due']=x['balance'].replace('-',' ')
                    due_dt = qj['due_date']
                elif ( float(x['balance']) > 0 ):
                    data['amount_due']=  x['balance'] + " [Credit]"
                    due_dt = "No Payment Due"
                else:
                    data['amount_due']=  x['balance']
                    due_dt = "No Payment Due"
                i +=1
            else:
                data['carry_forward']="{:.2f}".format(x['balance'])
                data['carry_forward_date']=x['tdate'].split('T')[0]
                #print("BAD: ", x)
                garbage = h1.pop(i)
            
        data['transactions']=h1
    else:
        print("NO transaction to report, no statements will be generated and no email will eb sent")
        return
    
    
    

    data['rent']="{:.2f}".format(data['rent'])
    data['deposit']="{:.2f}".format(data['deposit'])
    data['due_date']=due_dt
    data['statement_date']=today.strftime('%d %b %Y %H:%M:%S %Z')
    if ( 'action' in qj and qj['action'] == 'STATEMENTS2'):
        data['subject']='HP Tenant Statement [REMINDER] : '+tdate
        data['description']="You still have unpaid balance as of today. Please make the payment right away to avoid default. Please see attached PDF file for more information. Please call our office, if you like to get on a payment plan."
        if ( float(data['amount_due'].replace(' [Credit]','')) > 100 ):
            print("Amount due:",data['amount_due'], " < 100, no Email message, will be sent.")
    else:
        data['subject']='HP Monthly Statement : '+tdate
        data['description']="Your monthly statement is here. Please let us know right away, if there are any discrepancy. Please see attached PDF file for more information."
    data['description2']="If you have already sent a payment, please allow 2 days to process once payment is received by our office."
    data['account'] = "TC."+str(data['tenancy_id'])+".P."+str(data['property_id'])+".T."+str(data['tenant_id'])
    h_comments = "Emailed the statement with: Amount Due: "+data['amount_due'] + " Due Date:"+data['due_date']+" Statement Date:" + data['statement_date'] 
    h_comments += " Account:" + data['account'] + " Email:" + data['email']
    # Company info
    c_pd = ref_data.get_company_info_pd(db1,app.logger)
    for ind in c_pd.index:
        if ( c_pd['label'][ind] == data['company']):
            data['company']=c_pd['name'][ind]
            data['company_address']=c_pd['m_address'][ind]
            data['company_address2']=c_pd['m_city'][ind]+"  "+c_pd['m_state'][ind]+" "+c_pd['m_zip'][ind]

    data['h_logo']=app.config['LOGO_PRINT'] 
    
    
    options = {
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'page-size': 'A4',
        'orientation' : 'Portrait',
        'footer-right': '[page]/[topage]'
    }
    
    #print("generateStatements:", data)
    rep1=""
    with app.app_context():
        rep1=flask.render_template(qj['template_file'], data=data)
    #rep1 =flask.render_template(qj['template_file'], data=data)
    #config = pdfkit.configuration(wkhtmltopdf="C:/ProgramData/Anaconda3/Lib/site-packages/wkhtmltopdf/")
    #config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
    config = pdfkit.configuration(wkhtmltopdf=app.config['PRINT_SERVER'])
    
    rep = pdfkit.from_string(rep1, qj['output_file'], configuration=config, options=options)
    
    print("generateStatements.25:", rep)
    if ( 'email' not in data or data['email'] == ''):
        data['email']='pgp6758@gmail.com'
    data['attachment']=qj['output_file']
    data['company_name']=data['company']
    data['template_file']='HP Tenant Email Statement.html'

    
    noticeEmail(app, data)
    
    h={}
    h['tenant_id']=data['tenant_id']
    h['title']=data['subject']
    h['updatedby']=appname
    h['comments']=h_comments
        
    ret = pm_update.tenantHistory(db1, app.logger, h)
    
def processInvestors(app, db1,action, tdate, company, attachment, Investors=""):
    
    qry =" SELECT tc.tenancy_id, t.tenant_id,t.first_name,t.last_name,t.email, t.phone, p.property_id, p.label, p.city, p.state, p.zip, "
    qry += " pc.name as company_name, pc.legal_name as company_legal_name "
    qry += " FROM pm.Investors t, pm.property p, pm.tenancy tc, pm.company pc "
    qry += " WHERE p.property_id > 0 and t.tenant_id = tc.tenant_id and p.property_id = tc.property_id  and p.llc=pc.label and t.status=1 and tc.status in (1,4,5) "
    qry += " and t.first_name not like 'A Himalaya PA%' "
    if ( company != ""):
        qry += " and p.llc = '"+company+"' "
    if ( Investors != ""):
        qry += " and t.tenant_id in ("+Investors+")"
    #qry += " and t.tenant_id=119"
    
    i=0
    print("processInvestors.1:", qry)    
    tc_list = db1.query_list(qry, None)
    
    #print(tc_list)
    for x in tc_list:
        print("TENANT----------------------",x)
        i += 1
        x['action']=action

        if ( 1< 0 and action == 'NOTICE'):
            x['attachment']=attachment
            x['template_file']='HP Tenant Notice.html'
            if ( 'email' in x and x['email'] != '' ):
                x['email']='pgp6758@gmail.com'
            noticeEmail(app, x)
        elif ( action == 'MESSAGE'):
            x['template_file']='HP Tenant Message Card.html'
            x['subject']='Happy Holidays from Himalaya Properties'
            if ( 'email' not in x or x['email'] == '' ):
                x['email']='pgp6758@gmail.com'
            noticeEmail(app, x)
        elif (action == 'FINANCIALS' ):
            updateFinancials(db1, x['tenant_id'], tdate)
        elif (action == 'STATEMENTS' ):
            x['due_date']=tdate
            x['template_file']='HP Tenant Statement.html'
            generateStatements(app,db1, x, tdate)
        elif (action == 'STATEMENTS2' ):
            x['due_date']=tdate
            x['template_file']='HP Tenant Statement.html'
            generateStatements(app, db1, x, tdate)
        elif (action == 'PAYMENTS' ):
            x['due_date']=tdate
            x['template_file']='HP Tenant Payment Update.html'
            paymentUpdates(app, db1, x, tdate)
        elif (action == 'NOTICE' ):
            x['due_date']=tdate
            if ( attachment != ""):
                x['attachment']=attachment
            x['subject']='HP Tenant ['+tdate+']: Welcome Letter'
            x['template_file']='HP Tenant Notice.html'
            noticeEmail(app, x)
        else:
            print("Not a valid action")
            
    print("processInvestors.10 :Processed :", i)

def main(argv):
    
    
    action='FINANCIALS'
    Investors=""
    company=""
    attachment=''
    today =  datetime.today()
    tdate=today.strftime('%Y-%m-%d')  
    ts=today.strftime('%Y%m%d%H%M')
       
    #python pm-receivable-batch.py -t 2020-04-01 -c HC
    #python pm-receivable-batch.py -t 2020-04-01 -c SHARV
    hc_home = os.environ.get('HC_HOME','NA')
    hc_config = os.environ.get('HC_CONFIG','NA')
    if ( hc_config == 'NA'):
        hc_config ="./files/pm-conf.json"
    
    print("OS:", os.name, " 2:", platform.system(), " config file:", hc_config)    
        
    CONFIG = pm_conf.read_conf_from_file(hc_config, platform.system().lower())


    if ( 'allowed_extensions' in CONFIG ):
        ALLOWED_EXTENSIONS = CONFIG["allowed_extensions"]
    app.config['UPLOAD_FOLDER'] = CONFIG["upload_folder"]
    app.config['LOGO_PRINT'] = CONFIG["logo_print"]    
    app.config['LOGO_HTML'] = CONFIG["logo_html"]    
    app.config['LOGO_VENMO'] = CONFIG["logo_venmo"]    
    app.config['LOGO_CASHAPP'] = CONFIG["logo_cashapp"]    
    app.config['LOGO_ZELLE'] = CONFIG["logo_zelle"]    
    app.config['PRINT_SERVER'] = CONFIG["print_server"]    
    app.config['LOGDIR'] = CONFIG["log_dir"]
    app.config['LOGDIR'] = CONFIG["log_file"]
    app.config['HP_SUPPORT_EMAIL'] = 'support@himalayaproperties.org'
    
    log_dir = CONFIG["log_dir"]
    LOG_FILE = log_dir + '/'+ appname +'.log.'+ts
    LOG_FORMAT = "%(thread)d|%(levelname)s|%(asctime)s|%(filename)s|%(funcName)s|L:%(lineno)d|%(message)s"

    file_handler = logging.FileHandler(filename=LOG_FILE)
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    app.logger = logging
    app.logger.basicConfig(format=LOG_FORMAT, level=logging.DEBUG, handlers=handlers)

    app.logger.info("========= HP %s started ==========", appname)
    app.logger.info("OS: %s  Platform:%s Config:%s", os.name, platform.system(), hc_config)

    db = PMDB(
        CONFIG["db"]["host"],
        int(CONFIG["db"]["port"]),
        CONFIG["db"]["user"],
        CONFIG["db"]["pass"],
        CONFIG["db"]["schema"],
        app.logger
    )
    
    try:
        opts, args = getopt.getopt(argv,"ht:a:c:f:i:",["attachment=","action=","company=","tenant_ids="])
    except getopt.GetoptError:
        print('pm-b-investors.py -a <STATEMENTS | FINANCIALS | EMAIL | NOTICE> -t <tdate> -c <company name> -f <attachment> -i <tenant ids>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python pm-b-investors.py -t 2018-11-01 -c HC')
            sys.exit()
        elif opt in ("-t", "--tdate"):
            tdate = arg
        elif opt in ("-a", "--action"):
            action = arg
        elif opt in ("-f", "--attachment"):
            attachment = arg
        elif opt in ("-c", "--company"):
            company = arg
        elif opt in ("-i", "--tenant_ids"):
            Investors = arg
    print("Processing for [", action, "]date=", tdate , " company=", company)
    if ( company != "" or Investors != "" ):
        processInvestors(app, db,action, tdate, company, attachment, Investors)
    else:
        print('pm-b-investors.py. ERR. Please provide company name, or a tenant info')
    
if __name__ == "__main__":
   main(sys.argv[1:])

print("I am done")