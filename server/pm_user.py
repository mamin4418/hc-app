# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 20:30:43 2020

@author: ppare
"""
import secrets
from flask import json
import pandas as pd
from datetime import datetime
from utils.pm_db import PMDB

global logged_user
logged_user = {}

def logoutUser(db, logger, qj):
    print("pm_user:logoutUser:", qj)

def verifyRequest(db, logger, qj):
    core={}
    # verifies request headers
    
    #logger.debug("verifyRequest: %s", qj)
    print("pm_user.verifyRequest.0:", qj)
    if ( 'User-Agent'in qj ):
        core['User-Agent']=qj['User-Agent']
    else:
        core['User-Agent']="NA"
    if ( 'Origin'in qj ):
        core['Origin']=qj['Origin']
    else:
        core['Origin']="NA"
    if ( 'Application'in qj ):
        core['Application']=qj['Application']
    else:
        core['Application']="NA"
    if ( 'X-Forwarded-For'in qj ):
        core['Source-IP']=qj['X-Forwarded-For']
    else:
        core['Source-IP']=qj['Referer']

    if ('Login' in qj and 'Authorization' in qj ):
        core['login']=qj['Login']
        core['Login']=qj['Login']
        core['Authorization']=qj['Authorization'].split(' ')[1]
        
        core['code']=0
        if ( core['Authorization'] in  logged_user and logged_user[core['Authorization']][1] == core['login']):
            core['code']=0
            core['status']="SUCCESS"
            core['user_id']=logged_user[core['Authorization']][0]
            core['Updatedby']=str(core['user_id'])+':'+qj['Login']+':'+qj['Application']
            core['navigation']=logged_user[core['Authorization']][2]
        else:
            mdict = verifyUser(db, logger, core, 1)
            if ( mdict['code'] == 0):
                core['user_id']=mdict['user_id']
                core['status']="SUCCESS"
                core['code']=0
                core['Updatedby']=str(core['user_id'])+':'+qj['Login']+':'+qj['Application']
                core['navigation']=mdict['navigation']
            else:
                core['code']=999
                core['status']="FAIL"
                core['message']='1:Invalid user id - token'
        # check token, update touch point
    else:
        core['code']=999
        core['status']="FAIL"
        core['message']='2:Invalid/Missing user id - token'
        
    logger.info("pm_user.verifyRequest.10:%s", core)

    return core
        
    
def getAccessInfo(db, logger, user_id):
        
    mdict = {}
    rep = {}
    rep['status']='FAIL'
    rep['message']='User not found'
    rep['code']=1
    roles={}
    role=""
    authority={}
    
    logger.info("pm_user.getAccessInfo.0:%s", user_id)

    qry = "SELECT au.user_id,au.login, ar.name as role, ar.type as role_type, aa.authority_id, aa.name as authority, aa.icon as icon, aa.class as class, aa.component, ar.navigation "
    qry += "FROM pm.auth_users au, pm.auth_roles ar, pm.auth_users_roles aur, pm.auth_roles_authority ara, pm.auth_authority aa "
    qry += "WHERE au.user_id = aur.user_id AND ar.role_id = aur.role_id AND ar.role_id = ara.role_id AND ara.authority_id = aa.authority_id "
    qry += "AND aur.status=1 AND ar.status=1 AND au.status=1 AND aa.status=1 "
    qry += "AND au.user_id="+str(user_id)
    
    logger.info("pm_user.getAccessInfo::[%s]:%s",user_id, qry)    
    mlist = PMDB.query_list(db,qry, None)

    for x in mlist:
        mdict['user_id']=x['user_id']
        roles[x['role']]=[x['role'],x['role_type']]
        role=x['role']
        mdict['navigation']=x['navigation']
        authority[x['component']]=[x['component'],x['authority'],x['icon'],x['class']]
        
    
    mdict['type']=role
    mdict['roles']=roles
    mdict['authority']=authority
    
    logger.info("pm_user.getAccessInfo.10:%s", mdict)
    return mdict
    
def verifyUser(db, logger, core, tp = 0):
    
    mdict = {}
    mdict['status']='FAIL'
    mdict['message']='User not found'
    mdict['code']=1
    
    #for x in qj:
        #core[x] = fetchTextfromQ(qj,x)
        #print("pm_user.verifyUser.1:"+x+"="+str(core[x]))

    qryS = "SELECT au.user_id, au.login, au.password, au.email, au.phone, au.status,au.first_name,au.last_name, au.avatar, au.navigation, au.id_type, au.id_value, aue.*  "
    qry = " FROM pm.auth_users au , pm.auth_users_ext aue "
    
    
    if ( 'Authorization' in core ):
        qryS += ", aus.token as token "
        qry += ", pm.auth_usage aus where au.user_id = aus.user_id and au.user_id=aue.user_id and aus.status=1 and "
    else:
        qry += " where au.user_id=aue.user_id and  "
    if ( 'user_id' in core):
        qry += " au.user_id="+str(core['user_id'])
    elif ( 'login' in core):
        core['login']= core['login'].lower()
        qry += "  ( au.login='" + core['login'] +"' "
        qry += " OR au.phone='" + core['login'] + "' "
        qry += " OR au.email='" + core['login'] + "') "
    
    qry = qryS + qry
    logger.debug("pm_user.verifyUser::[%s]:%s",core['login'], qry)    
    mlist = PMDB.query_list(db,qry, None)
    logdb=0
    for x in mlist:
        mdict['user_id']=x['user_id']
        mdict['first_name']=x['first_name']
        mdict['last_name']=x['last_name']
        mdict['login']=x['login']
        mdict['status']=x['status']
        mdict['email']=x['email']
        mdict['phone']=x['phone']
        mdict['avatar']=x['avatar']
        mdict['navigation']=x['navigation']
        mdict['id_value']=x['id_value']
        mdict['id_type']=x['id_type']
        mdict['color']=x['color']
        mdict['tenant_id']=x['tenant_id']
        mdict['tenancy_id']=x['tenancy_id']
        mdict['property_id']=x['property_id']
        
        if ( x['status'] < 0 ):
            mdict['message']='User ID has expired'
            mdict['status']='FAIL'
            mdict['code']=1
        elif ( 'password' in core and core['password'] == x['password'] ):
            mdict['message']='User OK'
            mdict['status']='SUCCESS'
            mdict['token']=secrets.token_hex(64)
            logdb=1
            logged_user[mdict['token']]=[x['user_id'],x['login'],x['navigation']]
            mdict['code']=0
            break
        elif ( 'Authorization' in core and 'token' in x and core['Authorization'] == x['token']):
            mdict['message']='User OK'
            mdict['token']=x['token']
            logged_user[mdict['token']]=[x['user_id'],x['login'],x['navigation']]
            logdb=2
            mdict['status']='SUCCESS'
            mdict['code']=0
            break
        else:
            mdict['message']='Password DO NOT MATCH'
            mdict['status']='FAIL'
            mdict['code']=1
    
    if ( mdict['code']== 0 and tp == 0 ):
        idict = getAccessInfo(db, logger, mdict['user_id'])
        mdict['type']=idict['type']
        mdict['roles']=idict['roles']
        mdict['authority']=idict['authority']
    
    if (mdict['code'] == 0 and logdb == 1 ):
        logUser(db, logger,'NEW', x['user_id'], mdict['token'])
        mdict['last_login']=datetime.today().strftime('%c')
    if (mdict['code'] == 0 and  logdb == 2 ):
        logUser(db, logger,'UPDATE', x['user_id'], mdict['token'])
        mdict['last_login']=datetime.today().strftime('%c')
        
    return mdict

def logUser(db, logger, action, user_id, token):
    ret = {}
    ret['status']='FAIL'
    ret['message']='Saving user info failed'
    ret['code']=1
    qry=""
    
    if ( action == 'NEW' ):
        qry = "INSERT pm.auth_usage(user_id, status, token) values("+str(user_id)+",1,'"+token+"')"
    else:
        qry = "UPDATE pm.auth_usage SET updated=now() WHERE token='"+token+"' and user_id="+str(user_id)
        
    logger.debug("pm_user.logUser.4:%s", qry)
    try:    
        db.insert(qry,None)
        ret['code'] = 0
        ret['status'] = 'SUCCESS'
        ret['message']='User information updated'
        logger.debug("pm_user.logUser.5:%s", ret['message'])
    except ValueError:
        logger.error("pm_user.logUser.6::Query Failed:%s", qry) 
            
    return ret
        
def saveUser(db, logger, qj):
    ret = {}
    ret['status']='FAIL'
    ret['message']='Saving user info failed'
    ret['code']=1
    include=['first_name','last_name','address','address2','city','state','zip','phone','email','avatar','updatedby']
    qry=""
    core = {}
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)
    logger.debug("pm_user.saveUser.1: %s",core)
    
    if ( core['ACTION'] == 'PASS' ):
        ret = savePassword(db, logger, core['user_id'], core['password'], core['password2'])
    else:
        qry = "UPDATE pm.auth_users SET updated=now() "
        for x in core :
            if ( x in include ):
                qry += "," + x +"='" +str(core[x])+ "' "
                
        qry += " WHERE user_id="+str(core['user_id'])
        
        logger.debug("pm_user.saveUser.4:%s", qry)
        try:    
            db.update(qry)
            ret['code'] = 0
            ret['status'] = 'SUCCESS'
            ret['message']='User information updated'
            logger.debug("pm_user.saveUser.5: %s", ret['message'])
        except ValueError:
            logger.error("pm_user.saveUser.6::Query Failed: %s", qry) 
            ret = -1
        
    return ret

def savePassword(db, logger, u_id, p1, p2, tmp=0):
    ret = {}
    ret['status']='FAIL'
    ret['message']='PASSWORD update failed'
    ret['code']=1
    
    #Tmp=1 will allowe to reset password w/o knowing old password
    
    qry = "UPDATE pm.auth_users SET updated=now(), password='"+p2+"' where user_id="+str(u_id)
    if ( tmp != 1 ):
        qry +=" and password='"+p1+"'"
        
    logger.debug("pm_user.savePassword.4: %s", qry)
    try:    
        db.update(qry)
        logger.info("pm_user.savePassword.5:: password updated")
        ret['code'] = 0
        ret['status'] = 'SUCCESS'
        ret['message'] = 'PASSWORD update ok'
    except ValueError:
        logger.error("pm_user.savePassword::Query Failed: %s", qry) 
        ret = 1
        
    return ret
    
def updatePassword(db, logger, qj):
    ret = {}
    ret['status']='FAIL'
    ret['message']='Saving user info failed'
    ret['code']=1
    user_id=-1

    logger.debug("pm_user.resetPassword.1: %s", qj)
    
    if ( 'tenant_user_id' in qj):
        user_id=qj['tenant_user_id']
    elif ( 'user_id' not in qj):
        udict = getUser(db, logger, qj, 1)
        user_id=udict['user_id']
    
    if ( qj['ACTION'] == 'PASSWORD RESET' ):
        p2 = secrets.token_hex(16)[:12] # only 8 characters
        ret = savePassword(db, logger, user_id, 'NA', p2, 1)
        ret['password']=p2
        
    elif ( qj['ACTION' == 'PASSWORD UPDATE']):
        ret = savePassword(db, logger, user_id, qj['password'],qj['password2'])
     
    ret['email']=qj['email']
    ret['user_id']=user_id
            
    logger.debug("pm_user.resetPassword.10: %s", ret)
    return ret

def getUser(db, logger, qj, tmp=0):
    
    mdict = {}
    core = {}
    
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)
    logger.debug("pm_user.getUser.1: %s",core)
    

    qry = "select au.user_id, first_name, last_name, login, address, address2, city,state,zip, email, phone, status,"
    qry += " createdby, created, updatedby, updated, avatar, navigation,id_type, id_value, aue.* "
    qry += " FROM pm.auth_users au, pm.auth_users_ext aue where au.user_id=aue.user_id and "
    
    if ( 'id_type' in core and 'id_value' in core and core['id_type'] == 'tenant_id' ):
        qry += " au.id_type='"+ core['id_type'] +"' and au.id_value=" + str(core['id_value']) 
    elif ( 'user_id' in core):
        qry += " au.user_id=" + str(core['user_id'])
    elif ('email' in core):
        qry += " au.email='" + core['email'] +"'"
    elif ('login' in core):
        qry += " au.login='" + core['login'] +"'"
    elif ('phone' in core):
        qry += " au.phone='" + core['phone'] +"'"
    
    logger.debug("pm_user.getUser: %s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    for x in mlist:
        mdict['user_id']=x['user_id']
        mdict['first_name']=x['first_name']
        mdict['last_name']=x['last_name']
        mdict['login']=x['login']
        mdict['address']=x['address']
        mdict['address2']=x['address2']
        mdict['city']=x['city']
        mdict['state']=x['state']
        mdict['zip']=x['zip']
        mdict['avatar']=x['avatar']
        mdict['status']=x['status']
        mdict['email']=x['email']
        mdict['phone']=x['phone']
        mdict['createdby']=x['createdby']
        mdict['created']=x['created']
        mdict['updatedby']=x['updatedby']
        mdict['updated']=x['updated']
        mdict['navigation']=x['navigation']
        mdict['id_type']=x['id_type']
        mdict['id_value']=x['id_value']
        mdict['color']=x['color']
        mdict['tenant_id']=x['tenant_id']
        mdict['tenancy_id']=x['tenancy_id']
        mdict['property_id']=x['property_id']

    # check for last login
    mdict['last_login']="Never Logged In"
    
    if ( 'user_id' in mdict):
        
        qry = "SELECT max(updated) as last_login FROM pm.auth_usage where user_id="+str(mdict['user_id'])
        logger.debug("pm_user.getUser.2::%s", qry)  
        mlist = db.query_list(qry,None)
        for x in mlist:
            mdict['last_login']=x['last_login']
    
        if ( tmp == 0):
            idict = getAccessInfo(db, logger, mdict['user_id'])
            mdict['type']=idict['type']
            mdict['roles']=idict['roles']
            mdict['authority']=idict['authority']    

    return mdict

def getUsers_PD(O_db, logger, qj):
    core = {}
    qry = ""
    logger.debug("pm_user.getUsers.1:%s",qj)

    if ( qj != None and 'params' in qj ):
        core = qj['params']

    qry = "select user_id, first_name, last_name, login, address, address2, city, email, phone, status,"
    qry += " createdby, created, updatedby, updated "
    qry += " FROM pm.auth_users au "

    if ( 'status' in core ):
        qry += " WHERE au.status =" + str(core['status'])
    else:
        qry += " WHERE au.status =1 "

    if ( 'id_type' in core ):
        qry += " AND au.id_type='"+ core['id_type'] +"'"
    
    qry += " ORDER BY au.first_name, au.last_name"
    
    logger.debug("pm_user.getUsers.3:%s", qry)    
    mlist = PMDB.query_list(O_db,qry, None)
    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.set_index('user_id')
    return t_pd
    
############# usage
def updateUsage(db, logger, core1, core2):
    ret = {}
    ret['status']='FAIL'
    ret['message']='PASSWORD update failed'
    ret['code']=1
    user_data=""
    logger.debug("pm_user.updateUsage.1: %s | %s",  core1, core2)
    try:

        usage_data = core2["usage"]

        if ( "params" in core2 ):
            user_data=json.dumps(core2["params"]).replace('},}','}}')[:511]
     
        sqls = 'call updateAuthUsage (%s,%s,%s,%s,%s, %s,%s, %s)'
        logger.debug("pm_user.updateUsage.2: %s | %s | %s |%s", sqls, usage_data['authority'],usage_data['sub_authority'],usage_data['operation'])
        try:
            db.update2(sqls,
                (core1['user_id'], usage_data['authority'],usage_data['sub_authority'].upper(),usage_data['operation'],user_data,
                core1['User-Agent'],core1['Source-IP'], core1['Application']))
                
        except ValueError:
            logger.error("pm_user.updateUsage.10:Query Failed: %s", sqls) 
            ret = 1
    except Exception as e:
        logger.error("pm_user.updateUsage.12:Failed: %s", str(e)) 
        ret = 1
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