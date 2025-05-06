# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 09:55:27 2020

@author: ppare
"""
from flask import json
import pandas as pd
from utils.pm_db import PMDB
import utils.pm_file


def updateTX(O_db, logger, qj):
    core={}
    debit=0.0
    credit=0.0
    ret = -1
    sqls = ""
    
    qf = fetchTextfromQ(logger, qj,'qualifier')
    tt = fetchTextfromQ(logger,qj,'tx_type')
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)
        #print("pm_tx.updateTX.1:"+x+"="+str(core[x]))
    
    if ( 'tenant_id' not in core):
        core['tenant_id'] = 0;
    if ( 'attachment' not in core):
        core['attachment']=''
    
    logger.info("pm_tx.updateTX.2:%s, %s", tt ,core)

    if ( 'sdate' not in core or core['sdate'] == '' ):
        sqls = 'call updateTransactions (%s,%s,%s,%s, %s,%s,%s,%s,%s,%s, %s,null, %s,%s, %s, %s)'
        try:
            mlist = O_db.query_list(sqls,
                        (core['tx_id'],core['property_id'],core['category_id'],core['tenant_id'],
                        core['tdate'],core['debit'],core['credit'],core['payee'],core['type'],core['reference'],
                        core['description'], core['status'],core['updatedby'],core['invoice'], core['invoice_dt']))
            
            for x in mlist:
                ret = x['@ntx_id']
            logger.info("updateTransactions:2.2:%s[ret:%s]", sqls, ret)
        except ValueError:
            logger.warn("pm_tx::Query Failed:%s", sqls) 
            ret = -1
    else:
        sqls = 'call updateTransactions (%s,%s,%s,%s, %s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s)'
        try:
            mlist = O_db.query_list(sqls,
                        (core['tx_id'],core['property_id'],core['category_id'],core['tenant_id'],
                        core['tdate'],core['debit'],core['credit'],core['payee'],core['type'],core['reference'],
                        core['description'],core['sdate'],core['status'],core['updatedby'],core['invoice'], core['invoice_dt']))
            
            for x in mlist:
                ret = x['@ntx_id']
            logger.info("updateTransactions:3.3:%s[ret:%s]", sqls, ret)
        except ValueError:
            logger.warn("pm_tx::Query Failed:%s", sqls) 
            ret = -1
 
    return ret

def updateTR(O_db, logger, qj):
    core={}
    ret = -1
    sqls = ""
    
    tt = fetchTextfromQ(logger, qj,'tx_type')
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)
    
    if ( 'tenant_id' not in core):
        core['tenant_id'] = 0;
    if ( 'tx_id' not in core):
        core['tx_id'] = 0;

    logger.info("pm_tx.updateTR1: %s",core)
    
    if (tt == 'TENANT_RECEIVABLE' and core['tr_id'] == -1 ):
        sqls = "INSERT INTO `pm`.`tenants_receivable` (`tenant_id`,`category_id`,`property_id`,`tdate`,`description`,`amount`,`updatedby`) "
        sqls += " VALUES (%s,%s,%s,%s,%s, %s,%s) "
        try:
            O_db.insert(sqls,(core['tenant_id'],core['category_id'],core['property_id'],core['tdate'],core['description'],core['amount'], core['updatedby']))
            logger.info("pm_tx.updateTR:3: data updated")
        except ValueError:
            logger.error("pm_tx.updateTR:4:Query Failed:%s", sqls) 
            ret = -1
        
    elif (tt == 'TENANT_RECEIVABLE' and core['tr_id'] != -1 ):
        sqls = "UPDATE pm.tenants_receivable SET category_id=%s,property_id=%s,tenant_id=%s"
        sqls += ", description=%s, amount=%s, updatedby=%s, updated=now(), tdate=%s, tx_id=%s WHERE tr_id=%s"
        try:
            O_db.insert(sqls,(core['category_id'],core['property_id'],core['tenant_id'],core['description'],core['amount'], core['updatedby'] ,core['tdate'],core['tx_id'], core['tr_id']))
            logger.info("pm_tx.updateTR:5: data updated")
        except ValueError:
            logger.warn("pm_tx.updateTR:7:Query Failed: %s", sqls) 
            ret = -1
    else: # new transaction
        logger.info("pm_tx.updateTR.4: Unknown action")
        return ret
    
    logger.info("pm_tx.updateTX:%s",sqls)

    
    if ( core['tr_id'] < 0 ):
        sqls = "select tr_id from pm.tenants_receivable where tdate=%s and category_id=%s and property_id=%s "
        sqls += " and tenant_id=%s and amount=%s and description=%s and updatedby=%s"
        mlist = O_db.query_list(sqls, ( core['tdate'], core['category_id'], core['property_id'], core['tenant_id'], core['amount'], core['description'],core['updatedby']))
        ret= 1
        logger.info("pm_tx.updateTR.6:%s", sqls)
        for x in mlist:
            ret=x['tr_id']
    else:
        ret = core['tr_id']

    return ret


def getTX(db, logger, tt,t_id):
    mdict = {}
    qry = ""
    hist_qry=""
    if ( tt == 'TX' ):
        qry = "call getTransactions ('TX',"+ str(t_id) +")"
        hist_qry = "SELECT * FROM pm.transactions_history WHERE tx_id="+str(t_id)
    elif ( tt == 'STX' ):
        qry = "select t.stx_id, 1 as status, date_format(t.tdate,'%Y-%m-%dT%H:%i:%S') as tdate, t.category_id, t.property_id, t.tenant_id,"
        qry += " t.credit, t.stx_id as tx_id, t.debit,t.payee, t.type, t.reference,t.description,t.updatedby, "
        qry += " date_format(t.updated,'%Y-%m-%dT%H:%i:%S') as updated,  '' as status_label, c.label as category_name, p.label as property_name,"
        qry += " concat(tn.first_name,' ', tn.last_name) as tenant_name "
        qry +=" FROM pm.sd_transactions t, pm.tenants tn,pm.category c, pm.property p where t.category_id=c.category_id and t.property_id=p.property_id and t.tenant_id=tn.tenant_id and t.stx_id=" + str(t_id)
    else:
        qry = "select t.tr_id, 1 as status, date_format(t.tdate,'%Y-%m-%dT%H:%i:%S') as tdate, t.category_id, t.property_id, t.tenant_id,"
        qry += " t.received, t.tx_id, t.amount,'Tenant' as payee, '' as type, '' as reference,t.description,t.updatedby, "
        qry += " date_format(t.updated,'%Y-%m-%dT%H:%i:%S') as updated,  '' as status_label, c.label as category_name, p.label as property_name,"
        qry += " concat(tn.first_name,' ', tn.last_name) as tenant_name "
        qry +=" FROM pm.tenants_receivable t, pm.tenants tn,pm.category c, pm.property p where t.category_id=c.category_id and t.property_id=p.property_id and t.tenant_id=tn.tenant_id and t.tr_id=" + str(t_id)
    
    logger.info("pm_tx_getTX::[%s]:%s",tt, qry)    
    mlist = PMDB.query_list(db,qry, None)
    logger.info("pm_tx_getTX2:%s",mlist) 
    for x in mlist:
        mdict['tx_id']=x['tx_id']
        mdict['tdate']=x['tdate']
        mdict['category_id']=x['category_id']
        mdict['category_name']=x['category_name']
        mdict['property_id']=x['property_id']
        mdict['property_name']=x['property_name']
        mdict['tenant_id']=x['tenant_id']
        mdict['tenant_name']=x['tenant_name']
        mdict['payee']=x['payee']
        mdict['type']=x['type']
        mdict['reference']=x['reference']
        mdict['description']=x['description']
        mdict['status']=x['status']
        mdict['status_label']=x['status_label']
        mdict['updatedby']=x['updatedby']
        mdict['updated']=x['updated']
        if ( tt == 'TX'):
            mdict['debit']=x['debit']
            mdict['credit']=x['credit']
            mdict['sdate']=x['sdate']
            mdict['invoice']=x['invoice']
            mdict['invoice_dt']=x['invoice_dt']
        elif ( tt == 'STX'):
            mdict['debit']=x['debit']
            mdict['credit']=x['credit']
            mdict['tx_id']=x['stx_id']
            mdict['stx_id']=x['stx_id']
        else:
            mdict['tr_id']=x['tr_id']
            mdict['amount']=x['amount']
            mdict['received']=x['received']
    
    qj = {}
    qj['key_type'] = 'TX'
    qj['tx_id'] = t_id
    pd_f = utils.pm_file.getDocuments(db, logger, qj)
    
    if ( pd_f.empty != True ):
            mdict['documents'] = pd_f.to_json(orient='table')
    
    if ( hist_qry != ""):
        mlist = PMDB.query_list(db, hist_qry, None)
        pd_h = pd.DataFrame(mlist)
        if ( pd_h.empty != True ):
            mdict['history'] = pd_h.to_json(orient='table')    
    

    return mdict

def getTXS(O_db, logger, qj):
    core = {}
    qry = ""
    logger.info("pm_tx.getTXS.1:",qj)
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)    
    
    logger.info("pm_tx::getTXS.2=%s", core)

    qry = "SELECT p.property_id, t.category_id, c.label as category_name, p.label,p.group, p.llc, t.tenant_id, t.tx_id, p.label, t.payee, t.debit, t.credit, t.description, "
    qry += "date_format(t.tdate,'%Y-%m-%dT%H:%i:%S') as tdate, date_format(t.sdate,'%Y-%m-%dT%H:%i:%S') as sdate, t.status, t.type, t.reference "
    qry += ", date_format(t.updated,'%Y-%m-%dT%H:%i:%S') as updated, t.updatedby, tch.tranche_name, p.tranche_id "
    qry += "FROM pm.transactions t, pm.property p, pm.category c, pm.tranche tch "
    qry += "WHERE t.property_id=p.property_id and c.category_id = t.category_id and p.tranche_id=tch.tranche_id "
    
    if ( 'property_id' in core and core['property_id'] > 0 ):
        qry += " AND p.property_id =" + str(core['property_id'])
    if ( 'tenant_id' in core and core['tenant_id'] > 0 ):
        qry += " AND t.tenant_id =" + str(core['tenant_id'])    
    if ( 'category_id' in core ):
        qry += " AND t.category_id =" + str(core['category_id'])
    if ( 'status' in core ):
        qry += " AND t.status =" + str(core['status'])
    if ( 'company' in core):
        qry += " AND p.llc = '" + core['company'] + "'"
    if ( 'tranche_id' in core):
        qry += " AND p.tranche_id = " + str(core['tranche_id'])
    if ('group' in core):
        qry += " AND p.group = '" + core['group'] + "'"
        
    if ( core['start_date'] != "" ):  
        qry += " and t.tdate >= '" + core['start_date'] + "' "
    if ( core['end_date'] ):  
        qry += " and t.tdate <= '" + core['end_date'] + "' "
        
    qry += " ORDER BY t.tdate, p.label, t.category_id "
    
    logger.info("pm_tx.getTXS.3:%s", qry)    
    mlist = PMDB.query_list(O_db,qry, None)
    t_pd = pd.DataFrame(mlist)

    return t_pd
    
def getTRS(O_db, logger, qj):
    core = {}
    qry = ""
    logger.debug("pm_tx.getTRS.1:%s",qj)
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)    

    qry = "SELECT tr.tr_id, p.property_id, tr.category_id,p.label,p.group, p.llc, t.tenant_id, tr.tx_id, p.label, c.label as category_name "
    qry += ", concat(t.first_name,' ', t.last_name) as payee, tr.amount as debit, ifnull(tr.received,0.0) as credit, tr.description, date_format(tr.tdate,'%Y-%m-%dT%H:%i:%S') as tdate "
    qry += ", date_format(tr.updated,'%Y-%m-%dT%H:%i:%S') as updated, tr.updatedby, p.tranche_id, tch.tranche_name "
    qry += " FROM pm.tenants t, pm.property p, pm.tenants_receivable tr, pm.category c, pm.tranche tch "
    qry += "WHERE tr.property_id=p.property_id  and tr.tenant_id=t.tenant_id and c.category_id = tr.category_id and p.tranche_id=tch.tranche_id "
    
    if ( 'property_id' in core and core['property_id'] > 0 ):
        qry += " AND p.property_id =" + str(core['property_id'])
    if ( 'tenant_id' in core and core['tenant_id'] > 0 ):
        qry += " AND t.tenant_id =" + str(core['tenant_id'])    
    if ( 'category_id' in core ):
        qry += " AND t.category_id =" + str(core['category_id'])
    
    if ( 'company' in core):
        qry += " AND p.llc = '" + core['company'] + "'"
    if ( 'tranche_id' in core):
        qry += " AND p.tranche_id = " + str(core['tranche_id'])
    if ('group' in core):
        qry += " AND p.group = '" + core['group'] + "'"
        
    if ( core['start_date'] != "" ):  
        qry += " and tr.tdate >= '" + core['start_date'] + "' "
    if ( core['end_date'] ):  
        qry += " and tr.tdate <= '" + core['end_date'] + "' "
        
    qry += " ORDER BY tr.tdate, p.label, tr.category_id "
    
    logger.info("pm_tx.getTRS.3:%s", qry)    
    mlist = PMDB.query_list(O_db,qry, None)
    t_pd = pd.DataFrame(mlist)

    return t_pd

def getTXSDUPS(O_db, logger, qj):

    core = {}
    qry = ""
    start_date="2021-01-01"
    end_date="2021-08-01"
    logger.info("pm_tx.getTXSDUPS.1:",qj)
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)    
    
    logger.info("pm_tx::getTXSDUPS.2=%s", core)

    qry = "SELECT p.property_id, t.category_id, c.label as category_name, p.label,p.group, p.llc, t.tenant_id, t.tx_id, p.label, t.payee, t.debit, t.credit, t.description, "
    qry += "date_format(t.tdate,'%Y-%m-%dT%H:%i:%S') as tdate , t.status "
    qry += "FROM pm.transactions t, pm.property p, pm.category c "
    qry += "WHERE t.property_id=p.property_id and c.category_id = t.category_id "
    
    if ( 'property_id' in core and core['property_id'] > 0 ):
        qry += " AND p.property_id =" + str(core['property_id'])
    if ( 'tenant_id' in core and core['tenant_id'] > 0 ):
        qry += " AND t.tenant_id =" + str(core['tenant_id'])    
    if ( 'category_id' in core ):
        qry += " AND t.category_id =" + str(core['category_id'])
    if ( 'status' in core ):
        qry += " AND t.status =" + str(core['status'])
    if ( 'company' in core):
        qry += " AND p.llc = '" + core['company'] + "'"
    
    if ('group' in core):
        qry += " AND p.group = '" + core['group'] + "'"
        
    qry += " and t.tdate between '" + start_date + "' and '" + end_date + "' "
        
    qry += " ORDER BY t.tdate, p.label, t.category_id "
    
    logger.info("pm_tx.getTXSDUPS.3:%s", qry)    
    mlist = PMDB.query_list(O_db,qry, None)
    t_pd = pd.DataFrame(mlist)

    return t_pd

########################################################## General #####################
   
def fetchNumberfromQ(logger, qj, val):
    lv=0
    if ( val in qj):
        try:
            lv = qj[val]
        except ValueError:
            logger.warn("VE2=Not found %s %s", val, qj[val])
        except AttributeError:
            logger.warn("AE2=Not found %s %s", val, qj[val])
    return lv  

def fetchTextfromQ(logger, qj, val):
    lv=""
    if ( val in qj):
        try:
            lv = qj[val]
        except ValueError:
            logger.warn("Not Found: %s", val)
    if ( lv == None ):
        lv = ""
    else:
        try:
            lv = lv.strip()
        except AttributeError:
            logger.warn("No Action: %s", val)
        
        
    return lv
