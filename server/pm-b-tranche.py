# -*- coding: utf-8 -*-
"""
Tranche Financials, updates etc.
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
from analysis.pm_cashflow import PMCashflow
from utils.pm_db import PMDB

import pandas as pd
from datetime import datetime
from datetime import timedelta
from calendar import monthrange

db = PMDB

app = flask.Flask(__name__, static_url_path="/templates", static_folder="files")


appname="pm-b-tranche"
logfile=appname+".log"
errfile=appname+".err"

def trancheAnalytics(app, db1,core, tdate):
    c_pd = pd.DataFrame()
    dates = findDates(tdate)

    app.logger.debug("trancheAnalytics.0:%s %s [%s]",tdate,core, dates)
    updatedby="pm-b-tranche"
    core["start_date"]=dates['mon_start']
    core["end_date"]=dates['mon_end']
    core["tdate"]=dates['mon_end']
    app.logger.debug("trancheAnalytics.0:%s %s",tdate,core)
    #sys.exit(0)

    try:
        O_pmcf = PMCashflow(app.logger,db1, core)
        r_type="PCF"
        if ( r_type == "TAX" ):
            O_pmcf.updateTaxTS(db1)
            c_pd = O_pmcf.getTS()
        elif( r_type == "PCF" ):
            O_pmcf.updatePCF(db1)
            c_pd = O_pmcf.getTS()    
            option = 1
        elif( r_type == "PROJECT" ):
            O_pmcf.updateProjectTS(db1)
            c_pd = O_pmcf.getTS()    
            option = 1
        else:
            O_pmcf.updateTS(db1)
            c_pd = O_pmcf.getTS()
        app.logger.debug("trancheAnalytics info:%s", c_pd)
        for column in c_pd:
            print(c_pd[column])
        to_units = 0
        oc_units = 0
        rr_units = 0
        ot_units =0
        m_rent=0.0
        sd_r=0.0
        sd_a=0.0
        deliquency = 0.0
        rent=0.0
        cur_rent=0.0
        for ind in c_pd.index:
            #app.logger.debug("trancheAnalytic.5:%s rent[%s] %s %s",c_pd['label'][ind],c_pd['rent'][ind], c_pd['income'][ind], c_pd['receivable'][ind])
            to_units +=1
            if ( c_pd['p_status'][ind] == 'RENT READY'):
                rr_units += 1
            elif(c_pd['p_status'][ind] == 'OCCUPIED'):
                oc_units += 1
                if ( c_pd['receivable'][ind] > 0 ):
                    cur_rent += c_pd['receivable'][ind]
                if ( c_pd['rent'][ind] > 0 ):
                    rent += c_pd['income'][ind]
                if ( c_pd['balance'][ind] != 0 and not pd.isna(float(c_pd['balance'][ind]))):
                    deliquency += c_pd['balance'][ind]
                if ( c_pd['deposit'][ind] > 0 ):
                    sd_r += c_pd['deposit'][ind]
                if ( c_pd['deposit_a'][ind] > 0 ):
                    sd_a += c_pd['deposit_a'][ind]
            else:
                ot_units += 1
            m_rent += c_pd['market_rent'][ind]
            
        app.logger.debug("trancheAnalytics.10:occupied[%s] vacant[%s] ot[%s] rent[%s] m_rent[%s] sdr[%s] sda[%s] tdate[%s]", oc_units, rr_units,ot_units, rent, m_rent, sd_r, sd_a, core['tdate'])
            
        qry = "select * from pm.tranche_analytics ta where ta.tdate='"+str(tdate) +"' and ta.tranche_id="+str(core['tranche_id']);
        mlist = db1.query_list(qry, None)
        t_count=0
        for x in mlist:
            print("trancheAnalytics:",x)
            t_count=1
        if ( t_count > 0):
            qry = "update pm.tranche_analytics "
            qry += "set oc_units ="+str(oc_units)+ ",rr_units= "+str(rr_units)+ ",ot_units="+str(ot_units) 
            qry += ",expected_rent="+str(m_rent)+",current_rent="+str(cur_rent)+",paid_rent="+str(rent)+",deliquency="+str(deliquency)
            qry += ",sd_r="+str(sd_r)+", sd_a="+str(sd_a)+",updated=now(), updatedby='"+ updatedby +"'"
            qry +=" where tdate='"+ str(tdate) +"' and tranche_id="+str(core['tranche_id']);
        else:
            qry = "INSERT INTO pm.tranche_analytics (tranche_id,tdate,rr_units,oc_units,ot_units,expected_rent,current_rent,paid_rent,deliquency,sd_r, sd_a,updated,updatedby)"
            qry += "VALUES ("+str(core['tranche_id'])+",'"+str(tdate)+"',"+str(rr_units)+","+str(oc_units)+","+str(ot_units)+","+str(m_rent)+","+str(cur_rent)
            qry += ","+str(rent)+","+str(deliquency)+","+ str(sd_r)+","+str(sd_a)+",now(),'"+updatedby +"')"
        app.logger.debug("trancheAnalytics.10: %s", qry)
        mlist = db1.query_list(qry, None)
    except Exception as e:
        app.logger.debug("trancheAnalytics.20: Error in tranche loop: %s", e)

def generateStatements(app, db1,core, tdate):
    app.logger.debug("generateStatements.0:%s %s",tdate,core)

def processTranche(app, db1,action, tdate, company, tranche=""):
    
    qry = " select tr.*, cp.label as company, cp.name as company_name "
    qry += " from pm.tranche tr, pm.company cp "
    qry += " where tr.company_id=cp.company_id and tr.status = 'ACTIVE' "
    if ( company != ""):
        qry += " and cp.label = '"+company+"' "
    if ( tranche != ""):
        qry += " and tr.tranche_id in ("+str(tranche)+")"
    
    i=0
    app.logger.debug("processTranche.1:%s", qry)    
    tc_list = db1.query_list(qry, None)
    
    #print(tc_list)
    for x in tc_list:
        print("Tranche----------------------",x)
        i += 1
        x['action']=action

        if (action == 'ANALYTICS' ):
            trancheAnalytics(app, db1, x, tdate)
        elif (action == 'STATEMENTS' ):
            x['due_date']=tdate
            x['template_file']='HP Tenant Statement.html'
            generateStatements(app,db1, x, tdate)
        else:
            print("Not a valid action")
            
    print("processTranche.10 :Processed :", i)

def findDates(mdate):
    dates={}
    dt = datetime.strptime(mdate, "%Y%m%d").date()
    dates['mon_start'] = dt.replace(day=1).strftime('%Y%m%d')
    dt = dt - timedelta(days=-31)
    dt = dt.replace(day=1)
    dates['mon_end'] = (dt - timedelta(days=1)).strftime('%Y%m%d')

    return dates

def main(argv):
    action='FINANCIALS'
    mode=""
    config_type = platform.system().lower()
    tranche=""
    company=""
    attachment=''
    today =  datetime.today()
    dt = today
    tdate=today.strftime('%Y%m%d')  
    ts=today.strftime('%Y%m%d%H%M')

    hc_home = os.environ.get('HC_HOME','NA')
    hc_config = os.environ.get('HC_CONFIG','NA')
    if ( hc_config == 'NA'):
        hc_config ="./files/pm-conf.json"
    
    print("OS:", os.name, " 2:", platform.system(), " config file:", hc_config)    
    try:
        opts, args = getopt.getopt(argv,"ht:a:c:f:i:m:",["attachment=","action=","company=","tranche_ids=","mode="])
    except getopt.GetoptError:
        print('pm-b-tranche.py -a <STATEMENTS | FINANCIALS | EMAIL | NOTICE> -t <tdate> -c <company name> -f <attachment> -i <tranche ids>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python pm-b-tranche.py -t 2018-11-01 -c HC')
            sys.exit()
        elif opt in ("-t", "--tdate"):
            tdate = arg
        elif opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-a", "--action"):
            action = arg
        elif opt in ("-f", "--attachment"):
            attachment = arg
        elif opt in ("-c", "--company"):
            company = arg
        elif opt in ("-i", "--tranche_id"):
            tranche = arg
    print("Processing for [", action, "]date=", tdate , " company=", company, " tranche=", tranche)
        
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
    app.logger.info("OS: %s  Platform:%s Config:%s db:%s", os.name, platform.system(), hc_config)

    db = PMDB(
        CONFIG["db"]["host"],
        int(CONFIG["db"]["port"]),
        CONFIG["db"]["user"],
        CONFIG["db"]["pass"],
        CONFIG["db"]["schema"],
        app.logger
    )
    
    
    if ( company != "" or tranche != "" ):
        processTranche(app, db,action, tdate, company, tranche)
    else:
        print('pm-b-tranche.py. ERR. Please provide company name, or a tranche info')
    
if __name__ == "__main__":
   main(sys.argv[1:])

print("I am done")