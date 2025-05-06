# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 11:09:35 2019

@author: ppare
"""

import ref_data

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
excelout="../data/output.xlsx"
sqlf = open("../data/mysql-log.txt", "w")
sqle = open("../data/mysql-error.txt", "w")
filename = '../data/AHPA HPM GL - update.xlsx'
df = pd.read_excel(filename)
debug=1
db_update=0
ignore_dups = 0
pm='HPM'
      
AllKeys = []
properties = []
payees = []
tenants = []
categories = {}
my_categories = {}

    
my_properties = ref_data.get_my_properties(db)
my_tenants = ref_data.get_my_tenants_on(db)

data = 0
hc_payment=0.0
total_rent=0.0
total_expenses=0.0
c_fail=0.0
t_fail=0.0
p_fail=0.0

# Sections of the data feed
section=""

#lines = [line.rstrip('\n') for line in open('filename')]

def get_hpm_categories():
    
    mdict = {}
    
    mdict['gas']=[28,'6172']
    mdict['sewer & water']=[29,'6173']
    mdict['garbage']=[30,'6175']
    mdict['electric']=[27,'6171']
    mdict['maint & repairs']=[13,'6073']
    mdict['maint charges']=[13,'6073']
    mdict['rent due']=[8,'4100']
    mdict['utilities - trash']=[30,'6175']
    mdict['subsidy due']=[71,'4102']
    mdict['recv\'d from owner']=[6,'3150']
    mdict['fusion maintenance']=[73,'6110']
    mdict['late fee']=[11,'4460']
    mdict['eft payment to owner']=[7,'3250']
    mdict['eft payment to owne']=[7,'3250']
    mdict['m2m charge']=[70,'4471']
    mdict['payment to owner']=[7,'3250']
    mdict['management fees']=[34,'6270']
    mdict['turn over']=[23,'6148']
    mdict['locksmith services']=[23,'6148']
    mdict['pest control']=[45, '6300']
    mdict['site visit']=[73,'6110']
    mdict['snow']=[16,'6077']
    mdict['plumbing']=[20,'6142']
    mdict['repair-other']=[49,'6147']
    mdict['hvac-repair']=[24,'6149']
    mdict['legal charge']=[18, '6101']
    mdict['owner contribution']=[6,'3150']
    mdict['security']=[31,'6191']
    mdict['refund']=[74,'4472']
    mdict['laundry']=[75,'4473']

    #print(mdict)
    return mdict
def findTenants(c, d):
    ret = -1
    
    c = c.replace(">","").lower().strip()
    if ( c in my_tenants):
        ret = my_tenants[c][0]
        
    print("findTenants:b4d:",d, "|")
    d = d.replace(">","").lower()
       
    if ( ret < 1 and  d != None and d != '' ):
        if ( d in my_tenants):
            ret = my_tenants[d][0] 
    
    print("findTenants::tenants:", str(ret), " name1:", c, " name2:|", d, "|")

    
    return ret

def findCategory(c, d, pay):
    ret = -1
    
    pay = pay.lower()
    d=d.lower()
    
    if ( c != None and c != "" ):    
        c = c.replace(">","").lower().strip()
        if ( c in my_categories):
            ret = my_categories[c][0]
        
    if (ret < 1 or ( 'move out' in c and ( 'trash' in d or 'cleaning' in d ))):
        ret = my_categories['turn over'][0]
        
    if ( ret < 1 and  ( 'meet ' in c or 'site ' in d )):
        ret = my_categories['site visit'][0]

    if ( ( ret == 73 or ret < 1) and ( 'snow' in d or 'salt ' in d )):
        ret = my_categories['snow'][0]
        
    if ( ( ret == 13 or ret < 1) and (( 'mice' in d or 'pest ' in d or 'roach' in d  ) or ( 'aaa enviro pest' in pay))):
        ret = my_categories['pest control'][0]
        
    if ( ret == 13 and  ( 'bath ' in d or 'leak ' in d ) and 'roof' not in d ):    
        ret = my_categories['plumbing'][0]
        
    if ( ret == 13 and  ( 'hvac' in d or 'heater' in d )):    
        ret = my_categories['hvac-repair'][0]
    
    if ( (ret < 1 or ret == 13) and  'security' in d ):    
        ret = my_categories['security'][0]
        
    if ( ret > 0 and  'refund' in d ):    
        ret = my_categories['refund'][0]
    
    if ( ret < 0 and 'capital region water' in pay ):
        ret = my_categories['sewer & water'][0] #=[29,'6173']        
    if ( ret < 0 and 'ppl electric' in pay ):
        ret = my_categories['electric'][0]     
    if ( ret < 0 and 'city treasurer' in pay and 'garbage' in c ):
        ret = my_categories['garbage'][0]     
    
    if ( ( ret < 0 or ret == 8) and 'laundry' in d and 'rent' in c):
        ret = my_categories['laundry'][0]
    
    print("findCategory::cat:", ret, " desc:", c)
    
    return ret
        
def findAddress(desc, ref):
    
    ret = -1
    st1=""
    
    if ( ref != '' and ref != None ):
        ref = ref.strip(' ').lower()
        if ( ref in my_properties.keys() ):
            ret = my_properties[ref][0]
    
    if ( ret < 1):
        desc = desc.replace("IA-","")
        desc = desc.replace("-",",").lower().strip()
        desc = desc.replace("120-122","120")
        desc = desc.replace("  "," ")
        desc = desc.replace(", ",",")
        desc = desc.replace(" ,",",")
        fstr= desc.split(',')
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
            if ( "261" in desc and "apt 1" in desc):
                st1 = "261 cumberland st # 1"
            elif ("261" in desc and "apt 2" in desc):
                st1 = "261 cumberland st # 2"
            elif ("261" in desc and "apt 3" in desc):
                st1 = "261 cumberland st # 3"
            elif ( "265" in desc and "apt 1" in desc):
                st1 = "265 cumberland st # 1"
            elif ("265" in desc and "apt 2" in desc):
                st1 = "265 cumberland st # 2"
            elif ("265" in desc and "apt 3" in desc):
                st1 = "265 cumberland st # 3"    
            elif ( "263" in desc and "apt 1" in desc):
                st1 = "263 cumberland st # 1"
            elif ("263" in desc and "apt 2" in desc):
                st1 = "263 cumberland st # 2"
            elif ("263" in desc and "apt 3" in desc):
                st1 = "263 cumberland st # 3"        
            elif ("261" in desc):
                st1 = "261 cumberland st" 
            elif ("263" in desc):
                st1 = "263 cumberland st" 
            elif ("265" in desc):
                st1 = "265 cumberland st" 
        elif ( fstr[0] == "walnut st"):
            if ( "commercial 1" in desc ):
                st1="120 walnut st # c1"
            elif ("commercial 2" in desc):
                st1="120 walnut st # c2"
            elif ("apt 10" in desc):
                st1="120 walnut st # 10"
            elif ("apt 1" in desc):
                st1="120 walnut st # 1"
            elif ("apt 2" in desc):
                st1="120 walnut st # 2"
            elif ("apt 3" in desc):
                st1="120 walnut st # 3"
            elif ("apt 4" in desc):
                st1="120 walnut st # 4"
            elif ("apt 5" in desc):
                st1="120 walnut st # 5"
            elif ("apt 6" in desc):
                st1="120 walnut st # 6"
            elif ("apt 7" in desc):
                st1="120 walnut st # 7"
            elif ("apt 8" in desc):
                st1="120 walnut st # 8"
            elif ("apt 9" in desc):
                st1="120 walnut st # 9"
            else:
                st1="120 walnut st"
        else:
            st1 = "unknown"
    
        if ( st1 in my_properties.keys() ):
        
            ret = my_properties[st1][0]
    
        if ( 'zeplin' in desc):
            ret = my_properties['1312 derry st'][0]
        
    print("findAddress:property id=", str(ret) , " desc:", desc, "|", ref, "|", st1)
    return ret


t_fail=0.0
i=0
i_error=0.0
isql=0
month=""
type=""
work_month="11"
o_date=""
amount=0.0
ref=""
desc=""
cat=""

df.rename(columns = {'Unnamed: 0':'View', 'Unnamed: 9':'Misc', 'Transaction Name':'Category'}, inplace = True) 
df['property_id']=0
df['category_id']=0
df['tenant_id']=0
df['tx_id']=0
df['Payee'].fillna("", inplace=True)
df['Ref'].fillna("", inplace=True)
df['Source'].fillna("", inplace=True)
#df['Misc'].fillna("", inplace=True)
#df['Market Rent'].fillna(0.0, inplace=True)

print("tenants:",my_tenants)
print("properties:",my_properties)
print("Processing ",pm," data size:", df.index)
my_categories = get_hpm_categories()

print(df)
i=0
m=0
for ind in df.index:

    i += 1;
    if ( i < 1 ):
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
    property_id=0
    updStatus=df.at[ind, 'Status']
    if ( updStatus != 'View' ):
        continue
                        
    category=df.at[ind,'Category']
    
    if ( 'EFT Payment' in category or 'Payment to Owner' in category ):
        continue
    
    source = df.at[ind,'Source']
    ref = str( df.at[ind,'Ref'])
    payee=str(df.at[ind,'Payee'])
    tdate=df.at[ind, 'Date'].strftime('%Y-%m-%d')
    ttype=ref
    
  
    property_id = findAddress( source, ref)
    if ( property_id < 1 and source != ""):
        p_fail += 1
        print("property ----------------------")
        break
    
 
    # Category
    cat = findCategory(category,source, payee)
    if ( cat < 1 ):
        c_fail += 1
    
    tenant_id = findTenants(source , payee)
    if ( tenant_id < 1 and cat == 8):
        t_fail += 1
        print("tenant ----------------------")
        break
        
    credit = df.at[ind,'Paid']
    fees = df.at[ind, 'Fees']
    amt = df.at[ind,'Amount']
    if ( amt < 0):
        exp = abs(amt)
    else:
        inc = credit
        
    desc = source.replace("'"," ")
    
    print("HPM: i=", i, " sql=", isql, " date:",tdate, " Cat:", cat, " Property: ", str(property_id), "tenant_id:", str(tenant_id), " inc:", inc," Desc:", desc)    

    if payee not in payees:
        payees.append(payee)
    
    if ( property_id < 0):
        break

    if ( debug and ( cat < 1 or ( tenant_id < 1 and cat == 8 ) or ( property_id < 1 and cat != 6 ) ) ):
        print("failed1:", cat, "|", tenant_id, "|",property_id)
        continue
    
    if ( property_id > 0 and cat > 0 and tdate != '' ):
        isql +=1
        sqls = "INSERT INTO `pm`.`transactions` (`tdate`,`category_id`,`property_id`,`tenant_id`,`payee`,`type`,`reference`,`debit`,`credit`,`description`) "
        sqls += " VALUES ('"+ tdate + "',"
        sqls += str(cat) + ","
        sqls += str(property_id) + "," + str(tenant_id)
        sqls += ",'" + payee + "','" + ttype + "','" + ref + "',"
        sqls += str(exp) + "," + str(inc) + ",'" + desc + "')"
        
        sqlf.write(sqls + ";\n")
        print(str(cat)+" property:" + str(property_id) + " "+sqls)
       # Update only if db_update is enabled
       # Also verify if record exists before doing an insert
    
        c_sqls = "SELECT pt.tx_id FROM pm.transactions pt WHERE pt.tdate='"+tdate+"'"
        c_sqls += " AND pt.category_id=" + str(cat)
        c_sqls += " AND pt.property_id=" + str(property_id)
        c_sqls += " AND pt.reference='" + ref + "'"
        c_sqls += " AND pt.type='" + ttype + "'"
        c_sqls += " AND pt.payee='" + payee + "'"
        c_sqls += " AND pt.credit=" + str(inc) 
        c_sqls += " AND pt.debit=" + str(exp)
        ct = PMDB.query_one(db,c_sqls, None)
        print("updated7: Duplicate check: ", c_sqls)
        if (ct != None and ct['tx_id'] and ignore_dups == 0 ):
            print("updated7: Duplicate found: ", ct['tx_id'])
            sqle.write(sqls + ";\n")
            df.at[ind, 'Status'] = str(ct['tx_id'])
            i_error += 1
        else:
            print("updated8: Inserted: "+sqls)
            if ( db_update):
                db.insert(sqls,None)  

    if ( fees != 0 and property_id > 0 and tdate != '' ): # Management fees
        isql +=1
        cat = 34
        sqls = "INSERT INTO `pm`.`transactions` (`tdate`,`category_id`,`property_id`,`tenant_id`,`payee`,`type`,`reference`,`debit`,`credit`,`description`) "
        sqls += " VALUES ('"+ tdate + "',"
        sqls += str(cat) + ","
        sqls += str(property_id) + "," + str(tenant_id)
        sqls += ",'" + payee + "','" + ttype + "','" + ref + "',"
        sqls += str(fees) + "," + str(exp) + ",'" + desc + "')"
        sqlf.write(sqls + ";\n")
        print("update10:"+sqls)
       # Update only if db_update is enabled
       # Also verify if record exists before doing an insert
    
        c_sqls = "SELECT pt.tx_id FROM pm.transactions pt WHERE pt.tdate='"+tdate+"'"
        c_sqls += " AND pt.category_id=" + str(cat)
        c_sqls += " AND pt.property_id=" + str(property_id)
        c_sqls += " AND pt.reference='" + ref + "'"
        c_sqls += " AND pt.type='" + ttype + "'"
        c_sqls += " AND pt.payee='" + payee + "'"
        c_sqls += " AND pt.credit=" + str(inc) 
        c_sqls += " AND pt.debit=" + str(exp)
        ct = PMDB.query_one(db,c_sqls, None)
        
        if (ct != None and ct['tx_id'] and ignore_dups == 0 ):
            print("Duplicate found:", ['tx_id'], c_sqls)
            sqle.write(str(ct['tx_id'])+" "+ sqls+ ";\n")
            df.at[ind, 'Status'] = df.at[ind, 'Status'] + "," + str(ct['tx_id'])
            i_error += 1
        else:
            print("update14:Inserted: "+sqls)
            if ( db_update ):
                db.insert(sqls,None) 
 

    else :
        print ("Incorrect data")



    
# Rent
df.to_excel(excelout)  

print("I am done :: Processed "+str(i) + " sqls:" + str(isql) + " Error:" + str(i_error) + " p:" + str(p_fail)+ " c:" + str(c_fail)+ " t:" + str(t_fail))

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
