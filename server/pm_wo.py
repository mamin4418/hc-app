# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 12:46:01 2020
Work order management
@author: ppare
"""

import pandas as pd
from utils.pm_db import PMDB
import utils.pm_file, utils.pm_mail, utils.pm_print

def woReports(O_db, logger, core):
    qry = ""
    logger.info("pm_wo.pdfWOS.1:%s",core)
    l_format='html'
    core['template_file']='HP Daily WO List.html'
    

    core['format']='html'
    core['template_file']='HP Daily WO List.html'
    
    return response

def createWEBWO(app, db, qj):
    
    app.logger.info("createWBWO.Property:%s" , qj)
    if ( 'category_id' not in qj ):
        qj['categoy_id']=-1;
    if ( 'property_id' not in qj ):
        qj['property_id']=-1;
    if ( 'tenant_id' not in qj ):
        qj['tenant_id']=-1;
    
    if ( int(qj['property_id']) < 100 ):
        qj['owner']='Scott LeCain'
    else:
        qj['owner']='Support'
    qj['createdby']=1 # should change to logged in ID
    qj['status']=1
    qj['coordinator']=1 # should change to appropriate coordinator
    
    ret={}
    ret['code']=-1  
    ret['message']='Could not create WO: from createWEBWO'    
    wo = updateWO(app, db, qj)
    if ( wo > 0 ):
        ret['code']=0
        ret['error']=''
        ret['wo_id']=wo
        ret['message']='New Work Order created'
        
    return ret
    
def getWO(db, logger, qj):
    
    h_pd = pd.DataFrame()
    mdict = {}
    core = {}
    wo_id = fetchNumberfromQ(logger, qj,"wo_id")
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)
        #print("pm_wo.getWO.1:"+x+"="+str(core[x]))

    qry = " SELECT w.* FROM pm.wo w, pm.auth_users_attributes aua WHERE w.property_id = aua.id_value and aua.id_type='property_id' "
    qry += " and aua.user_id = "+ str(core['user_id']) + " and w.wo_id="+  str(wo_id)
    
    logger.debug("getWO::[%s] %s",wo_id, qry)    
    mlist = PMDB.query_list(db,qry, None)

    for x in mlist:
        for k in x:
            mdict[k]=x[k]
    
    qj = {}
    qj['wo_id'] = wo_id
    qj['key_type'] = 'WO'
    pd_f = utils.pm_file.getDocuments(db, logger, qj)
    
    if ( pd_f.empty ):
        logger.info("pm_wo:getWO: No documents")
        mdict['documents']=""
    else:
        mdict['documents'] = pd_f.to_json(orient='table')
    
    h_pd = getWOH(db, logger, qj)
    
    if ( h_pd.empty ):
        logger.debug("pm_wo.getWO: History Empty")
        mdict['history']=""
    else:
        mdict['history'] = h_pd.to_json(orient='table')
    
    qry = "select * FROM pm.wo_ext WHERE wo_id="+str(wo_id)
    
    logger.debug("pm_wo.getWO.3:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)
    for x in mlist:
        for y in x:
            mdict[y]=x[y]

    return mdict

def getWOS(O_db, logger, qj):
    core = {}
    qryS = ""
    qry = ""
    logger.debug("pm_wo.getWOS.1:%s",qj)
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)    
    
    logger.info("pm_wo.getWOS.2==================== %s", core)

    if ('property_id' in core and int(core['property_id']) > 0 ):
        qryS = "select wo.wo_id, wo.category_id, wo.property_id, ifnull(wo.tenant_id,-1) as tenant_id,wo.priority, wo.title, "
        qryS += " wo.description, wo.status, wo.coordinator, wo.tags, wo.createdby, wo.tdate, wo.updatedby, wo.updated as updated, wo.contact_name, wo.contact_info, "
        qryS += " wo.reporting_method, wo.reportedby, p.label, wo.owner, p.label "
        qryS += " FROM pm.wo wo, pm.property p WHERE p.property_id = wo.property_id "
                
        if ( 'status' in core and core['status'] ):  
            qryS += " and wo.status in ( " + core['status'] + ") "
        if ( 'priority' in core and core['priority'] ):  
            qryS += " and wo.priority =" + core['priority'] + " "
        if ( 'start_date' in core and core['start_date'] != "" ):  
            qryS += " and wo.tdate >= '" + core['start_date'] + "' "
        if ( 'end_date' in core and core['end_date'] ):  
            qryS += " and wo.tdate <= '" + core['end_date'] + "' "

        qry = qryS + " and ( wo.property_id = " + str(core['property_id']) +" OR wo.property_id in ("
        qry += " select ifnull(p1.parent,0) from pm.property p1 where p1.property_id="+str(core['property_id'])+"))"

        logger.info("pm_wo.getWOS.3:===================== %s", qry)    
        mlist = PMDB.query_list(O_db,qry, None)
        t_pd = pd.DataFrame(mlist)
    elif ('vendor_id' in core and int(core['vendor_id']) > 0 ):
        qryS = "select wo.wo_id, wo.category_id, wo.property_id, ifnull(wo.tenant_id,-1) as tenant_id,wo.priority, wo.title, "
        qryS += " wo.description, wo.status, wo.coordinator, wo.tags, wo.createdby, wo.tdate, wo.updatedby, wo.updated as updated, wo.contact_name, wo.contact_info, "
        qryS += " wo.reporting_method, wo.reportedby, p.label, wo.owner "
        qryS += " FROM pm.wo wo,pm.wo_ext woe, pm.property p WHERE wo.property_id=p.property_id AND wo.wo_id=woe.wo_id "
        #qry += "WHERE t.property_id=p.property_id "
        
        if ( 'status' in core and core['status'] ):  
            qryS += " and wo.status in ( " + core['status'] + ") "
        if ( 'priority' in core and core['priority'] ):  
            qryS += " and wo.priority =" + core['priority'] + " "
            
        if ( 'start_date' in core and core['start_date'] != "" ):  
            qryS += " and wo.tdate >= '" + core['start_date'] + "' "
        if ( 'end_date' in core and core['end_date'] ):  
            qryS += " and wo.tdate <= '" + core['end_date'] + "' "

        qry = qryS + " and woe.vendor_id =" + str(core['vendor_id'])
        logger.info("pm_wo.getWOS.5: %s", qry)    
        mlist = PMDB.query_list(O_db,qry, None)
        t_pd = pd.DataFrame(mlist)
    else:
        qryS = "select wo.wo_id, wo.category_id, wo.property_id, ifnull(wo.tenant_id,-1) as tenant_id,wo.priority, wo.title, "
        qryS += " wo.description, wo.status, wo.coordinator, wo.tags, wo.createdby, wo.tdate, wo.updatedby, wo.updated as updated, wo.contact_name, wo.contact_info, "
        qryS += " wo.reporting_method, wo.reportedby, p.label, wo.owner "
        qryS += " FROM pm.wo wo, pm.property p, pm.auth_users_attributes aua  WHERE wo.property_id=p.property_id "
        qryS += " and wo.property_id = aua.id_value and aua.id_type='property_id' and aua.user_id = "+ str(core['user_id'])
        #qry += "WHERE t.property_id=p.property_id "
        
        if ( 'status' in core and core['status'] ):  
            qryS += " and wo.status in ( " + core['status'] + ") "
        if ( 'priority' in core and core['priority'] ):  
            qryS += " and wo.priority =" + core['priority'] + " "
            
        if ( 'start_date' in core and core['start_date'] != "" ):  
            qryS += " and wo.tdate >= '" + core['start_date'] + "' "
        if ( 'end_date' in core and core['end_date'] ):  
            qryS += " and wo.tdate <= '" + core['end_date'] + "' "

        if ( 'tenant_id' in core and int(core['tenant_id']) > 0 and 'property_id' in core and int(core['property_id']) > 0):  
            qry = qryS + " and wo.tenant_id =" + str(core['tenant_id']) + " UNION "
            qry += qryS + " and wo.property_id =" + str(core['property_id']) 
        elif ( 'tenant_id' in core and int(core['tenant_id']) > 0 ):  
            qry = qryS + " and wo.tenant_id =" + str(core['tenant_id']) 
        elif ( 'property_id' in core and int(core['property_id']) > 0 ):  
            # shall improvise to include parent property
            qry = qryS + " and wo.property_id =" + str(core['property_id'])
        else:
            qry = qryS
    
        qry += " ORDER BY updated "
    
        logger.info("pm_wo.getWOS.7: %s", qry)    
        mlist = PMDB.query_list(O_db,qry, None)
        t_pd = pd.DataFrame(mlist)

    return t_pd

def getWOH(O_db, logger, qj):
    core = {}
    qry = ""
    wo_id = fetchNumberfromQ(logger, qj,"wo_id")
    
    logger.debug("pm_wo.getWOH.1:%s",qj)
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)    
    
    logger.info("pm_wo.getWOH.2=%s",core)

    qry = "select * "
    qry += " FROM pm.wo_history WHERE wo_id="+str(wo_id)
    qry += " ORDER BY tdate desc"
    
    logger.info("pm_wo.getWOH.3:%s", qry)    
    mlist = PMDB.query_list(O_db,qry, None)
    t_pd = pd.DataFrame(mlist)

    return t_pd


 
def getWOH2(O_db, logger, qj):
    core = {}
    qry = ""
    wo_id = fetchNumberfromQ(logger, qj,"wo_id")
    
    logger.info("pm_wo.getWOH2.1:%s",qj)
    for x in qj:
        core[x] = fetchTextfromQ(logger, qj,x)    
    
    logger.debug("pm_wo.getWOH2.2= %s", core)

    qry = "select * "
    qry += " FROM pm.wo_history WHERE wo_id="+str(wo_id)
    qry += " ORDER BY tdate desc"
    
    logger.debug("pm_wo.getWOH2.3:%s", qry)    
    mlist = PMDB.query_list(O_db,qry, None)

    return mlist

def updateWO(app,O_db, qj):
    ret=-1
    core = qj
    wo_id=-1
    sqls=""
    diff=""
    tab = qj['tab'] 
    app.logger.info("pm_wo.updateWO.1: entered: %s", qj)

    #for x in qj:
        #core[x] = fetchTextfromQ(app.logger, qj,x)    
        #print("pm_wo.updateWO.2=", x, "=", core[x])
       
    if ('wo_id' in core):
        wo_id = int(core['wo_id'])
        
    # use basic algo , use description to identify tags
    if ( 'tags' not in core ):
        core['tags']='No Tags'
    if ( 'owner' not in core ):
        core['owner']='NA'

    numberList = ['priority','status','coordinator','property_id','tenant_id','tx_id','supply_cost','total_cost','vendor_id','reporting_method']
    fieldList = ['title','description','tags','contact_name','contact_info','availability','owner','reportedby','pet']
    if (wo_id > 0 and tab == 'PRIMARY'):
        numberList = ['priority','status','coordinator','property_id','tenant_id','tx_id']
        
        c_wo = getWO(O_db, app.logger, qj)
        # update - not all fields can be updated
        sqls = "UPDATE pm.wo SET priority=%s,status=%s,coordinator=%s,property_id=%s,tenant_id=%s,title=%s,"
        sqls += "description=%s,tags=%s,contact_name=%s,contact_info=%s,availability=%s,reporting_method=%s,owner=%s,"
        sqls += "reportedby=%s, updated=now(), pet=%s "
        sqls += " WHERE wo_id=%s"
        
        for x in c_wo:
            #app.logger.debug("pm_wo.updateWO.20.LOOP=%s = %s = %s", x,c_wo[x], core[x])
            if ( x in numberList and c_wo[x] != core[x] ):
                diff += x +" : updated "+str(c_wo[x])+"->"+str(core[x])+"; "
            elif ( x in fieldList and c_wo[x] != core[x] ):
                diff += x +" : updated "+c_wo[x]+"->"+core[x]+"; "
            else:
                app.logger.debug("pm_wo.updateWO.21.LOOP=IGNORED=%s %s", c_wo[x], x)
        
        if ( diff == ""):
            return core['wo_id']
        try:
            app.logger.info("pm_wo.updateWO:Diff: %s" , diff)
            O_db.insert(sqls,(core['priority'], core['status'],core['coordinator'],core['property_id'], core['tenant_id'],
                              core['title'],core['description'],core['tags'],core['contact_name'],core['contact_info'],
                              core['availability'], core['reporting_method'], core['owner'], core['reportedby'],
                              core['pet'], core['wo_id']))
            app.logger.info("pm_wo.updateWO[%s].23.update success: %s" , tab, sqls)
            ret=0
        except Exception as e:
            app.logger.error("pm_wo.updateWO::Query Failed: %s", e) 
            ret = -1

        if ( diff != '' and ret > -1 ):
            core['h_description'] = diff
            updateWOH(app.logger, O_db, core)

        ret = core['wo_id']
    elif (wo_id > 0 and tab == 'MAINTENANCE'):
        app.logger.debug("pm_wo.updateWO=%s", tab)
        numberList = ['tx_id','supply_cost','total_cost','vendor_id']
        fieldList = ['notes','vendor_name','vendor_email','vendor_phone','vendor_notes']
        c_wo = getWO(O_db, app.logger, qj)
        try:
            for x in core:
                if ( x in numberList and x not in c_wo):
                    diff += x +" : added["+str(core[x])+"]; "
                elif ( x in numberList and c_wo[x] != core[x] ):
                    diff += x +" : updated["+str(c_wo[x])+"->"+str(core[x])+"]; "
                elif ( x in fieldList and x not in c_wo ):
                    diff += x +" : added["+core[x]+"]; "
                elif ( x in fieldList and c_wo[x] != core[x] ):
                    diff += x +" : updated["+c_wo[x]+"->"+core[x]+"]; "
                elif ( x == 'vendor_notify' and c_wo[x] != core[x]):
                    core[x]=str(core[x])
                    diff += x +" : updated["+c_wo[x]+"->"+core[x]+"]; "
                else:
                    app.logger.debug("pm_wo.updateWO.29.LOOP=IGNORED=%s %s", x, core[x])
        except Exception as e:
            app.logger.error("pm_wo.updateWO::Comp Failed: %s", e) 
        # update - not all fields can be updated
        app.logger.info("pm_wo.updateWO:Diff: %s" , diff)
        if ( diff == ""):
            return core['wo_id']

        
        ret = updateWOEXT(app.logger, O_db, core['wo_id'], core, 1)
        

        if ( diff != '' and ret > -1):
            core['h_description'] = diff
            updateWOH(app.logger, O_db, core)

        ret = core['wo_id']
    else:
        # New
        if ( 'vendor_id' not in core ):
            core['vendor_id']="-1"
        sqls= " INSERT pm.wo (property_id,tenant_id,priority, title, description, owner,"
        sqls += "status, coordinator, tags, createdby, updatedby,"
        sqls += "contact_name, contact_info, reporting_method, reportedby, pet ) "
        sqls += "VALUES(%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s) "       
        
        app.logger.info("pm_wo.updateWO.3=%s %s",wo_id, sqls)

        try:
            O_db.insert(sqls, (core['property_id'],core['tenant_id'],core['priority'],core['title'],core['description'],core['owner']
            ,core['status'],core['coordinator'],core['tags'],core['createdby'],core['updatedby']
            ,core['contact_name'],core['contact_info'],core['reporting_method'],core['reportedby'],core['pet']))
            app.logger.debug("pm_wo.updateWO.4:: data updated: %s", sqls)
            h=core
            # FIND WO ID
            sqls = "select wo_id, updated from pm.wo where reportedby=%s and property_id= %s and tenant_id=%s "
            sqls += " and title=%s and description=%s and contact_name=%s and status=%s and priority=%s and contact_info=%s and updatedby=%s"
            
            app.logger.debug("pm_wo.updateWO.6:%s", sqls)
            mlist = O_db.query_list(sqls,(core['reportedby'],core['property_id'],core['tenant_id'],core['title'],core['description'], 
                            core['contact_name'],core['status'],core['priority'], core['contact_info'],core['updatedby']))
            for x in mlist:
                ret=x['wo_id']
            h['wo_id']=ret
            core['wo_id']=ret
            h['h_description'] = "New Work order created"
            updateWOH(app.logger, O_db, h)

            #updateWOEXT(app.logger, O_db, core['wo_id'], core, 0)
            
        except ValueError:
            app.logger.error("pm_wo.updateWO::Query Failed: %s", sqls) 
            ret = -1
    
    if (ret > 0 and 'vendor_notify' in core and core['vendor_notify'].lower() == 'true' ):
        #notification
         
        if ( 'vendor_email' in core and core['vendor_email'] != ""):
            core['receiver_email'] = core['vendor_email']
            
        try:
            utils.pm_mail.sendWONotification(app, O_db, core) 
        except Exception as e:
            app.logger.error("pm_wo.updateWO::Query Failed: Could not send email: %s", e) 
        
    return ret

def updateWOContractor(logger, O_db, core):
    logger.info("pm_wo.updateWOContractor.1: entered -> %s", core)

def updateWOH(logger, O_db,core):
    
    logger.info("pm_wo.updateWOH.1: entered -> %s", core)
    
    ret = -1    
    title= "WO Update"#str(core['priority'])+",
    sqls= " INSERT pm.wo_history (wo_id, title, comments, updatedby)"
    sqls += "VALUES("+str(core['wo_id'])+",'"+title+"','"+core['h_description']+"','"+core['updatedby'] + "')"
    
    logger.info("pm_wo.updateWOH.2: %s", sqls)    

    try:
        logger.info("pm_wo.updateWOH.4:: Date updated-> %s", sqls)    
        O_db.insert(sqls,None)
        ret = 1
    except ValueError:
        logger.error("pm_wo.updateWOH.5:Query Failed-> %s", sqls) 

    return ret



def updateWOEXT(logger, O_db, wo_id, core, i):
    
    sqls = ""
    logger.info("updateWOEXT: %s", core)
    ret=-1

    if ( 'vendor_notes' not in core):
        core['vendor_notes']=''
    if ( 'vendor_notify' not in core):
        core['vendor_notify']='false'
    if ( 'tx_id' not in core):
        core['tx_id']=-1
    if ( 'supply_cost' not in core):
        core['supply_cost']=-1
    if ( 'total_cost' not in core):
        core['total_cost']=-1
    if ( i > 0 ):
        sqls = "SELECT count(*) as value FROM pm.wo_ext pa WHERE pa.wo_id="+str(wo_id)
        logger.debug("updateWOEXT: %s", sqls)
        mlist = O_db.query_list(sqls, None)
        for y in mlist:
            i = y['value']
    
    if ( i == 0):
        sqls = "INSERT pm.wo_ext (vendor_id, vendor_name, vendor_email, vendor_phone, vendor_notes, vendor_notify,supply_cost, total_cost, tx_id,updatedby, wo_id ) VALUES(%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s) " 
    
    else:
        sqls = "UPDATE pm.wo_ext SET vendor_id=%s, vendor_name=%s,vendor_email=%s, vendor_phone=%s, vendor_notes=%s, vendor_notify=%s,"
        sqls += " supply_cost=%s, total_cost=%s, tx_id=%s, updatedby=%s, updated=now()"
        sqls += " WHERE wo_id=%s"
    try:
        logger.debug("updateWOEXT:3: %s",sqls)
        O_db.insert(sqls,(core['vendor_id'], core['vendor_name'], core['vendor_email'], core['vendor_phone'], core['vendor_notes'], core['vendor_notify'], core['supply_cost'],core['total_cost'],core['tx_id'],core['updatedby'],wo_id))
        ret = wo_id
    except ValueError:
        logger.error("pm_wo.updateWOH.5:Query Failed-> %s", sqls) 

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
            logger.warn("No Action: %s %s", val,lv)
        
        
    return lv


