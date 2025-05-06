# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:04:13 2020

@author: ppare
"""
import traceback
from flask import json
import pandas as pd
from utils.pm_db import PMDB

def get_my_vendors_pd(db, logger, tt, vid=-1):
    
    qry = "select * from pm.vendors v"
    
    if ( vid > 0 ):
        qry += " where v.vendor_id=" + str(vid)
    elif ( tt != None and tt != "ALL"):
        qry += " where v.status='" + tt + "'"
    
    qry += " order by v.name "

    logger.debug("get_my_vendors_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)
    t_pd = t_pd.set_index('vendor_id')

    return t_pd

def get_vendor_tx_pd(db, logger, qj):

    logger.debug("get_vendors_tx_pd:entered : %s", qj)        
    qry = "select tx.*, p.label as property, c.label as category, 'tx' as tx_type, p.llc, trc.tranche_name "
    qry += "from pm.transactions tx, pm.vendors v, pm.property p, pm.category c, pm.tranche trc " 
    qry += "where p.property_id=tx.property_id and tx.category_id=c.category_id and tx.payee = v.name "
    qry += " and trc.tranche_id = p.tranche_id and v.vendor_id=" + str(qj['vendor_id'])
    
    if ( 'start_date' in qj):
        qry += " and tx.tdate >= '"+ qj['start_date'] +"' "
            
    if ( 'start_date' in qj):
        qry += " and tx.tdate <= '"+ qj['end_date'] +"' "
    
    qry += " order by tx.tdate "

    logger.debug("get_vendors_tx_pd:%s", qry)    
    mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(mlist)

    return t_pd

########################################################## vendor #####################

def updateVendor(O_db, logger, qj):
    core = {}
    t_id=-999
    ret={}
    ret['message']="no actions"
    ret['code']=-1
    sqls = ""
    qf = 'UPDATE'

    logger.debug("pm_vendor::updateVendor:%s",qj)
    
    qf = fetchTextfromQ(logger,qj,'qualifier')
    for x in qj:
        core[x] = fetchTextfromQ(logger,qj,x)    
    if ( 'vendor_id' in core ):
            t_id=int(core['vendor_id'])
    
    for x in core:
        logger.debug("pm_vendor::updateVendor1=%s [%s]", x, core[x])
    ret['vendor_id']=t_id

    if (t_id < 0) :
        
        fieldList = ['account','description','tax_id','site_login','site_password','phone2','contact','address2','website']
        for x in fieldList:
            if( x not in core ):
                core[x]=''
        logger.debug("pm_vendor.updateVendor:: new vendor id=%s",t_id)

        try:
            mlist = O_db.query_list('call updateVendor (-1, %s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s)',
                    (core['name'],core['label'],core['address1'],core['address2'], core['city'],core['state'],core['zip'],
                    core['tax_id'], core['phone'], core['email'], core['contact'], core['services'], 
                    core['website'], core['account'], core['site_login'], core['site_password'],
                    core['description'],core['status'], core['user_id'] ))
        
            for x in mlist:
                logger.debug("pm_vendor.updateVendor:%s",x)
                ret['vendor_id']=x['vendor_id']
            ret['message']="Vendor creation successful"
            ret['code']=0
        except Exception as e:
            logger.error("pm_vendor.updateVendor: vendor creation failed:%s", e);
            ret['message']=traceback.format_exc()
            ret['code']=-1
        
        return(ret)
        
    elif ( t_id > 0 ) :
        
        logger.debug("pm_vendor.updateVendor::PRIMARY[%s]",t_id)
        try:
            mlist = O_db.query_list('call updateVendor (%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s)',
                    (core['vendor_id'], core['name'],core['label'],core['address1'],core['address2'], core['city'],core['state'],core['zip'],
                    core['tax_id'], core['phone'], core['email'], core['contact'],
                    core['services'], core['website'], core['account'], core['site_login'], core['site_password'],
                    core['description'],core['status'], core['user_id'] ))
            for x in mlist:
                #logger.debug("pm_vendor.updateVendor:%s",x)
                t_id=x['vendor_id']
            ret['message']="Vendor update successful"
            ret['code']=0
        except Exception as e:
            logger.error("pm_vendor.updateVendor: vendor update failed:%s", e);
            ret['message']=traceback.format_exc()
            ret['code']=-1
        
        return(ret)

    return(ret)


def vendorHistory(O_db, logger, core):
    logger.debug("vendorHistory.0:%s", core)
    sqls = "INSERT INTO pm.vendors_history(`vendor_id`,`title`,`comments`,`updatedby`) VALUES(%s,%s,%s,%s)"
    ret=0
    
    try:
         logger.debug("vendorHisotry.1:%s", sqls)
         mlist = O_db.query_list(sqls,(core['vendor_id'], core['title'], core['comments'], core['updatedby']))
         ret=1
    except:
         logger.error("vendorHistory2: vendor history update failed");
         ret=-1
        
        
    return ret;
                

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
    
