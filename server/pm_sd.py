# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 10:15:27 2020
Security Deposit
@author: ppare
"""
from flask import json
import pandas as pd
from utils.pm_db import PMDB
import utils.pm_file


def updateSTX(O_db, logger, qj):
    core={}
    debit=0.0
    credit=0.0
    ret = -1
    sqls = ""
    
    qf = fetchTextfromQ(qj,'qualifier')
    tt = fetchTextfromQ(qj,'tx_type')
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)
    logger.debug("pm_sd.updateSTX.1:%s",core)
    
    if ( 'tenant_id' not in core):
        return -1
    
    if ( 'debit' in core and core['debit']!= ''):
        debit=core['debit']
    if ( 'credit' in core or core['credit']!= ''):
        credit=core['credit']

    logger.debug("pm_sd.updateSTX.2: type=%s|stx_id=%s|credit=%s|debit=%s", tt ,core['stx_id'],credit,debit)
    # SP call, need to fix python to make this work.
    #sqls = "CALL updateTransactions ("+str(core['tx_id'])+","+str(core['property_id'])+","+str(core['category_id']) +","+ str(core['tenant_id'])
    #sqls += ",'"+ core['tdate'] +"',"+str(debit) +","+ str(credit) +",'"+ core['payee'] +"','"+core['type'] + "','" + core['reference']
    #sqls += "','" + core['description']+"','"+core['attachment']+"','"+core['updatedby']+"')"
    
    if ( core['stx_id'] > 0 and qf == 'UPDATE'):
        sqls="UPDATE pm.sd_transactions SET category_id="+ str(core['category_id']) + ",property_id=" + str(core['property_id']) + ",tenant_id=" + str(core['tenant_id'])
        sqls += ",payee='"+ core['payee'] + "', type = '" + core['type'] + "', reference='"+ core['reference'] + "', debit=" + str(debit) + ", credit="+str(credit)
        sqls += ",description='" + core['description'] + "', tdate='" +core['tdate'] + "'"
        sqls += ", updatedby = '" + core['updatedby'] + "', updated = now() , sdate='"+core['sdate']+"', status="+ str(core['status'])
        sqls += " WHERE stx_id="+str(core['stx_id'])
        qf="UPDATE"
    elif ( core['stx_id'] == -1):    
        qf="NEW"
        sqls="INSERT INTO `pm`.`sd_transactions` (`tdate`,`category_id`,`property_id`,`tenant_id`,`payee`,`type`,`reference`,`debit`,`credit`,`description`,`updatedby`) "
        sqls += "VALUES ('" + core['tdate'] + "',"+ str(core['category_id']) + "," + str(core['property_id']) + "," + str(core['tenant_id']) + ",'" + core['payee'] + "','" 
        sqls += core['type'] + "','"+ core['reference'] + "'," + str(debit) + ","+str(credit) +",'" + core['description'] + "','"
        sqls += core['updatedby'] + "')"
    
    else: # new transaction
        logger.debug("pm_sd.updateSTX.3: Unknown action")
        return ret
    
    logger.debug("pm_sd.updateSTX:4[%s] %s", qf,sqls)

    try:
        O_db.insert(sqls,None)
        logger.debug("pm_sd.updateSDTX.5:: data updated:%s", sqls)
        if ( qf == "NEW"):
            sqls = "select stx_id from pm.sd_transactions where tdate='"+core['tdate']+"' and category_id="+ str(core['category_id']) + " and property_id= "
            sqls += str(core['property_id']) + " and tenant_id=" + str(core['tenant_id']) + " and payee='" + core['payee'] + "' and type='" 
            sqls += core['type'] + "' and reference='"+ core['reference'] + "' and debit=" + str(debit) + " and credit="+str(credit) 
            sqls +=" and description='" + core['description'] + "' and updatedby='"+ core['updatedby'] +"'"
            logger.debug("pm_update.updateSTX.6:%s", sqls)
            mlist = PMDB.query_list(O_db,sqls, None)
            ret= 1
            for x in mlist:
                ret=x['stx_id']
        else:
            ret = core['stx_id']
    except ValueError:
        logger.debug("pm_sd.updateSTX::Query Failed:%s",sqls) 
        ret = -1
      
    return ret

def getSTX(db, logger,tt,t_id):
    mdict = {}
    qry = ""
    if ( tt == 'STX' ):
        qry = "SELECT stx_id, date_format(tdate,'%Y-%m-%dT%H:%i:%S') as tdate, category_id, property_id, ifnull(tenant_id,-1) as tenant_id, payee, type, reference, debit, credit,"
        qry += "description, updatedby, date_format(updated,'%Y-%m-%dT%H:%i:%S') as updated,date_format(sdate,'%Y-%m-%dT%H:%i:%S') as sdate, status "
        qry += " FROM pm.sd_transactions where stx_id=" + str(t_id)

    
    logger.debug("pm_sd.getSTX::[%s]:%s", tt,qry)    
    mlist = PMDB.query_list(db,qry, None)

    for x in mlist:
        mdict['stx_id']=x['stx_id']
        mdict['tdate']=x['tdate']
        mdict['category_id']=x['category_id']
        mdict['property_id']=x['property_id']
        mdict['tenant_id']=x['tenant_id']
        mdict['payee']=x['payee']
        mdict['type']=x['type']
        mdict['reference']=x['reference']
        mdict['description']=x['description']
        mdict['updatedby']=x['updatedby']
        mdict['updated']=x['updated']
        mdict['sdate']=x['sdate']
        mdict['status']=x['status']
        if ( tt == 'STX'):
            mdict['debit']=x['debit']
            mdict['credit']=x['credit']

    
    qj = {}
    qj['key_type'] = 'STX'
    qj['stx_id'] = t_id
    pd_f = utils.pm_file.getDocuments(db, None, qj)
    
    if ( pd_f != None and pd_f.empty != True ):
            mdict['documents'] = pd_f.to_json(orient='table')
    
    return mdict

def getSTXS(O_db, logger, qj):
    core = {}
    qry = ""
    logger.debug("pm_sd.getSDTX.1:%s",qj)
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)    
    

    qry = "SELECT p.property_id, t.category_id,p.label,p.group, p.llc, t.tenant_id, t.stx_id, p.label, t.payee, t.debit, t.credit, t.description, "
    qry += "t.type, t.reference, date_format(t.tdate,'%Y-%m-%dT%H:%i:%S') as tdate, t.updatedby, date_format(t.updated,'%Y-%m-%dT%H:%i:%S') as updated, "
    qry += "date_format(t.sdate,'%Y-%m-%dT%H:%i:%S') as sdate, t.status, tch.tranche_name, p.tranche_id "
    qry += "FROM pm.sd_transactions t, pm.property p, pm.tranche tch "
    qry += "WHERE t.property_id=p.property_id and p.tranche_id=tch.tranche_id "
    
    if ( 'property_id' in core and core['property_id'] > 0 ):
        qry += " AND p.property_id =" + str(core['property_id'])
    if ( 'tenant_id' in core and core['tenant_id'] > 0 ):
        qry += " AND t.tenant_id =" + str(core['tenant_id'])    
    if ( 'category_id' in core ):
        qry += " AND t.category_id =" + str(core['category_id'])
    
    if ( 'company' in core):
        qry += " AND p.llc = '" + core['company'] + "'"
    
    if ('group' in core):
        qry += " AND p.group = '" + core['group'] + "'"
        
    if ( 'start_date' in core and core['start_date'] != "" ):  
        qry += " and t.tdate >= '" + core['start_date'] + "' "
    if ( 'end_date' in core and core['end_date'] ):  
        qry += " and t.tdate <= '" + core['end_date'] + "' "
        
    qry += " ORDER BY t.tdate, p.label, t.category_id "
    
    logger.debug("pm_sd.getSTXS.3:%s", qry)    
    mlist = PMDB.query_list(O_db,qry, None)
    t_pd = pd.DataFrame(mlist)

    return t_pd
    

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