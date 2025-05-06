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

filename = 'AHPA GL 20181101-20190831.txt'
#filename = 'AHPA II GL 2019 08-Tab.txt'
filename = 'AHPA II GL - 2019 09.txt'
filename = 'AHPA - HPM - GL.txt'
debug=1
db_update=0
pm='HPM'
      
AllKeys = []
properties = []
payees = []
tenants = []
categories = {}
my_categories = ref_data.get_my_categories(db)
if ( pm == 'HPM'):
    my_categories = ref_data.get_hpm_categories()
    
my_properties = ref_data.get_my_properties(db)

data = 0
hc_payment=0.0
hlpm_payment = 0.0
total_rent=0.0
total_expenses=0.0

# Sections of the data feed
section=""

#lines = [line.rstrip('\n') for line in open('filename')]

#if (debug > 0 ):
#    file_handler = FileHandler(log_dir + "/" + "auronia.log")
#    file_handler.setLevel(logging.DEBUG)
#    file_handler.setFormatter(Formatter(
#        '%(asctime)s %(levelname)s: %(message)s '
#        '[in %(pathname)s:%(lineno)d]'
#    ))
#    app.logger.addHandler(file_handler)

def findCategory(c):
    if ( c == '' or c == None ):
        return "0"
    
    c = c.replace(">","").lower().strip()
    
    s = my_categories[c][0]
    
    print("findCategory::cat:", s, " desc:", c)
    
    return s
        
def findAddress(desc, ref):
    
    if ( ref != '' and ref != None ):
        ref = ref.strip(' ').lower()
        if ( ref in my_properties.keys() ):
            return ref
        
    desc = desc.replace("-",",").lower().strip()
    desc = desc.replace("  "," ")
    desc = desc.replace(", ",",")
    desc = desc.replace(" ,",",")
    fstr= desc.split(',')
    un = ''
    st1 = ''
    
    if (fstr[0] == "buckthorn st" or fstr[0] == "vernon st" ):
        if (fstr[1].find(' ')!= -1):
            st1 = fstr[1].strip(' ').split(' ')[0] + " " + fstr[0]
        else:
            st1 = fstr[1] + " " + fstr[0]
    elif ( fstr[0] == "haehnlen st" or fstr[0] == "haenhlen st"):
        st1 = "1349 haenhlen st"
    elif ( fstr[0] == "13th st"):
        st1 = fstr[2] + " s " + fstr[0]
    elif ( fstr[0] == "derry st"):
        if ( fstr[1] == "1312" or fstr[1] == "1330" or fstr[1] == "1252" or fstr[1] == "1254"):
            if ( len(fstr) > 2 and fstr[2].find ('apt') != -1 ):
                st1 = fstr[1] + " " + fstr[0] + " " + fstr[2].replace("apt","#").strip()
            else:
                st1 = fstr[1] + " " + fstr[0]
        else:
            l = fstr[1].split(' ')
            st1 = l[0] + " " + fstr[0]
    elif ( fstr[0] == "cumberland st"):
        st1 = fstr[1] + " " + fstr[0] + " " + fstr[2].replace("apt","#").strip()
    elif ( fstr[0] == "walnut st"):
        st1 = fstr[1] + " " + fstr[0] + " " + fstr[2].replace("apt","#").strip()     
    else:
        st1 = "unknown"
         
#    if ( st1 != '' and int(st1) < 10 ):
    un = st1
        
    print("findAddress:"+ desc + "|"+ un)
    return un

sqlf = open("mysql-log.txt", "w")
sqle = open("mysql-error.txt", "w")

lines = open(filename).read().splitlines()
i=0
i_error=0.0
cat=""
month=""
type=""
work_month="11"
o_date=""
amount=0.0
ref=""
desc=""

print("Processing ",pm," data:", filename)

