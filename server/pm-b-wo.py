# -*- coding: utf-8 -*-
"""
Monthly receivable updates
Created on Mon Jan 20 08:59:13 2020

@author: ppare
"""
import sys, getopt, os, platform
from flask import json
import flask
import pm_mail, pm_conf, pm_wo, ref_data
import pandas as pd
from datetime import datetime

import pdfkit

from pm_db import PMDB

db = PMDB

app = flask.Flask(__name__, static_url_path="/templates", static_folder="files")

appname="pm-b-wo"

def noticeEmail(core):
    print("pm_mail.noticeEmail.0:", core)
    core['h_logo']=app.config['LOGO_HTML']
    core['sender_email']='himalayacapitalllc@gmail.com'
    core['sender_name']=core['company_name']
    core['receiver_email']=core['email']
    core['receiver_name']=core['first_name']+" "+core['last_name']
    core['message_format']='html'
    if ( 'subject' not in core ):
        core['subject']='IMPORTANT: Himalaya Properties - Todays WO List'
    core['reference']= datetime.today().strftime('%Y%m%d%H%M%S')
    
    with app.app_context():
        core['message']=flask.render_template(core['template_file'], data=core)

    if ( 'attachment' in core and core['attachment'] != ''):        
        pm_mail.sendMailWAttachment(core)    
    else:
        pm_mail.sendMail(core)
    
def genWOReport(app1, db, core):
    
    ws_pd = ref_data.get_my_cores_pd(db, 'WO_STATUS')
    ws_pd = ws_pd.set_index('co_name')
    wp_pd = ref_data.get_my_cores_pd(db, 'WO_PRIORITY')
    wp_pd = wp_pd.set_index('co_name')

    print("pm_print.wo_reports.1:",core)
    core['format']='pdf'
    core['output_file']="statements/daily_wolist_scott.pdf"
    l_format=core['format'] 
    core['template_file']='HP Daily WO List.html'
    core['user_id']=1
    data={}
    w_pd = pm_wo.getWOS(db, app1.logger, core)
    if ( not w_pd.empty ):
        h1= json.loads(w_pd.to_json(orient='table', double_precision=2))['data']
    #print(" format: length:",len(h1))
        i=0
        while i < len(h1):
            #print("history=>", i, "=>", h1[i])
            x = h1[i]
            x['tdate']=x['tdate'].split('T')[0]
            if ( x['status'] > 0 and x['owner'] == 'Scott LeCain'):
                #print("GOOD: ",ws_pd.at['2','co_value'])
                x['status_l']=ws_pd.at[str(x['status']),'co_value']
                x['priority_l']=wp_pd.at[str(x['priority']),'co_value']
                x['address']=x['label']
                i +=1
            else:
                #print("BAD: ", x)
                garbage = h1.pop(i)            
    data['transactions'] = h1
    data['statement_date']=datetime.today().strftime('%d %b %Y')
    
    print("pm_print.wo_reports:", data)

    data['h_logo']=app1.config['LOGO_PRINT'] 
    options = {
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'page-size': 'A4',
        'orientation' : 'Portrait',
        'footer-right': '[page]/[topage]'
    }
    with app1.app_context():
        rep1 =flask.render_template(core['template_file'], data=data)

    
    config = pdfkit.configuration(wkhtmltopdf=app.config['PRINT_SERVER'])
    
    rep = pdfkit.from_string(rep1, core['output_file'], configuration=config, options=options)
    
    print("generateStatements.25:", rep)
    data['email']='pgp6758@gmail.com'
    data['attachment']=core['output_file']
    data['first_name'] = 'Scott'
    data['last_name'] = 'LeCain'
    data['company_name']='Himalaya Properties'
    data['template_file']='HP Daily WO List.html'
    data['subject']='HP Todays WO'
    noticeEmail(data)
  

def main(argv):
    
    action='DAILY REPORT'
    tenants=""
    wos=""
    company=""
    attachment=''
    today =  datetime.today()
    tdate=today.strftime('%Y-%m-%d')  
       
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
    app.config['PRINT_SERVER'] = CONFIG["print_server"]    
    app.config['LOGDIR'] = CONFIG["log_dir"]
    app.config['HP_SUPPORT_EMAIL'] = 'support@himalayaproperties.org'
    
    db = PMDB(
        CONFIG["db"]["host"],
        int(CONFIG["db"]["port"]),
        CONFIG["db"]["user"],
        CONFIG["db"]["pass"],
        CONFIG["db"]["schema"],
        app.logger
    )
    
    try:
        opts, args = getopt.getopt(argv,"ht:a:c:f:i:w:",["attachment=","action=","company=","tenant_ids=", "wo_ids="])
    except getopt.GetoptError:
        print('pm-b-tenants.py -a <action> -t <tdate> -c <company name> -f <attachment> -i <tenant ids>, -w <wo_ids>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python pm-b-tenants.py -t 2018-11-01 -c HC')
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
            tenants = arg
        elif opt in ("-w", "--wo_ids"):
            wos = arg
    print("Processing for [", action, "]date=", tdate , " action=", action, " company=", company, " tenants=", tenants, " wos=", wos)

    core = {}
    core['REPORT']='DAILY MORNING REPORT'
    genWOReport(app, db, core)
    
    
if __name__ == "__main__":
   main(sys.argv[1:])

print("I am done")