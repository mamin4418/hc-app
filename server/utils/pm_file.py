# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 13:50:49 2020
File operations
@author: ppare
"""
from flask import json
import pandas as pd
from utils.pm_db import PMDB


def updateFiles(db, logger, core):
    
    sqls=""
    ret = -1
    
    if ( core['key_type'] == 'TENANCY' ):
        sqls = "INSERT INTO pm.tenancy_docs (`tenancy_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','"+ core['updatedby']+"')"
        logger.debug("updateFiles[TENANCY]:%s", sqls)
    elif ( core['key_type'] == 'TENANT' ):    
        sqls = "INSERT INTO pm.tenants_docs (`tenant_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','"+ core['updatedby']+"')"
        logger.debug("updateFiles[TENANT]:%s", sqls)
    elif ( core['key_type'] == 'PROPERTY' ):    
        sqls = "INSERT INTO pm.property_docs (`property_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','"+ core['updatedby']+"')"
        logger.debug("updateFiles[PROPERTY]:%s", sqls)
    elif ( core['key_type'] == 'TX' ):    
        sqls = "INSERT INTO pm.transactions_docs (`tx_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','" + core['updatedby']+"')"
        logger.debug("updateFiles[TX]:%s", sqls)
    elif ( core['key_type'] == 'WO' ):    
        sqls = "INSERT INTO pm.wo_docs (`wo_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','" + core['updatedby']+"')"
        logger.debug("updateFiles[WO]%s", sqls)
    elif ( core['key_type'] == 'INVESTOR' ):    
        sqls = "INSERT INTO pm.investor_docs (`investor_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','" + core['updatedby']+"')"
        logger.debug("updateFiles[INVESTOR]:%s", sqls)
    elif ( core['key_type'] == 'TRANCHE' ):    
        sqls = "INSERT INTO pm.tranche_docs (`tranche_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','" + core['updatedby']+"')"
        logger.debug("updateFiles[TRANCHE]:%s", sqls)
    elif ( core['key_type'] == 'MASTER' ):        
        sqls = "INSERT INTO pm.master_docs (`master_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','" + core['updatedby']+"')"
        logger.debug("updateFiles[MASTER]:%s", sqls)
    elif ( core['key_type'] == 'COMPANY' ):        
        sqls = "INSERT INTO pm.company_docs (`company_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','" + core['updatedby']+"')"
        logger.debug("updateFiles[COMPANY]:%s", sqls)
    elif ( core['key_type'] == 'VENDOR' ):    
        sqls = "INSERT INTO pm.vendor_docs (`vendor_id`,`doc_name`,`doc_type`,`doc_path`,`doc_format`,`updatedby`) VALUES ("
        sqls += str(core['key_value']) + ",'"+core['doc_name']+"','"+core['doc_type']+"','"
        sqls += core['doc_path'] + "','" + core['doc_format']+"','" + core['updatedby']+"')"
        logger.debug("updateFiles[VENDOR]:%s", sqls)
    else:
        return -1

    try:
        logger.debug("pm_file.updateFiles.7:%s", sqls)
        db.insert(sqls,None)
        ret = 0
    except ValueError:
        logger.error("pm_file.updateFiles.8:Query Failed:%s", sqls) 
        ret = -1        
    return ret

def deleteFiles(db, logger, core):
    
    sqls=""
    ret = -1
    key_type=core['key_type']
    if ( key_type == 'TENANCY' ):
        sqls = "DELETE FROM pm.tenancy_docs where doc_id="+ str(core['doc_id'])
        logger.debug("deleteFiles.2:%s", sqls)
    elif ( key_type == 'TENANT' ):    
        sqls = "DELETE FROM pm.tenants_docs where doc_id="+ str(core['doc_id'])
        logger.debug("deleteFiles.3:%s", sqls)
    elif ( key_type == 'PROPERTY' ):    
        sqls = "DELETE FROM pm.property_docs where doc_id="+ str(core['doc_id'])
        logger.debug("deleteFiles.4:%s", sqls)
    elif ( key_type == 'TX' ):    
        sqls = "DELETE FROM pm.transactions_docs where doc_id="+ str(core['doc_id'])
        logger.debug("deleteFiles.5:%s", sqls)
    elif ( key_type == 'WO' ):    
        sqls = "DELETE FROM pm.wo_docs where doc_id="+ str(core['doc_id'])
        logger.debug("deleteFiles.6:%s", sqls)
    elif ( key_type == 'INVESTOR' ):    
        sqls = "DELETE FROM pm.investor_docs where doc_id="+ str(core['doc_id'])
        logger.debug("deleteFiles.7:%s", sqls)
    elif ( key_type == 'MASTER' ):    
        sqls = "DELETE FROM pm.master_docs where doc_id="+ str(core['doc_id'])
        logger.debug("deleteFiles.7:%s", sqls)
    elif ( key_type == 'COMPANY' ):    
        sqls = "DELETE FROM pm.company_docs where doc_id="+ str(core['doc_id'])
        logger.debug("deleteFiles.7:%s", sqls)
    elif ( key_type == 'VENDOR' ):    
        sqls = "DELETE FROM pm.vendor_docs where doc_id="+ str(core['doc_id'])
        logger.debug("deleteFiles.7:%s", sqls)
    else:
        return -1
    
    try:
        logger.debug("pm_file.deleteFiles[%s]:%s",key_type, sqls)
        db.insert(sqls,None)
        ret = core['doc_id']
    except ValueError:
        logger.error("pm_file.deleteFiles[%s]:Query Failed:%s", key_type, sqls) 
        ret = -1        
    return ret

def getDocuments(db, logger, core):
    t_pd = None
    key_type=core['key_type']
        
    sqls = " select doc_id, doc_name, doc_type, doc_path, doc_format, updatedby, date_format(updated,'%Y-%m-%d %H:%i:%S') as updated,'"+key_type+"' as key_type from "
    if ( key_type == 'TENANCY' ):
        sqls += "pm.tenancy_docs where tenancy_id="+str(core['tenancy_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( key_type == 'TENANT' ):    
        sqls += "pm.tenants_docs where tenant_id="+str(core['tenant_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( core['key_type'] == 'PROPERTY' ):    
        sqls += "pm.property_docs where property_id="+str(core['property_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( core['key_type'] == 'TX' ):    
        sqls += "pm.transactions_docs where tx_id="+str(core['tx_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( core['key_type'] == 'WO' ):    
        sqls += "pm.wo_docs where wo_id="+str(core['wo_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( core['key_type'] == 'INVESTOR' ):    
        sqls += "pm.investor_docs where investor_id="+str(core['investor_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( core['key_type'] == 'TRANCHE' ):    
        sqls += "pm.tranche_docs where tranche_id="+str(core['tranche_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( core['key_type'] == 'MASTER' ):    
        sqls += "pm.master_docs where master_id="+str(core['master_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( core['key_type'] == 'COMPANY' ):    
        sqls += "pm.company_docs where company_id="+str(core['company_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( core['key_type'] == 'VENDOR' ):    
        sqls += "pm.vendor_docs where vendor_id="+str(core['vendor_id'])
        logger.debug("getDocuments[%s]:%s",key_type, sqls)
    elif ( key_type == 'MASTER' ):
        sqls = " select doc_id, master_id, doc_name, doc_type, doc_path, doc_format, updatedby, date_format(updated,'%Y-%m-%d %H:%i:%S') as updated,'"+key_type+"' as key_type from "
        if ( "master_id" in core ):
            sqls += " where master_id="+str(core['master_id'])
        sqls += " order by doc_id"
    else:
        return t_pd
    
    try:
        logger.debug("pm_file.getDocuments.7:%s", sqls)
        mlist = db.query_list(sqls,None)
        
        t_pd = pd.DataFrame(mlist)
        

    except ValueError:
        logger.error("pm_file.getDocuments.8:Query Failed:%s", sqls) 
     
        
    return t_pd
        
        
    
    
    