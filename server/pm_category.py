# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 13:13:41 2019
Category Analysis
@author: ppare
"""
import pandas as pd
import datetime

from utils.pm_db import PMDB

class PMCategory:
    
    def __init__(self, db, cid, d1, d2, logger):
        self.id = cid
        
        self.d1= d1
        self.d2= d2
        self.c_list = ""
        self.logger = logger
        self.c_pd = None
        self.table = "transacrions"
        self.tx_id = "tx_id"
        self.findChildCategories(db, cid)

    def findChildCategories(self, db, cid):

        t_c = str(cid)
        if ( t_c in ('0,2,3,4,115')):
            self.table="sd_transactions"
            self.tx_id = "stx_id"
        else:
            self.table="transactions"
            self.tx_id = "tx_id"

        sqls = "select c1.category_id from pm.category c1 where c1.parent="+t_c
        print("category:findChildCategories.1:",sqls)
        mlist = PMDB.query_list1(db, sqls)
        for x in mlist:
            t_c += ","+str(x['category_id'])

        self.c_list = t_c

    def updateFTS3(self, db, company_id):
        
        sqls = "SELECT t."+ self.tx_id+" as tx_id, p.llc, p.group, p.label,c.code, c.name, date_format(t.tdate,'%Y-%m-%d') as tdate, t.payee, t.type, t.reference, t.credit, t.debit,(t.credit - t.debit) as amount, 0 as balance, t.description "
        sqls += "FROM pm.property p, pm." +self.table + " t, pm.category c "
        sqls += "WHERE p.property_id = t.property_id AND t.category_id = c.category_id "
        sqls += " AND c.category_id in (" + self.c_list + ") "
        
            
        if ( self.d1 != '' and self.d2 != '' ):
            sqls += " AND t.tdate >= '"+self.d1+"' and t.tdate <= '" + self.d2 + "' "
        elif ( self.d1 != ''):
            sqls += " AND t.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 != ''):
            sqls += " AND t.tdate <= '"+ self.d2 +"'"
        
        
        sqls += " AND p.llc='" + company_id + "' "
        
        sqls +=" ORDER BY t.tdate, p.llc, p.group, p.label"
            
        print("category:updateFTS.1:",sqls)
        mlist = PMDB.query_list1(db, sqls)
        self.c_pd = pd.DataFrame(mlist)   
    def updateFTS(self, db, pid):
        
        sqls = "SELECT t."+ self.tx_id+" as tx_id, p.llc, p.group, p.label,c.code, c.name, date_format(t.tdate,'%Y-%m-%d') as tdate, t.payee, t.type, t.reference, t.credit, t.debit,(t.credit - t.debit) as amount, 0 as balance, t.description "
        sqls += "FROM pm.property p, pm." +self.table + " t, pm.category c "
        sqls += "WHERE p.property_id = t.property_id AND t.category_id = c.category_id "
        if ( self.id ):
            sqls += " AND c.category_id = " + str(self.id)
        elif ( self.code ):
            sqls += " AND c.code " + str(self.code)
        elif ( self.name ):
            c = '%'+self.name+'%'
            sqls += " AND c.name LIKE '" + str(c) +"'"
            
        if ( self.d1 != '' and self.d2 != '' ):
            sqls += " AND t.tdate >= '"+self.d1+"' and t.tdate <= '" + self.d2 + "' "
        elif ( self.d1 != ''):
            sqls += " AND t.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 != ''):
            sqls += " AND t.tdate <= '"+ self.d2 +"'"
        
        if ( pid > 0 ):
            sqls += " AND p.property_id=" + str(pid)
        
        sqls +=" ORDER BY t.tdate, p.llc, p.group, p.label"
            
        print("category:updateFTS.1:",sqls)
        mlist = PMDB.query_list1(db, sqls)
        self.c_pd = pd.DataFrame(mlist)
        
    def updateFTS2(self, db, t_id):
        
        sqls = "SELECT t."+ self.tx_id+" as tx_id, tn.tenant_id, tn.first_name, tn.last_name,c.code, c.name, date_format(t.tdate,'%Y-%m-%d') as tdate, t.payee, t.type, t.reference, t.credit, t.debit,(t.credit - t.debit) as amount, 0 as balance, t.description "
        sqls += "FROM pm.tenants tn, pm." +self.table + " t, pm.category c "
        sqls += "WHERE tn.tenant_id = t.tenant_id AND t.category_id = c.category_id "
        if ( self.id ):
            sqls += " AND c.category_id = " + str(self.id)
        elif ( self.code ):
            sqls += " AND c.code " + str(self.code)
        elif ( self.name ):
            c = '%'+self.name+'%'
            sqls += " AND c.name LIKE '" + str(c) +"'"
            
        if ( self.d1 != '' and self.d2 != '' ):
            sqls += " AND t.tdate >= '"+self.d1+"' and t.tdate <= '" + self.d2 + "' "
        elif ( self.d1 != ''):
            sqls += " AND t.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 != ''):
            sqls += " AND t.tdate <= '"+ self.d2 +"'"
        
        sqls += " AND tn.tenant_id=" + str(t_id)
        
        sqls +=" ORDER BY t.tdate"
            
        print("category:updateFTS2.1:",sqls)
        mlist = PMDB.query_list1(db, sqls)
        self.c_pd = pd.DataFrame(mlist)
        
    def updateTS(self, db):
        
        sqls = "SELECT t.property_id, month(t.tdate) as mon, sum(t.credit - t.debit) as amount "
        sqls += "FROM pm." +self.table + " t, pm.category c "
        sqls += "WHERE t.category_id = c.category_id "
        if ( self.id ):
            sqls += " AND c.category_id = " + str(self.id)
        elif ( self.code ):
            sqls += " AND c.code " + str(self.code)
        elif ( self.name ):
            c = '%'+self.name+'%'
            sqls += " AND c.name LIKE '" + str(c) +"'"
            
        if ( self.d1 != '' and self.d2 != '' ):
            sqls += " AND t.tdate >= '"+self.d1+"' and t.tdate <= '" + self.d2 + "' "
        elif ( self.d1 != ''):
            sqls += " AND t.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 != ''):
            sqls += " AND t.tdate <= '"+ self.d2 +"'"
            
        print(sqls)
        mlist = PMDB.query_list1(db, sqls)
        self.c_pd = pd.DataFrame(mlist)
        
        #self.c_pd['month'] = pd.DatetimeIndex(self.c_pd['tdate']).month
        #self.c_pd['year'] = pd.DatetimeIndex(self.c_pd['tdate']).year
        #self.updateSTATS()
       
#    def updateMonth(self):
#        t = pd.tslib.Timestamp(self.c_pd['date'])
#        return t.month
        
    def getSTATS(self, col):
        
        #self.c_pd['month'] = self.c_pd.apply(self.updateMonth(), axis=1)
        st = {}
        st["mean"] = self.c_pd[col].mean()
        st["median"] = self.c_pd[col].median()
        st["min"] = self.c_pd[col].min()
        st["max"] = self.c_pd[col].max()
        st["sum"] = self.c_pd[col].sum()
        st["std"] = self.c_pd[col].std()
        
        return st
        
    def getTS(self):
        return self.c_pd 
        
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