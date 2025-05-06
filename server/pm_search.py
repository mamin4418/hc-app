# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 07:50:14 2020
Search
@author: ppare
"""
import pandas as pd
from utils.pm_db import PMDB

def searchMe(db, logger, src, user_id):
    qry = "SELECT sv.* "
    qry += "FROM pm.search_view sv, pm.auth_users_attributes aua where sv.search like lower('%" + src + "%') "
    qry += " and sv.key_type=aua.id_type and sv.key_value=aua.id_value and sv.key_type != 'tenant_id' and aua.user_id="+str(user_id)
    qry += " UNION "
    qry += " SELECT sv.* "
    qry += " FROM pm.search_view sv where sv.search like lower('%"+src +"%') and sv.key_type='tenant_id'"
    qry += " ORDER BY search"
    
    logger.debug("pm_search:searchMe::%s", qry)    
    #mlist = PMDB.query_list(db,qry, None)

    t_pd = pd.DataFrame(PMDB.query_list(db,qry, None))
    t_pd = t_pd.rename(columns={0:'type',1:'id',2:'search'})
    #t_pd = t_pd.set_index('type')
    
    logger.debug("searchMe:%s",t_pd)
    
    return t_pd
    