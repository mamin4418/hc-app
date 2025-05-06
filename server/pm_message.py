# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:04:13 2020

@author: ppare
"""
from flask import json, render_template
import pandas as pd
from datetime import datetime
from utils.pm_db import PMDB
import pm_user, pm_update

def get_message(O_db, app, qj):
    ret=-1
    sqls = ""
    mlist = {}
    core={}
    core['code']='1'

    ts=datetime.today().strftime('%Y%m%d%H%S')
    tdate=datetime.today().strftime('%Y-%m-%d')

    app.logger.debug("get_message:%s",qj)
    

    try:
        sql = "select m.* from pm.messages m where m.m_status=1 and m.message_key='"+qj['report']+"'"
        if ( 'tdate' in qj and qj['tdate'] != ""):
            sql += " and m.start_date <='"+qj['tdate']+"' and m.end_date >='"+qj['tdate']+"'"
        app.logger.debug("get_message:2: %s", sql)
        
        mlist = O_db.query_list(sql, None)
        app.logger.debug("get_message:5: %s", mlist)
        for x in mlist:
            core = x
            core['code'] = '0'
        app.logger.debug("get_message:7: %s", core)
    except Exception as e:
        app.logger.error("get_message: failed:%s", e);
    

    return core

    

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