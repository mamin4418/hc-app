# -*- coding: utf-8 -*-
"""
Monthly receivable updates
Created on Mon Jan 20 08:59:13 2020

@author: ppare
"""
import sys, getopt, os, platform

from datetime import timedelta, datetime
from flask import  json
import flask
from locale import LC_ALL
from locale import setlocale
from logging import FileHandler
from logging import Formatter
import logging


from utils.pm_db import PMDB
import utils.pm_conf

db = PMDB

global G_VARS
G_VARS = {}
G_VARS['parent_utilities']=0

appname="pm-receivable-batch"
logfile=appname+".log"
errfile=appname+".err"

app = flask.Flask(__name__, static_url_path="/templates", static_folder="files")


def processFormula(formula, amount):
    #REIMBURSE @ 33.33%
    #REIMBURSE @ 32.34$
    #REIMBURSE > 32.34$
    #FIX @ 50$
    #5 DAYS @ 50$ WEEK, 10 DAYS @ 50$ FIXED, 1 DAYS @ 5$ DAY, 5 DAYS @ 10% RENT
    val = 0.0
    f = formula.split(" ")
    if ( f[0] == 'REIMBURSE'):
        print("processFormula.1: REIMBURSE: ", f[2])
        if ( f[1] == '@' and '%' in f[2]):
            v = float(f[2].replace('%',''))
            val = v * amount / 100
        elif ( f[1] == '@' and '$' in f[2]):
            val = float(f[2].replace('$',''))
        elif ( f[1] == '>' and '$' in f[2]):
            v = float(f[2].replace('$',''))
            if ( amount > v ):
                val = amount - v
    elif ( f[0] == 'FIX'):
        print("processFormula.1: FIX: ", f[2])
        if ( f[1] == '@' and '$' in f[2]):
            val = float(f[2].replace('$',''))
    elif ( f[1] == 'DAYS'):
        print("processFormula.6: DAYS: ", f[0])
        day = int(datetime.today().strftime('%d'))
        day = day - int(f[0])
        if ( day < 1 ):
            return val

        if ( '$' in f[3] and f[4] == 'DAY'):
            v = float(f[3].replace('$',''))
            val = v * day
        elif ( '$' in f[3] and f[4] == 'WEEK'):
            v = float(f[3].replace('$',''))
            val = v * day / 7
        elif ( '$' in f[3] and 'FIX' in f[4]):
            val = float(f[3].replace('$',''))
        elif ( '%' in f[3] and f[4] == 'RENT'):
            v = float(f[3].replace('%',''))
            val = v * amount / 100
        
    return val

def getUtilities(db1, tdate, p_id):
    qry = "SELECT tx.tx_id, date_format(tx.tdate,'%Y-%m-%d') as tdate, tx.debit, tx.description, tx.category_id FROM pm.transactions tx "
    qry += " WHERE tx.debit > 0 and tx.tdate > '"+tdate+"' and tx.property_id in ("+str(p_id)+")"
    app.logger.info("getUtilities.1:%s", qry)    
    mlist = db1.query_list(qry, None)
    app.logger.info("getUtilities.2:%s", mlist)
    return mlist

def updateLateFees(db1, tdate, core):
    # Receivable category_id=106
    app.logger.info("updateLateFees.0:%s | %s", core , G_VARS)
    qry = "SELECT tf.tenant_id, tf.balance, tf.last_payment, tf.last_payment_date, tf.payment_due, tf.payment_due_date "
    qry += ", tca.value , tca.reference "
    qry += "FROM pm.tenants_financials tf, pm.tenancy_attributes tca, pm.tenancy tc "
    qry += " WHERE tc.tenancy_id=tca.tenancy_id and tc.tenant_id=tf.tenant_id and tc.tenant_id = tf.tenant_id "
    qry += " and tca.name='106' and tc.tenancy_id="+str(core['tenancy_id'])
    app.logger.info("updateLateFees.1: %s", qry)
    mlist = db1.query_list(qry, None)
    for x in mlist:
        app.logger.info("updateLateFees.2: %s", x)
        d1 = x['last_payment_date'].now().strftime('%d')
        
        if ( x['balance'] < 0 and abs(x['balance']) >= core['rent'] and len(x['reference']) > 3 ):
            late_fees = 0
            late_fees = processFormula(x['reference'].upper(), core['rent'])
            app.logger.info("updateLateFees.2: OVER DUE PAYMENT: %s | %s ", d1, late_fees)    
            if ( late_fees > 0 ):
                core['amount']=late_fees
                core['description']="Late Fees "+x['value']+" : "+x['reference']
                core['category_id']='106'
                updateReceivables(db1, tdate, core)

