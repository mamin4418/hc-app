# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 08:51:46 2019
Cashflow
@author: ppare
"""
import pandas as pd
from datetime import datetime

import ref_data
from utils.pm_db import PMDB
import utils.pm_file

def getTrancheList( db, logger, core):
        
    qry = ""
    attr_pd = None
    mlist={}
    
    logger.debug("pgetTranchList:1:%s", core)
    qry = " SELECT c.*, c1.label "
    qry += " from pm.tranche c, pm.company c1, pm.auth_users_attributes aua where aua.id_type= 'company_id' and aua.id_value=c.company_id "
    qry += " and c.company_id = c1.company_id and aua.user_id="+str(core['user_id'])
    qry += " order by c.tranche_name"
    
    logger.debug("pm_tranche:getTranchList:Query1:%s", qry)
    mlist = PMDB.query_list(db,qry, None)
    
    attr_pd = pd.DataFrame(mlist)
    
    logger.debug("getTrancheList:%s", attr_pd)

    return attr_pd

def getLoanList( db, logger, core):
        
    qry = ""
    attr_pd = None
    mlist={}
    
    logger.debug("pgetTranchList:1:%s", core)
    qry = " SELECT c.*, c1.label as company_name, t.tranche_name, t.company_id from pm.tranche_loan c, pm.tranche t, pm.company c1, pm.auth_users_attributes aua where aua.id_type= 'company_id' "
    qry += " and aua.id_value=t.company_id and c.tranche_id = t.tranche_id and t.company_id = c1.company_id and aua.user_id="+str(core['user_id'])
    
    logger.debug("pm_tranche:getLoanList:Query1:%s", qry)
    mlist = PMDB.query_list(db,qry, None)
    
    attr_pd = pd.DataFrame(mlist)
    
    logger.debug("getLoanList:%s", attr_pd)

    return attr_pd

def updateTranche(db, logger, core):
    r ={}
    r['status']='Failure'
    r['message']='Request failed'
    r['tranche_id']='-1'
    r['code']=1

    logger.debug("updateTranche:%s", core)

    try:
        sqls = "UPDATE pm.tranche SET tranche_name=%s, company_id=%s, purchase_date=%s, purchase_price=%s,"
        sqls += " closing_cost=%s, total_cost=%s, `current_date`=%s, current_price=%s , notes=%s, "
        sqls += " sell_date=%s, sell_price=%s, sell_cost=%s, status=%s, updatedby=%s, updated=now() "
        sqls += " WHERE tranche_id=%s"
        mlist = PMDB.query_list(db,sqls,(core['tranche_name'],core['company_id'],core['purchase_date'],core['purchase_price'], 
            core['closing_cost'],core['total_cost'],core['current_date'], core['current_price'],core['notes'],
            core['sell_date'],core['sell_price'],core['sell_cost'],core['status'], core['updatedby'],
            core['tranche_id']))
    
        
        logger.debug("updateTranche:: %s",sqls)

        r['status']='Success'
        r['code']=core['tranche_id']
        r['tranche_id']=core['tranche_id']
        r['message']="Tranche "+ core['tranche_name'] + " updated."
    
    except Exception as e:
        logger.error("pm_tranche.updateTranche.10:Failed: %s", str(e)) 
        r['code']=-1
        r['message']=str(e)
    

    return r


def getTrancheAnalytics( db, logger, core):
        
    qry = ""
    a_pd = None
    mlist={}
    
    logger.debug("pgetTranchList:1:%s", core)
    qry = "SELECT c.*, c1.label as company_label, date_format(ta.tdate,'%Y-%m-%d') as tdate, ta.rr_units, ta.oc_units, ta.ot_units, ta.expected_rent, ta.current_rent, ta.paid_rent, ta.deliquency, ta.sd_r, ta.sd_a, date_format(ta.updated,'%Y-%m-%dT%H:%i:%S') as updated, ta.updatedby as updatedby "
    qry += " from pm.tranche c, pm.company c1, pm.tranche_analytics ta, pm.auth_users_attributes aua where aua.id_type= 'company_id' and aua.id_value=c.company_id "
    qry += " and ta.tranche_id = c.tranche_id and c.company_id = c1.company_id and aua.user_id="+str(core['user_id'])

    if ( 'company_id' in core and core['company_id'] != ''):
        qry += " and c.company_id="+str(core['company_id'])
    if ( 'tranche_id' in core and core['tranche_id'] != ''):
        qry += " and c.tranche_id="+str(core['tranche_id'])
    if ( 'start_date' in core and core['start_date'] != ''):
        qry += " and ta.tdate >='"+ core['start_date'] +"'"
    if ( 'end_date' in core and core['end_date'] != ''):
        qry += " and ta.tdate <='"+ core['end_date'] +"'"
    qry += " order by c.tranche_id, ta.tdate "

    logger.debug("pm_tranche:getTranchList:Query1:%s", qry)
    mlist = PMDB.query_list(db,qry, None)
    
    a_pd = pd.DataFrame(mlist)
    
    logger.debug("getTrancheList:%s", a_pd)

    return a_pd


def getLTTXS(db, logger, qj):
    mdict = {}
    sqls = ""
    
    sqls = "SELECT tx.tx_id, date_format(tx.tdate,'%Y-%m-%d') as tdate, tx.category_id "
    sqls += ", tx.tranche_id, tx.loan_id, tx.payee, tx.type, tx.reference "
    sqls += ", tx.payment, tx.interest, tx.principal, tx.description, tx.status "
    sqls += ", tx.updatedby, tx.updated"
    sqls += " FROM pm.tranche_loan_tx tx "
    sqls += " WHERE tx.payment > 0 and tx.tranche_id in ("+ str(qj['tranche_id'])   + ") order by tx.tdate"
    logger.info("getLTTXS::[%s]:%s",qj, sqls)    
    mlist = PMDB.query_list(db,sqls, None)

    
    mdict['data']=mlist
    
    return mdict

def getLTTX(db, logger, qj):
    mdict = {}
    sqls = ""
    
    sqls = "SELECT tx.tx_id, date_format(tx.tdate,'%Y-%m-%d') as tdate, tx.category_id "
    sqls += ", tx.tranche_id, tx.loan_id, tx.payee, tx.type, tx.reference "
    sqls += ", tx.payment, tx.interest, tx.principal, tx.description, tx.status "
    sqls += ", tx.updatedby, tx.updated"
    sqls += " FROM pm.tranche_loan_tx tx "
    sqls += " WHERE tx.tx_id = "+ str(qj['tx_id'])    
    logger.info("getLTTX::[%s]:%s",qj, sqls)    
    mlist = PMDB.query_list(db,sqls, None)

    for x in mlist:
        mdict['data']=x
    
    qj1 = {}
    qj1['key_type'] = 'LTTX'
    qj1['tx_id'] = qj['tx_id']
    pd_f = utils.pm_file.getDocuments(db, logger, qj1)
    
    if ( pd_f != None and pd_f.empty != True ):
            mdict['data']['documents'] = pd_f.to_json(orient='table')
    
    return mdict

def updateLTTX(O_db, logger, qj):
    core={}
    debit=0.0
    tx_id=-1;
    ret = -1
    sqls = ""
    
    for x in qj:
        core[x] = qj[x]
        #print("pm_tx.updateTX.1:"+x+"="+str(core[x]))
    if ('tx_id' in core ):
        tx_id=int(core['tx_id'])

    sqls = 'call updateLTransactions (%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s)'
    try:
        mlist = O_db.query_list(sqls,
                    (tx_id,core['loan_id'],core['tranche_id'], core['category_id'], core['tdate'],core['payment'],
                    core['interest'],core['principal'], core['payee'],core['type'],core['reference'],
                    core['description'],core['status'],core['updatedby']))
        for x in mlist:
            ret = x['@ntx_id']
        logger.info("updateLTTX:2.2:%s[ret:%s]", sqls, ret)
    except ValueError:
        logger.warn("updateLTTX::Query Failed:%s", sqls) 
        ret = -1
 
    resp={}
    resp['data']={}
    resp['data']['tx_id']=ret
    return resp

class PMTranche:
    
    def __init__(self, db, logger, tid, qj):
        today = datetime.today()
        self.tranche_id = tid
        self.d2 = today.strftime('%Y-%m-%d')
        self.d1 = self.d2
        self.p_id = -1
        self.company = "HC"
        self.group = ""
        self.logger = logger
        self.core = {}
        self.loan_pd = pd.DataFrame()
        self.c_pd = pd.DataFrame()
        self.t_pd = pd.DataFrame()
        self.t_dict = {}
        self.stats = {}
        self.fetchParams( qj)
        self.updateTInfo( db)
        self.my_categories = ref_data.get_my_categories_by_id(db, self.logger, None)

    def updateTInfo(self, db):
        mlist={}
        data={}

        qry = " SELECT * from pm.tranche where tranche_id= " + str(self.tranche_id)
        
        self.logger.debug("getTranche:Query1: %s", qry)
        mlist = PMDB.query_list(db,qry, None)

        for x in mlist:
            self.core=x

        qry = "SELECT * from pm.tranche_loan where tranche_id= " + str(self.tranche_id)

        self.logger.debug("getTranche:Query4: %s", qry)
        mlist = PMDB.query_list(db,qry, None)

        self.loan_pd = pd.DataFrame(mlist)
        

    def getTInfo(self):

        self.core['loans'] = self.loan_pd.to_json(orient='table')
        
        self.logger.debug("getTInfo: %s", self.core)        

        return self.core


            
# creates cashflow table by time period, Month 1, Month 2, Month 3.. Total    
    def updateTS(self, db):
             
        t_dict = {}

        sqls = "SELECT tx.tx_id, date_format(tx.tdate,'%Y-%m-%d') as tdate, tx.category_id "
        sqls += ", tx.tranche_id, tx.loan_id, tx.payee, tx.type, tx.reference "
        sqls += ", tx.payment, tx.interest, tx.principal, tx.description, tx.status "
        sqls += ", tx.updatedby, tx.updated"
        sqls += " FROM pm.tranche_loan_tx tx "
        sqls += " WHERE tx.tranche_id = "+ str(self.tranche_id)
            
        if ( self.d1 and self.d2 ):
            sqls += " AND tx.tdate >= '"+self.d1+"' and tx.tdate <= '" + self.d2 + "' "
        elif ( self.d1 ):
            sqls += " AND tx.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 ):
            sqls += " AND tx.tdate <= '"+ self.d2 +"'"

            
        sqls += " order by tx.tdate, tx.loan_id"
        self.logger.debug("PMTranche::updateTS.1=>%s",sqls)
        mlist = PMDB.query_list1(db, sqls)
        bal=0.0
        for x in mlist:
            bal += x['principal']
            x['balance']= bal
        
        self.t_pd = pd.DataFrame(mlist)

        self.logger.debug("PMTranche::updateTS:%s", self.t_pd)
        
        
        
    def updateSTATS(self):
        
        #self.c_pd['month'] = self.c_pd.apply(self.updateMonth(), axis=1)
        
        self.stats["mean"] = self.c_pd["amount"].mean()
        self.stats["median"] = self.c_pd["amount"].median()
        self.stats["min"] = self.c_pd["amount"].min()
        self.stats["max"] = self.c_pd["amount"].max()
        self.stats["sum"] = self.c_pd["amount"].sum()
        self.stats["std"] = self.c_pd["amount"].std()
        
        self.stats["monthly"] = self.c_pd.groupby(['month'])['amount'].sum()
         
        self.logger.debug("Update STATS:%s", self.stats)
        
    def getTS(self):
        return self.t_pd
    
    def getTS2(self):
        return self.t_dict
    
    def getSTATS(self):
        return self.stats    
            
        
    def setCode(self, code):
        self.code=code
        self.updateSTATS()
        
    def setCID(self, cid):
        self.id = cid    
        self.updateSTATS()
        
    def setProperty(self, pid):
        self.id = pid
        
    def setPeriod(self, d1, d2):
        self.d1 = d1
        self.d2 = d2

    def fetchParams (self, qj):
        
        if ( 'company' in qj):   
            self.company = qj['company']
        if ( 'group' in qj):   
            self.group = qj['group']
        
        if ( 'property_id' in qj):   
            self.p_id = qj['property_id']
        if ( 'start_date' in qj):   
            self.d1 = qj['start_date']
        if ( 'end_date' in qj):   
            self.d2 = qj['end_date']
        
        self.logger.debug("PMCashflow: company:%s group:%s property:%s", self.company, self.group,  self.p_id)