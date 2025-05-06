# -*- coding: utf-8 -*-
"""
Created on Tue Seo 13 15:04:13 2020

@author: ppare
"""
import traceback
from flask import json
import pandas as pd
from utils.pm_db import PMDB
import utils.pm_file

def getInvestors(db, logger, qj):
    mdict = {}
    core = qj['params']
    qry = "select * from pm.investor "

    if ( 'company_id' in core and core['company_id'] > 0 ):
        qry += " where company_id =" + str(core['company_id'])
    
    logger.debug("pm_investor.getInvestors:: %s", qry)    
    mlist = PMDB.query_list(db,qry, None)
    t_pd = pd.DataFrame(mlist)

    return t_pd


def getInvestor(db, logger, qj):
    mdict = {}
    core = qj['params']

    qry = "select * from pm.investor where investor_id =" + str(core['investor_id'])
    logger.debug("pm_investor.getInvestor:1: %s", qry)    
    mlist = PMDB.query_list(db,qry, None) 
    for x in mlist:
        mdict=x

    qry = "SELECT inf.investor_id, inf.company_id, c.label  as company_label, c.legal_name, inf.equity, inf.balance, inf.last_payment, inf.payment_due, "
    qry += "ifnull(date_format(inf.payment_due_date,'%Y-%m-%d'),'') as payment_due_date, ifnull(date_format(inf.last_payment_date,'%Y-%m-%d'),'') as last_payment_date, "
    qry += "ifnull(date_format(inf.join_date,'%Y-%m-%d'),'') as join_date, ifnull(inf.notes,'') as notes, inf.updatedby, date_format(inf.payment_due_date,'%Y-%m-%dT%H:%M:%S') as updated "
    qry +=" FROM pm.investor_financials inf, pm.company c "
    qry += " WHERE inf.company_id = c.company_id and inf.investor_id =" + str(core['investor_id'])
    logger.debug("pm_investor.getInvestor:2: %s", qry)    
    tlist = PMDB.query_list(db,qry, None) 
    t_pd = pd.DataFrame(tlist)

    if ( t_pd.empty ):
        mdict['financials']=""
    else:
        mdict['financials'] = t_pd.to_json(orient='table')

    qj = {}
    qj['key_type'] = 'INVESTOR'
    qj['investor_id'] = core['investor_id']
    pd_f = utils.pm_file.getDocuments(db, logger, qj)

    if ( pd_f.empty ):
        mdict['documents']=""
    else:
        mdict['documents'] = pd_f.to_json(orient='table')

    return mdict

def updateInvestor(O_db, logger, qj):
    core = {}
    t_id=-999
    ret={}
    ret['message']="no actions"
    ret['code']=-1
    sqls = ""
    qf = 'UPDATE'

    logger.debug("pm_investor::updateInvestor:%s",qj)
    
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)    
    if ( 'investor_id' in core ):
            t_id=int(core['investor_id'])
    
    for x in core:
        logger.debug("pm_investor::updateInvestor1=%s [%s]", x, core[x])
    ret['investor_id']=t_id

    if (t_id < 0) :
        
        fieldList = ['address1','address2','city','zip','state','email','phone','account','note']
        for x in fieldList:
            if( x not in core ):
                core[x]=''
        logger.debug("pm_investor.updateinvestor:: new investor id=%s",core)

        try:
            mlist = O_db.query_list('call updateInvestor (-1,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s)',
                    (core['name'],core['legal_name'],core['label'],core['address1'],core['address2'], core['city'],core['state'],core['zip'],
                    core['tax_id'], core['phone'], core['email'], core['account'], 
                    core['note'],core['status'], core['user_id'] ))
        
            for x in mlist:
                logger.debug("pm_investor.updateinvestor:%s",x)
                ret['investor_id']=x['investor_id']
            ret['message']="investor creation successful"
            ret['code']=0
        except Exception as e:
            logger.error("pm_investor.updateinvestor: investor creation failed:%s", e);
            ret['message']=traceback.format_exc()
            ret['code']=-1
        
        return(ret)
        
    elif ( t_id > 0 ) :
        
        logger.debug("pm_investor.updateinvestor::PRIMARY[%s]",t_id)
        try:
            mlist = O_db.query_list('call updateInvestor (%s,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s)',
                    (t_id,core['name'],core['legal_name'],core['label'],core['address1'],core['address2'], core['city'],core['state'],core['zip'],
                    core['tax_id'], core['phone'], core['email'], core['account'], 
                    core['note'],core['status'], core['user_id'] ))
            for x in mlist:
                #logger.debug("pm_investor.updateinvestor:%s",x)
                t_id=x['investor_id']
            ret['message']="investor update successful"
            ret['code']=0
        except Exception as e:
            logger.error("pm_investor.updateinvestor: investor update failed:%s", e);
            ret['message']=traceback.format_exc()
            ret['code']=-1
        
        return(ret)

    return(ret)


def investorHistory(O_db, logger, core):
    logger.debug("investorHistory.0:%s", core)
    sqls = "INSERT INTO pm.investors_history(`investor_id`,`title`,`comments`,`updatedby`) VALUES(%s,%s,%s,%s)"
    ret=0
    
    try:
         logger.debug("investorHisotry.1:%s", sqls)
         mlist = O_db.query_list(sqls,(core['investor_id'], core['title'], core['comments'], core['updatedby']))
         ret=1
    except:
         logger.error("investorHistory2: investor history update failed");
         ret=-1
        
        
    return ret;


