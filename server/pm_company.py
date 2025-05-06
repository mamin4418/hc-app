# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 11:00:05 2020

@author: ppare
"""

import pandas as pd
from utils.pm_db import PMDB

        
def getCompany( db, logger, core):
        
    qry = ""
    mlist={}
    data={}

    logger.debug("getCompany:Query1: %s", core)
    id_v=-1;
    company_id=-1
    if ('id_value' in core ):
        id_v = str(core['id_value'])

    if ( 'company_id' in core and core['company_id'] > 0 ):
        company_id = core['company_id']

    if ( company_id > 0):
        qry = " SELECT * from pm.company where company_id= " + str(core['company_id'])
    elif ( 'id_type' in core and core['id_type'] == 'property_id'):
        qry = " SELECT * from pm.company c, pm.property p where p.llc = c.label and p.property_id="+id_v
    elif ( 'id_type' in core and core['id_type'] == 'tenant_id'):
        qry = " SELECT * from pm.company c, pm.property p, pm.tenancy tc where p.property_id=tc.property_id and p.llc = c.label and tc.tenant_id="+id_v
    elif ( 'id_type' in core and core['id_type'] == 'tenancy_id'):
        qry = " SELECT * from pm.company c, pm.property p, pm.tenancy tc where p.property_id=tc.property_id and p.llc = c.label and tc.tenancy_id="+id_v
    else:
        mlist['status']='FAILED'
        mlist['code']=1
        mlist['message']="No valid identifier available for company"
        return mlist
    
    logger.debug("getCompany:Query1: %s", qry)
    mlist = PMDB.query_list(db,qry, None)

    for x in mlist:
        data=x

    logger.debug("getCompany:Query1: %s", data)

    if ( company_id < 0 ):
        company_id = data['company_id']

    if ( company_id > 0 ):
        qry = "select ca.* from pm.company_attribute ca where ca.company_id="+str(company_id)
        tlist = PMDB.query_list(db,qry, None)
        data['attributes'] = pd.DataFrame(tlist).to_json(orient='table')
        

    return data

def getCompanies( db, logger, core):
        
    qry = ""
    attr_pd = None
    mlist={}
    
    logger.debug("pm_company:getCompanies:1:%s", core)
    qry = " SELECT c.* from pm.company c, pm.auth_users_attributes aua where aua.id_type= 'company_id' and aua.id_value=c.company_id "
    qry += " and aua.user_id="+str(core['user_id'])
    qry += " order by c.label"
    
    logger.debug("pm_company:getCompanies:Query1:%s", qry)
    mlist = PMDB.query_list(db,qry, None)
    
    attr_pd = pd.DataFrame(mlist)
    
    logger.debug("getCompanies:%s", attr_pd)

    return attr_pd