def updateWasherDryer (db1, tdate, core):
    app.logger.info("updateWasherDryer.0:%s g_pu[%s] %s", tdate, G_VARS['parent_utilities'], core) 
    qry = "SELECT tca.*, co.* FROM pm.tenancy_attributes tca , pm.cores co where tca.name = co.co_name "
    qry += " and co.co_type='TENANCY_ATTRIBUTES' and tca.value='TENANT' "
    qry += " and tca.name = '210' and tca.reference != '' "
    qry += " and tca.tenancy_id="+str(core['tenancy_id'])
    app.logger.info("updateWasherDryer.1:%s", qry)    
    mlist = db1.query_list(qry, None)
    app.logger.info("updateWasherDryer.2:%s", mlist)
    if ( len(mlist) < 1):
        app.logger.info("updateWasherDryer.3: No WasherDryer paid by tenant")
        return
    core['description']="Monthly Washer - Dryer Rental Charges"
    core['category_id']='210'
    amount=0.0
    for x in mlist:
        app.logger.info("WASHER DRYER FEES: %s",x)
        amount = processFormula(x['reference'],0)
        core['description']="Monthly Washer - Dryer Rental Charges"
    core['amount']=amount    
    if ( amount > 0.0 ):
        updateReceivables(db1, tdate, core)

def updateDiscount (db1, tdate, core):
    app.logger.info("updateDiscount.0:%s g_pu[%s] %s", tdate, G_VARS['parent_utilities'], core) 
    qry = "SELECT tca.*, co.* FROM pm.tenancy_attributes tca , pm.cores co where tca.name = co.co_name "
    qry += " and co.co_type='TENANCY_ATTRIBUTES' and tca.value='TENANT' "
    qry += " and tca.name = '211' and tca.reference != '' "
    qry += " and tca.tenancy_id="+str(core['tenancy_id'])
    app.logger.info("updateDiscount.1:%s", qry)    
    mlist = db1.query_list(qry, None)
    app.logger.info("updateDiscount.2:%s", mlist)
    if ( len(mlist) < 1):
        app.logger.info("updateDiscount.3: No MTM Fees")
        return
    core['description']="Month to Month Charges"
    core['category_id']='211'
    amount=0.0
    for x in mlist:
        app.logger.info("updateDiscount.5: %s",x)
        amount = processFormula(x['reference'],0)
        core['description']="Month to Month Charges"
    core['amount']=amount    
    if ( amount > 0.0 ):
        updateReceivables(db1, tdate, core)

def updateMTM (db1, tdate, core):
    app.logger.info("updateMTM.0:%s g_pu[%s] %s", tdate, G_VARS['parent_utilities'], core) 
    qry = "SELECT tca.*, co.* FROM pm.tenancy_attributes tca , pm.cores co where tca.name = co.co_name "
    qry += " and co.co_type='TENANCY_ATTRIBUTES' and tca.value='TENANT' "
    qry += " and tca.name = '211' and tca.reference != '' "
    qry += " and tca.tenancy_id="+str(core['tenancy_id'])
    app.logger.info("updateMTM.1:%s", qry)    
    mlist = db1.query_list(qry, None)
    app.logger.info("updateMTM.2:%s", mlist)
    if ( len(mlist) < 1):
        app.logger.info("updateMTM.3: No MTM Fees")
        return
    core['description']="Month to Month Charges"
    core['category_id']='211'
    amount=0.0
    for x in mlist:
        app.logger.info("MTM FEES: %s",x)
        amount = processFormula(x['reference'],0)
        core['description']="Month to Month Charges"
    core['amount']=amount    
    if ( amount > 0.0 ):
        updateReceivables(db1, tdate, core)

