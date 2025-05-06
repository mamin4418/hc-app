# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 21:23:02 2020

@author: ppare
"""
from flask import json
import utils.pm_mail
import pandas as pd

FileName='pm_application'

def getTenancyApplication(app, O_db, core):
    FNAME=FileName+":getTenancyApplication"
    core = {}
    sqls = ""
    app.logger.info("%s.0:%s",FNAME,core)
    
    if ( 'tenancy_app_id' not in core ):
        return("")
    
    sqls = "SELECT ta.* FROM pm.tenancy_applications ta where ta.tenancy_app_id="+str(core['tenancy_app_id'])
    mlist = O_db.query_list(sqls, None)
    
    return(mlist[0])
        
def getTenancyApplications(app, O_db, core):
    FNAME=FileName+":getTenancyApplication"
    sqls = ""
    app.logger.info("%s.0:%s",FNAME,core)
    
    sqls = "SELECT ta.* FROM pm.tenancy_applications ta "
    where="where ";
    if ( 'status' in core ):
        sqls += where + " ta.status in ("+core['status']+")"
        where=" and " 

    if ( 'start_date' in core and core['start_date'] != '' ):
        sqls += where + " DATE(ta.app_date) >= '"+core['start_date']+"'"
        where=" and " 
    if ( 'end_date' in core and core['end_date'] != ''):
        sqls += where + " DATE(ta.app_date) <= '"+core['end_date']+"'"
    app.logger.info("%s.10:%s",FNAME, sqls) 
    mlist = O_db.query_list(sqls, None)
    t_pd = pd.DataFrame(mlist)

    return t_pd

def updateTenancyApplication(app, O_db, qj):
    FNAME=FileName+":updateTenancyApplication"
    core = {}
    app_id=-1
    ret=-1
    sqls = ""
    r={}
    app.logger.info("%s.0:%s",FNAME,qj)
    
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)  
        
    #application = json.dumps(core).replace('},}','}}')
    
    if ( 'tenancy_app_id' in core and core['tenancy_app_id'] != ''):
        app_id=int(core['tenancy_app_id'])

    if ( app_id < 1 ):
        r['message']='Application could not be updated, incorrect data.'
        r['status']='Failure'
        r['code']=-1
        r['tenancy_app_id']=app_id
        return r

    sqls = "UPDATE pm.tenancy_applications tca SET "
    sqls += " tca.credit_score=%s, tca.identification=%s, tca.income_proof=%s,"
    sqls +=" tca.property_id=%s, status=%s,note=%s,updatedby=%s, updated=now() WHERE tca.tenancy_app_id = %s"
    
    try:
        app.logger.info("%s:4:%s",FNAME, sqls)
        O_db.insert(sqls,(core['credit_score'],core['identification'],core['income_proof'],core['property_id'], core['status'], core['note'], core['updatedby'], app_id))
        ret = app_id
    except ValueError:
        app.logger.error("%s::Query Failed1:%s" , FNAME, sqls) 
        ret=-1
        
    app.logger.info("%s: new tenancy id=%s", FNAME,app_id)

    if ( ret > 0 ):
        r['message']='Application updated'
        r['status']='Success'
        r['code']=0
        r['tenancy_app_id']=app_id
    else:
        r['message']='Application could not be updated'
        r['status']='Failure'
        r['code']=ret
        r['tenancy_app_id']=ret
    
    return(r)

def createTenancyApplication(app, O_db, qj):
    FNAME=FileName+":createTenancyApplication"
    core = {}
    app_id=-1
    ret=-1
    sqls = ""
    r={}
    app.logger.info("%s.0:%s",FNAME,qj)
    
    for x in qj:
        core[x] = fetchTextfromQ(qj,x)  
        
    application = json.dumps(core).replace('},}','}}')
    
    if ( 'tenancy_app_id' in core and core['tenancy_app_id'] != ''):
        app_id=int(core['tenancy_app_id'])
        
    if (app_id < 0):
        
        sqls = "INSERT INTO `pm`.`tenancy_applications` (`property_id`,`application`,`updatedby`) "
        sqls +="VALUES (%s, %s, %s) "

        try:
            app.logger.info("%s:2:%s",FNAME, sqls)
            O_db.insert(sqls,(core['property_id'], application,  core['updatedby']))
            
        except ValueError:
            app.logger.error("%s::Query Failed1:%s" , FNAME, sqls) 
            ret=-1
    else:
        sqls = "UPDATE pm.tenancy_applications tca SET "
        sqls +=" tca.property_id=%s, tca.application=%s, status='UPDATED', updatedby=%s WHERE tca.tenancy_app_id = %s"
        
        try:
            app.logger.info("%s:4:%s",FNAME, sqls)
            O_db.insert(sqls,(core['property_id'], application,  core['updatedby'], app_id))
            
            ret = app_id
        except ValueError:
            app.logger.error("%s::Query Failed1:%s" , FNAME, sqls) 
            ret=-1
        
    if ( app_id < 0):
        sqls = "SELECT max(t.tenancy_app_id) as tenancy_app_id from pm.tenancy_applications t where t.property_id="+str(core['property_id'])
        mlist = O_db.query_list(sqls, None)
        for x in mlist:
            app_id = x['tenancy_app_id']
            core['tenancy_app_id']=app_id
            ret = app_id
    app.logger.info("%s: new tenancy id=%s", FNAME,app_id)

    if ( ret > 0 ):
        r['message']='Application submitted'
        r['status']='Success'
        r['code']=0
        r['tenancy_app_id']=app_id
    else:
        r['message']='Application could not be saved'
        r['status']='Failure'
        r['code']=ret
        r['tenancy_app_id']=ret

    try:
        utils.pm_mail.sendApplicationNotification(app, O_db, core)
    except:
        app.logger.error("%s: Count not send email", FNAME)
    
    return(r)


########################################################## General #####################
   
def fetchNumberfromQ(qj, val):
    lv=0
    if ( val in qj):
        try:
            lv = qj[val]
    
        except ValueError:
            print(val , ": VE2=Not found", qj[val])
        except AttributeError:
            print(val , ": AE2=Not found", qj[val])
    return lv  

def fetchTextfromQ(qj, val):
    lv=""
    if ( val in qj):
        try:
            lv = qj[val]
        except ValueError:
            print(val + ": Not found")
    if ( lv == None ):
        lv = ""
    else:
        try:
            lv = lv.strip()
        except AttributeError:
            print(val + ": No Action..")
        
        
    return lv