def verifyFile(O_db, logger, qj):
    logger.debug("pm_investor::verifyFile: %s", qj)
    if ( qj['user_id'] == 1):
        return 1
    
    sqls = " select count(*) as docs from pm.investor_docs i where i.investor_id=%s and i.doc_id=%s"
    mlist = O_db.query_list(sqls, (qj['investor_id'], qj['doc_id']));
    docs = mlist[0]['docs']

    logger.debug("pm_investor::verifyFile:[%s] %s",docs, sqls)

    return docs
                    

def updateITX(O_db, logger, qj):
    core={}
    debit=0.0
    credit=0.0
    sqls = ""
    ret ={}
    ret['status']='Failure'
    ret['code']=1
    ret['itx_id']='-1'


    
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)
        #print("pm_tx.updateTX.1:"+x+"="+str(core[x]))
    if ( 'itx_id' not in core or core['itx_id'] == ''):
        core['itx_id']=-1
    logger.debug("pm_tx.updateTX.2: %s",core)
    
    try:
        mlist = O_db.query_list('call updateITransactions (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (core['itx_id'],core['investor_id'],core['category_id'],core['company_id'],
                    core['tdate'],core['debit'],core['credit'],core['payee'],core['type'],core['reference'],
                    core['description'],core['updatedby']))
        logger.debug("updateTransactions:2.2:%s", mlist)
        ret['itx_id'] = mlist[0]['@ntx_id']
        ret['status']='Success'
        ret['code']=0
    except Exception as e:
        logger.error("pm_tx::Query Failed: %s", e) 
        ret['message']='DB Query Failed'
 
    return ret


def getITX(db,logger, qj):
    mdict = {}
    core = qj['params']
    logger.debug("pm_investor.getITX:1: %s", core)  
    qry = "select itx_id, date_format(it.tdate,'%Y-%m-%dT%H:%i:%S') as tdate, it.category_id, "
    qry += "it.investor_id,  it.company_id, it.payee, it.type, it.reference, it.debit, it.credit, it.balance,"
    qry += "it.description, it.updatedby, date_format(it.updated,'%Y-%m-%dT%H:%i:%S') as updated  "
    qry += " FROM pm.investor_transactions it WHERE "

    if( 'itx_id' in core and core['itx_id'] > 0 ):
        qry += " it.itx_id ="+str(core['itx_id'])
    else:
        return mdict 

    logger.debug("pm_investor.getITX:2: %s", qry)  
    mlist = PMDB.query_list(db,qry,None) 

    for x in mlist:
        mdict['itx_id']=x['itx_id']
        mdict['tdate']=x['tdate']
        mdict['category_id']=x['category_id']
        mdict['company_id']=x['company_id']
        mdict['investor_id']=x['investor_id']
        mdict['payee']=x['payee']
        mdict['type']=x['type']
        mdict['reference']=x['reference']
        mdict['description']=x['description']
        mdict['updatedby']=x['updatedby']
        mdict['updated']=x['updated']
        mdict['debit']=x['debit']
        mdict['credit']=x['credit']
        mdict['amount']=x['balance']

    qj = {}
    qj['key_type'] = 'ITX'
    qj['itx_id'] = core['itx_id']
    pd_f = utils.pm_file.getDocuments(db, None, qj)

    if ( pd_f == None or pd_f.empty ):
        mdict['documents'] = ""
    else:
        mdict['documents'] = pd_f.to_json(orient='table')

    return mdict

def getITXS(db, logger, qj):
    core = qj['params']
    qry = ""
    logger.debug("pm_tx.getTXS.1:",qj)
    
    for x in core:
        logger.debug("pm_investor::getITXS.2[%s]=%s", x, core[x])

    qry = "SELECT c.company_id, it.category_id,c.label as company_label, c.name as company_name,it.investor_id, it.itx_id, it.payee, it.debit, it.credit,it.balance, it.description, "
    qry += "date_format(it.tdate,'%Y-%m-%dT%H:%i:%S') as tdate "
    qry += "FROM pm.investor_transactions it, pm.company c "
    qry += "WHERE it.company_id=c.company_id "
    if ( 'investor_id' in core and int(core['investor_id']) > 0 ):
        qry += " AND it.investor_id =" + str(core['investor_id'])    
    if ( 'category_id' in core ):
        qry += " AND it.category_id =" + str(core['category_id'])
    
    if ( 'company_id' in core):
        qry += " AND it.company_id = " + str(core['company_id'])
        
    if ( 'start_date' in core and core['start_date'] != "" ):  
        qry += " and it.tdate >= '" + core['start_date'] + "' "
    if ( 'end_date' in core and core['end_date'] ):  
        qry += " and it.tdate <= '" + core['end_date'] + "' "
    
        
    qry += " ORDER BY it.tdate, it.category_id "
    
    logger.debug("pm_investor.getITXS.3: %s", qry)    
    mlist = PMDB.query_list(db,qry, None)
    t_pd = pd.DataFrame(mlist)

    lb = 0.0
    for ind in t_pd.index:
            lb = t_pd.at[ind,'credit'] - t_pd.at[ind,'debit'] + lb
            t_pd.at[ind,'balance'] = lb
        #self.logger.debug("PMTenant::updateFTS: %s", l_pd);        
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