for x in lines:
    i += 1;
    if ( i < 2):
        continue
    inc=0.0
    exp=0.0
    fees = 0.0
    amt = 0.0
    tdate=""  
    unit = ""
    desc = ""
    debit=0.0
    credit=0.0
    x= x.replace("Harrisburg, PA 17104","")
    x= x.replace("Harrisburg, PA 17101","")
    x= x.replace("Harrisburg, PA 17102","")
    x= x.replace("Street","St")
    x= x.replace("120-122","120")
    x = x.replace('"','')
    strs = x.split("\t")

    if ( debug == 1 ):
        print (str(i),":",len(strs)," :", x)

    if ( pm == 'HPM' and len(strs) == 11):
        # Harrisbug Properties Management Format
        addr=""
        
        if ( strs[1] != '' ):
        #o_date=datetime.datetime.strptime(strs[1], '%m/%d/%y').date()
            ds = strs[1].split('/')
            if (len(ds) == 3):
                tdate= ds[2] + "-" + ds[0] + "-" + ds[1]
                month = ds[0]
        # Category
        cat = findCategory(strs[3])
        
        if ( strs[10] != ''):
            desc = strs[10].rstrip()
            addr = findAddress( desc, strs[2])
            
            
        print("HPM: date:",tdate, " Cat:", cat, " Property: ", addr, " Desc:", desc)
        if ( cat != '' ):
            
            p = strs[2].lower().rstrip()
            ttype = strs[3].lower().rstrip()
            payee = p
            ref = strs[4]          
            
        
            if addr not in properties:    
                properties.append(addr)
    
            if payee not in payees:
                payees.append(payee)
    
            if ( strs[5] != '' and len(strs[5])> 0):          
                inc = float(strs[5].replace(',','').replace('$',''))
            if ( strs[6] != '' and len(strs[6])> 0):          
                fees = float(strs[6].replace(',','').replace('$',''))
            if ( strs[7] != '' and len(strs[7])> 0):          
                if (strs[7].find('(') != -1 ):
                    amt = float(strs[7].replace(',','').replace('$','').replace('(','').replace(')',''))
                else:
                    amt = float(strs[7].replace(',','').replace('$',''))
            if ( amt < 0):
                exp = abs(amt)
                
            # strs[8] = balance - ignore
            # strs[9] = empty
            
        # Rental unit count
            if ( cat == '4100' and a != '' and p != ''):
                tenant = a + '|' + p
                if tenant not in tenants:
                    tenants.append(tenant)
        
            if ( addr != '' and cat != '' and tdate != '' ):
                sqls = "INSERT INTO `pm`.`transactions` (`tdate`,`category_id`,`property_id`,`payee`,`type`,`reference`,`debit`,`credit`,`description`) "
                sqls += " VALUES ('"+ tdate + "',"
                sqls += str(cat) + ","
                sqls += str(my_properties[addr][0])
                sqls += ",'" + payee + "','" + ttype + "','" + ref + "',"
                sqls += str(exp) + "," + str(inc) + ",'" + desc + "')"
                
                sqlf.write(sqls + ";\n")
                print(str(cat)+" addr:" + addr + " "+sqls)
               # Update only if db_update is enabled
               # Also verify if record exists before doing an insert
                if ( db_update ):
                    c_sqls = "SELECT COUNT(*) FROM pm.transactions pt WHERE pt.tdate='"+tdate+"'"
                    c_sqls += " AND pt.category_id=" + cat
                    c_sqls += " AND pt.property_id=" + str(my_properties[addr][0])
                    c_sqls += " AND pt.reference='" + ref + "'"
                    c_sqls += " AND pt.type='" + ttype + "'"
                    c_sqls += " AND pt.payee='" + payee + "'"
                    c_sqls += " AND pt.credit=" + str(inc) 
                    c_sqls += " AND pt.debit=" + str(exp)
                    ct = PMDB.query_one(db,c_sqls, None)
                    
                    if (ct['COUNT(*)']):
                        print("Duplicate found: "+c_sqls)
                        sqle.write(sqls + ";\n")
                        i_error += 1
                    else:
                        print("Inserted: "+sqls)
                        db.insert(sqls,None)  
        
            if ( fees > 0 and addr != '' and tdate != '' ): # Management fees
                cat = 34
                sqls = "INSERT INTO `pm`.`transactions` (`tdate`,`category_id`,`property_id`,`payee`,`type`,`reference`,`debit`,`credit`,`description`) "
                sqls += " VALUES ('"+ tdate + "',"
                sqls += str(cat) + ","
                sqls += str(my_properties[addr][0])
                sqls += ",'" + payee + "','" + ttype + "','" + ref + "',"
                sqls += str(exp) + "," + str(inc) + ",'" + desc + "')"
                sqlf.write(sqls + ";\n")
                print(str(cat)+" addr:" + addr + " "+sqls)
               # Update only if db_update is enabled
               # Also verify if record exists before doing an insert
                if ( db_update ):
                    c_sqls = "SELECT COUNT(*) FROM pm.transactions pt WHERE pt.tdate='"+tdate+"'"
                    c_sqls += " AND pt.category_id=" + cat
                    c_sqls += " AND pt.property_id=" + str(my_properties[addr][0])
                    c_sqls += " AND pt.reference='" + ref + "'"
                    c_sqls += " AND pt.type='" + ttype + "'"
                    c_sqls += " AND pt.payee='" + payee + "'"
                    c_sqls += " AND pt.credit=" + str(inc) 
                    c_sqls += " AND pt.debit=" + str(exp)
                    ct = PMDB.query_one(db,c_sqls, None)
                    
                    if (ct['COUNT(*)']):
                        print("Duplicate found: "+c_sqls)
                        sqle.write(sqls + ";\n")
                        i_error += 1
                    else:
                        print("Inserted: "+sqls)
                        db.insert(sqls,None) 
    else:  
        # Heavy Lifting Properties Management Format    
        if ( len(strs) == 10 and strs[1] != '' ):
            #o_date=datetime.datetime.strptime(strs[1], '%m/%d/%y').date()
            ds = strs[1].split('/')
            if (len(ds) == 3):
                tdate= ds[2] + "-" + ds[0] + "-" + ds[1]
                month = ds[0]
        
        if ( len(strs) == 10 and strs[0].rfind('"') < 0 and strs[0].rfind('-') > 0 and strs[1] == ''):
            cat = strs[0].lower().rstrip()
            cat = cat.split(' ')[0]
        
        if ( cat != '' and len(strs) == 10 and strs[0] != '' ):
            a = strs[0].lower().rstrip()
            p = strs[2].lower().rstrip()
            ttype = strs[3].lower().rstrip()
            #addr = a +'|' + cat
            #payee = p +'|' + cat
            addr = a
            payee = p
            ref = strs[4]          
            desc = strs[8].replace("'", "\\'")
        
            if ( strs[9] != ''):
                tu = strs[9].split(' ')
                if ( tu[1] != '' ):
                    tu[0] = tu[0].lower().strip()
                    tu[1] = tu[1].strip()
                    if ( tu[0] == 'commercial' and tu[1] == '120'):
                        unit = 'c1'
                    elif ( tu[0] == 'commercial' and tu[1] == '122'):
                        unit = 'c2'
                    else:                    
                        unit = tu[1].strip()
                    addr += " # "+unit
            
            a_keys = addr + '|' + cat
            
            if addr not in properties:    
                properties.append(addr)
    
            if a_keys not in AllKeys:
                AllKeys.append(a_keys)
                
            if payee not in payees:
                payees.append(payee)
    
            if ( strs[5] != '' and len(strs[5])> 0):          
                exp = float(strs[5].replace(',',''))
                    #print(strs)                  
            if ( strs[6] != '' and len(strs[6])> 0):
                #if (strs[4].rfind('receipt')):
                inc = float(strs[6].replace(',',''))
        
        # Rental unit count
            if ( cat == '4100' and a != '' and p != ''):
                tenant = a + '|' + p
                if tenant not in tenants:
                    tenants.append(tenant)
            if ( addr != '' and cat != '' and tdate != '' and month == "12" ):
                sqls = "INSERT INTO `pm`.`transactions` (`tdate`,`category_id`,`property_id`,`payee`,`type`,`reference`,`debit`,`credit`,`description`) "
                sqls += " VALUES ('"+ tdate + "',"
                sqls += str(my_categories[int(cat)][0]) + ","
                sqls += str(my_properties[addr][0])
                sqls += ",'" + payee + "','" + ttype + "','" + ref + "',"
                sqls += str(exp) + "," + str(inc) + ",'" + desc + "')"
                
                sqlf.write(sqls + ";\n")
                print(cat+" addr:" + addr + " "+sqls)
                if ( cat == 6171 ):
                    print ("--------------------------------------------------")
               # Update only if db_update is enabled
               # Also verify if record exists before doing an insert
                if ( db_update ):
                    c_sqls = "SELECT COUNT(*) FROM pm.transactions pt WHERE pt.tdate='"+tdate+"'"
                    c_sqls += " AND pt.category_id=" + str(my_categories[int(cat)][0])
                    c_sqls += " AND pt.property_id=" + str(my_properties[addr][0])
                    c_sqls += " AND pt.reference='" + ref + "'"
                    c_sqls += " AND pt.type='" + ttype + "'"
                    c_sqls += " AND pt.payee='" + payee + "'"
                    c_sqls += " AND pt.credit=" + str(inc) 
                    c_sqls += " AND pt.debit=" + str(exp)
                    ct = PMDB.query_one(db,c_sqls, None)
                    
                    if (ct['COUNT(*)']):
                        print("Duplicate found: "+c_sqls)
                        sqle.write(sqls + ";\n")
                        i_error += 1
                    else:
                        print("Inserted: "+sqls)
                        db.insert(sqls,None)    
    
        else :
            print ("Incorrect data")



    
# Rent

print("I am done :: Processed "+str(i) + " Error:" + str(i_error))

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
