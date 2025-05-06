# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:04:13 2020

@author: ppare
"""
from flask import json
import pandas as pd
from utils.pm_db import PMDB
import pm_user, utils.pm_mail, analysis.pm_financials, utils.pm_print, ref_data


def updateProperty(O_db, logger, qj):

    core = {}
    ret=-1
    sqls = ""
    logger.info("pm_update::updateProperty0:%s",qj)
    
    qf = fetchTextfromQ(logger,qj,'qualifier')
    for x in qj:
        core[x] = fetchTextfromQ(logger,qj,x)  
    
    p_id = int(core['property_id'])
    if ( 'end_date' not in core or core['end_date'] == ''):
        core['end_date'] = '2100-12-31';
    if ( 'parent' not in core or core['parent'] == ''):
        core['parent'] = 1;

    if (p_id < 0):
        sqls = "call updateProperty (-1,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s)"
        mlist = PMDB.query_list(O_db,sqls,(core['company'],core['tranche_id'], core['group'],core['start_date'],core['end_date'],
            core['label'],core['label2'],core['street'],core['unit'],core['city'],core['state'], core['zip'],core['parent'],
            core['tax_id'],core['p_type'],core['built'],core['size'],core['bed'],core['bath'],core['total_rooms'],core['p_status'],
            core['market_rent'], core['sub_units'],core['location'],core['description'], core['user_id']))
        
        for x in mlist:
            p_id=x['property_id']
        
        logger.debug("pm_update.updateProperty:: new property id=%s",p_id)

        return p_id

    elif ( qf == 'PRIMARY') :
        
        try:
            sqls = "call updateProperty (%s,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s)"
            mlist = PMDB.query_list(O_db,sqls,(core['property_id'],core['company'],core['tranche_id'],core['group'],core['start_date'],
                core['end_date'],core['label'],core['label2'],core['street'],core['unit'],core['city'],core['state'], core['zip'],
                core['parent'],core['tax_id'],core['p_type'], core['built'],core['size'],core['bed'],core['bath'],core['total_rooms'],
                core['p_status'],core['market_rent'], core['sub_units'],core['location'],core['description'], core['user_id']))

            for x in mlist:
                #logger.debug("pm_update.updateProperty:%s",x)
                ret=x['property_id']
            logger.debug("pm_update.updateProperty:: updated property id=%s[%s]",p_id, ret)            
        except Exception as e:
            logger.error("pm_update.updateProperty: update property failed:%s", e);
        
        return ret    
    elif ( qf == 'RENTAL'):   
        qj['rental']['updatedby']=core['updatedby']
        qj['rental']['market_rent']=core['market_rent']
        return updatePRental(O_db, logger, qj['rental'], p_id, 1)
    elif ( qf == 'ADMIN'):   
        return updatePAttributes(O_db, logger, qj['admin'], p_id, 1)
    elif ( qf == 'ATTRIBUTES'):   
        ret = updatePAttributes(O_db, logger, qj['amenities'], p_id, 1)
        return updatePAttributes(O_db, logger, qj['schools'], p_id, 1)
    elif ( qf == 'APPLIANCES'):   
        return updatePAppliances(O_db, logger, qj['appliances'], p_id, 1)
    elif ( qf == 'SERVICES'):   
        return updatePServices(O_db, logger, qj['services'], p_id, 1)
    elif ( qf == 'DELETE' ):
        sqls = "UPDATE pm.property SET status='TERMINATED', updatedby='" + core['updatedby'] + "', updated=now() WHERE property_id='"+str(core['property_id'])
        O_db.insert(sqls,None)
        return p_id
    else:
        return("NOP")

    return(ret)
def updatePRental(O_db, logger, qj , p_id, act):
    core={}
    sqls = ""
    logger.debug("updatePRental:%s", qj)
    
    sqls = "UPDATE pm.property_rental SET move_in=%s, market_rent=%s, special=%s,description= %s,apartments=%s,zillow=%s,trulia=%s,pr_status=%s,updatedby=%s,updated=now() WHERE property_id=%s"
    logger.debug("updatePRental:31:%s", sqls)
    O_db.insert(sqls,(qj['move_in'],qj['market_rent'],qj['special'],qj['description'],qj['apartments'],qj['zillow'],qj['trulia'],qj['pr_status'],qj['updatedby'],p_id))

    return p_id

def updatePAttributes(O_db, logger, qj , p_id, act):
    core={}
    sqls = ""
    logger.debug("updatePAttributes:%s", qj['data'])
    
    q1 = qj['data']
    
    for x in q1:
        core[x['co_name']] = x['pa_value']
    
    if ( act == 0 ):
        for x in core:
            sqls = "INSERT INTO pm.property_attribute values("+str(p_id) + ",'" + x + "','" + core[x] + "')"
            logger.debug("updatePAttributes:1:%s", sqls)
            O_db.insert(sqls,None)
    else:
        for x in core:
            s = ""
            i = 0
            sqls = "SELECT pa.name, pa.value FROM pm.property_attribute pa WHERE pa.property_id="+str(p_id)+ " and pa.name='"+x+"'"
            logger.debug("updateTAttributes11:%s",sqls)
            mlist = O_db.query_list(sqls, None)
            for y in mlist:
                s = y['value']
                i = 1
            if ( i == 0):
                sqls = "INSERT INTO pm.property_attribute values("+str(p_id) + ",'" + x + "','" + core[x] + "')"
                logger.debug("updatePAttributes:2:%s", sqls)
                O_db.insert(sqls,None)
            elif ( i== 1 and s != str(core[x])):
                sqls = "UPDATE pm.property_attribute SET value = '"+ core[x] + "' where property_id="+str(p_id) + " and name='" + str(x) + "'"
                logger.debug("updatePAttributes:3:%s", sqls)
                O_db.insert(sqls,None)
            else:
                logger.debug("updatePAttributes:4: NO Update Required:%s [%s]", s,core[x])
    return p_id
def updatePAppliances(O_db, logger, qj , p_id, act):
    sqls = ""
    logger.debug("updatePAppliances:[%s] %s", act, qj['data'])
    
    core = qj['data']

    if ( act == 0 ):
        for x in core:
            if ( 'status' not in x):
                x['status']=1
            sqls = "INSERT INTO pm.property_appliance values("+str(p_id) + ",'" + x['appliance'] + "','" + x['make'] + "','" + x['model'] +"','" + x['value']+ "','" + x['start_date'] +"',"+str(x['status'])+")"
            logger.debug("updatePAppliances:1:%s", sqls)
            O_db.insert(sqls,None)
    else:
        for x in core:
            s = ""
            i = 0
            logger.debug("updatePAppliances:10:%s",x)
            
            if ( 'status' not in x):
                x['status']=1
            sqls = "SELECT pa.* FROM pm.property_appliance pa WHERE pa.property_id="+str(p_id)+ " and pa.appliance='"+x['appliance']+"'"
            logger.debug("updatePAppliances:11:%s",sqls)
            mlist = O_db.query_list(sqls, None)
            for y in mlist:
                s = y
                i = 1
            if ( i == 0):
                sqls = "INSERT INTO pm.property_appliance values("+str(p_id) + ",'" + x['appliance'] + "','" + x['make'] + "','" + x['model'] +"','" + x['value']+ "','" + x['start_date'] +"',"+str(x['status'])+")"
                logger.debug("updatePAppliances:2:%s", sqls)
                O_db.insert(sqls,None)
            elif ( i== 1 and ( s['make'] != x['make'] or s['model'] != x['model'] or s['value'] != x['value'] or s['status'] != x['status'] or s['start_date'] != x['start_date'])):
                sqls = "UPDATE pm.property_appliance SET value = '"+ x['value'] + "',make='"+x['make']+"',model='"+x['model']+"',start_date='"+x['start_date']+"', status="+str(x['status'])+" WHERE property_id="+str(p_id) + " and appliance='" + x['appliance']+"'"
                logger.debug("updatePAppliances:3:%s", sqls)
                O_db.insert(sqls,None)
            else:
                logger.debug("updatePAppliances:4: NO Update Required:%s [%s]", s,x)
    return p_id

def updatePServices(O_db, logger, qj , p_id, act):
    sqls = ""
    logger.debug("updatePServices:[%s] %s", act, qj['data'])
    
    core = qj['data']

    if ( act == 0 ):
        for x in core:
            sqls = "INSERT INTO pm.property_service values("+str(p_id) + ",'" + x['service'] + "'," + str(x['vendor_id']) 
            + ",'" + x['account'] +"','" + x['reference']+ "','" + x['value'] +"')"
            logger.debug("updatePServices:1:%s", sqls)
            O_db.insert(sqls,None)
    else:
        for x in core:
            s = ""
            i = 0
            logger.debug("updatePServices:10:%s",x)
            if ( 'vendor_id' not in x or x['vendor_id'] == ''):
                continue
            sqls = "SELECT pa.* FROM pm.property_service pa WHERE pa.property_id="+str(p_id)+ " and pa.service='"+x['service']+"'"
            logger.debug("updatePServices:11:%s",sqls)
            mlist = O_db.query_list(sqls, None)
            for y in mlist:
                s = y
                i = 1
            if ( i == 0):
                sqls = "INSERT INTO pm.property_service values("+str(p_id) + ",'" + x['service'] + "'," + str(x['vendor_id']) + ",'" + x['account'] +"','" + x['reference']+ "','" + x['value'] +"')"
                logger.debug("updatePServices:2:%s", sqls)
                O_db.insert(sqls,None)
            elif ( i== 1 and ( s['account'] != x['account'] or s['reference'] != x['reference'] or s['value'] != x['value']) or s['vendor_id'] != x['vendor_id']):
                sqls = "UPDATE pm.property_service SET value = '"+ x['value'] + "',account='"+x['account']+"',reference='"+x['reference']+"',vendor_id=" + str(x['vendor_id'])+" WHERE property_id="+str(p_id) + " and service='" + str(x['service']) + "'"
                logger.debug("updatePServices:3:%s", sqls)
                O_db.insert(sqls,None)
            else:
                logger.debug("updatePServices:4: NO Update Required:%s [%s]", s,x)
    return p_id
                
########################################################## Tenant #####################

def updateTenant(O_db, logger, qj):
    core = {}
    t_id=-1
    ret={}

    sqls = ""
    qf = 'UPDATE'

    qf = fetchTextfromQ(logger,qj,'qualifier')
    logger.debug("pm_update::updateTenant:[%s] %s",qf,qj)
    core = qj    
    if ( 'tenant_id' in core ):
        t_id=int(core['tenant_id'])
    
    if ( qf == 'PRIMARY'):
        if ( 'middle_name' not in core):
            core['middle_name'] = '';
        if ( 'gender' not in core):
            core['gender'] = 'NA';
        if ( 'relationship' not in core):
            core['relationship'] = 'S';
        if ( 'parent' not in core or core['parent'] == ''):
            core['parent'] = 'null';
        
        core['other_names']=core['first_name']+" "+core['last_name']+";"+core['last_name']+" "+core['first_name']    

        if ( 'dl_state' not in core):
            core['dl_state'] =''
        if ( 'dl_id' not in core):
            core['dl_id'] =''
        if ( 'tax_id' not in core or core['tax_id'] ==''):
            core['tax_id'] ='XXX-XX-XXXX'
        if ( 'dob' not in core or core['dob'] ==''):
            core['dob'] ='1901-01-01'
        if ( 'description' not in core ):
            core['description']=''
        if ( 'phone2' not in core ):
            core['phone2']=''
        if ( 'parent' in core and core['parent'] == 'null'):
            core['parent']=-1
        core['EXCLUDE_TENANT_ID']=t_id
        if ( 1 < 0 ):
            ts_pd = ref_data.search_my_tenants_pd(O_db, logger, core)
            logger.debug("pm_update::updateTenant.Search: %s",ts_pd)
            if ( not ts_pd.empty ):
                ret['status']='Failure'
                ret['message']='Update failed, duplicate tenant found'
                ret['data']=ts_pd.to_json(orient='table')
                ret['code']=-1
                return(ret)
    

    if (t_id < 0) :
        logger.debug("pm_update.updateTenant:: new tenant id=%s",t_id)
        try:
            mlist = O_db.query_list('call updateTenant (-1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s,%s,%s,%s, %s,%s)',
                    (core['first_name'],core['middle_name'],core['last_name'], core['other_names'],core['tax_id'], 
                    core['phone'], core['phone2'], core['dob'], core['email'], core['description'], core['relationship'], 
                    core['parent'], core['gender'], core['user_id'], core['dl_state'], core['dl_id'] ))
        
            for x in mlist:
                #logger.debug("pm_update.updateTenant:%s",x)
                t_id=x['tenant_id']
            ret['status']='Success'
            ret['message']='New Tenant created'
            ret['tenant_id']=t_id
            ret['code']=0
        except Exception as e:
            logger.error("pm_update.updateTenant: tenant creation failed:%s", e);
            t_id=-1
            ret['status']='Failure'
            ret['message']='New Tenant creation failed'
            ret['code']=-2        
        
    elif ( qf == 'PRIMARY') :
        
        logger.debug("pm_update.updateTenant::PRIMARY[%s]",t_id)
        try:
            mlist = O_db.query_list('call updateTenant (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s)',
                    (core['tenant_id'], core['first_name'],core['middle_name'],core['last_name'], core['other_names'],core['tax_id'], core['phone'], core['phone2']
                     , core['dob'], core['email'], core['description'], core['status'], core['relationship'], core['parent'], core['gender'], core['user_id'],  core['dl_state'], core['dl_id'] ))
        
            for x in mlist:
                #logger.debug("pm_update.updateTenant:%s",x)
                t_id=x['tenant_id']
            ret['status']='Success'
            ret['message']='Tenant Information Updated'
            ret['tenant_id']=t_id
            ret['code']=0
        except Exception as e:
            logger.error("pm_update.updateTenant: tenant creation failed:%s", e);
            ret['status']='Failure'
            ret['message']='Tenant update Failed'
            ret['tenant_id']=t_id
            ret['code']=-3
        
    elif ( qf == 'TAB2'):    
        return updateTAttributes(O_db, logger, qj['attributes'], t_id)
    elif ( qf == 'FAMILY'):
        return updateTFamily(O_db, logger, qj['family'], t_id,qj['updatedby'])
    elif ( qf == 'VEHICLES'):    
        return updateTVehicles(O_db, logger, qj['vehicles'], t_id)
    elif ( qf == 'PETS'):
        return updateTPets(O_db, logger, qj['pets'], t_id,qj['updatedby'])
    elif ( qf == 'DELETE' ):
        sqls = "UPDATE pm.tenants SET status=0, updated=now(), updatedby='" + core['updatedby'] + " WHERE tenant_id='"+ str(core['tenant_id'])
        logger.debug("pm_update.updateTenant::[%s] %s",qf,sqls)
        O_db.insert(sqls,None)
        logger.debug("pm_update.updateTenant:: data updated")
        ret=t_id
        ret['status']='Success'
        ret['message']='Tenant Status updated'
        ret['tenant_id']=t_id
        ret['code']=0
    else:
        ret['status']='NOP'
        ret['message']='No Operation executed'
        ret['tenant_id']=t_id
        ret['code']=0
    return(ret)

def updateTFamily(O_db, logger, qj, t_id, updated_by):
    sqls = ""
    ret = {}
    logger.debug("updateTFamily:%s", qj)
    fields = ['occupation','notes','tax_id','phone','email','relationship']
    core={}
    sqls = "DELETE FROM pm.tenants_family WHERE tenant_id="+str(t_id)
    logger.debug("updateTFamily:%s",sqls)
    mlist = PMDB.query_list(O_db, sqls, None)
    for core in qj:
        i = 0
        logger.debug("pm_update.updateTFamily:core:%s", core)
        if ( 'tenant_id' not in core or core['tenant_id'] < 0):
            for x in fields:
                if ( x not in core or core[x] == None):
                    core[x]=''
            sqls = "INSERT INTO `pm`.`tenants_family`(`tenant_id`,`first_name`,`last_name`,`relationship`,`occupation`,`dob`,`tax_id`,`phone`,`email`, `notes`,`updatedby`) VALUES ("
            sqls +=str(t_id)+",'"+ core['first_name'] +"','"+core['last_name']+"','"+core['relationship']+"','"+core['occupation']+"','"+core['dob']+"','"
            sqls += core['tax_id']+"','"+core['phone']+"','"+core['email']+"','"+core['notes']+"','"+updated_by+"')" 
            logger.debug("updateTFamily:3:%s", sqls)
            O_db.insert(sqls,None)
    ret['status']='Success'
    ret['message']='Tenant Family Information Updated'
    ret['tenant_id']=t_id
    ret['code']=0

def updateTVehicles(O_db, logger, qj, t_id):
    sqls = ""
    logger.debug("updateTVehicles:%s", qj)
    fields = ['state','make','model','color','parking_lot']
    core={}
    ret={}
    for core in qj:
        i = 0
        logger.debug("pm_update.updateTVehicles:core:%s", core)
        for x in fields:
            if ( x not in core or core[x] == None):
                core[x]=''
        sqls = "SELECT count(*) as total FROM pm.tenants_vehicle ta WHERE ta.tenant_id="+str(t_id)+ " and ta.parking_tag_id="+str(core['parking_tag_id'])
        logger.debug("updateTVehicles:%s",sqls)
        mlist = PMDB.query_list(O_db, sqls, None)
        for y in mlist:
            i = y['total']
        if ( i == 0 and 'tag' in core and core['tag'] != ''):
            if ( 'setup_charge' not in core):
                core['setup_charge']=25
            if ( 'monthly' not in core):
                core['monthly']=35
            sqls = "INSERT INTO `pm`.`tenants_vehicle`(`tenant_id`,`state`,`tag`,`make`,`model`,`color`,`pl_id`,`expiry`,`setup_charge`,`monthly`)VALUES "
            sqls += " (" + str(t_id) + ",'"+ core['state'] +"','"+core['tag']+"','"+core['make']+"','"+core['model']+"','"+core['color']+"','"+str(core['pl_id'])+"'"
            if ( 'expiry' in core ):
                sqls += ",'"+core['expiry']+"'"
            else:
                sqls += ",null"
            sqls += ","+str(core['setup_charge'])+","+str(core['monthly'])+")"            
            logger.debug("updateTVehicles:3:%s", sqls)
            O_db.insert(sqls,None)
            ret['status']='Success'
            ret['message']='Tenant Vehicle Information Updated'
        elif ( i== 1):
            sqls = "UPDATE pm.tenants_vehicle SET state='"+core['state']+"', make='"+core['make']+"', model='"+core['model']+"', color='"+core['color']+"',"
            sqls += " pl_id="+str(core['pl_id'])+", expiry='"+core['expiry']+"', setup_charge="+str(core['setup_charge'])+", monthly="+str(core['monthly'])
            sqls += " WHERE tenant_id="+str(t_id)+ " and parking_tag_id="+str(core['parking_tag_id'])
            logger.debug("updateTVehicles:4:%s", sqls)
            O_db.insert(sqls,None)
            ret['status']='Success'
            ret['message']='Tenant Vehicle Information Updated'
        else:
            logger.debug("updateTVehicles:5: NO Update Required:%s", x)
            ret['status']='NOP'
            ret['message']='Tenant Vehicle Information Update not applied'
    
    ret['tenant_id']=t_id
    ret['code']=0
    return(ret)

def updateTPets(O_db, logger, qj, t_id, updatedby):

    sqls = ""
    logger.debug("updateTPets:%s", qj)
    fields = ['pet_role','pet_type','breed','weight','vaccination','insurance','notes']
    core={}
    ret={}
    for core in qj:
        i = 0
        logger.debug("pm_update.updateTPets:core:%s", core)
    
        for x in fields:
            if ( x not in core or core[x] == None):
                core[x]=''
        
        sqls = "SELECT count(*) as total FROM pm.tenants_pet ta WHERE ta.tenant_id="+str(t_id)+ " and ta.pet_id="+str(core['pet_id'])
        logger.debug("updateTPets:%s",sqls)
        mlist = PMDB.query_list(O_db, sqls, None)
        for y in mlist:
            i = y['total']
        if ( i == 0 and 'breed' in core and core['breed'] != ''):
            if ( 'setup_charge' not in core):
                core['setup_charge']=250
            if ( 'monthly' not in core):
                core['monthly']=25
            
            sqls = "INSERT INTO pm.tenants_pet(tenant_id,pet_role,pet_type,breed,weight,vaccination,insurance,expiry,notes,setup_charge,monthly,updatedby)VALUES "
            sqls += " (" + str(t_id) + ",'"+ core['pet_role'] +"','"+core['pet_type']+"','"+core['breed']+"','"+core['weight']+"','"+core['vaccination']+"','" +core['insurance']+"'"
            if ( 'expiry' in core ):
                sqls += ",'"+core['expiry']+"'"
            else:
                sqls += ",null"
            sqls += ",'"+core['notes']+"',"+str(core['setup_charge'])+","+str(core['monthly'])+",'"+updatedby+"')"

            logger.debug("updateTPets:3:%s", sqls)
            O_db.insert(sqls,None)
            ret['status']='Success'
            ret['message']='Tenant PET Information Updated'
        elif ( i== 1):
            sqls = "UPDATE pm.tenants_pet SET pet_role='"+core['pet_role']+"', pet_type='"+core['pet_type']+"', breed='"+core['breed']+"', weight='"+core['weight']+"',insurance='"+core['insurance']+"',"
            sqls += " vaccination='"+core['vaccination']+"', expiry='"+core['expiry']+"',notes='"+core['notes']+"', setup_charge="+str(core['setup_charge'])+", monthly="+str(core['monthly'])
            sqls += " , updatedby='"+updatedby+"', updated=now() "
            sqls += " WHERE tenant_id="+str(t_id)+ " and pet_id="+str(core['pet_id'])
            logger.debug("updateTPets:4:%s", sqls)
            O_db.insert(sqls,None)
            ret['status']='Success'
            ret['message']='Tenant PET Information Updated'
        else:
            logger.debug("updateTPets:5: NO Update Required:%s", x)
            ret['status']='NOP'
            ret['message']='Tenant PET Information Not Updated'
    ret['tenant_id']=t_id
    ret['code']=0
    return(ret)

def updateTAttributes(O_db, logger, qj, t_id):
    core={}
    ret={}
    sqls = ""
    logger.debug("updateTAttributes:%s",qj)

    for x in qj['data']:
        core[x['co_name']] = x['ta_value']
    
    for x in core:
        s = ""
        i = 0
        sqls = "SELECT ta.name, ta.value FROM pm.tenants_attributes ta WHERE ta.tenant_id="+str(t_id)+ " and ta.name='"+x+"'"
        logger.debug("updateTAttributes2:%s",sqls)
        mlist = PMDB.query_list(O_db, sqls, None)
        for y in mlist:
            s = y['value']
            i = 1
        if ( i == 0):
            sqls = "INSERT pm.tenants_attributes values("+str(t_id) + ",'" + x + "','" + core[x] + "')"
            logger.debug("updateTAttributes:3:%s", sqls)
            O_db.insert(sqls,None)
            ret['status']='Success'
            ret['message']='Tenant Attribute Information Updated'
        elif ( i== 1 and s != str(core[x])):
            sqls = "UPDATE pm.tenants_attributes SET value = '"+ core[x] + "' where tenant_id="+str(t_id) + " and name='" + str(x) + "'"
            logger.debug("updateTAttributes:4:%s", sqls)
            O_db.insert(sqls,None)
            ret['status']='Success'
            ret['message']='Tenant Attribute Information Updated'
        else:
            logger.debug("updateTAttributes:5: NO Update Required:%s = %s", s,core[x])
            ret['status']='Success'
            ret['message']='Tenant Attribute Information Not Updated'
    ret['tenant_id']=t_id
    ret['code']=0
    return(ret)

def tenantHistory(O_db, logger, core):
    logger.debug("tenantHistory.0:%s", core)
    sqls = "INSERT INTO pm.tenants_history(`tenant_id`,`title`,`comments`,`updatedby`) VALUES(%s,%s,%s,%s)"
    ret=0
    
    try:
         logger.debug("tenantHisotry.1:%s", sqls)
         mlist = O_db.query_list(sqls,(core['tenant_id'], core['title'], core['comments'], core['updatedby']))
         ret=1
    except:
         logger.error("tenantHistory2: tenant history update failed");
         ret=-1
        
        
    return ret;


########################################################## Tenancy #####################

def updateTenancy (O_db, logger, qj):
    core = {}
    ret=-1
    sqls = ""
    tc_id=-1
    tc_action=1
    lsd=""
    mid=""

    logger.debug("pm_update::updateTenancy.0:%s",qj) 
    qf = fetchTextfromQ(logger,qj,'qualifier')

    for x in qj:
        core[x] = fetchTextfromQ(logger,qj,x)    
 
    if ( 'responsible' not in core):
        core['responsible'] = 1;
   
    t_id=int(core['tenant_id'])
    
    if ( 'tenancy_id' in core ):
        tc_id=int(core['tenancy_id'])  
        
    if ( tc_id > 0 and core['status'] == '5' ):
        qf = "NEW"
        sqls = "UPDATE pm.tenancy set status=0 where tenancy_id=" + str(tc_id)
        logger.debug("updateTenancy10=%s", sqls)
        O_db.insert(sqls,None)
        tc_id=-1
    
    logger.debug("updateTenancy2:[%s]: tenancy_id[%s] tenant_id[%s]",qf, tc_id, t_id)
    
    if (tc_id < 1 ):
        sqls = "INSERT INTO pm.tenancy (tenant_id,property_id,start_date,end_date,move_in,move_out,description,family_members, "
        sqls += "rent,deposit,email, phone,responsible,status,term, updatedby) VALUES ( "
        sqls += str(core['tenant_id']) + "," + str(core['property_id']) + ",'"+core['lease_start_date'] + "','" + core['lease_end_date']+"'"
        if ( 'move_in_date' not in core or core['move_in_date'] == None or core['move_in_date'] ==''):
            sqls += ",null,"
        else:
            sqls += ",'" + core['move_in_date'] +"',"  
        if ( 'move_out_date' not in core or core['move_out_date'] == None or core['move_out_date'] ==''):
            sqls += "null,"
        else:
            sqls += "'" + core['move_out_date'] +"',"
        
        if ( 'description' in core ):
            sqls += "'" + core['description'] +"',"
        else:
            sqls += "null,"  

        sqls += str(core['family_members']) + "," + str(core['rent'])+ "," + str(core['deposit'])
        if ( 'email' in core ):
            sqls += ",'" + core['email'] +"',"
        else:
            sqls += ",null," 
        if ( 'phone' in core ):
            sqls += "'" + core['phone'] +"',"
        else:
            sqls += "null," 
        sqls += "'" + core['responsible'] + "'," + str(core['status']) + ",'"+core['term']+"','" + core['updatedby'] +"')"    
        logger.debug("updateTenancy:3:%s", sqls)
        try:
            O_db.insert(sqls,None)
            logger.debug("pm_update.updateTenancy21:: data updated")
            ret=0
        except:
            logger.debug("pm_update.updateTenancy25::Query Failed:%s", sqls) 
            ret=-1
            tc_action = -1
  
        if ( ret > -1 ):      
            sqls = "select tenancy_id from pm.tenancy where tenant_id="+str(core['tenant_id']) + " and property_id=" +str(core['property_id'])
            sqls += " and start_date='" + core['lease_start_date'] + "' and end_date='" +core['lease_end_date'] + "' and rent=" + str(core['rent']) + " and deposit=" + str(core['deposit'])
            sqls += " and status=" + str(core['status']) + " and family_members="+ str(core['family_members']) +" and responsible='"+core['responsible']+"'"
            
            mlist = PMDB.query_list(O_db, sqls, None)
            logger.debug("pm_update.updateTenancy26:: data updated: %s", sqls)
            for y in mlist:
                tc_id = y['tenancy_id']
                ret = tc_id
                tc_action = 0
    
    elif ( qf == 'PRIMARY'):
        sqls = "UPDATE pm.tenancy SET property_id = " + str(core['property_id']) +", family_members="+ str(core['family_members'])
        sqls += ", start_date='" + core['lease_start_date'] + "',"
        
        if ( 'lease_end_date' in core and core['lease_end_date'] !=''):
            sqls += "end_date='" + core['lease_end_date'] +"',"
        else:
            sqls += "end_date=null,"
            
        if ( 'move_in_date' in core and core['move_in_date'] !=''):
            sqls += "move_in='" + core['move_in_date'] +"',"
        else:
            sqls += "move_in=null,"
            
        if ( 'move_out_date' in core and core['move_out_date'] !=''):
            sqls += "move_out='" + core['move_out_date'] +"',"
        else:
            sqls += "move_out=null,"
            
        if ( 'description' in core ):
            sqls += "description='" + core['description'] +"',"
        else:
            sqls += "description=null,"  
        
        if ( 'email' in core ):
            sqls += "email='" + core['email'] +"',"
        else:
            sqls += "email=null,"  
        if ( 'phone' in core ):
            sqls += "phone='" + core['phone'] +"',"
        else:
            sqls += "phone=null,"  

        sqls += "rent=" + str(core['rent'])+ ", deposit=" + str(core['deposit'])
        sqls += ", responsible='" + core['responsible'] + "',status=" + str(core['status']) +",term='"+core['term']
        sqls += "', updatedby='" + core['updatedby'] +"', updated=now() "
        sqls += " WHERE tenancy_id="+str(tc_id)
                                      
        logger.debug("updateTenancy:4:%s",sqls)
    
        try:
            O_db.insert(sqls,None)
            logger.debug("pm_update.updateTenancy41:: data updated")
            ret=tc_id
            tc_action = 1
        except:
            logger.debug("pm_update.updateTenancy45::Query Failed:%s",sqls) 
            ret=-1
            tc_action = -1
    elif (qf == 'ATTRIBUTES'):
        if ( 'attributes' in qj and 'data' in qj['attributes']):
            updateTCAttributes(O_db, logger, qj['attributes']['data'], tc_id, tc_action)
        return(tc_id)
    else:
        return(tc_id)
    # Update property status is not active (1); if tenant moved out (2) or evicted(3) or inactive 1)    
    logger.debug("pm_update.updateTenancy25:%s %s", ret, core['status'])
    if ( ret > 0 and ( int(core['status']) == 1 or int(core['status']) == 5 )):
        sqls = "update pm.property set p_status='OCCUPIED' where property_id=" + str(core['property_id'])
        try:
            O_db.insert(sqls,None)
            logger.debug("pm_update.updateTenancy8:: Data updated: %s", sqls)
        except:
            logger.debug("pm_update.updateTenancy9::Query Failed: %s" , sqls) 
            ret=-1
    elif ( ret > 0 and int(core['status']) > 1 ):
        sqls = "update pm.property set p_status='RENT READY' where property_id=" + str(core['property_id'])
        try:
            O_db.insert(sqls,None)
            logger.debug("pm_update.updateTenancy6:: data updated: %s", sqls)
        except:
            logger.debug("pm_update.updateTenancy7::Query Failed: %s" , sqls) 
            ret=-1
        
        
    return(ret)

def updateTCAttributes(O_db, logger, qj, t_id, act):
    core={}
    ref={}
    sqls = ""
    logger.debug("updateTCAttributes:%s", qj)

    if ( len(qj) < 1 ):
        logger.debug("updateTCAttributes: NO attributes for: %s", t_id)
        return

    for x in qj:
        core[x['co_name']] = x['ta_value']
        ref[x['co_name']] = x['ta_ref']
    

    if ( act == 0 ):
        for x in core:
            sqls = "INSERT pm.tenancy_attributes values("+str(t_id) + ",'" + x + "','" + core[x] + "','" + ref[x] + "')"
            logger.debug("updateTCAttributes:1:%s", sqls)
            O_db.insert(sqls,None)
    elif ( act == 1):
        for x in core:
            s = ""
            i = 0
            sqls = "SELECT ta.name, ta.value, ta.reference FROM pm.tenancy_attributes ta WHERE ta.tenancy_id="+str(t_id)+ " and ta.name='"+x+"'"
            logger.debug("updateTCAttributes11:%s",sqls)
            mlist = PMDB.query_list(O_db, sqls, None)
            for y in mlist:
                s = y['value']
                r = y['reference']
                i = 1
            if ( i == 0):
                sqls = "INSERT pm.tenancy_attributes values("+str(t_id) + ",'" + x + "','" + core[x] + "','" + ref[x] +"')"
                logger.debug("updateTCAttributes:2: %s", sqls)
                O_db.insert(sqls,None)
            elif ( i== 1 and ( s != str(core[x]) or  r != str(ref[x]))):
                sqls = "UPDATE pm.tenancy_attributes SET value = '"+ core[x] + "',reference = '"+ ref[x] + "' where tenancy_id="+str(t_id) + " and name='" + str(x) + "'"
                logger.debug("updateTCAttributes:3: %s", sqls)
                O_db.insert(sqls,None)
            else:
                logger.debug("updateTCAttributes:4: NO Update Required:%s[%s]=[%s]", s,core[x],ref[x])
    else:
        logger.debug("updateTCAttributes:4: NO Action:%s", act)


        
def updateHistory(db, logger, core):
    sqls=""
    ret = -1
    logger.debug("pm_update:updateHistory:%s", core)
    if ( 'updatedby' not in core):
        core['updatedby']=core['login']
    
    if ( core['key_type'] == 'TENANCY' ):
        sqls = "INSERT INTO pm.tenancy_history (`tenancy_id`,`title`,`comments`,`updatedby`) VALUES (%s, %s,%s,%s) "
    elif ( core['key_type'] == 'TENANT' ):    
        sqls = "INSERT INTO pm.tenants_history (`tenant_id`,`title`,`comments`,`updatedby`) VALUES (%s, %s,%s,%s) "
    elif ( core['key_type'] == 'PROPERTY' ):    
        sqls = "INSERT INTO pm.property_history (`property_id`,`title`,`comments`,`updatedby`) VALUES (%s, %s,%s,%s) "
    elif ( core['key_type'] == 'WO' ):    
        sqls = "INSERT INTO pm.wo_history (`wo_id`,`title`,`comments`,`updatedby`) VALUES (%s,%s, %s,%s) "
    else:
        return -1

    try:
        logger.debug("pm_file.updateFiles.6:%s", sqls)
        db.insert(sqls,(core['id_value'], core['title'],core['comment'], core['updatedby']))
        ret = 0
    except:
        logger.debug("pm_file.updateFiles.7:Query Failed:%s", sqls) 
        ret = -1        
    return ret

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
    