def updateUtilities(db1, tdate, core):
    app.logger.info("updateUtilities.0:%s g_pu[%s] %s", tdate, G_VARS['parent_utilities'], core) 
    qry = "SELECT tca.*, co.* FROM pm.tenancy_attributes tca , pm.cores co where tca.name = co.co_name and co.co_type='TENANCY_ATTRIBUTES' and tca.value='TENANT' and tca.reference != '' and tca.tenancy_id="+str(core['tenancy_id'])
    app.logger.info("updateUtilities.1:%s", qry)    
    mlist = db1.query_list(qry, None)
    app.logger.info("updateUtilities.2:%s", mlist)
    if ( len(mlist) < 1):
        app.logger.info("updateUtilities.3: No utilities paid by tenant")
        return
    p_id = str(core['property_id'])
    if ( int(G_VARS['parent_utilities']) == 1 and 'parent' in core and core['parent'] != '' and core['parent'] != None):
        p_id += ","+str(core['parent'])

    dt = datetime.strptime(tdate,"%Y-%m-%d")
    t_dt = dt - timedelta(days=15)
    tdate = t_dt.strftime("%Y-%m-%d")
    check_dt = core['start_date']
    check_dt = check_dt + timedelta(days=31)

    if ( t_dt < check_dt):
        app.logger.info("TENANT UTILITIES CHECK: LOWER 30DAY THRESHOLD IGNORE %s TDATE[%s] Startdate[%s] Check Dt[%s], ",t_dt, tdate, core['start_date'] , check_dt)
        return
        
    ulist = getUtilities(db1, tdate, p_id)
    for x in mlist:
        u_ids = x['name'].split('|')
        app.logger.info("TENANT UTILITIES O-:%s | %s",x, u_ids)
        for u in ulist:
            #print("TENANT UTILITIES I----------------------",u['category_id'], "=", u_ids[0])
            if ( str(u_ids[0]) == str(u['category_id'])):
                core['amount']= processFormula(x['reference'], u['debit'])
                core['description']=x['co_value']+" "+x['reference']+" of "+ str(u['debit']) +" TX["+str(u['tx_id'])+"]"
                core['category_id']=u_ids[1]
                core['tx_id']=u['tx_id']
                updateReceivables(db1, u['tdate'], core)

############ Pet receivables
def updatePetReceivables(db1, tdate, core):
    # Parking receivable category_id=107
    qry = "select * from pm.tenants_pet tp where tp.monthly > 0 and tp.tenant_id="+str(core['tenant_id'])
    app.logger.info("updatePetReceivables.1:%s", qry)    
    mlist = db1.query_list(qry, None)
    
    core['description']="Monthly Pet Charges for : "
    core['category_id']='116'
    amount=0.0
    for x in mlist:
        app.logger.info("PET FEES: %s",x)
        amount += x['monthly']
        core['description'] += str(x['pet_id'])+":"+x['pet_type']+" "+x['pet_role']+" "+x['breed'] +" | "
    core['amount']=amount    
    if ( amount > 0.0 ):
        updateReceivables(db1, tdate, core)

def updateParkingReceivables(db1, tdate, core):
    # Parking receivable category_id=107
    qry = "select * from pm.tenants_vehicle tv where tv.monthly > 0 and tv.tenant_id="+str(core['tenant_id'])
    app.logger.info("updateParkingReceivables.1:%s", qry)    
    mlist = db1.query_list(qry, None)
    
    core['description']="Monthly Parking Charge for : "
    core['category_id']='107'
    amount=0.0
    for x in mlist:
        app.logger.info("TENANT PARKING ---: %s",x)
        amount += x['monthly']
        core['description'] += str(x['parking_tag_id'])+":"+x['state']+" "+x['tag']+" "+x['make']
        if ( 'model' in x and x['model'] != None):
            core['description'] +=" "+x['model']
        if ( 'color' in x and x['color'] != None):
            core['description'] +=" "+x['color']
        
        core['description'] += ", "
    core['amount']=amount    
    if ( amount > 0.0 ):
        updateReceivables(db1, tdate, core)
    
