# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 08:51:46 2019
Cashflow
@author: ppare
"""

import pandas as pd
from datetime import datetime


import ref_data, pm_tranche
from utils.pm_db import PMDB

class PMCashflow:
    
    def __init__(self, logger, db, qj):
        today = datetime.today()
        self.d2 = today.strftime('%Y-%m-%d')
        self.d1 = self.d2
        self.p_id = -1
        self.company = "HC"
        self.tranche_id = -1
        self.group = ""
        self.c_id = -1
        self.logger = logger
        self.c_pd = pd.DataFrame()
        self.t_pd = pd.DataFrame()
        self.t_dict = {}
        self.stats = {}
        self.fetchData( qj)
        self.my_categories = ref_data.get_my_categories_by_id(db, self.logger, None)

    
    def fetchData (self, qj):
        if ( 'company' in qj):   
            self.company = qj['company']
        if ( 'tranche_id' in qj):   
            self.tranche_id = int(qj['tranche_id'])
        if ( 'group' in qj):   
            self.group = qj['group']
        if ( 'category_id' in qj):   
            self.c_id = qj['category_id']
        if ( 'property_id' in qj):   
            self.p_id = qj['property_id']
        if ( 'start_date' in qj):   
            self.d1 = qj['start_date']
        if ( 'end_date' in qj):   
            self.d2 = qj['end_date']
        
        self.logger.debug("PMCashflow: company:%s group:%s property:%s tranche:%s", self.company, self.group,  self.p_id, self.tranche_id)
            
# creates cashflow table by time period, Month 1, Month 2, Month 3.. Total    

    def updateTS(self, db):
             
        t_dict = {}

        sqls = "SELECT c.code, date_format(t.tdate,'%Y-%m-%d') as tdate, year(t.tdate) as year,month(t.tdate) as month"
        sqls += ", c.category_id as category_id, c.parent as pcategory, (t.credit - t.debit) as amount, p.tranche_id "
        sqls += "FROM pm.transactions t, pm.category c, pm.property p "
        sqls += "WHERE t.category_id = c.category_id and p.property_id=t.property_id "
        if ( self.company and self.company != 'ALL' ):
            sqls += " AND p.llc ='" + self.company +"'"
        if ( self.group and self.group != 'ALL' ):
            sqls += " AND p.group = '" + self.group +"' "
            
        if ( self.c_id and self.c_id > 0):
            sqls += " AND c.code =" + str(self.c_id)
            
        if ( self.p_id and self.p_id > 0):
            sqls += " AND p.property_id =" + str(self.p_id)
            
        if ( self.d1 and self.d2 ):
            sqls += " AND t.tdate >= '"+self.d1+"' and t.tdate <= '" + self.d2 + "' "
        elif ( self.d1 ):
            sqls += " AND t.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 ):
            sqls += " AND t.tdate <= '"+ self.d2 +"'"

        if ( self.tranche_id > 0 ):
            sqls += " and p.tranche_id="+str(self.tranche_id)
            
        sqls += " order by c.display_order, tdate"
        self.logger.debug("PMCashflow::updateTS.1=>%s",sqls)
        mlist = PMDB.query_list1(db, sqls)
        
        t_dict = self.my_categories.keys()
        #print("pm_cashflow:Dict=", t_dict)
        t_pd = pd.DataFrame(t_dict)
        t_pd = t_pd.rename(columns={0:'category'})
        t_pd['total']=0.0
        t_pd['parent']=""
        
        t_pd = t_pd.set_index('category')   
        l_tranche={}
        tranche_ids=""
        for x in mlist:
            #print("updateTS:loop:", x)
            if str(x['tranche_id']) not in tranche_ids:
                if ( tranche_ids != ""):
                    tranche_ids += ","+ str(x['tranche_id'])
                else:
                    tranche_ids = str(x['tranche_id'])
            s = x['category_id']
            c = str(x['year'])+"-"+str(x['month'])
            if c in t_pd.columns:
                t_pd.at[s,c] += x['amount']
            else:
                t_pd[c]=0.0
                t_pd.at[s,c]=x['amount']
                     
            ps = self.my_categories[s][4]
            while ( ps and ps != '' ):
                #print ("pm_cashflow.updateTS: code:", s, " parent:", ps, " column:", c, " amount:", x['amount'])
                t_pd.at[ps,c] += x['amount']
                #t_pd.at[ps,'display_order']=self.my_categories[ps][6]
                ps = self.my_categories[ps][4]                
                
        # add financials
        l_tranche['tranche_id']=tranche_ids #mlist[0]['tranche_id']
        self.logger.debug("PMCashflow::updateTS: Tranche ID:%s = %s", tranche_ids, l_tranche)

        t_fin = pm_tranche.getLTTXS(db, self.logger, l_tranche)

        #self.logger.debug("PMCashflow::updateTS: Tranche Fin:%s", t_fin)
        #self.logger.debug("PMCashflow::updateTS: Tranche Fin:%s", t_pd.index)
        for x in t_fin['data']:
            
            c = x['tdate'][:7].replace('-0','-')
            #self.logger.debug("PMCashflow::updateTS: Tranche Fin:%s", c)
            
            if ( c in t_pd.columns ):
                t_pd.at[201,c] += x['interest']
                t_pd.at[200,c] += x['principal']
                t_pd.at[189,c] += x['payment']

        t_pd['total'] = t_pd.sum(axis=1)
        t_pd['ratio']=0.00
        # set ratio against income RENT-38
        for ind in t_pd.index:
            #print("pm_cashflow.updateTaxTS.5:",t_pd['total'][ind], t_pd['total'][38] )
            t_pd['ratio'][ind] = t_pd['total'][ind] / t_pd['total'][38]
        
        t_pd['name']=""
        for k in t_dict:
            #print("pm_cashflow.updateTS.6::", k)
            t_pd.at[k,'name'] = self.my_categories[k][2]
            t_pd.at[k,'parent'] = self.my_categories[k][4]

        self.logger.debug("PMCashflow::updateTS:%s", t_pd)
        self.t_pd = t_pd
    
    def updateProjectTS(self, db):
        
        self.updateTS( db)

        self.t_pd = self.t_pd.transpose().drop(index="ratio")

        
        self.logger.debug("PMCashflow::updateProjectTS:%s", self.t_pd)
        
# creates cashflow table by Tax IDs for a time period
    def updateTaxTS(self, db):
             
        t_dict = {}

        sqls = "SELECT c.code, date_format(t.tdate,'%Y-%m-%d') as tdate, year(t.tdate) as year,month(t.tdate) as month"
        sqls += ", c.category_id as category_id, c.parent as pcategory, (t.credit - t.debit) as amount, p.tax_id "
        sqls += "FROM pm.transactions t, pm.category c, pm.property p "
        sqls += "WHERE t.category_id = c.category_id and p.property_id=t.property_id "
        if ( self.company and self.company != 'ALL' ):
            sqls += " AND p.llc ='" + self.company +"'"
        if ( self.group and self.p_group != 'ALL' ):
            sqls += " AND p.group = '" + self.group +"' "
        if ( self.d1 and self.d2 ):
            sqls += " AND t.tdate >= '"+self.d1+"' and t.tdate <= '" + self.d2 + "' "
        elif ( self.d1 ):
            sqls += " AND t.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 ):
            sqls += " AND t.tdate <= '"+ self.d2 +"'"
         
        sqls += " order by c.display_order, tdate"
        self.logger.debug("PMCashflow::updateTaxTS.1=>%s",sqls)
        mlist = PMDB.query_list1(db, sqls)
        
        t_dict = self.my_categories.keys()
        #print("pm_cashflow:updateTaxTS.2=", t_dict)
        t_pd = pd.DataFrame(t_dict)
        t_pd = t_pd.rename(columns={0:'category'})
        t_pd['total']=0.0
                
        t_pd = t_pd.set_index('category')
                 
        for x in mlist:
            #print("updateTaxTS:loop:", x)
            s = x['category_id']
            c = x['tax_id']
            if c in t_pd.columns:
                t_pd.at[s,c] += x['amount']
            else:
                t_pd[c]=0.0
                t_pd.at[s,c]=x['amount']   
                
            ps = self.my_categories[s][4]
            while ( ps and ps != '' ):
                #print ("pm_cashflow.updateTaxTS.4: code:", s, " parent:", ps, " column:", c, " amount:", x['amount'])
                t_pd.at[ps,c] += x['amount']
                ps = self.my_categories[ps][4]                  
        
        t_pd['total'] = t_pd.sum(axis=1)
        t_pd['name']=""
        for k in t_dict:
            #print("pm_cashflow.updateTaxTS.6::", k)
            t_pd.at[k,'name'] = self.my_categories[k][2]
            t_pd.at[k,'parent'] = self.my_categories[k][4]
        
        indexNames = t_pd[ t_pd['total'] == 0 ].index 
            # Delete these row indexes from dataFrame
        t_pd.drop(indexNames , inplace=True)
        
        t_pd['parent']=""

        self.logger.debug("PMCashflow::updateTaxTS:%s", t_pd)
        
        self.t_pd = t_pd
        
    def updatePCF(self, db):
        
        sqls=""
            
        params={}
        params['tranche_id']=self.tranche_id
        params['company']=self.company
        params['report_date']=self.d1
        l_pd = ref_data.get_my_tenancy_pd(db, self.logger, params)
        #l_pd = l_pd.set_index('property_id')
        l_pd['income']=0.0
        l_pd['expense']=0.0
        l_pd['receivable']=0.0
        l_pd['past30']=0.0
        
        ############# txs
        sqls = "SELECT tx.property_id, sum(tx.credit) as credit, sum(tx.debit) as debit "
        sqls += " FROM pm.transactions tx "
        
        if ( self.d1 and self.d2 ):
            sqls += " WHERE tx.tdate >= '"+self.d1+"' and tx.tdate <= '" + self.d2 + "' "
        elif ( self.d1 ):
            sqls += " WHERE tx.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 ):
            sqls += " WHERE tx.tdate <= '"+ self.d2 +"'"
        
        if ( self.tranche_id > 0 ):
            sqls += " and tx.property_id in (select property_id from pm.property where tranche_id="+str(self.tranche_id) +") "

        sqls += " GROUP BY tx.property_id order by tx.property_id "
        
        self.logger.debug("pm_cashflow.updatePCF.3=%s",sqls)
        dlist = PMDB.query_list1(db, sqls)
        self.logger.debug("pm_cashflow.updatePCF:[0] %s", dlist)
        for x in dlist:
            #print("Data:", x)
            #self.logger.debug("pm_cashflow.updatePCF:[LOOP] %s", x)
            s = x['property_id']
            c = x['credit']
            d = x['debit']
            if ( s in l_pd.index):
                l_pd.at[s,'income']=c
                l_pd.at[s,'expense']=d
            else:
                self.logger.debug("pm_cashflow.updatePCF.LOOP.TRANSACTION Not found: %s", s)
        
        #self.logger.debug("pm_cashflow.updatePCF:[0] %s", l_pd)
        ############# receivable
        
        sqls = "SELECT tx.property_id, sum(tx.amount) as amount "
        sqls += " FROM pm.tenants_receivable tx "
        
        if ( self.d1 and self.d2 ):
            sqls += " WHERE tx.tdate >= '"+self.d1+"' and tx.tdate <= '" + self.d2 + "' "
        elif ( self.d1 ):
            sqls += " WHERE tx.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 ):
            sqls += " WHERE tx.tdate <= '"+ self.d2 +"'"
        
        if ( self.tranche_id > 0 ):
            sqls += " and tx.property_id in (select property_id from pm.property where tranche_id="+str(self.tranche_id) +") "

        sqls += " GROUP BY tx.property_id order by tx.property_id"
        
        self.logger.debug("pm_cashflow.updatePCF.4=%s",sqls)
        dlist = PMDB.query_list1(db, sqls)

        for x in dlist:
            #print("Data:", x)
            s = x['property_id']
            if ( s in l_pd.index):
                l_pd.at[s,'receivable']=x['amount']
            else:
                self.logger.debug("pm_cashflow.updatePCF.LOOP.RECEIVABLE Not found: %s", s)
          
        #self.logger.debug("pm_cashflow.updatePCF:[1] %s", l_pd)

        if ( self.company != 'ALL' and self.company != '' ):
            indexNames = l_pd[ l_pd['company'] != self.company ].index 
            #print("pm_cashflow.updatePCF.8:", indexNames)
            # Delete these row indexes from dataFrame
            l_pd.drop(indexNames , inplace=True)
        
        if ( self.group != 'ALL' and self.group != '' ):
            indexNames = l_pd[ l_pd['group'] != self.group ].index 
            # Delete these row indexes from dataFrame
            #print("pm_cashflow.updatePCF.9:", indexNames)
            l_pd.drop(indexNames , inplace=True)
            
        self.logger.debug("pm_cashflow.updatePCF:%s", l_pd)
        
        self.t_pd= l_pd


    
    def updatePCF2(self, db):
        
        l_dict={}
        
        sqls = "SELECT p.property_id, p.label, p.llc as company, p.group, p.p_status, pts.category_id, date_format(pts.tdate,'%Y-%m-%d') as tdate, pts.value "
        sqls += "FROM pm.property_ts pts, pm.property p "
        sqls += "WHERE pts.property_id = p.property_id AND pts.category_id in (100,38,39) "
        if ( self.company != ''):
            sqls += " AND p.llc = '" + self.company +"'"
        if ( self.group ):
            sqls += " AND p.group = '" + self.group +"' "
        if ( self.d1 and self.d2 ):
            sqls += " AND pts.tdate >= '"+self.d1+"' and pts.tdate <= '" + self.d2 + "' "
        elif ( self.d1 ):
            sqls += " AND pts.tdate >= '"+ self.d1 +"'"
        elif ( self.d2 ):
            sqls += " AND pts.tdate <= '"+ self.d2 +"'"
            
        if ( self.company != None and self.company != ""):
            sqls += " and p.llc = '"+self.company+"'"
        if(self.group != None and self.group != ""):
            sqls += " and p.group = '"+self.group+"'"
        sqls += " and p.p_status in ('OCCUPIED','RENT_READY')"
        
        self.logger.debug("pm_cashflow.updatePCF.3=%s",sqls)
        dlist = PMDB.query_list1(db, sqls)
               
        for x in dlist:
            #print("Data:", x)
            s = x['property_id']
            d = x['tdate']
            c = x['category_id']
            if ( s not in l_dict):
                l_dict[s] = {'INFO':{x['property_id'],x['company'],x['group'],x['p_status']}}
            if ( d not in l_dict[s]):
                l_dict[s][d] = {x['category_id']:x['value']}
            else:
                l_dict[s][d][x['category_id']] = x['value']
        
        self.logger.debug("pm_cashflow.updatePCF2:%s", l_dict)
            
        self.t_dict = l_dict
    
      
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