# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 11:09:35 2019

@author: ppare
"""
import sys
import zlib, gzip, io
import ref_data

from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from locale import LC_ALL
from locale import setlocale
from logging import FileHandler
from logging import Formatter
import logging
import pandas as pd

from pm_db import PMDB

db = PMDB

db = PMDB(
        "127.0.0.1",
        3310,
        "root",
        "Auronia2018",
        "pm",
        None
)


filename = 'AHPA GL - 2019 09.txt'
        
AllKeys = []
properties = []
payees = []
tenants = []
income = {}
expenses = {}

my_properties = ref_data.get_my_properties(db)
my_tenants = ref_data.get_my_tenants(db)
properties = my_properties.keys()
tenants = my_tenants.keys()

data = 0
hc_payment=0.0
hlpm_payment = 0.0
total_rent=0.0
total_expenses=0.0

# Sections of the data feed
section=""

#lines = [line.rstrip('\n') for line in open('filename')]
debug=1
db_update=0
#if (debug > 0 ):
#    file_handler = FileHandler(log_dir + "/" + "auronia.log")
#    file_handler.setLevel(logging.DEBUG)
#    file_handler.setFormatter(Formatter(
#        '%(asctime)s %(levelname)s: %(message)s '
#        '[in %(pathname)s:%(lineno)d]'
#    ))
#    app.logger.addHandler(file_handler)

   

sqlf = open("pm-rr-sql-log.txt", "w")
sqle = open("pm-rr-sql-error.txt", "w")


df = pd.read_excel(r'AHPA RR - 2019 01.xlsx')

i=0
i_error=0.0
o_date=""
tdate=""
amount=0.0
ref=""
desc=""
prop=""
m_prop=""
p_id=""

df.rename(columns = {'Rent Roll':'Property','Unnamed: 1':'Tags', 'Unnamed: 2':'Type', 'Unnamed: 3':'Tenant','Unnamed: 4':'Status', 
                     'Unnamed: 5':'Sq, Ft.', 'Unnamed: 6':'Market Rent', 'Unnamed: 7':'Rent', 'Unnamed: 8':'Deposit', 'Unnamed: 9':'Lease From',
                     'Unnamed: 10':'Lease To', 'Unnamed: 11':'MoveIn', 'Unnamed: 12':'MoveOut'}, inplace = True) 
df['Property'].fillna("nan", inplace=True)
df['Tenant'].fillna("nan", inplace=True)
df['Market Rent'].fillna(0.0, inplace=True)
df['Rent'].fillna(0.0, inplace=True)
df['Deposit'].fillna(0.0, inplace=True)
df['MoveOut'].fillna(0, inplace=True)
#print(df)

for ind in df.index:

    i += 1;
    inc=0.0
    exp=0.0

    prop = df.at[ind,'Property'].lower()
    print(ind, ":", prop, " = ", df.at[ind, 'Tenant'])
        
    if ( prop == 'nan' ):
        continue


    if 'as of:' in prop :
        t_d= prop.split(":")
        ds = t_d[1].strip().split("/")
        tdate= ds[2] + "-" + ds[0] + "-" + ds[1]
        
    if 'harrisburg' in prop:    
        t_p= prop.split("harrisburg")
        m_prop = t_p[0].rstrip()
    
    if (df.at[ind,'Tenant'] == 'nan'):
        continue
    
    if ( 'unit' in prop ):
        ps = prop.split(' ')
        if (len(ps) == 2):
            p_unit = ps[1]
            prop = m_prop + " # " + p_unit
        
    # find property id
    p_id=""
    if prop in properties:
        p_id = str(my_properties[prop][0])
    else:
        print("Property not found:", prop)
        sqle.write("Property not found:"+ prop + ";\n")
        i_error += 1
        continue
    
    print("As of date:", tdate, " Property: "+ p_id + ": "+ prop)
    if ( p_id == '' ):
        continue
      
    t_id = ""
    t_name=df.at[ind,'Tenant'].lower()
    t_name=t_name.replace("  "," ")
    
    t_family=2
    if ( t_name in tenants ):
        t_id = str(my_tenants[t_name][0])
    else:
        print("Tenant not found:", t_name)
        sqle.write("Tenant not found:"+ t_name + ";\n")
        i_error += 1
        continue
    
    
    md= df.at[ind,'MoveIn']
    if ( md == 'nan' ):
        continue
    movein= md.strftime("%Y-%m-%d")

    moveout="null"
    md= df.at[ind,'MoveOut']
    if ( md != 0 ):
        moveout= md.strftime("%Y-%m-%d")

    amount = df.at[ind,'Rent']
    rent = amount

    sqls=""
    if moveout != 'null':
        sqls = "INSERT INTO `pm`.`tenancy` (`tenant_id`,`property_id`,`start_date`,`end_date`,`name`,`family_members`,`rent`,`deposit`) "
    else:
        sqls = "INSERT INTO `pm`.`tenancy` (`tenant_id`,`property_id`,`start_date`,`name`,`family_members`,`rent`,`deposit`) "
    sqls += " VALUES ("+ t_id + ","
    sqls += p_id + ",'"
    sqls += movein
    if moveout != 'null':
        sqls += "','" + moveout + "','" 
    else:
        sqls += "','" 
    
    sqls += t_name + "'," + str(t_family) + ","
    sqls += str(rent) + "," + str(amount) +")"
    
    sqlf.write(sqls + ";\n")
    print(" addr:" + p_id + " "+sqls)
   # Update only if db_update is enabled
   # Also verify if record exists before doing an insert

    c_sqls = "SELECT COUNT(*) FROM pm.tenancy pt WHERE "
    c_sqls += " pt.tenant_id=" + t_id
    c_sqls += " AND pt.property_id=" + p_id
    c_sqls += " AND pt.start_date='" + movein + "'"
    c_sqls += " AND pt.rent=" + str(rent) 
    c_sqls += " AND pt.deposit=" + str(amount)
    ct = PMDB.query_one(db,c_sqls, None)
    
    if (ct['COUNT(*)']):
        print("Duplicate found: "+c_sqls)
        sqle.write(sqls + ";\n")
        i_error += 1
    else:
        if ( db_update ):
            print("Inserted: ")
            db.insert(sqls,None)    



print("I am done :: Processed "+str(i) + " Error:" + str(i_error))