def updateReceivables(db1, tdate, core):
    
    app.logger.info("updateReceivables.0: %s", core)
    oa = -999
    tr_id=-1
    tx_id=-1
    updatedby=''
    desc=core['description']
    amount = core['amount']
    p_id=core['property_id']
    t_id=core['tenant_id']
    c_id=core['category_id']
    if ('tx_id' in core):
        tx_id=core['tx_id']
    
    sqls = "SELECT tr.tr_id, tr.amount, tr.updated, tr.updatedby FROM pm.tenants_receivable tr "
    sqls += " where tr.category_id="+str(c_id)+" and tr.tenant_id="+ str(t_id) + " and  ( tr.tx_id=-1 or tr.tx_id="+str(tx_id)
    sqls += " ) and tr.property_id="+str(p_id) 
    if ( c_id == '106' ):
        sqls += " and tr.tdate > '"+G_VARS['curMonth']+"'"
    else:
        sqls += " and tr.tdate='"+tdate+"'"
    
    app.logger.info("updateReceivables.2::%s", sqls)
    
    ct = db1.query_one(sqls, None)
    if ( ct != None ):
        oa = ct['amount']
        tr_id=ct['tr_id']
        updatedby=ct['updatedby']
    
    app.logger.info("updateReceivables.3::tr_id[%s] new amount[%s] from DB[%s]", tr_id, amount, oa)
    if ( oa == -999 and amount != 0 ):
        sqls = "INSERT INTO pm.tenants_receivable(`tenant_id`,`category_id`,`property_id`,`tdate`,`description`,`tx_id`,`amount`,`updatedby`) "
        sqls += "VALUES ("+str(t_id)+ "," + str(c_id)+","+str(p_id)+",'"+tdate+"','"+desc+"',"+str(tx_id)+","+ str(amount)+",'pm-receivable-batch')"
        try:
            app.logger.info("updateReceivables.4:[INSERT] %s", sqls)
            if ( core['UPDATEDB'] == '1' ):
                ct = db1.insert(sqls, None)
        except ValueError:
            app.logger.info("updateReceivables.41 Failed: %s", sqls) 
    elif ( updatedby != 'pm-receivable-batch' ):
        app.logger.info("updateReceivables.5:NO update required - Manual override by %s", updatedby)
    elif ( oa != -999 and oa != amount ):
        sqls = "UPDATE pm.tenants_receivable SET amount="+str(amount)+", description='"+desc+"', updatedby='pm-receivable-batch' "
        if ( c_id != '106' ):
            sqls += ",tdate='"+tdate+"'"
        sqls += " WHERE tr_id=" + str(tr_id)
        try:
            app.logger.info("updateReceivables.6:[UPDATE]%s", sqls)
            if ( core['UPDATEDB'] == '1' ):
                ct = db1.update(sqls)
        except ValueError:
            app.logger.info("updateReceivables.61 Failed:%s", sqls) 
    else:
        app.logger.info("updateReceivables.7:NO update required")
            
    app.logger.info("updateReceivables.10 :Processed[tenant_id:%s]", t_id)
    

def processTenants(db1, tdate, company, action,dbUpdate, group, tenants=""):
    
    qry =" SELECT tc.tenancy_id, t.tenant_id,t.first_name,t.last_name,t.email, t.phone, p.property_id,p.parent, "
    qry += " pc.name as company_name, pc.legal_name as company_legal_name, tc.rent as rent, "
    qry += " tc.start_date, tc.end_date, tc.term "
    qry += " FROM pm.tenants t, pm.property p, pm.tenancy tc, pm.company pc"
    qry += " WHERE p.property_id > 0 and t.tenant_id = tc.tenant_id and p.property_id = tc.property_id and p.llc=pc.label and t.status=1 and tc.status in (1,4,5) "
    qry += " and tc.responsible != '' and lower(t.first_name) not like 'himalaya%' "
    if ( company != ""):
        qry += " and p.llc = '"+company+"' "
    if ( group != ""):
        qry += " and p.group = '"+group+"' "
    if ( tenants != ""):
        qry += " and t.tenant_id in ("+tenants+")"
    #qry += " and t.tenant_id=119"
    
    i=0
    app.logger.info("processTenants:%s", qry)    
    tc_list = db1.query_list1(qry)
    
    #print(tc_list)
    for x in tc_list:
        print("TENANT-------------------------- [", action, "]--",x)
        i += 1
        x['UPDATEDB'] = dbUpdate
        if (action == 'MONTHLY' ):
            x['description']='Monthly Rent'
            x['amount']=x['rent']
            x['category_id']='102'
            updateReceivables(db1, tdate, x)
            updateParkingReceivables(db1, tdate, x)
            updatePetReceivables(db1, tdate, x)
            updateWasherDryer(db1, tdate, x)
            if ( x['term'] == 'MTM'):
                updateMTM(db1, tdate, x)
        elif (action == 'UTILITIES' ):
            updateUtilities(db1, tdate, x)
        elif (action == 'LATEFEES' ):
            updateLateFees(db1, tdate, x)
        else:
            print("Not a valid action")
            
    print("processTenants.10 :Processed :", i)
    

