# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 13:13:03 2019
Analysis by Property
@author: ppare
"""


import pandas as pd

from utils.pm_db import PMDB


def get_my_pi_pd(db, logger, core):
    
    if ( 'status' not in core ):
        core['status']='RENT READY'

    logger.debug("get_my_properties_com_pd:%s", core)
    qry = "SELECT pi.pi_id, pi.property_id, pi.tenancy_id, pi.label, date_format(pi.idate,'%Y-%m-%dT%H:%i:%S') as idate, pi.pm, pi.technician,"
    qry += "pi.notes, pi.updatedby, date_format(pi.updated,'%Y-%m-%dT%H:%i:%S') as updated FROM pm.property_inspection"
    qry +=" WHERE pi.property_id = "+str(core['property_id'])    
    qry += " order by pi.idate"    
    logger.debug("get_my_pi_pd: %s", qry)    
    mlist = PMDB.query_list(db,qry, None)
    t_pd = pd.DataFrame(mlist)
    #t_pd = t_pd.rename(columns={0:'property_id',1:'company',2:'group',3:'label',4:'unit',5:'label2', 6:'parent', 7:'city', 8:'state', 9:'zip', 10:'status', 11:'bed', 12:'bath',13:'market_rent',14:'total_rooms',15:'size'})
                    
        
    print("get_my_pi_pd.6:", t_pd)
    
    return t_pd

def get_my_pi(db, logger, core):
    
    logger.debug("get_my_pi.2:%s", core)
    qry = "SELECT pi.pi_id, pi.property_id, pi.tenancy_id, pi.label, date_format(pi.idate,'%Y-%m-%dT%H:%i:%S') as idate, pi.pm, pi.technician,"
    qry += "pi.notes, pi.updatedby, date_format(pi.updated,'%Y-%m-%dT%H:%i:%S') as updated FROM pm.property_inspection"
    qry +=" WHERE pi.pi_id = "+str(core['pi_id'])
    logger.debug("get_my_pi_pd: %s", qry)    
    mlist = PMDB.query_list(db,qry, None)
    
    qry = "SELECT pid.* from pm.property_insp_details pid "
    qry +=" WHERE pid.pi_id = "+str(core['pi_id'])
    logger.debug("get_my_pi.4: %s", qry)    
    mlist1 = PMDB.query_list(db,qry, None)                
    t_pd = pd.DataFrame(mlist)
    print("get_my_pi.6:", mlist1)

    mlist["details"] = t_pd.to_json(orient='table')
    
    return mlist

def updatePI(O_db, logger, core):
    ret = -1
    sqls = ""
    pi_id=-1;
    
    logger.info("updatePI.updateTR1: %s",core)
    
    sqls = "call pm.updatePI (%s,%s,%s,%s,%s, %s,%s,%s,%s,now())"

    try:
        O_db.insert(sqls,(pi_id, core['property_id'], core['tenancy_id'],core['label'],core['tdate'],core['pm'],core['technician'], core['notes'],core['updatedby']))
        logger.info("updatePI.:3: data updated")
    except ValueError:
        logger.error("updatePI:4:Query Failed:%s", sqls) 
        ret = -1
        
    return ret

def updatePID(O_db, logger, core):
    ret = -1
    sqls = ""
    pi_id=-1;
    
    logger.info("updatePI.updateTR1: %s",core)
    
    sqls = "call pm.updatePI (%s,%s,%s,%s,%s, %s,%s,%s,%s,now())"

    try:
        O_db.insert(sqls,(pi_id, core['property_id'], core['tenancy_id'],core['label'],core['tdate'],core['pm'],core['technician'], core['notes'],core['updatedby']))
        logger.info("updatePI.:3: data updated")
    except ValueError:
        logger.error("updatePI:4:Query Failed:%s", sqls) 
        ret = -1
        
    return ret
