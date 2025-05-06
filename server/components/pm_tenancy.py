# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 09:59:41 2020

@author: ppare
"""
import pandas as pd
from utils.pm_db import PMDB

class PMTenancy:
    
    def __init__(self, db, logger, tcid, tid, pid):
        
        self.tenant_id = tid
        self.tenancy_id = tcid
        self.property_id = pid
        self.core = {}
        self.status=0
        self.logger = logger
        self.attr_pd = None
        self.docs_pd = None
        self.fetchTenancyInfo(db)
    
    def getTenancyInfo(self):
        mdict = {}
        
        for x in self.core:
            mdict[x]= self.core[x]
    
        if ( not self.attr_pd.empty ):
            mdict['attributes'] = self.attr_pd.to_json(orient='table')
        if ( not self.docs_pd.empty ):
            mdict['documents'] = self.docs_pd.to_json(orient='table')
        
        return mdict
        
        
    def fetchTenancyInfo(self, db):
        
        qry = " SELECT tc.tenancy_id, tc.tenant_id, p.property_id, p.label, p.p_status , date_format(tc.start_date,'%Y-%m-%dT%H:%i:%S')  as start_date,"
        qry +=" date_format(tc.end_date,'%Y-%m-%dT%H:%i:%S') as  end_date, date_format(tc.move_in,'%Y-%m-%dT%H:%i:%S') as move_in,"
        qry +=" ifnull(date_format(tc.move_out,'%Y-%m-%dT%H:%i:%S'),'') as move_out, tc.status, tc.family_members,tc.deposit_a, tc.term,"
        qry += " tc.rent, tc.deposit, tc.responsible, tc.updatedby, date_format(tc.updated,'%Y-%m-%dT%H:%i:%S') as updated, tn.first_name, tn.last_name, tn.phone, tn.email, tc.description "
        qry += " FROM pm.tenancy tc, pm.property p , pm.tenants tn "
        qry += " WHERE p.property_id=tc.property_id "
        qry += " and tn.tenant_id = tc.tenant_id "
        
        if ( self.tenancy_id > 0 ):
            qry += " and tc.tenancy_id=" + str(self.tenancy_id)
        elif ( self.property_id > 0 ):
            qry += " and tc.property_id=" + str(self.property_id) + " and tc.status != 2 "
        else:
            qry += " and tc.tenant_id=" + str(self.tenant_id) + " and tc.status != 2 "
            
        self.logger.debug("PMTenancy::Query1:%s", qry)
        mlist = PMDB.query_list(db,qry, None)
        for x in mlist:
        #print(x)
            if ( self.tenancy_id < 1):
                self.tenancy_id = x['tenancy_id']
            if ( self.property_id < 1):
                self.property_id = x['property_id']
            if ( self.tenant_id < 1):
                self.tenant_id = x['tenant_id']
            self.core['tenancy_id'] = x['tenancy_id']    
            self.core['tenant_id'] = x['tenant_id']   
            self.core['property_id'] = x['property_id']
            self.core['label'] = x['label']
            self.core['first_name'] = x['first_name']
            self.core['last_name'] = x['last_name']
            self.core['phone'] = x['phone']
            self.core['email'] = x['email']
            self.core['p_status'] = x['p_status']
            self.core['lease_start_date'] = x['start_date']
            self.core['lease_end_date'] = x['end_date']
            self.core['move_in_date'] = x['move_in']
            self.core['move_out_date'] = x['move_out']
            self.core['status'] = x['status']
            self.core['family_members'] = x['family_members']
            self.core['rent'] = x['rent']
            self.core['deposit'] = x['deposit']
            self.core['deposit_a'] = x['deposit_a']
            self.core['responsible'] = x['responsible']
            self.core['description'] = x['description']
            self.core['term'] = x['term']
            self.core['updatedby'] = x['updatedby']
            self.core['updated'] = x['updated']
            
        if ( self.tenancy_id < 0):
            return
            
          # attributes
        qry = " SELECT IFNULL(ta.tenancy_id," + str(self.tenancy_id) +") as tenancy_id , co.co_name, co.co_value, IFNULL(ta.value,'')  as ta_value, IFNULL(ta.reference,'')  as ta_ref "
        qry += "FROM pm.tenancy_attributes ta, pm.cores co "
        qry += "WHERE co.co_name=ta.name and co.co_type='TENANCY_ATTRIBUTES' and ta.tenancy_id="+ str(self.tenancy_id)
        qry += " UNION "
        qry += " SELECT "+ str(self.tenancy_id) + " as tenancy_id , co.co_name, co.co_value, '' as ta_value, '' as ta_ref "
        qry += "FROM pm.cores co "
        qry += " WHERE co.co_type='TENANCY_ATTRIBUTES' and co.co_name not in ("
        qry += " SELECT c1.co_name FROM pm.tenancy_attributes ta1, pm.cores c1 WHERE c1.co_name=ta1.name "
        qry += " and ta1.tenancy_id=" + str(self.tenancy_id) + ")"
        
        self.logger.debug("PMTenancy::Query2:%s", qry)
        
        mlist = PMDB.query_list(db,qry, None)
        self.attr_pd = pd.DataFrame(mlist)
        
        # documents
         
        self.fetchDocuments(db)

    def fetchDocuments(self, db):
        
        
        qry = " select * from pm.tenancy_docs where tenancy_id="+str(self.core['tenancy_id'])
        self.logger.debug("PMTenancy::fetchDocuments:%s", qry)
        
        mlist = PMDB.query_list(db,qry, None)
        self.docs_pd = pd.DataFrame(mlist)
    
    def getDocuments(self):
        return self.docs_pd
        