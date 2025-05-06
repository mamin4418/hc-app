# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 14:26:13 2019

@author: ppare
"""
import pandas as pd
from utils.pm_db import PMDB

def get_parking_lot_pd(db, logger, qj):

    core = {}
    if ( 'params' in qj):
        core = qj['params']
    else:
        core = qj
    
    qry = "SELECT p.* "
    qry += " FROM pm.parking_lot p "
    qry +=" WHERE p.pl_status = 'ACTIVE' "
        
    if ( 'company' in core and core['company'] != "" ):
        qry += " and p.llc = '"+core['company']+"'"
    
    if('group' in core and core['group'] != ""):
        qry += " and p.group = '"+core['group']+"'"
    
    if('status' in core):
        qry += " and p.pl_status = '"+core['status']+"'"

    if('tranche_id' in core):
        qry += " and p.tranche_id = "+str(core['tranche_id'])

    qry += " order by p.label2"    
    logger.debug("get_parking_lot_pd::%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.set_index('pl_id')
    return t_pd

def get_company_info_pd(db, logger):
    
    
    qry = "SELECT * FROM pm.company "
        
    logger.debug("get_company_info_pd: %s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.set_index('company_id')
    
    return t_pd
# Properties    
def get_my_properties(db, logger, user_id=-1):
    
    qry = "SELECT p.property_id, p.llc, p.group, lower(p.label) as label, p.unit, p.label2 FROM pm.property p";
    if ( user_id > 0 ):
        qry +=", pm.auth_users_attributes aua where p.property_id > 0 and aua.id_type='property_id' and aua.id_value = p.property_id and aua.user_id ="+str(user_id)
        
    mlist = PMDB.query_list(db,qry, None)
    mdict = {}
    
    for x in mlist:
        s = x['label']
        mdict[s]=[x['property_id'],x['label'],x['label2'], x['unit'],x['llc'], x['group']]
    
    return mdict
    
    
def get_my_properties_pd(db, logger, qj, user_id=-1):

    core = {}
    if ( 'params' in qj):
        core = qj['params']
    
    qry = "SELECT p.property_id, p.llc as company, p.group, p.label, p.unit, p.label2, p.parent, p.city, p.state, p.zip, p.p_status, p.bed, p.bath, p.market_rent, p.total_rooms, p.size, p.location "
    qry += " FROM pm.property p "
    
    if ( user_id > 0 ):
        qry +=", pm.auth_users_attributes aua where p.property_id > 0 and aua.id_type='property_id' and aua.id_value = p.property_id and aua.user_id ="+str(user_id)
    else:
        qry +=" WHERE p.property_id > 0 "
        
    if ( 'company' in core and core['company'] != "" ):
        qry += " and p.llc = '"+core['company']+"'"
    
    if('group' in core and core['group'] != ""):
        qry += " and p.group = '"+core['group']+"'"
    
    if('status' in core):
        qry += " and p.p_status = '"+core['status']+"'"

    if('tranche_id' in core):
        qry += " and p.tranche_id = "+str(core['tranche_id'])
    qry += " order by p.label2"    
    logger.debug("get_my_properties_pd::%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    if ( not t_pd.empty ):
        t_pd = t_pd.rename(columns={0:'property_id',1:'company',2:'group',3:'label',4:'unit',5:'label2', 6:'parent', 7:'city', 8:'state', 9:'zip', 10:'status', 11:'bed', 12:'bath',13:'market_rent',14:'total_rooms',15:'size', 16:'location'})
        t_pd = t_pd.set_index('property_id')
    
    return t_pd
def get_my_property_by_id(db, logger, id):
    
    mlist = PMDB.query_list(db,"SELECT p.property_id, p.llc, p.group, p.label, p.unit, p.label2, p.city, p.state, p.zip FROM pm.property p WHERE p.property_id= %s", id)
    mdict = {}
    logger.debug("Query List: Property:%s", id)
    for x in mlist:
        mdict=x

    return mdict    
def get_my_property(db, logger, c):
    
    c = '%'+c+'%'
    mlist = PMDB.query_list(db,"SELECT p.property_id, p.llc, p.group, p.label, p.unit, p.label2, p.city, p.state, p.zip FROM pm.property p WHERE p.label LIKE %s", c)
    mdict = {}
    logger.debug("Query List: Property:%s", c)
    for x in mlist:
        #print(x)
        s = x['label']
        if (str(x['unit']) != 'None'):
            s = str(x['label'])+str('-')+str(x['unit'])
        mdict[s]=[x['property_id'],x['label'], x['label2'], x['unit'], x['llc'], x['group']]

    return mdict

def get_property_ts(db, logger, c):
    
    c = '%'+c+'%'
    mlist = PMDB.query_list(db,"SELECT p.label,c.code, c.name, t.date, t.payee, t.type, t.reference, t.amount, t.description FROM pm.property p, pm.transactions t, pm.category c WHERE p.label LIKE %s AND p.property_id = t.property_id AND t.category_id = c.category_id order by c.display_order", c)
    
    b = pd.DataFrame(mlist) 
    
    return b
def get_my_categories(db, logger):
    
    mlist = PMDB.query_list(db,"SELECT c.category_id, c.code, c.keyword, c.label, c.name, c.parent, c.display_order,c.type FROM pm.category c order by c.label", None)
    mdict = {}
    for x in mlist:
        #print(x)
        label = x['label']
        mdict[x['code']]=[x['category_id'],x['code'],x['keyword'],x['name'], x['parent'], label, x['display_order'], x['type']]

    #print(mdict)
    return mdict

def get_my_categories_pd(db, logger, c_type=""):
    
    qry = "SELECT c.category_id, c.code, c.keyword, c.label, c.name, c.parent, c.display_order, c.type FROM pm.category c "
    if ( c_type != None and c_type != ""):
        qry += " WHERE c.type='"+c_type+"' "
    qry += " ORDER BY c.name"

    logger.debug("get_my_categories_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.rename(columns={0:'category_id',1:'code',2:'keyword',3:'label',4:'name',5:'parent', 6:'order', 7:'type'})
    
    t_pd = t_pd.set_index('category_id')

    return t_pd
def get_my_categories_by_id(db, logger, tp):
    mdict = {}
    sqls = "SELECT c.category_id, c.code, c.keyword, c.label, c.name, c.parent, c.display_order, c.type FROM pm.category c order by c.name"
    if ( tp == 'EXPENSE'):
        sqls = "SELECT c.category_id, c.code, c.keyword, c.label, c.name, c.parent, c.display_order, c.type FROM pm.category c "
        sqls += " WHERE c.type='EXPENSE' order by c.name"
    elif ( tp == 'RECEIVABLE' ):
        sqls = "SELECT c.category_id, c.code, c.keyword, c.label, c.name, c.parent, c.display_order, c.type FROM pm.category c "
        sqls += " WHERE c.type='RECEIVABLE' order by c.name"
        
    mlist = PMDB.query_list1(db,sqls)
    for x in mlist:
        #print(x)
        label = x['label']
        if ( x['type'] == 'EXPENSE'):
            label += " (E)"
        if ( x['type'] == 'RECEIVABLE'):
            label += " (R)"
            
        mdict[x['category_id']]=[x['category_id'],x['code'],x['keyword'],x['name'], x['parent'], label, x['display_order'], x['type']]

    #print(mdict)
    return mdict  
def get_my_categories_by_id2(db, logger, cat):
    mdict = {}
    sqls = "SELECT c.* FROM pm.category c WHERE c.category_id="+str(cat)
        
    mlist = PMDB.query_list1(db,sqls)
    for x in mlist:
        #print(x)
        mdict=x

    #print(mdict)
    return mdict        
def get_my_tenants_on(db, logger, user_id=-1):
    
    mlist = PMDB.query_list(db,"SELECT tenant_id,first_name,last_name,other_names,tax_id,phone,email,status FROM pm.tenants where tenant_id order by first_name", None)
    mdict = {}
    s1=""
    s2=""
    for x in mlist:
        #print(x)
        if ( x['last_name'] != ""):
            s1 = x['last_name']+", "+x['first_name']
            s2 = x['first_name'] + " " + x['last_name']
        else:
            s1 = x['first_name'].strip()
            s2 = x['first_name'].strip()
        mdict[s1.lower()]=[x['tenant_id'],x['first_name'],x['last_name'], x['other_names'],x['tax_id'], x['phone'],x['email'],x['status']]
        #print(s, "=>", x, " Tenant:", str(x['other_names']), "key:", s)
        
        mdict[s2.lower()]=[x['tenant_id'],x['first_name'],x['last_name'], x['other_names'],x['tax_id'], x['phone'],x['email'],x['status']]
        #print(s, "=>", x, " Tenant:", str(x['other_names']), "key:", s)
        s = x['other_names']
        mdict[s.lower()]=[x['tenant_id'],x['first_name'],x['last_name'], x['other_names'],x['tax_id'], x['phone'],x['email'],x['status']]

    return mdict 
def get_my_tenants_names_pd(db, logger, sta, user_id=-1):
    
    qry = "SELECT t.tenant_id,t.first_name,t.last_name,t.other_names FROM pm.tenants t "
    qry += " order by t.first_name, t.last_name"
    logger.debug("get_my_tenants_names_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.rename(columns={0:'tenant_id',1:'first_name',2:'last_name',3:'other_names'})
    t_pd = t_pd.set_index('tenant_id')

    return t_pd

def get_my_tenants_pd(db, logger, qj, user_id=-1):
    
    user_id=0
    logger.debug("get_my_tenants_pd:entering: %s", qj)    
    qry = "SELECT t.tenant_id,t.first_name,t.last_name,t.other_names,'' as tax_id,t.phone,t.email,t.status,t.relationship FROM pm.tenants t "
    
    if ( user_id > 0 and qj['navigation'] not in ['/sm','/m','/admin']):
        qry +=", pm.auth_users_attributes aua where t.tenant_id > 0 and aua.id_type='tenant_id' and aua.id_value = t.tenant_id and aua.user_id ="+str(user_id)
    else:
        qry +=" where t.tenant_id > 0 "

    if ('status' in qj and qj['status'] != ""):
        qry += " and t.status="+str(qj['status'])
    else:
        qry += " and t.status in (1,2) "

    if ( 'tenant_type' in qj and qj['tenant_type'] == "LEASABLE" ):
        qry += " and t.relationship in ('S','HH') "
    elif ('relationship' in qj):
        qry += " and t.relationship='"+qj['relationship']+"' "

    #if ('company' in qj):
    #    qry += " and t.status="+str(qj['company'])
    #else:
    #    qry += " and t.status=1 "

    qry += " order by t.first_name, t.last_name"
    logger.debug("get_my_tenants_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.rename(columns={0:'tenant_id',1:'first_name',2:'last_name',3:'other_names',4:'tax_id',5:'phone', 6:'email', 7:'status'})
    if ( not t_pd.empty ):
        t_pd = t_pd.set_index('tenant_id')

    return t_pd

def get_my_tenants_pet_pd(db, logger, qj, user_id=-1):
    
    user_id=0
    logger.debug("get_my_tenants_pet_pd:entering: %s", qj)    
    qry = "SELECT t.tenant_id,t.first_name,t.last_name,t.other_names,t.phone,t.email,t.status, tp.* FROM pm.tenants t, pm.tenants_pet tp "
    
    if ( user_id > 0 and qj['navigation'] not in ['/sm','/m','/admin']):
        qry +=", pm.auth_users_attributes aua where t.tenant_id > 0 and aua.id_type='tenant_id' and aua.id_value = t.tenant_id and aua.user_id ="+str(user_id)
    else:
        qry +=" where t.tenant_id > 0 "

    qry += " and t.tenant_id = tp.tenant_id "
    if ('status' in qj and qj['status'] != ''):
        qry += " and t.status="+str(qj['status'])
    else:
        qry += " and t.status=1 "


    qry += " order by t.first_name, t.last_name"
    logger.debug("get_my_tenants_pet_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    #t_pd = t_pd.rename(columns={0:'tenant_id',1:'first_name',2:'last_name',3:'other_names',4:'tax_id',5:'phone', 6:'email', 7:'status'})
    t_pd = t_pd.set_index('tenant_id')

    return t_pd

def get_my_tenants_vehicle_pd(db, logger, qj, user_id=-1):
    
    user_id=0
    logger.debug("get_my_tenants_pd:entering: %s", qj)    
    qry = "SELECT t.tenant_id,t.first_name,t.last_name,t.other_names,'' as tax_id,t.phone,t.email,t.status,tv.* FROM pm.tenants t, pm.tenants_vehicle tv "
    
    if ( user_id > 0 and qj['navigation'] not in ['/sm','/m','/admin']):
        qry +=", pm.auth_users_attributes aua where t.tenant_id > 0 and aua.id_type='tenant_id' and aua.id_value = t.tenant_id and aua.user_id ="+str(user_id)
    else:
        qry +=" where t.tenant_id > 0 "

    qry += " and t.tenant_id = tv.tenant_id "
    if ('status' in qj and qj['status'] != ''):
        qry += " and t.status="+str(qj['status'])
    else:
        qry += " and t.status=1 "

    qry += " order by t.first_name, t.last_name"
    logger.debug("get_my_tenants_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    #t_pd = t_pd.rename(columns={0:'tenant_id',1:'first_name',2:'last_name',3:'other_names',4:'tax_id',5:'phone', 6:'email', 7:'status'})
    t_pd = t_pd.set_index('tenant_id')

    return t_pd

def get_my_tenants_by_id(db,logger, tenant_id):
    mdict={}
    qry = "SELECT * FROM pm.tenants t "   
    qry +=" where t.tenant_id = "+str(tenant_id)
        
    logger.debug("get_my_tenants_by_id:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    for x in mlist:
        mdict=x

    return mdict
def get_my_tenants_pd2(db,logger, tenant_id):
    
    qry = "SELECT t.tenant_id,t.first_name,t.last_name,t.other_names,'' as tax_id,t.phone,t.email,t.status,t.relationship FROM pm.tenants t "   
    qry +=" where t.tenant_id = "+str(tenant_id)
        
    logger.debug("get_my_tenants_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.rename(columns={0:'tenant_id',1:'first_name',2:'last_name',3:'other_names',4:'tax_id',5:'phone', 6:'email', 7:'status'})
    t_pd = t_pd.set_index('tenant_id')

    return t_pd

def search_my_tenants_pd(db,logger, core):
    logger.debug("search_my_tenants_pd1:%s", core)    
    qry = "SELECT t.tenant_id,t.first_name,t.last_name,t.other_names,t.tax_id,t.phone,t.email,t.dob,t.dl_state,t.dl_id,t.status FROM pm.tenants t "   
    qry +=" where ( lower(t.other_names) like '%" + core['first_name'].lower() +"%' "
        
    if ( "dl_id" in core and core['dl_id'] != None ):
        qry += " OR ( t.dl_id = '"+core['dl_id'] + "' and t.dl_state='" + core['dl_state'] +"' ) "
    if ( "tax_id" in core and core['tax_id'] != '' ):
        qry += " OR ( t.tax_id = '"+core['tax_id'] + "') "
    if ( "dob" in core and core['dob'] != '' ):
        qry += " OR ( t.dob = '"+core['dob'] + "') )"

    if ( 'EXCLUDE_TENANT_ID' in core ):
        qry += " AND t.tenant_id != "+str(core['EXCLUDE_TENANT_ID'])
    logger.debug("search_my_tenants_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    if ( not t_pd.empty ):
        t_pd = t_pd.rename(columns={0:'tenant_id',1:'first_name',2:'last_name',3:'other_names',4:'tax_id',5:'phone', 6:'email', 7:'dob', 8:'dl_state', 9:'dl_id', 10:'status'})
        t_pd = t_pd.set_index('tenant_id')

    return t_pd

def get_my_tenancy_pd(db, logger, params):
    logger.debug("get_my_tenancy_pd:%s", params)    
    if ( 'user_id' not in params):
        params['user_id']=-1
    if ( 'company' not in params or params['company'] == ''):
        params['company']='ALL'
    if ( 'tranche_id' not in params):
        params['tranche_id']=-1

    if ( params['company'] == 'ALL' and params['tranche_id'] == -1 ):
        return pd.DataFrame
    # qry = "call getTenancy ("+str(params['user_id'])+",'"+params['company']+"',"+str(params['tranche_id'])+",'"+ params['report_date']+"')"
    
    # logger.debug("ref_data.get_my_tenancy_pd:%s", qry)    
    
    # mlist = PMDB.query_list1(db,qry)
    # t_pd = pd.DataFrame(mlist)
    # t_pd = t_pd.set_index('property_id')
    # return t_pd


    qry = "select p.property_id, p.label, p.street, p.city, p.state, p.zip, p.llc as company, p.group as p_group "
    qry += ", p.market_rent, p.p_status, p.unit  "
    qry += " from pm.property p "
    if (  int(params['tranche_id']) > 0 ):
        qry += "where p.tranche_id="+str(params['tranche_id']) + " and p.p_status not in ('SOLD', 'MASTER', 'ROOT')"
    elif (params['company'] != 'ALL'):
        qry += "where p.llc='"+params['company'] + "' and p.p_status not in ('SOLD', 'MASTER', 'ROOT')"
    else:
        qry += "where p.p_status not in ('SOLD', 'MASTER', 'ROOT')"
    qry += " order by p.property_id "
    logger.debug("get_my_tenancy_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)
    flist = []
    for p in mlist:

        logger.debug("get_my_tenancy_pd:2:%s", p)
        #t_pd.at[ind,'balance'] = l_pd.at[ind,'credit'] - l_pd.at[ind,'debit'] + lb
        #lb = l_pd.at[ind,'balance']
        qry = "SELECT tc.tenancy_id, t.tenant_id,t.first_name,t.last_name,t.status as t_status, t.email as tenant_email,"
        qry += " date_format(tc.start_date,'%Y-%m-%d') as lease_start_date, date_format(tc.end_date,'%Y-%m-%d') as lease_end_date,"
        qry += " date_format(tc.move_in,'%Y-%m-%d') as move_in, date_format(ifnull(tc.move_out,'20991231'),'%Y-%m-%d') as move_out,"
        qry += "tc.rent, tc.deposit, tc.deposit_a, tc.phone, tc.email,tc.responsible,tc.family_members, tf.balance as balance,"
        qry += "tc.status as tc_status"
        qry += " FROM pm.tenants t, pm.tenancy tc, pm.tenants_financials tf "
        qry += " WHERE tc.property_id = "+str(p['property_id'])+" and t.tenant_id = tc.tenant_id  and tf.tenant_id = t.tenant_id "
        qry += " and tc.start_date <= '"+params['report_date']+"' and ( tc.end_date>='"+params['report_date']+"' OR tc.status in (1)) "
        qry += " order by move_out"
        logger.debug("ref_data.get_my_tenancy_pd:%s", qry)    

        nlist = PMDB.query_list1(db,qry)
        logger.debug("get_my_tenancy_pd:%s, %s", qry, len(nlist))
        for x in nlist:
            logger.debug("get_my_tenancy_pd:========%s | %s", x, params['report_date'])
            if ( len(nlist) == 1 and x['tc_status'] != 2):
                p['tenancy_id']=x['tenancy_id']
                p['tenant_id']=x['tenant_id']
                p['first_name']=x['first_name']
                p['last_name']=x['last_name']
                p['t_status']=x['t_status']
                p['tenant_email']=x['tenant_email']
                p['lease_start_date']=x['lease_start_date']
                p['lease_end_date']=x['lease_end_date']
                p['move_in']=x['move_in']
                p['move_out']=x['move_out']
                p['rent']=x['rent']
                p['deposit']=x['deposit']
                p['deposit_a']=x['deposit_a']
                p['phone']=x['phone']
                p['email']=x['email']
                p['responsible']=x['responsible']
                p['family_members']=x['family_members']
                p['balance']=x['balance']
                p['tc_status']=x['tc_status']
                p['aa_name']=""
                p['aa_value']=""
            elif( x['move_out'] > params['report_date']):
                p['tenancy_id']=x['tenancy_id']
                p['tenant_id']=x['tenant_id']
                p['first_name']=x['first_name']
                p['last_name']=x['last_name']
                p['t_status']=x['t_status']
                p['tenant_email']=x['tenant_email']
                p['lease_start_date']=x['lease_start_date']
                p['lease_end_date']=x['lease_end_date']
                p['move_in']=x['move_in']
                p['move_out']=x['move_out']
                p['rent']=x['rent']
                p['deposit']=x['deposit']
                p['deposit_a']=x['deposit_a']
                p['phone']=x['phone']
                p['email']=x['email']
                p['responsible']=x['responsible']
                p['family_members']=x['family_members']
                p['balance']=x['balance']
                p['tc_status']=x['tc_status']
                p['aa_name']=""
                p['aa_value']=""
            else:
                p['rent']=0.0
                p['deposit']=0.0
                p['deposit_a']=0.0
                p['balance']=0.0

        flist.append(p)

    t_pd = pd.DataFrame(flist)
    t_pd = t_pd.set_index('property_id')
    return t_pd

def get_my_cores_info(db, logger, co_type, co_name):
    mdict = {}
    qry = "select * from pm.cores co where co.co_type='" + co_type + "' and co.co_name='"+co_name+"'"

    logger.debug("get_my_cores_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    for x in mlist:
        mdict=x
    return mdict
def get_my_cores_pd(db, logger, co_type):
    
    qry = "select * from pm.cores co"
    
    if ( co_type != None and co_type != ""):
        qry += " where co.co_type='" + co_type + "'"
    
    qry += " order by co.co_value "

    logger.debug("get_my_cores_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.rename(columns={0:'co_id',1:'co_type',2:'co_name',3:'co_value'})
    t_pd = t_pd.set_index('co_id')

    return t_pd

def get_my_cores_pd2(db, logger, co_type):
    

    qry = "select * from pm.cores co"
    
    if ( co_type != None and co_type != ""):
        qry += " where co.co_type='" + co_type + "'"
    
    qry += " order by co.co_value "

    logger.debug("get_my_cores_pd2:%s", qry)    
    mlist = db.query_list(qry, None)

    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.rename(columns={0:'co_id',1:'co_type',2:'co_name',3:'co_value'})
    t_pd = t_pd.set_index('co_id')

    return t_pd



def getSTATS(c_pd, ts):
    if ( ts == None or ts == ""):
        ts = "value"
    stats = {}
    stats["mean"] = c_pd[ts].mean()
    stats["median"] = c_pd[ts].median()
    stats["min"] = c_pd[ts].min()
    stats["max"] = c_pd[ts].max()
    stats["sum"] = c_pd[ts].sum()
    stats["std"] = c_pd[ts].std()
    
    return stats