def main(argv):
    dbUpdate=0

    action ='UTILITIES'
    tdate=""
    mode=""
    config_type = platform.system().lower()
    curDate = datetime.today()
    ts=curDate.strftime('%Y%m%d%H%M')  
    nextMonth = ""
    today=curDate.strftime('%Y-%m-%d')  # always choose first of the month
    
    day = curDate.day
    mon = curDate.month
    curDate = curDate.replace(day=1)
    curMonth=curDate.strftime('%Y-%m-%d')

    companies={'HC','SHARV', 'AHPA','AHPA II'}
    company=""
    tenants=""
    group=""

    if ( day > 25):
        if ( mon < 12 ):
            nextMonth = curDate.replace(month=mon+1).strftime('%Y-%m-%d')
        else:
            nextMonth = curDate.replace(month=1).strftime('%Y-%m-%d')
    
    due_date=curDate.strftime('%Y-%m-%d')  # always choose first of the month

    G_VARS['day']=day
    G_VARS['mon']=mon
    G_VARS['curMonth']=curMonth
    G_VARS['nextMonth']=due_date
    
    try:
        opts, args = getopt.getopt(argv,"ht:m:c:a:i:g:u:x:",["action=","company=","group=","tenant_ids=","tdate=", "updateDB=", "updatePU="])
    except getopt.GetoptError:
        print('pm-receivable-batch.py -t <tdate> -c <company name> -g <group> -a <action: MONTHLY | UTILITIES | LATEFEES> -i <12,13> -u <1|0> -m mode')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python pm-receivable-batch.py -u 1 -t 2018-11-01 -c HC -a UTILITIES')
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-t", "--tdate"):
            tdate = arg
        elif opt in ("-a", "--action"):
            action = arg
        elif opt in ("-c", "--company"):
            company = arg
        elif opt in ("-g", "--group"):
            group = arg
        elif opt in ("-i", "--tenant_ids"):
            tenants = arg
        elif opt in ("-u", "--updateDB"):
            dbUpdate = arg
        elif opt in ("-x", "--updatePU"):
            G_VARS['parent_utilities'] = arg
    
    print(" Today:", today, day, " Due Date:", due_date, " NM:", nextMonth, " PM:", curMonth)
    
    
    if ( mode != None ):
        config_type += "-" + mode
    else:
        mode = ""

    #python pm-receivable-batch.py -t 2020-04-01 -c HC
    #python pm-receivable-batch.py -t 2020-04-01 -c SHARV
    
    hc_home = os.environ.get('HC_HOME','NA')
    hc_config = os.environ.get('HC_CONFIG','NA')
    if ( hc_config == 'NA'):
        hc_config ="./files/pm-conf.json"
    
    print("OS:", os.name, " 2:", platform.system(), " config file:", hc_config, " config:", config_type)    
        
    CONFIG = utils.pm_conf.read_conf_from_file(hc_config, config_type);

    app.config['UPLOAD_FOLDER'] = CONFIG["upload_folder"]
    app.config['LOGO_PRINT'] = CONFIG["logo_print"]    
    app.config['LOGO_HTML'] = CONFIG["logo_html"]    
    app.config['PRINT_SERVER'] = CONFIG["print_server"]    
    app.config['LOG_DIR'] = CONFIG["log_dir"]
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
    
    if ( tdate == "" and action == 'MONTHLY' ):
        tdate = nextMonth
    elif ( tdate == ""):
        tdate = today
    
    app.logger.info("Processing for date[%s] company[%s] group[%s] action[%s] tenant_ids[%s] update_parent[%s]", tdate, company, group, action, tenants, G_VARS['parent_utilities'])
    app.logger.info(" Today: %s %s Due Date: %s  NM: %s PM: %s", today, day, due_date, nextMonth, curMonth)

    if ( company != "" or group != "" or tenants != ""):
        processTenants(db, tdate, company, action, dbUpdate, group, tenants)
    else:
        for company in companies:
            processTenants(db, tdate, company, action,dbUpdate, group, tenants)
    
    
if __name__ == "__main__":
   main(sys.argv[1:])

print("I am done")
