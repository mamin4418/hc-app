# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 13:13:03 2019
Analysis by Property
@author: ppare
"""


import pandas as pd
import ref_data

from utils.pm_db import PMDB


def get_my_properties_com_pd(db, logger, core, user_id=-1):
    
    if ( 'status' not in core ):
        core['status']='RENT READY'

    logger.debug("get_my_properties_com_pd:%s", core)
    qry = "SELECT p.property_id, p.llc as company, p.group, p.label, p.unit, p.label2, p.parent, p.city, p.state, p.zip, p.p_status, p.bed, p.bath, "
    qry += "p.market_rent, p.total_rooms, p.size , p.location, ifnull(p.description,'') as features"
    qry += " FROM pm.property p "
    if ( user_id > 0 ):
        qry +=", pm.auth_users_attributes aua where p.property_id > 0 and aua.id_type='property_id' and aua.id_value = p.property_id and aua.user_id ="+str(user_id)
    else:
        qry +=" WHERE p.property_id > 0 "    
    qry += " and p.p_status = '"+core['status']+"'"
    if('llc' in core and core['llc'] != ""):
        qry += " and p.llc = '"+core['llc']+"'"
    if('group' in core and core['group'] != ""):
        qry += " and p.group = '"+core['group']+"'"
    if('state' in core and core['state'] != ""):
        qry += " and p.state = '"+core['state']+"'"
    
    
    qry += " order by p.state, p.city"    
    logger.debug("get_my_properties_pd: %s", qry)    
    mlist = PMDB.query_list(db,qry, None)
    t_pd = pd.DataFrame(mlist)
    #t_pd = t_pd.rename(columns={0:'property_id',1:'company',2:'group',3:'label',4:'unit',5:'label2', 6:'parent', 7:'city', 8:'state', 9:'zip', 10:'status', 11:'bed', 12:'bath',13:'market_rent',14:'total_rooms',15:'size'})
    if ( core['status'] =='RENT READY'):
        for ind in t_pd.index:
            sqls = "select * from pm.property_rental where property_id= "+ str(t_pd['property_id'][ind]);
            logger.debug("pm_property.get_my_properties_com_pd 5:%s", sqls)
            mlist = PMDB.query_list(db,sqls,None)
            
            for x in mlist:
                ##print(x)
                for k in x:
                    if k in t_pd.columns:
                        t_pd.at[ind, k] = x[k]
                    else:
                        t_pd[k]=""
                        t_pd.at[ind,k]=x[k]

                    
        
    print("get_my_properties_pd.6:", t_pd)
    
    return t_pd


class PMProperty:
    
    def __init__(self, pid, d1, d2, logger, db):
        self.p_id = pid
        self.children_p_id = ""
        self.children_pd = pd.DataFrame()
        self.label = ""
        self.label2 = ""
        self.group = ""
        self.tranche_id = 0
        self.llc = ""
        self.unit = ""
        self.p_status=""
        self.street=""
        self.city = ""
        self.zip = ""
        self.state = "NJ"
        self.parent = 0
        self.d1= d1
        self.d2= d2
        self.freq = "MONTHLY"
        self.core = {} 
        self.attr_pd = None
        self.service_pd = None
        self.appl_pd = None
        self.tenancies_pd = None
        self.fins = {}
        self.logger = logger
        self.c_pd = None
        self.t_pd = None
        self.pics_pd = None
        self.rental_pd = None
        self.admin_pd = None
        self.school_pd = None
        self.amenities_pd = None
        self.info_updated=0;
        self.d_dict = {}
        self.my_categories = ref_data.get_my_categories_by_id(db, self.logger, None)
        self.updatePInfo(db)
    
    def getPCInfo(self):
        fieldList = ['size','description','bed','bath','total_rooms','market_rent','p_type','available_date','location','built']
        mdict = {
                    "property_id":self.p_id,
                    "label":self.label,
                    "label2":self.label2,
                    "street":self.street,
                    "unit":self.unit,
                    "zip": self.zip,
                    "city": self.city,
                    "state": self.state,
                    "parent": self.parent,
                    "p_status": self.p_status
                }
        
        if ( self.pics_pd.empty ):
            self.logger.debug("PMProperty: Default Pics")
            mdict['pics']=""
        else:
            mdict['pics'] = self.pics_pd.to_json(orient='table')

        
        if ( self.appl_pd.empty ):
            self.logger.debug("PMProperty: Default Appliances")
            mdict['appliances']=""
        else:
            mdict['appliances'] = self.appl_pd.to_json(orient='table')

        if ( self.service_pd.empty ):
            self.logger.debug("PMProperty: Service Attributes")
            mdict['services']=""
        else:
            mdict['services'] = self.service_pd.to_json(orient='table')
        
        if ( self.amenities_pd.empty ):
            mdict['amenities']=""
        else:
            mdict['amenities'] = self.amenities_pd.to_json(orient='table')

        if ( self.school_pd.empty ):
            mdict['schools']=""
        else:
            mdict['schools'] = self.school_pd.to_json(orient='table')
            
        if ( self.rental_pd.empty ):
            mdict['rental']=""
        else:
            mdict['rental'] = self.rental_pd.to_json(orient='table')

        for x in self.core:
            if ( x in fieldList ):
                mdict[x] = self.core[x]
        mdict['security_deposit']=mdict['market_rent']
        mdict['rent']=mdict['market_rent']
        if ( 'availability' not in mdict ):
            mdict['availability']="Now"
        return mdict  
    
    def getPInfo(self, info):
        
        mdict = {
                    "property_id":self.p_id,
                    "label":self.label,
                    "label2":self.label2,
                    "street":self.street,
                    "unit":self.unit,
                    "company":self.llc,
                    "tranche_id":self.tranche_id,
                    "group":self.group,
                    "zip": self.zip,
                    "city": self.city,
                    "state": self.state,
                    "parent": self.parent,
                    "p_status": self.p_status
                }
        
        if ( info == 'ALL' or info == 'APPLIANCES'):
            if ( self.appl_pd.empty ):
                self.logger.debug("PMProperty: Default Appliances")
                mdict['appliances']=""
            else:
                mdict['appliances'] = self.appl_pd.to_json(orient='table')

        if ( info == 'ALL' or info == 'SERVICES'):
            if ( self.service_pd.empty ):
                self.logger.debug("PMProperty: Service Attributes")
                mdict['services']=""
            else:
                mdict['services'] = self.service_pd.to_json(orient='table')
        
        if ( info == 'ALL' or info == 'PICS'):
            if ( self.pics_pd.empty ):
                self.logger.debug("PMProperty: Default Pics")
                mdict['pics']=""
            else:
                mdict['pics'] = self.pics_pd.to_json(orient='table')

        if ( info == 'ALL' or info == 'RENTAL'):
            if ( self.rental_pd.empty ):
                mdict['rental']=""
            else:
                mdict['rental'] = self.rental_pd.to_json(orient='table')

        if ( info == 'ALL' or info == 'AMENITIES'):
            if ( self.amenities_pd.empty ):
                mdict['amenities']=""
            else:
                mdict['amenities'] = self.amenities_pd.to_json(orient='table')

        if ( info == 'ALL' or info == 'SCHOOLS'):
            if ( self.school_pd.empty ):
                mdict['schools']=""
            else:
                mdict['schools'] = self.school_pd.to_json(orient='table')
            
        if ( info == 'ALL' or info == 'ADMIN'):
            if ( self.admin_pd.empty ):
                mdict['admin']=""
            else:
                mdict['admin'] = self.admin_pd.to_json(orient='table')

        if ( info == 'ALL' or info == 'TENANCIES'):
            if ( self.tenancies_pd.empty ):
                mdict['tenancies']=""
            else:
                mdict['tenancies'] = self.tenancies_pd.to_json(orient='table')

        for x in self.core:
            mdict[x] = self.core[x]
        
        if ( info == 'ALL' or info == 'CHILDREN'):
            if ( self.children_pd.empty ):
                self.logger.debug("PMProperty: Default children")
                mdict['children']=""
            else:
                mdict['children'] = self.children_pd.to_json(orient='table')

        if ( info == 'ALL' or info == 'RENTAL'):
            if ( self.rental_pd.empty ):
                mdict['rental']=""
            else:
                mdict['rental'] = self.rental_pd.to_json(orient='table')

        return mdict
        
        
    def updatePInfo(self, db):
        
        sqls = "SELECT p.label,p.label2,p.unit, p.llc, p.tranche_id, p.group, p.city, p.state, p.zip, p.parent, p.bed, p.bath, p.total_rooms, p.market_rent, "
        sqls += " p.built, p.p_type, p.tax_id, p.size, p.street, p.p_status, p.updatedby, date_format(p.updated,'%Y-%m-%d %H:%i:%S') as updated, "
        sqls += " date_format(p.start_date,'%Y-%m-%dT%H:%i:%S') as sdate, ifnull(date_format(p.end_date,'%Y-%m-%dT%H:%i:%S'),'') as edate, p.sub_units, p.location, p.description "
        sqls += " FROM pm.property p WHERE p.property_id in (" + str(self.p_id) + ")"

        s = ""
        self.logger.debug("PMProperty::updatePInfo 1: %s", sqls)
        mlist = PMDB.query_list(db,sqls,None)
        
        for x in mlist:
        #print(x)
            s = x['label']
            self.label = s
            self.label2 = x['label2']
            self.street = x['street']
            self.unit = x['unit']
            self.llc = x['llc']
            self.tranche_id = x['tranche_id']
            self.group = x['group']
            self.city = x['city']        
            self.state = x['state']
            self.zip = x['zip']
            self.p_status = x['p_status']
            self.core['market_rent']=x['market_rent']
            self.core['bed'] = x['bed']
            self.core['bath'] = x['bath']
            self.core['total_rooms'] = x['total_rooms']
            self.core['sub_units'] = x['sub_units']
            self.core['built'] = x['built']
            self.core['tax_id'] = x['tax_id']
            self.core['p_type'] = x['p_type']
            self.core['size'] = x['size']
            self.core['start_date'] = x['sdate']
            self.core['end_date'] = x['edate']
            self.parent = x['parent']
            self.core['location']=x['location']
            self.core['description']=x['description']
            self.core['updated']=x['updated']
            self.core['updatedby']=x['updatedby']
        # amenities
        qry = " SELECT pa.property_id as property_id , co.co_name, co.co_value, IFNULL(pa.value,'') as pa_value "
        qry += " FROM pm.property_attribute pa ,pm.cores co "
        qry += " WHERE co.co_name=pa.name  and co.co_type='PROPERTY_AMENITIES' and pa.property_id=" + str(self.p_id)
        qry += " UNION "
        qry += " SELECT "+ str(self.p_id) + " as property_id , co2.co_name, co2.co_value, '' "
        qry += " FROM pm.cores co2 WHERE co2.co_type='PROPERTY_AMENITIES' and co2.co_name not in "
        qry += "( select pa2.name FROM pm.property_attribute pa2 where pa2.property_id="+ str(self.p_id) +")"
        self.logger.debug("PMProperty::updatePInfo 15:%s", qry)
        mlist = PMDB.query_list(db, qry, None)
        #print("PMProperty::Query List: Property Attribute: ", self.p_id)
        self.amenities_pd = pd.DataFrame(mlist)
        # attributes
        qry = " SELECT pa.property_id as property_id , co.co_name, co.co_value, IFNULL(pa.value,'') as pa_value "
        qry += " FROM pm.property_attribute pa ,pm.cores co "
        qry += " WHERE co.co_name=pa.name  and co.co_type='PROPERTY_SCHOOLS' and pa.property_id=" + str(self.p_id)
        qry += " UNION "
        qry += " SELECT "+ str(self.p_id) + " as property_id , co2.co_name, co2.co_value, '' "
        qry += " FROM pm.cores co2 WHERE co2.co_type='PROPERTY_SCHOOLS' and co2.co_name not in "
        qry += "( select pa2.name FROM pm.property_attribute pa2 where pa2.property_id="+ str(self.p_id) +")"
        self.logger.debug("PMProperty::updatePInfo 16:%s", qry)
        mlist = PMDB.query_list(db, qry, None)
        #print("PMProperty::Query List: Property Attribute: ", self.p_id)
        self.school_pd = pd.DataFrame(mlist)

        # admin info
        qry = " SELECT pa.property_id as property_id , co.co_name, co.co_value, IFNULL(pa.value,'') as pa_value "
        qry += " FROM pm.property_attribute pa ,pm.cores co "
        qry += " WHERE co.co_name=pa.name  and co.co_type='PROPERTY_ADMIN' and pa.property_id=" + str(self.p_id)
        qry += " UNION "
        qry += " SELECT "+ str(self.p_id) + " as property_id , co2.co_name, co2.co_value, '' "
        qry += " FROM pm.cores co2 WHERE co2.co_type='PROPERTY_ADMIN' and co2.co_name not in "
        qry += "( select pa2.name FROM pm.property_attribute pa2 where pa2.property_id="+ str(self.p_id) +")"
        self.logger.debug("PMProperty::updatePInfo 18:%s", qry)
        mlist = PMDB.query_list(db, qry, None)
        #print("PMProperty::Query List: Property Attribute: ", self.p_id)
        self.admin_pd = pd.DataFrame(mlist)

        # appliances
        qry = " SELECT pa.property_id as property_id , co.co_name, co.co_value, pa.appliance, pa.make, pa.model, pa.value, date_format(pa.start_date,'%Y-%m-%dT%H:%i:%S') as start_date, pa.status, co1.co_value as a_status "
        qry += " FROM pm.property_appliance pa ,pm.cores co, pm.cores co1 "
        qry += " WHERE co.co_name=pa.appliance  and co.co_type='PROPERTY_APPLIANCE' and co1.co_type='APPLIANCE_STATUS' and co1.co_name=pa.status and pa.property_id=" + str(self.p_id)
        qry += " UNION "
        qry += " SELECT "+ str(self.p_id) + " as property_id , co2.co_name, co2.co_value, co2.co_name, '','','','1900-01-01T00:00:00',0,'Unknown' "
        qry += " FROM pm.cores co2 WHERE co2.co_type='PROPERTY_APPLIANCE' and co2.co_name not in "
        qry += "( select pa2.appliance  from pm.property_appliance pa2 where pa2.property_id="+ str(self.p_id) +")"
        self.logger.debug("PMProperty::updatePInfo 21:%s", qry)
        mlist = PMDB.query_list(db, qry, None)
        #print("PMProperty::Query List: Property Attribute: ", self.p_id)
        self.appl_pd = pd.DataFrame(mlist)

        # services
        qry = " SELECT pa.property_id as property_id , co.co_name, co.co_value, pa.service, pa.vendor_id, v.label, pa.account, pa.reference, pa.value "
        qry += " FROM pm.property_service pa ,pm.cores co, pm.vendors v "
        qry += " WHERE co.co_name=pa.service  and pa.vendor_id = v.vendor_id and co.co_type='PROPERTY_SERVICE' and pa.property_id=" + str(self.p_id)
        qry += " UNION "
        qry += " SELECT "+ str(self.p_id) + " as property_id , co2.co_name, co2.co_value, co2.co_name,-1,'','','','' "
        qry += " FROM pm.cores co2 WHERE co2.co_type='PROPERTY_SERVICE' and co2.co_name not in "
        qry += "( select pa2.service  from pm.property_service pa2 where pa2.property_id="+ str(self.p_id) +")"
        self.logger.debug("PMProperty::updatePInfo 22:%s", qry)
        mlist = PMDB.query_list(db, qry, None)
        #print("PMProperty::Query List: Property Attribute: ", self.p_id)
        self.service_pd = pd.DataFrame(mlist)

        # tenancy list
        qry = " SELECT * FROM pm.tenancy WHERE property_id="+ str(self.p_id) +" ORDER BY end_date"
        self.logger.debug("PMProperty::updatePInfo TENANCY 23:%s", qry)
        mlist = PMDB.query_list(db, qry, None)
        #print("PMProperty::Query List: Property Attribute: ", self.p_id)
        self.tenancies_pd = pd.DataFrame(mlist);
        
        # pics
        qry = "call getPropertyPics ("+str(self.p_id)+")"
        self.logger.debug("PMProperty::updatePInfo 25:%s", qry)
        mlist = PMDB.query_list(db, qry, None)
        self.pics_pd = pd.DataFrame(mlist)

        sqls = "select * from pm.property_rental where property_id= "+ str(self.p_id);
        self.logger.debug("PMProperty::updatePInfo 26:%s", sqls)
        mlist = PMDB.query_list(db,sqls,None)
        self.rental_pd = pd.DataFrame(mlist)
            
        # Tenant Info
        if ( self.p_status.lower() == 'occupied'):
            sqls = "select p.label, tc.tenant_id, tc.rent, tc.deposit, date_format(tc.start_date,'%Y-%m-%dT%H:%i:%S') as sdate, date_format(tc.end_date,'%Y-%m-%dT%H:%i:%S') as edate, tn.first_name, tn.last_name "
            sqls += " from pm.property p, pm.tenancy tc, pm.tenants tn "
            sqls += " where p.property_id=tc.property_id "
            sqls += " and tc.tenant_id=tn.tenant_id and tc.status=1 "
            sqls += " and p.property_id=" + str(self.p_id) 
            sqls += " order by tc.start_date"
            
            self.logger.debug("PMProperty::updatePInfo 3:%s", sqls)
            mlist = PMDB.query_list(db,sqls,None)
            for x in mlist:
            #print(x)
                self.core['tenant_id']=x['tenant_id']
                self.core['tenant']=x['first_name']+ " " + x['last_name']
                self.core['lease_start']=x['sdate']
                self.core['lease_end']=x['edate']
                self.core['sd']=x['deposit']
                self.core['rent']=x['rent']
        
        
            
        # check for child
        if ( self.parent == "" or self.parent == None ):
            qry = "call getPropertyChildren (" + str(self.p_id) +")";
            self.logger.debug("PMTenant::updatePInfo 4: %s", qry)
            
            mlist = PMDB.query_list(db,qry, None)
            
            self.children_pd = pd.DataFrame(mlist)
        
        if ( self.children_pd.empty != True ):
            self.children_p_id = str(self.p_id);
            for ind in self.children_pd.index:
                sqls = "select p.property_id, tc.tenant_id, tc.rent, tc.deposit, date_format(tc.start_date,'%Y-%m-%dT%H:%i:%S') as lease_start, date_format(tc.end_date,'%Y-%m-%dT%H:%i:%S') as lease_end, tn.first_name, tn.last_name "
                sqls += " from pm.property p, pm.tenancy tc, pm.tenants tn "
                sqls += " where p.property_id=tc.property_id "
                sqls += " and tc.tenant_id=tn.tenant_id "
                sqls += " and tc.responsible = 1 and tc.status in (1,4,5) "
                sqls += " and p.property_id=" + str(self.children_pd['property_id'][ind]);
                self.logger.debug("PMTenant::updatePInfo 5:%s", sqls)
                mlist = PMDB.query_list(db,sqls,None)
                #print("PMProperty::Query List: Property Attribute: ", self.p_id)
                #self.children_pd = pd.DataFrame(mlist)
                for x in mlist:
                #print(x)
                    self.children_pd['tenant_id'][ind]=x['tenant_id']
                    self.children_pd['tenant'][ind]=x['first_name']+ " " + x['last_name']
                    self.children_pd['lease_start'][ind]=x['lease_start']
                    self.children_pd['lease_end'][ind]=x['lease_end']
                    self.children_pd['deposit'][ind]=x['deposit']
                    self.children_pd['rent'][ind]=x['rent']
                    self.children_p_id += "," + str(x['property_id'])
                    
        self.info_updated=1
        
    def updateFTS(self, db):
        
        t_dict = {}

        sqls = "SELECT t.tx_id as t_id, 'TX' as type, p.property_id, p.label,c.category_id, date_format(t.tdate,'%Y-%m-%dT%H:%i:%S') as tdate, t.credit, t.debit, (t.credit - t.debit) as amount, t.description,"
        sqls += "c.label as category_name, t.payee, t.reference "
        sqls += "FROM pm.property p, pm.transactions t, pm.category c "
        sqls += "WHERE p.property_id = t.property_id AND t.category_id = c.category_id "
        if ( self.children_p_id != "" ):
            sqls += " AND p.property_id in ( " + str(self.children_p_id) + ")"
        elif (self.p_id != "" ):
            sqls += " AND p.property_id in (" + str(self.p_id) + ")"
        
        if ( self.d1 ):  
            sqls += " and t.tdate >= '" + self.d1 + "' "
        if ( self.d2 ):  
            sqls += " and t.tdate <= '" + self.d2 + "' "
 
        sqls += " ORDER BY t.tdate"
            
        self.logger.debug("pm_property.updateFTS:%s",sqls)
        mlist = PMDB.query_list1(db, sqls)
        self.c_pd = pd.DataFrame(mlist)
        #t_dict = {"Category": my_categories.keys()}
        t_dict = self.my_categories.keys()
        #print("Dict:", t_dict)
        t_pd = pd.DataFrame(t_dict)
        t_pd = t_pd.rename(columns={0:'category'})
 
        t_pd['total']=0.0
        
        t_pd = t_pd.set_index('category')
         
        for x in mlist:
            #print("Date:", x)
            s = x['category_id']
            c = x['label']
            
            if c in t_pd.columns:
                t_pd.at[s, c] += x['amount']
                #t_pd.at[s,'current'] += x['amount']
            else:
                t_pd[c]=0.0
                t_pd.at[s,c]=x['amount']
                #t_pd.at[s,'current'] += x['amount']
            # Parent update
            ps = self.my_categories[s][4]
            while ( ps and ps != '' ):
                #print ("updateFS: code:", s, " parent:", ps, " column:", c, " amount:", x['amount'])
                t_pd.at[ps,c] += x['amount']
                ps = self.my_categories[ps][4]             
        
        t_pd['total'] = t_pd.sum(axis=1)

        t_pd['name']=""
        for k in t_dict:
            t_pd.at[k,'name'] = self.my_categories[k][2]
        
        self.t_pd = t_pd #.drop([1,2,3,4,5,6,7])
        
    def updateTS(self, db):
        
        sqls = "SELECT c.category_id, t.tdate, sum(t.credit - t.debit) as amount "
        sqls += "FROM pm.property p, pm.transactions t, pm.category c "
        sqls += "WHERE p.property_id = t.property_id AND t.category_id = c.category_id "
        sqls += " AND p.property_id = " + str(self.p_id)
        sqls += " ORDER BY c.code, t.tdate"
            
        self.logger.debug("pm_property.updateTS:%s",sqls)
        mlist = PMDB.query_list1(db, sqls)
        
        
    def updateSTATS(self):
        #self.t_pd[]        
        
        self.logger.debug("Update STATS:%s", self.t_pd)
     
        
    def getTS(self):
        
        l_amount = 0
        
        for idx in self.c_pd.index:
#    print(ind, ":", df.at[ind,'Amount'], " = ", df.at[ind, 'Tenant'])
            #print("PProperty::getTS:debit: ", self.c_pd.at[idx,'debit'], " credit: ",self.c_pd.at[idx,'credit'], " amount: ", self.c_pd.at[idx,'amount'], " last:", l_amount)
            
            self.c_pd.at[idx,'amount'] += l_amount
            l_amount = self.c_pd.at[idx,'amount']
        
        return self.c_pd
    
    def getSTATS(self):

        return self.t_pd   
    
    def getCF(self):
        
        self.fins = {
                    "START_DATE": self.d1,
                    "END_DATE": self.d2 }
        
        for idx in self.t_pd.index:
        #    #print("PProperty::getCF:", self.t_pd.at[idx, 'total'], " category:", self.t_pd.at[idx, 'name'])
            self.fins[self.t_pd.at[idx, 'name']]= self.t_pd.at[idx, 'total']
        
        return self.fins
            
        
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