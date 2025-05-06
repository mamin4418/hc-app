# -*- coding: utf-8 -*-
"""
E Payments etc.
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
import utils.pm_conf, pm_tranche
from utils.pm_db import PMDB

import pandas as pd
from datetime import datetime
from datetime import timedelta
from calendar import monthrange

db = PMDB

app = flask.Flask(__name__, static_url_path="/templates", static_folder="files")

appname="pm-b-epayments"
logfile=appname+".log"
errfile=appname+".err"

def processZelle(app, db,core, attachment):
    
    d_payment={}

    #fd = open(attachment, "r")
    df = pd.read_excel(io=attachment)
    
    for index, row in df.iterrows():
        #Zelle Transfer Conf# 006GWU7OW;
        print(appname,".5 :ZELLE :", row)
        if ( "Zelle Transfer Conf#" in row['Description'] ):
            tx_id = row['Description'].replace("Zelle Transfer Conf# ","").split(";")[0]
            
            print("Row:",row['Credit'],row['Description'], tx_id,row['Date'])
            d_payment[tx_id]=row
    
    #print(appname,".10 :Processed :", d_payment)
    
    getTransactions(app, db, core, d_payment)
    
def processCashApp(app, db,core, attachment):
    
    d_payment={}

    #fd = open(attachment, "r")
    df = pd.read_excel(io=attachment)
    
    for index, row in df.iterrows():
        tx_id = row['Transaction ID'].upper().strip()
        print("Row:",row['Amount'],row['Status'], tx_id,row['Date'],row['Name of sender/receiver'], row['Notes'])
        d_payment[tx_id]=row
    
    print(appname,".10 :Processed :", d_payment)
    
    getTransactions(app, db,core, d_payment)            


def getTransactions(app, db,core, d_payment):
    print("getTransactions.1:", core)    
    qry ="select p.llc, p.group, p.label as p_label, c.label, t.first_name, t.last_name, tx.*, trn.tranche_name"
    qry += " from pm.transactions tx , pm.property p, pm.category c, pm.tenants t, pm.tranche trn"
    qry += " where tx.property_id=p.property_id and tx.category_id=c.category_id and t.tenant_id=tx.tenant_id"
    qry += " and c.category_id in ("+core['CATEGORY']+") and tx.tdate between '"+core['START DATE']+"' and '"+core['END DATE']+"'"
    qry += " and tx.type='"+core['TYPE']+"' and trn.tranche_id=p.tranche_id order by tx.tdate, c.label"
    
    i=0
    print("getTransactions.1:", qry)    
    tx_list = db.query_list(qry, None)

    of = open(core['OUT_FILE'], "w")
    
    #print(tc_list)
    miss=0
    i=0
    mapped=0
    for x in tx_list:
        i +=1
        k = x['reference'].replace("#","").upper().strip()

        if ( k in d_payment):
            print("TX[",x, "]======================", d_payment[k])
            ostr=str(d_payment[k]['Date'])+"|"+d_payment[k]['Transaction Type'] +"|"
            ostr+=str(d_payment[k]['Currency'])+"|"+str(d_payment[k]['Amount']) +"|"
            ostr+=str(d_payment[k]['Fee'])+"|"+str(d_payment[k]['Net Amount']) +"|"
            ostr+=str(d_payment[k]['Asset Type'])+"|"+str(d_payment[k]['Asset Price']) +"|"
            ostr+=str(d_payment[k]['Asset Amount'])+"|"+str(d_payment[k]['Status']) +"|"
            ostr+=str(d_payment[k]['Notes'])+"|"+str(d_payment[k]['Name of sender/receiver']) +"|"
            ostr+=str(d_payment[k]['Account'])+"|"+str(x['tranche_name']) +"|"
            ostr+= x['group']+"|"+ x['p_label'] +"|" 
            ostr += x['llc'] +"|" + str(x['property_id']) +"|" + str(x['tx_id']) +"\n"
            of.write(ostr)
            mapped += 1
        else:
            print(core['TYPE'],"=",k, "=", x)
            miss +=1
        if ( i > 10):
            break
            
    print("getTransactions.10 :Processed :", i, miss, mapped)

def main(argv):
    
    
    action='FINANCIALS'
    tranche=""
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
        
    CONFIG = utils.pm_conf.read_conf_from_file(hc_config, platform.system().lower())


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
    core = {}
    core['START DATE']='20230101'
    core['END DATE']='20230131'
    core['CATEGORY']='8'
    core['OUT_FILE']="..\data\zelle.txt"

    try:
        opts, args = getopt.getopt(argv,"ht:a:c:f:i:",["attachment=","action=","company=","tenant_ids="])
    except getopt.GetoptError:
        print('pm-b-epayments.py -a <STATEMENTS | FINANCIALS | EMAIL | NOTICE> -t <tdate> -c <company name> -f <attachment> -i <tenant ids>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python pm-b-epayments.py -t 2018-11-01 -a CASHAPP -f FILENAME')
            sys.exit()
        elif opt in ("-t", "--tdate"):
            tdate = arg
        elif opt in ("-a", "--action"):
            action = arg
        elif opt in ("-f", "--attachment"):
            attachment = arg
        elif opt in ("-c", "--company"):
            company = arg
        elif opt in ("-i", "--tranche_id"):
            tranche = arg
    print("Processing for [", action, "]date=", tdate , " company=", company)
    if ( action == 'CASHAPP' ):
        core['TYPE']='Cash App'
        
        processCashApp(app, db,core, attachment)
    elif( action == 'ZELLE' ):
        core['TYPE']='Zelle'
        processZelle(app, db,core, attachment)
    else:
        print('pm-b-epayments.py. ERR. Please provide all the information')
    
if __name__ == "__main__":
   main(sys.argv[1:])

print("I am done")