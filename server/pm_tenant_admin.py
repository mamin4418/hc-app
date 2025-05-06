# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:04:13 2020

@author: ppare
"""
from flask import json, render_template
import pandas as pd
from datetime import datetime
from utils.pm_db import PMDB
import pm_user, utils.pm_mail, analysis.pm_financials, utils.pm_print, pm_company, pm_update

def tenantAdmin(O_db, app, qj):
    core = {}
    h = {}
    t_id=-1
    ret=-1
    sqls = ""
    qf = 'UPDATE'
    ts=datetime.today().strftime('%Y%m%d%H%S')
    tdate=datetime.today().strftime('%Y-%m-%d')

    app.logger.debug("pm_update::tenantAdmin:%s",qj)
    
    qf = fetchTextfromQ(app.logger,qj,'qualifier')
    for x in qj:
        core[x] = fetchTextfromQ(app.logger,qj,x)    
    if ( 'tenant_id' not in core ):
        return -1

    h['tenant_id']=core['tenant_id']
    h['updatedby']=core['updatedby']
    
    t_id = int(core['tenant_id'])
    if ( core['ACTION'] == 'EMAIL PAYMENT REMINDER'):
        app.logger.debug("pm_update.tenantAdmin:EMAIL PAYMENT REMINDER")
        core['output_file']=app.config['LOG_DIR']+"/"+core['tenant_id']+"_"+ts+"_reminder.pdf"
        core['due_date']=tdate
        core['template_file']='HP Tenant Statement.html'
        subject='HP: PAYMENT REMINDER'
        r = utils.pm_print.tenant_statement(app, O_db, core)
        app.logger.debug("pm_update.tenantAdmin:EMAIL STATEMENT: %s", r)
        #r['receiver_email']='pgp6758@gmail.com'
        h['comments'] = subject + " with: Amount Due: "+r['amount_due'] + " Due Date:"+r['due_date']+" Statement Date:" + r['statement_date']
        h['comments'] += " Account:" + r['account'] + " Email:" + r['email']
        r['subject']=subject
        r['attachment']=core['output_file']
        noticeEmail(app, O_db, r)
    elif( qj['ACTION'] == 'EMAIL STATEMENT'):
    	core['output_file']=app.config['LOG_DIR']+"/"+core['tenant_id']+"_"+ts+"_stmt.pdf"
    	app.logger.debug("pm_update.tenantAdmin:EMAIL STATEMENT")
    	core['due_date']=tdate
    	core['template_file']='HP Tenant Statement.html'
    	subject='HP: TENANT STATEMENT'
    	r = utils.pm_print.tenant_statement(app, O_db, core)
    	h['comments'] = subject+" with: Amount Due: "+r['amount_due'] + " Due Date:"+r['due_date']+" Statement Date:" + r['statement_date']
    	h['comments'] += " Account:" + r['account'] + " Email:" + r['email']
    	#r['receiver_email']='pgp6758@gmail.com'
    	r['attachment']=core['output_file']
    	r['subject']=subject
    	noticeEmail(app, O_db, r)
    elif( qj['ACTION'] == 'ENABLE WEBLOGIN'):
        tenant_userid=''
        tenant_password='123456789'
        subject='Weblogin Enabled'
        h['comments'] = 'New weblogin account created'
        if ( 'phone' in core and len(core['phone']) > 6):
            tenant_password=core['phone'].replace(' ','').replace('-','').replace('+1','').replace('(','').replace(')','')
            #tenant_password=re.replace(r"[-\(\)]","",tenant_password)
        if ( 'email' in core and core['email'] != ''):
            tenant_userid=core['email'].split('@')[0]
        else:
            tenant_userid= core['first_name'].lower() + core['last_name'].lower()
        try:
            app.logger.debug("pm_update.tenantAdmin: call setupTenantWebAccess (%s,%s,%s,%s)",
                    core['tenant_id'], tenant_userid, tenant_password, core['user_id'] )
            mlist = O_db.query_list('call setupTenantWebAccess (%s,%s,%s,%s)',
                    (core['tenant_id'], tenant_userid, tenant_password, core['user_id'] ))
            
        except Exception as e:
            app.logger.error("pm_update.tenantAdmin: tenant creation failed:%s", e);
            t_id=-1
    elif( qj['ACTION'] == 'PASSWORD RESET'):
    	subject='Web Password Reset'
    	h['comments'] = 'Weblogin account password reset'
    	c = pm_user.updatePassword(O_db, app.logger, qj)    
    	if ( c['code'] == 0):
    		qj['password']=c['password']
    		utils.pm_mail.passwordResetEmail(app, qj)
    	else:
    		t_id=-1
  
    h['title']=subject
    
    ret = pm_update.tenantHistory(O_db, app.logger, h)

    return t_id

def noticeEmail(app, db1, core):
    core['h_logo']=app.config['LOGO_HTML']
    app.logger.debug("noticeEmail.0: %s", core)
    t={}
    t['id_value']=core['property_id']
    t['id_type']='property_id'
    core['description']="This is your account statement. Please let us know right away, if there are any discrepancy. Please see attached PDF file for more information."
    core['description2']="If you have already sent a payment, please allow 2 days to process once payment is received by our office."
    company = pm_company.getCompany(db1,app.logger, t)
    app.logger.debug("Company info:%s", company)
    core['company']=company['name']
    core['company_address']=company['m_address']
    core['company_address2']=company['m_city']+"  "+company['m_state']+" "+company['m_zip']
    
    company_data= json.loads(company['attributes'])['data']
    app.logger.debug("Company attributes 2:%s", company_data)
    for c in company_data:
        app.logger.debug("Company attributes:%s", c)
        if ( c['attribute'] == 'EPAY'):
            k = "company_"+c['name'].lower().replace(" ","_")
            core[k]=c['login']
    
    core['template_file']='HP Tenant Email Statement.html'
    core['sender_email']='support@himalayaproperties.org'
    core['sender_address1']='support@himalayaproperties.org'
    
    core['receiver_email']='pgp6758@gmail.com'
    if ( 'email' in core and core['email'] != ''):
        core['receiver_email']=core['email']

    #core['receiver_email']='pgp6758@gmail.com'
    if ( utils.pm_mail.verifyEmailAddress(app, core['receiver_email']) < 0 ):
        app.logger.debug("noticeEmail.2"+core['receiver_email'])
        return 0

    core['receiver_name']=core['first_name']+" "+core['last_name']
    core['message_format']='html'
    
    
    if ( 'subject' not in core ):
        core['subject']='HP: Tenant Statement'
    core['reference']= datetime.today().strftime('%Y%m%d%H%M%S')+"/"+str(core['tenancy_id'])+"/"+str(core['tenant_id'])+"/"+str(core['property_id'])
    
    
    core['message']=render_template(core['template_file'], data=core)

    utils.pm_mail.sendMailWAttachment(app, core)    
    

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