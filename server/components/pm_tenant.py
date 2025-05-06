# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 18:39:28 2020
Tenants
@author: ppare
"""
import pandas as pd
from datetime import timedelta, datetime

from utils.pm_db import PMDB


class PMTenant:
    
    def __init__(self, tid, qj, logger, db):
        self.property_id = -1
        self.tenant_id = tid
        self.d1= None
        self.d2= None
        self.phone = ""
        self.email = ""
        self.tax_id = ""
        self.fname = ""
        self.lname = ""
        self.parent = ""
        self.dob=""
        self.dl_state = ""
        self.dl_id = ""
        self.familymembers = 0
        self.rent = 0.0
        self.deposit = 0.0
        self.family_pd = None
        self.attr_pd = None
        self.core = {}
        self.params = qj
        self.status=0
        self.logger = logger
        self.c_pd = None
        self.t_pd = None
        self.sd_pd = None
        self.veh_pd = None
        self.pet_pd = None
        self.history_pd = None
        self.d_dict = {}
        self.docs_pd = None
        self.fetchParams(qj)
        self.updateTInfo(db)
    
    def getTInfo(self, info='ALL'):
        mdict = {
                    "tenant_id":self.tenant_id,
                    "property_id" : self.property_id,
                    "first_name":self.fname,
                    "last_name":self.lname,
                    "dob":self.dob,
                    "tax_id":self.tax_id,
                    "dl_state":self.dl_state,
                    "dl_id":self.dl_id,
                    "phone":self.phone,
                    "email":self.email,
                    "start_date": self.d1,
                    "end_date": self.d2,
                    "status": self.status,
                    "parent":self.parent
                }
        
        for x in self.core:
            mdict[x]= self.core[x]
    
        if ( info == 'ALL' or info == 'FAMILY'):
            mdict['family'] = self.family_pd.to_json(orient='table')
        if ( info == 'ALL' or info == 'ATTRIBUTES'):
            mdict['attributes'] = self.attr_pd.to_json(orient='table')
        if ( info == 'ALL' or info == 'DOCUMENTS'):
            mdict['documents'] = self.docs_pd.to_json(orient='table')
        if ( info == 'ALL' or info == 'VEHICLES'):
            mdict['vehicles'] = self.veh_pd.to_json(orient='table')
        if ( info == 'ALL' or info == 'PETS'):
            mdict['pets'] = self.pet_pd.to_json(orient='table')
        if ( info == 'ALL' or info == 'HISTORY'):
            mdict['history'] = self.history_pd.to_json(orient='table')

        return mdict
          
    def updateTInfo(self, db):
        
        qry = " SELECT t.tenant_id, t.first_name,t.middle_name, t.last_name, t.other_names, t.tax_id, t.phone, t.email,"
        qry += " t.status, t.relationship,t.parent,ifnull(date_format(t.dob,'%Y-%m-%dT%H:%i:%S'),'') as dob, t.dl_state, t.dl_id "
        qry += ", updatedby, date_format(updated,'%Y-%m-%dT%H:%i:%S') as updated, t.description, t.gender "
        qry += " FROM pm.tenants t where t.tenant_id= " + str(self.tenant_id)
        
        self.logger.debug("PMTenant:updateTInfo:Query1: Tenant: %s", qry)
        mlist = PMDB.query_list(db,qry, None)
        for x in mlist:
        #print(x)
            self.fname = x['first_name']
            self.core['middle_name'] = x['middle_name']
            self.lname = x['last_name']
            self.core['other_names'] = x['other_names']
            self.dob = x['dob']
            self.tax_id = x['tax_id']
            self.dl_id = x['dl_id']
            self.dl_state = x['dl_state']
            self.phone = x['phone']
            self.email = x['email']
            self.parent = x['parent']
            self.status = x['status']
            self.core['gender']=x['gender']
            self.core['relationship']=x['relationship']
            self.core['description']=x['description']
            self.core['updated']=x['updated']
            self.core['updatedby']=x['updatedby']
            
        qry = " SELECT t.tenant_id, t.balance, t.last_payment,ifnull(date_format(t.last_payment_date,'%Y-%m-%dT%H:%i:%S'),'') as last_payment_date "
        qry += ", t.payment_due,ifnull(date_format(t.payment_due_date,'%Y-%m-%dT%H:%i:%S'),'') as payment_due_date  "
        qry += " FROM pm.tenants_financials t where t.tenant_id= " + str(self.tenant_id)
        
        self.logger.debug("PMTenant:updateTInfo:Query1.1: Tenant: %s", qry)
        mlist = PMDB.query_list(db,qry, None)
        for x in mlist:
        #print(x)
            self.core['balance'] = x['balance']
            self.core['last_payment'] = x['last_payment']
            self.core['last_payment_date'] = x['last_payment_date']
            self.core['payment_due'] = x['payment_due']
            self.core['payment_due_date'] = x['payment_due_date']
        
        qry = " select p.property_id, p.city, p.zip, p.state,p.label, ifnull(date_format(tc.start_date,'%Y-%m-%dT%H:%i:%S'),'') as start_date, "
        qry += " ifnull(date_format(tc.end_date,'%Y-%m-%dT%H:%i:%S'),'') as end_date,  tc.deposit, tc.deposit_a, tc.rent, tc.responsible, tc.family_members, "
        qry += " ifnull(date_format(tc.move_in,'%Y-%m-%dT%H:%i:%S'),'') as move_in, ifnull(date_format(tc.move_out,'%Y-%m-%dT%H:%i:%S'),'') as move_out, tc.tenancy_id, p.llc, p.tranche_id "
        qry += " FROM pm.tenancy tc, pm.property p "
        qry += " where p.property_id = tc.property_id and tc.tenant_id=" + str(self.tenant_id)
        qry += " order by tc.move_out desc"
        
        self.logger.debug("PMTenant:updateTInfo:Query2: Tenant: %s  Parent:%s", qry, self.parent)
        mlist = PMDB.query_list(db,qry, None)
         
        for x in mlist:
            self.core['city'] = x['city']        
            self.core['state'] = x['state']
            self.core['zip'] = x['zip']
            self.core['lease_start_date'] = x['start_date']
            self.core['lease_end_date'] = x['end_date']
            self.core['move_in_date'] = x['move_in']
            self.core['move_out_date'] = x['move_out']
            self.core['responsible'] = x['responsible']
            self.core['rent'] = x['rent']
            self.core['deposit'] = x['deposit']
            self.core['deposit_a'] = x['deposit_a']
            self.property_id = x['property_id']
            self.core['familymembers'] = x['family_members']
            self.core['label'] = x['label']
            self.core['tenancy_id'] = x['tenancy_id']
            self.core['company'] = x['llc']
            self.core['tranche_id'] = x['tranche_id']
            
        # Family
        qry = "SELECT t.tenant_id, t.first_name, t.last_name, t.occupation, date_format(t.dob,'%Y-%m-%d') as dob, t.tax_id, t.phone, t.email,"
        qry +="t.description as notes, t.relationship, t.updatedby, date_format(t.updated,'%Y-%m-%dT%H:%i:%S') as updated "
        qry +="FROM pm.tenants t "
        qry +="where t.parent=" + str(self.tenant_id)
        qry +=" UNION "
        qry +="SELECT -1, tf.first_name, tf.last_name, tf.occupation, date_format(tf.dob,'%Y-%m-%d') as dob, tf.tax_id, tf.phone, tf.email, "
        qry +="tf.notes as notes, tf.relationship, tf.updatedby, date_format(tf.updated,'%Y-%m-%dT%H:%i:%S') as updated "
        qry +="FROM pm.tenants_family tf "
        qry +="WHERE tf.tenant_id="+str(self.tenant_id)

        self.logger.debug("PMTenant:updateTInfo:Query List2: Tenant: %s", qry)
        
        mlist = PMDB.query_list(db,qry, None)
        
        self.family_pd = pd.DataFrame(mlist)
        
        # attributes
        qry = " SELECT IFNULL(ta.tenant_id," + str(self.tenant_id) +") as tenant_id , co.co_name, co.co_value, IFNULL(ta.value,'')  as ta_value "
        qry += "FROM pm.tenants_attributes ta, pm.cores co "
        qry += "WHERE co.co_name=ta.name and co.co_type='TENANT_ATTRIBUTES' and ta.tenant_id="+ str(self.tenant_id)
        qry += " UNION "
        qry += " SELECT "+ str(self.tenant_id) + " as tenant_id , co.co_name, co.co_value, '' as ta_value "
        qry += "FROM pm.cores co "
        qry += " WHERE co.co_type='TENANT_ATTRIBUTES' and co.co_name not in ("
        qry += " SELECT c1.co_name FROM pm.tenants_attributes ta1, pm.cores c1 WHERE c1.co_name=ta1.name "
        qry += " and ta1.tenant_id=" + str(self.tenant_id) + ")"
        
        self.logger.debug("PMTenant:updateTInfo:Query List21: Tenant: %s", qry)
        
        mlist = PMDB.query_list(db,qry, None)
        self.attr_pd = pd.DataFrame(mlist)
        
        # Vehicles
        qry = "SELECT tv.*, pl.label as parking_lot FROM pm.tenants_vehicle tv, pm.parking_lot pl "
        qry += "where tv.pl_id = pl.pl_id and tv.tenant_id=" + str(self.tenant_id)
        self.logger.debug("PMTenant:updateTInfo:Query List22: Tenant: %s", qry)
        mlist = PMDB.query_list(db,qry, None)
        self.veh_pd = pd.DataFrame(mlist)
                
        # Pets
        qry = " SELECT * FROM pm.tenants_pet where tenant_id=" + str(self.tenant_id)
        self.logger.debug("PMTenant:updateTInfo:Query List23: Pets: %s", qry)
        mlist = PMDB.query_list(db,qry, None)
        self.pet_pd = pd.DataFrame(mlist)

        self.logger.debug("PMTenant.updateTInfo: %s", self.params)

        if ( 'FINANCIALS' in self.params ):
            self.logger.debug("PMTenant.updateTInfo: Fetching financials")
            self.updateFTS(db, self.d1, self.d2)
            #print(self.t_pd)
        
        
        self.fetchDocuments(db)
        self.fetchHistory(db)
        
        
    def updateFTS(self, db, d1, d2):
        dt = datetime.today()
        dt1 = datetime.today()
        sd1 = "2020-01-01"
        if ( d1 == None ): 
            d1 = self.core['lease_start_date'].split('T')[0]
            dt = dt.strptime(d1,'%Y-%m-%d') - timedelta(days=60)
        else:
            dt = dt.strptime(d1,'%Y-%m-%d')
            
        if ( d2 == None ):
            d2 = self.core['lease_end_date'].split('T')[0]
            
        
        #d11 = dt.strftime('%Y-%m-%d')
        
            
        sqls = "SELECT t.tenant_id as tenant_id, tr.tr_id as t_id, date_format(tr.tdate,'%Y-%m-%dT%H:%i:%S') as tdate, c.label as category_name, tr.category_id, tr.amount as debit, 0 as credit, tr.description, 'TR' as type, ' ' as payee, ' ' as ref, '' as reference " + \
                "FROM pm.tenants t, pm.tenants_receivable tr, pm.category c " + \
                "WHERE t.tenant_id = tr.tenant_id  AND c.category_id = tr.category_id " + \
                "AND t.tenant_id=" + str(self.tenant_id)
        sqls += " AND tr.tdate between '" + sd1 + "' and '"+ d2 + "' "
        sqls += " UNION "
        sqls += "SELECT tx.tenant_id as tenant_id, tx.tx_id as t_id, date_format(tx.tdate,'%Y-%m-%dT%H:%i:%S') as tdate, c.label as category_name, tx.category_id, tx.debit as debit, tx.credit as credit, tx.description, 'TX' as type, tx.payee as payee, tx.type as ref, tx.reference as reference " + \
                "FROM pm.transactions tx, pm.category c " 
        sqls += "WHERE tx.tenant_id=" + str(self.tenant_id)
        # AND tx.category_id in (8,9,10,11,53,54,70,71,74,78,79,80,81,82,83,84,186)"
        sqls += " AND tx.category_id=c.category_id AND tx.tdate between '" + sd1 + "' and '" + d2 + "' "
        sqls += " ORDER BY tdate, credit, debit"
            
        self.logger.debug("PMTenant.updateFTS: %s", sqls)
        mlist = PMDB.query_list1(db, sqls)
        self.c_pd = pd.DataFrame(mlist)
        l_pd=self.c_pd
        #t_dict = {"Category": my_categories.keys()}
 
        l_pd['balance']=0.0
        
        #print("PMTenant::updateFTS:", t_pd);
        #t_pd = t_pd.set_index('category')
        lb = 0 
        for ind in l_pd.index:
            l_pd.at[ind,'balance'] = l_pd.at[ind,'credit'] - l_pd.at[ind,'debit'] + lb
            lb = l_pd.at[ind,'balance']
        #self.logger.debug("PMTenant::updateFTS: %s", l_pd);        
        for ind in l_pd.index:
            #self.logger.debug("PMTenant::updateFTS:[%s] %s %s",ind, l_pd.at[ind,'tdate'], dt)
            dt1 = dt1.strptime(l_pd.at[ind,'tdate'].split('T')[0],'%Y-%m-%d')
            if ( dt1 < dt):
                l_pd= l_pd.drop([ind])
                ind-=1
            else:
                break
                

        #self.logger.debug("PMTenant::updateFTS: %s", l_pd);
        self.t_pd = l_pd
        
    def updateSD(self, db, d1, d2):
        dt = datetime.today()
        if ( d1 == None ): 
            d1 = self.core['lease_start_date'].split('T')[0]
            dt = dt.strptime(d1,'%Y-%m-%d') - timedelta(days=100)
        else:
            dt = dt.strptime(d1,'%Y-%m-%d')
            
        if ( d2 == None ):
            d2 = datetime.today().strftime('%Y-%m-%d')            

        d11 = dt.strftime('%Y-%m-%d')
            
        sqls = "SELECT tx.tenant_id as tenant_id, tx.stx_id as t_id, date_format(tx.tdate,'%Y-%m-%dT%H:%i:%S') as tdate, tx.category_id, tx.debit as debit, tx.credit as credit, tx.description, 'STX' as type, tx.payee as payee, tx.type as ref, tx.reference as reference " + \
                "FROM pm.sd_transactions tx, pm.category c " + \
                "WHERE tx.tenant_id=" + str(self.tenant_id) + " AND tx.category_id = c.category_id and c.type='SD'"
        #sqls += " AND tx.tdate between '" + d11 + "' and '" + d2 + "' "
        sqls += " ORDER BY tdate, credit, debit"
            
        self.logger.debug("PMTenant.updateSD:%s", sqls)
        mlist = PMDB.query_list1(db, sqls)
        l_pd = pd.DataFrame(mlist)
        
        #t_dict = {"Category": my_categories.keys()}
 
        l_pd['balance']=0.0
        
        #print("PMTenant::updateFTS:", t_pd);
        #t_pd = t_pd.set_index('category')
        lb = 0 
        for ind in l_pd.index:
            l_pd.at[ind,'balance'] = l_pd.at[ind,'credit'] - l_pd.at[ind,'debit'] + lb
            lb = l_pd.at[ind,'balance']
        
        self.logger.debug("PMTenant::updateSD:%s", l_pd);
        self.logger.debug("PMTenant::updateSD:%s", lb);
        
        self.sd_pd = l_pd
        
        return lb
        
    def getSTATS(self):
        
        return self.t_pd
    
    def getSDH(self):
        
        return self.sd_pd
    
    def fetchHistory(self, db):
        
        qry = " select * from pm.tenants_history where tenant_id="+str(self.tenant_id)
        self.logger.debug("PMTenant::fetchHistory:%s", qry)
        
        mlist = PMDB.query_list(db,qry, None)
        self.history_pd = pd.DataFrame(mlist)
        
    def fetchDocuments(self, db):
        
        qry = " select * from pm.tenants_docs where tenant_id="+str(self.tenant_id)
        self.logger.debug("PMTenant::fetchDocuments:%s", qry)
        
        mlist = PMDB.query_list(db,qry, None)
        self.docs_pd = pd.DataFrame(mlist)
    
    def getPetTagInfo(self, tag_id):
        mdict = {}
        mdict['status']=-1
        print("getPetTagInfo:", self.pet_pd)
        for ind in self.pet_pd.index:
            print("getPetTagInfo:", tag_id, "=",self.pet_pd.at[ind, 'pet_id'])
            if ( self.pet_pd.at[ind, 'pet_id'] == tag_id ):
                mdict['pet_id']=self.pet_pd.at[ind, 'pet_id']
                mdict['pet_role']=self.pet_pd.at[ind, 'pet_role']
                mdict['pet_type']=self.pet_pd.at[ind, 'pet_type']
                mdict['breed']=self.pet_pd.at[ind, 'breed']
                mdict['expiry']=self.pet_pd.at[ind, 'expiry']
                mdict['insurance']=self.pet_pd.at[ind, 'insurance']
                mdict['vaccination']=self.pet_pd.at[ind, 'vaccination']
                mdict['weight']=self.pet_pd.at[ind, 'weight']
                mdict['notes']=self.pet_pd.at[ind, 'notes']
                mdict['setup_charge']=self.pet_pd.at[ind, 'setup_charge']
                mdict['monthly']=self.pet_pd.at[ind, 'monthly']
                mdict['status']=0
    
        
        mdict['first_name']=self.fname
        mdict['last_name']=self.lname
        mdict['label']=self.core['label']
        mdict['city']=self.core['city']
        mdict['state']=self.core['state']
        mdict['zip']=self.core['zip']
        if ( 'expiry' not in mdict):
            mdict['expiry']=self.core['lease_end_date']
        
        return mdict

    def getParkingTagInfo(self, permit_id):
        mdict = {}
        mdict['status']=-1
        for ind in self.veh_pd.index:
            #print("getParkingTagInfo:", permit_id, "=",self.veh_pd.at[ind, 'parking_tag_id'])
            if ( self.veh_pd.at[ind, 'parking_tag_id'] == permit_id ):
                mdict['state']=self.veh_pd.at[ind, 'state']
                mdict['tag']=self.veh_pd.at[ind, 'tag']
                mdict['make']=self.veh_pd.at[ind, 'make']
                mdict['model']=self.veh_pd.at[ind, 'model']
                mdict['color']=self.veh_pd.at[ind, 'color']
                mdict['expiry']=self.veh_pd.at[ind, 'expiry']
                mdict['parking_lot']=self.veh_pd.at[ind, 'parking_lot']
                mdict['parking_tag_id']=self.veh_pd.at[ind, 'parking_tag_id']
                mdict['setup_charge']=self.veh_pd.at[ind, 'setup_charge']
                mdict['monthly']=self.veh_pd.at[ind, 'monthly']
                mdict['status']=0
    
        
        mdict['first_name']=self.fname
        mdict['last_name']=self.lname
        mdict['label']=self.core['label']
        mdict['city']=self.core['city']
        mdict['state']=self.core['state']
        mdict['zip']=self.core['zip']
        if ( 'expiry' not in mdict):
            mdict['expiry']=self.core['lease_end_date']
        
        return mdict
    
    def getDocuments(self):
        return self.docs_pd
    
    def getPropertyId(self):
        return self.property_id
    
    def fetchParams(self, qj):
        if ( 'property_id' in qj ):
            self.property_id = qj['property_id']
        if ( 'start_date' in qj ):
            self.d1 = qj['start_date']
        if ( 'end_date' in qj ):
            self.d2 = qj['end_date']
            
        self.logger.debug("PMTenants.fetchParams:property_id[%s] sd[%s] d2[%s]",self.property_id,self.d1,self.d2)