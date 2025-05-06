# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 20:51:10 2020

@author: ppare
"""

import pandas as pd
from datetime import datetime

from utils.pm_db import PMDB

def get_util_outliers(db,logger, qj):
    
    core = {}
    period=75
    print("pm_analysis.get_util_outliers.1:",qj)
    qj['stats']=1
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)    
    
    for x in core:
        print("pm_analysis.get_util_outliers.2=", x, "=", core[x])
    
    if ( 'period' in core):
        period = core['period']
        
    if ( core['tdate'] == None or core['tdate'] == ''):
        core['tdate'] = datetime.today().strftime('%Y-%m-%d')
    
    qry = "SELECT t.first_name,t.last_name,t.email, t.phone, pc.name as company, tf.balance, tf.last_payment_date,tf.last_payment, "
    qry += "tc.tenancy_id, t.tenant_id, p.property_id, pc.company_id "
    qry += "FROM pm.tenants t, pm.property p, pm.tenancy tc, pm.company pc , pm.tenants_financials tf "
    qry += "WHERE p.property_id > 0 and t.tenant_id = tc.tenant_id and p.property_id = tc.property_id "
    qry += "and tc.tenant_id = tf.tenant_id and p.llc=pc.label "
    qry += "and t.status=1 and tc.status in (1,4,5) "
    qry += "order by tf.balance asc"
        
    print("pm_analysis.get_util_outliers.3:", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    
    return t_pd

def get_deliquencies(db,logger, qj):
    
    core = {}
    period=75
    print("pm_analysis.get_deliquencies.1:",qj)
    qj['stats']=1
    user_id=-1
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)    
    
    if ( 'user_id' in qj ):
        user_id=int(qj['user_id'])
    
    qry = "SELECT t.first_name,t.last_name,t.email, t.phone, pc.name as company, tf.balance, date_format(tf.last_payment_date,'%Y-%m-%d') as last_payment_date,tf.last_payment, "
    qry += "p.label, tc.tenancy_id, t.tenant_id, p.property_id, pc.company_id "
    qry += "FROM pm.tenants t, pm.property p, pm.tenancy tc, pm.company pc , pm.tenants_financials tf "
    if ( user_id > 0 ):
        qry +=", pm.auth_users_attributes aua where p.property_id > 0 and aua.id_type='property_id' and aua.id_value = p.property_id and aua.user_id ="+str(user_id)
    else:
        qry +=" WHERE p.property_id > 0 "
    
    qry += " and tf.balance < 0 and t.tenant_id = tc.tenant_id and p.property_id = tc.property_id "
    qry += "and tc.tenant_id = tf.tenant_id and p.llc=pc.label "
    qry += "and t.status=1 and tc.status in (1,4,5) "


    qry += "order by tf.balance asc"
        
    print("pm_analysis.get_deliquencies.3:", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    
    return t_pd

def get_upcoming_tenancy(db,logger, qj):
    
    core = {}
    period=75
    logger.debug("pm_analysis.get_upcoming_tenancy.1: %s",qj)
    qj['stats']=1
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)    
    
    for x in core:
        logger.debug("pm_analysis.get_upcoming_tenancy.2=%s = %s", x,core[x])
    
    if ( 'period' in core):
        period = core['period']
        
    if ( 'tdate' not in core or core['tdate'] == ''):
        core['tdate'] = datetime.today().strftime('%Y-%m-%d')
    
    qry = "select p.property_id, p.label, p.llc, p.group, tc.tenancy_id, date_format(tc.start_date,'%Y-%m-%d') as start_date, date_format(tc.end_date,'%Y-%m-%d') as end_date,"
    qry += " DATEDIFF(tc.end_date, now()) as diff,tc.rent, tc.deposit, t.tenant_id, t.first_name, t.last_name, date_format(tc.move_in,'%Y-%m-%d') as move_in, date_format(tc.move_out,'%Y-%m-%d') as move_out "
    qry += " from pm.tenancy tc, pm.property p, pm.tenants t "
    qry += " where p.property_id = tc.property_id and tc.tenant_id = t.tenant_id and tc.status = 1 "
    qry += " and tc.end_date < DATE_ADD('" + core['tdate'] + "', INTERVAL " + str(period) + " DAY) "
    qry += " order by tc.end_date desc, tc.rent desc "
        
    logger.debug("pm_analysis.get_upcoming_tenancy.3:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    
    return t_pd

### Time series
def get_property_ts_pd(db,logger, pid, cid, sd, ed ):
    
    qry = "SELECT date_format(t.tdate,'%Y-%m-%d') as tdate, t.value "
    qry += "FROM pm.property_ts t "
    qry += " WHERE t.property_id="+str(pid) + " AND t.category_id=" +str(cid )
    qry += " AND t.tdate between '" + sd + "' AND '" + ed + "'"
    qry += " ORDER BY t.tdate "
        
    print("pm_analysis.get_property_ts_pd::", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    
    #t_pd = t_pd.rename(columns={0:'tdate',1:'value'})
    #t_pd = t_pd.set_index('tdate')
    
    print(t_pd)
    
    return t_pd
    
def getTS(O_db, logger, qj):
    core = {}
    c_pd = pd.DataFrame()
    m = 0
    
    print("pm_analysis.getTS.1:",qj)
    qj['stats']=1
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)    
    
    for x in core:
        print("pm_analysis::getTS.2=", x, "=", core[x])
    if ( 'category_id' in core):
        c_id = core['category_id']
        
    elif ( 'category_ids' in core):
        t = core['category_ids']
        print("pm_analysis.getTS.21=", t)
        c_ids = t.split(',')
        c_id = c_ids[0] # pick first one, will do multiple categories later
        
    else:
        return c_pd
    
    c_pd = get_property_ts_pd(O_db, logger, core['property_id'],c_id,core['start_date'],core['end_date'])
    
    if ( qj['stats'] != None and qj['stats'] == 1 and c_pd.empty != True):
        c_pd["mean"] = c_pd["value"].mean()
        c_pd["median"] = c_pd["value"].median()
        c_pd["low"] = c_pd["value"].min()
        c_pd["high"] = c_pd["value"].max()
        c_pd["sum"] = c_pd["value"].sum()
        c_pd["std"] = c_pd["value"].std()
        
    return c_pd
    
# -------------------------------------------------------------------------------
def fetchTextfromQ(qj, val):
    lv=""
    if ( val in qj):
        try:
            lv = qj[val]
        except ValueError:
            print(val + ": Not found")
    if ( lv == None ):
        lv = ""
    else:
        try:
            lv = lv.strip()
        except AttributeError:
            print(val + ": No Action..")
        
        
    return lv

def getSTATS(c_pd, ts):
    if ( ts == None or ts == ""):
        ts = "value"
    stats = {}
    stats["mean"] = c_pd[ts].mean()
    stats["median"] = c_pd[ts].median()
    stats["min"] = c_pd[ts].min()
    stats["max"] = c_pd[ts].max()
    stats["sum"] = c_pd[ts].sum()
    stats["std"] = c_pd[ts].std()
    
    return stats