# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 11:09:35 2019

@author: ppare
"""
import sys, getopt
import ref_data
from pm_property import PMProperty
import numpy as np

import pandas as pd



from pm_db import PMDB

mc_ALL = {}
mc_R = {}

db = PMDB

debug = 0

sqlf = open("mysql-log.txt", "w")
sqle = open("mysql-error.txt", "w")

def deleteTS(db1,tdate, tp):
    print("deleteTS:", tp)
    sqls = "DELETE FROM pm.property_ts ps WHERE ps.tdate='"+tdate+"'"
    print("deleteTS.1: amount:",sqls)
    try:
        db1.delete(sqls)
    except ValueError:
        print("deleteTS.2: Failed:" + sqls) 
    
def updateTS(db1,tdate, p_id, c_id, na ):
    print("updateTS:")
    oa=-999
     
    sqls = "SELECT ps.value FROM pm.property_ts ps WHERE ps.tdate='"+tdate+"' and ps.property_id="+str(p_id) + " and ps.category_id="+str(c_id)
    print("updateTS.1: amount:", na, sqls)
    ct = db1.query_one(sqls, None)
    if ( ct != None ):
        oa = ct['value']
    
    print("category:", c_id, " amount:", na, " from db:", oa)
    if ( oa == -999 and na != 0 ):
        sqls = "INSERT INTO pm.property_ts(`property_id`,`category_id`,`tdate`,`value`) "
        sqls += "VALUES ("+str(p_id)+","+str(c_id)+",'"+tdate+"',"+ str(na)+")"
        try:
            print("Final Query:", sqls)
            if ( debug < 1 ):
                ct = db1.insert(sqls, None)
            else:
                print("DEBUG MODE")
        except ValueError:
            print("Final Query Failed:" + sqls) 
    elif ( oa != -999 and oa != na ):
        sqls = "UPDATE pm.property_ts SET value="+str(na)+" WHERE property_id=" + str(p_id) + " and category_id="+str(c_id)+ " and tdate ='"+tdate+"'"
    
        try:
            print("Final Query:", sqls)
            if ( debug < 1 ):
                ct = db1.update(sqls)
            else:
                print("DEBUG MODE")
        except ValueError:
            print("Final Query Failed:" + sqls) 
    else:
        print("NO update required")
        
def updateParentTS(db1,tdate, p_id, pc_id, c_id ):
    print("updateTS:",tdate, p_id, pc_id, c_id )
    
    oa=-999
    na = -999
    
    sqls = "SELECT if(isnull(sum(ps.value)),-999,sum(ps.value)) as value FROM pm.property_ts ps WHERE ps.tdate='"+tdate+"' and ps.property_id in ("+str(p_id)+","+pc_id + ") and ps.category_id="+str(c_id)
    print("updateParentTS.1: amount:",  sqls)
    ct = db1.query_one(sqls, None)
    if ( ct != None):
        na = ct['value']
   
    if ( na == -999 ):  # clean up if there is no value
        return
        
    sqls = "SELECT ps.value FROM pm.property_ts ps WHERE ps.tdate='"+tdate+"' and ps.property_id="+str(p_id) + " and ps.category_id="+str(c_id)
    print("updateParentTS.2: amount:", sqls)
    ct = db1.query_one(sqls, None)
    if ( ct != None ):
        oa = ct['value']
    
    print("category:", c_id, " amount:", na, " from db:", oa)
    if ( oa == -999 and na != -999 ):
        sqls = "INSERT INTO pm.property_ts(`property_id`,`category_id`,`tdate`,`value`) "
        sqls += "VALUES ("+str(p_id)+","+str(c_id)+",'"+tdate+"',"+ str(na)+")"
        try:
            print("updateParentTS.3. Final Query:", sqls)
            if ( debug < 1 ):
                ct = db1.insert(sqls, None)
            else:
                print("DEBUG MODE")
        except ValueError:
            print("Final Query Failed:" + sqls) 
    elif ( oa != -999 and oa != na ):
        sqls = "UPDATE pm.property_ts SET value="+str(na)+" WHERE property_id=" + str(p_id) + " and category_id="+str(c_id)+ " and tdate ='"+tdate+"'"
    
        try:
            print("Final Query:", sqls)
            if ( debug < 1 ):
                db1.update(sqls)
            else:
                print("DEBUG MODE")
        except ValueError:
            print("Final Query Failed:" + sqls) 
    else:
        print("updateParentTS.7:NO update required")


# Loop for parents
def updateP_TS2 (db1, tdate, sdate, edate):
    
    my_categories = ref_data.get_my_categories_by_id(db1, None)   
    
    sqls = "SELECT p.property_id, if(isnull(p.parent),-1, p.parent) as parent FROM pm.property p where isnull(p.end_date) and p.property_id > 0"
    print("updateP_TS2.1: ",sqls)
    mlist = db1.query_list1(sqls)
    plist = {}
    for x in mlist:
        #print("updateP_TS2.2.loop:", x)
        if ( x['parent'] > 0 and x['parent'] in plist ):
            plist[x['parent']][0] += ","+ str(x['property_id'])
        elif ( x['parent'] > 0 and x['parent'] not in plist ):
            plist[x['parent']]=[str(x['property_id'])]
        
    print("updateP_TS2.4:",plist)

    for x in plist:        
        for c_id in my_categories:
            updateParentTS(db1, tdate, x, plist[x][0], c_id)
        
def updateP_TS1 (db1, tdate, sdate, edate):
    i=0
    my_categories = ref_data.get_my_categories_by_id(db1, None)    
    
    my_properties = ref_data.get_my_properties(db1)
    
    for p in my_properties:
        
        p_id = my_properties[p][0]
 
        label=""

        sqls = "SELECT t.tx_id, p.label as label, p.property_id, c.category_id, date_format(t.tdate,'%Y-%m-%d') as tdate, t.credit, t.debit, "
        sqls += " abs(t.credit - t.debit) as amount, t.description,c.name "
        sqls += "FROM pm.property p, pm.transactions t, pm.category c "
        sqls += "WHERE p.property_id = t.property_id AND t.category_id = c.category_id "
        sqls += " AND p.property_id in (" + str(p_id) + ")"
    
        sqls += " and t.tdate between '" + sdate + "' and '" + edate + "' "
        sqls += " ORDER BY t.tdate"
            
        print("pm_property.updateFTS: ",sqls)
        mlist = db1.query_list1(sqls)
 
        if ( len(mlist) < 1):
            continue       
            #t_dict = {"Category": my_categories.keys()}
        t_dict = my_categories.keys()
        #print("Dict:", t_dict)
        t_pd = pd.DataFrame(t_dict)
        t_pd = t_pd.rename(columns={0:'category'})
        t_pd = t_pd.set_index('category')
        
        for x in mlist:
            print("Data:", x)
            s = x['category_id']
            label = x['label']
            
            if label in t_pd.columns:
                t_pd.at[s, label] += x['amount']
                #t_pd.at[s,'current'] += x['amount']
            else:
                t_pd[label]=0.0
                t_pd.at[s,label]=x['amount']
                #t_pd.at[s,'current'] += x['amount']
            # Parent update
            ps = my_categories[s][4]
            while ( ps and ps != '' ):
                #print ("updateFS: code:", s, " parent:", ps, " column:", label, " amount:", x['amount'])
                t_pd.at[ps,label] += x['amount']
                ps = my_categories[ps][4]    
            
        t_pd['name']=""
        for k in t_dict:
            t_pd.at[k,'name'] = my_categories[k][2]
        
        #print(t_pd)

        for ind in t_pd.index:            
            if ( pd.notnull(t_pd[label][ind])  and t_pd[label][ind] != 0 ):  
                i += 1
                #print ("pandas TS loop:",ind, ":", rowData)
                updateTS(db1, tdate, p_id, ind, t_pd[label][ind])
           
    print("updateP_TS :Processed :", i)

def updateP_RC1 (db1, tdate, sdate, edate):
    i=0
    my_categories = ref_data.get_my_categories_by_id(db1, 'RECEIVABLE')    
    print(my_categories)
    my_properties = ref_data.get_my_properties(db1)
    
    for p in my_properties:
        
        p_id = my_properties[p][0]
 
        label=""

        sqls = "SELECT t.tx_id, p.label as label, p.property_id, c.category_id, date_format(t.tdate,'%Y-%m-%d') as tdate,"
        sqls += " t.amount, t.description,c.name "
        sqls += "FROM pm.property p, pm.tenants_receivable t, pm.category c "
        sqls += "WHERE p.property_id = t.property_id AND t.category_id = c.category_id "
        sqls += " AND p.property_id in (" + str(p_id) + ")"
    
        sqls += " and t.tdate between '" + sdate + "' and '" + edate + "' "
        sqls += " ORDER BY t.tdate"
            
        print("updateP_RC1.3: ",sqls)
        mlist = db1.query_list1(sqls)
 
        if ( len(mlist) < 1):
            continue       
            #t_dict = {"Category": my_categories.keys()}
        t_dict = my_categories.keys()
        #print("Dict:", t_dict)
        t_pd = pd.DataFrame(t_dict)
        t_pd = t_pd.rename(columns={0:'category'})
        t_pd = t_pd.set_index('category')
        
        for x in mlist:
            print("Data:", x)
            s = x['category_id']
            label = x['label']
            
            if label in t_pd.columns:
                t_pd.at[s, label] += x['amount']
                #t_pd.at[s,'current'] += x['amount']
            else:
                t_pd[label]=0.0
                t_pd.at[s,label]=x['amount']
                #t_pd.at[s,'current'] += x['amount']
            # Parent update
            ps = my_categories[s][4]
            while ( ps and ps != '' ):
                print ("updateFS: code:", s, " parent:", ps, " column:", label, " amount:", x['amount'])
                t_pd.at[ps,label] += x['amount']
                ps = my_categories[ps][4]    
            
        t_pd['name']=""
        for k in t_dict:
            t_pd.at[k,'name'] = my_categories[k][2]
        
        #print(t_pd)

        for ind in t_pd.index:            
            if ( pd.notnull(t_pd[label][ind])  and t_pd[label][ind] != 0 ):  
                i += 1
                #print ("pandas TS loop:",ind, ":", rowData)
                updateTS(db1, tdate, p_id, ind, t_pd[label][ind])
           
    print("updateP_RC1 :Processed :", i)
# find properties and create structure with parent-child
# run through all properties and update TS
def updateP_TS (db1, tdate, sdate, edate):
    
    # clean up current TS
    deleteTS(db1, tdate, 'PROPERTY')
    # work through each properties by property ID
    updateP_TS1 (db1, tdate, sdate, edate)
    # update receivables
    updateP_RC1 (db1, tdate, sdate, edate)
    # now work through parent units.. 
    updateP_TS2 (db1, tdate, sdate, edate)

def main(argv):
    tdate=""
    edate=""
    db = PMDB("127.0.0.1", 3310, "root", "Auronia2018", "pm", None)
    
    
    try:
        opts, args = getopt.getopt(argv,"ht:e:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('pm-batch1.py -t <tdate> -edate <end trade date>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('pm-batch1.py -t <tdate> -edate <end trade date>')
            print('python pm-batch1.py -t 2018-11-01 -e 2018-11-30')
            sys.exit()
        elif opt in ("-t", "--tdate"):
            tdate = arg
        elif opt in ("-e", "--etdate"):
            edate = arg
    print('Input file is "', tdate, edate)
    
    if ( -1> 0 ) :
        tdate="2018-10-01"
        edate="2018-10-31"
        updateP_TS(db, tdate, tdate, edate)
        tdate="2018-11-01"
        edate="2018-11-30"
        updateP_TS(db, tdate, tdate, edate)
        tdate="2018-12-01"
        edate="2018-12-31"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-01-01"
        edate="2019-01-31"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-02-01"
        edate="2019-02-28"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-03-01"
        edate="2019-03-31"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-04-01"
        edate="2019-04-30"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-05-01"
        edate="2019-05-31"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-06-01"
        edate="2019-06-30"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-07-01"
        edate="2019-07-31"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-08-01"
        edate="2019-08-31"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-09-01"
        edate="2019-09-30"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-10-01"
        edate="2019-10-31"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-11-01"
        edate="2019-11-30"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2019-12-01"
        edate="2019-12-31"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2020-01-01"
        edate="2020-01-31"
        updateP_TS(db,tdate, tdate, edate)
        tdate="2020-02-01"
        edate="2020-02-29"
        updateP_TS(db,tdate, tdate, edate)
    else:
        tdate="2020-03-01"
        edate="2020-03-31"
        updateP_TS(db,tdate, tdate, edate)
    
if __name__ == "__main__":
   main(sys.argv[1:])

print("I am done")

#print ("Categories ----------------------------------")
#for x in categories:
#    print(x)
#print ("Properties ----------------------------------")
#for x in properties:
#    print("Properties:", x, income[x], expenses[x])
#print ("Tenants ----------------------------------")
#    i=0
#    tenants.sort()
#    for x in tenants:
#        i += 1
    #print("Tenants:", i, x)
