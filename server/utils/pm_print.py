# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 20:11:48 2020

@author: ppare
"""

from flask import json, render_template

from datetime import timedelta, datetime
import pandas as pd
import pdfkit

import pm_wo, ref_data, pm_user, pm_tx, ref_data
from components.pm_tenant import PMTenant
from components.pm_property import PMProperty


logo_print = ""
logo_html = ""
print_server = ""
today = datetime.today().strftime('%Y-%m-%d')

def createPDF(app1, db, core):
    app1.logger.debug("pm_print.createPDF.1:%s",core)

    data={}
    l_format="pdf"
    r ={}
    r['function']='pdf'
    r['status']='failure'
    
    if ('format' in core):
        l_format=core['format']
    
    tt = core['type']
    t_id=core['tx_id']

    if ( tt == 'TR'):
        t_id=core['tr_id']
    
    data = pm_tx.getTX(db, app1.logger, tt ,t_id)
    
    app1.logger.debug("createPDF.4:[%s] %s", l_format, data)

    data['h_logo']=app1.config['LOGO_PRINT']
    
    if ( data['category_id'] > 0 ):
        cat = ref_data.get_my_categories_by_id2(db, app1.logger, data['category_id'])
        data['category']=cat['name']+"["+str(data['category_id'])+"]"

    if ( 'tenantcy_id' not in data):
        data['tenancy_id']=-1;
    if ( data['tenant_id'] > 0 ):
        op = ref_data.get_my_tenants_by_id(db,app1.logger,data['tenant_id'])
        
        data['first_name']=op['first_name']
        data['last_name']=op['last_name']
    
    if ( data['property_id'] > 0):
        op = ref_data.get_my_property_by_id(db, app1.logger, data['property_id'])
        data['label']=op['label']
        data['city']=op['city']
        data['state']=op['state']
        data['zip']=op['zip']
    
    if ( 'debit' in data):
        data['debit']="{:.2f}".format(data['debit'])
    if ( 'credit' in data):
        data['credit']="{:.2f}".format(data['credit'])
    if ( 'amount' in data):
        data['amount']="{:.2f}".format(data['amount'])

    op = ref_data.get_my_cores_info(db, app1.logger, 'TX_STATUS', str(data['status']))
    data['status_label']=op['co_value']
    
    data['statement_date']=datetime.today().strftime('%d %b %Y %H:%M:%S %Z')
    data['account'] = "TC."+str(data['tenancy_id'])+".P."+str(data['property_id'])+".T."+str(data['tenant_id'])

    if ( l_format == 'html'):
        app1.logger.debug("createPDF.7: HTML")
        data['h_logo']=app1.config['LOGO_HTML']
        rep =render_template('HP Parking Tag.html', data=data)
        mtype="text/html"
    else:

        app1.logger.debug("createPDF.8: PDF")
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
        }

        rep1 =render_template('HP TX.html', data=data)
        config = pdfkit.configuration(wkhtmltopdf=app1.config['PRINT_SERVER'])
        rep = pdfkit.from_string(rep1, False, configuration=config, options=options)    
        mtype="application/pdf"
    
    app1.logger.debug("createPDF.9: Generation complete");
    #response.headers['Content-Type'] = 'inline; filename=pktag.pdf'
    #response.headers['Content-Type'] = 'application/pdf'


    response = app1.response_class(
        response=rep,
        headers={'Content-Disposition':'inline; filename=pt.pdf', 'Content-Type':'application/pdf'},
        status=200,
        mimetype=mtype
    )        

    return response

#### WO Report
def wo_reports(app1, db, core):
    ws_pd = ref_data.get_my_cores_pd(db, app1.logger, 'WO_STATUS')
    ws_pd = ws_pd.set_index('co_name')
    wp_pd = ref_data.get_my_cores_pd(db, app1.logger, 'WO_PRIORITY')
    wp_pd = wp_pd.set_index('co_name')
    
    app1.logger.debug("pm_print.wo_reports.1:%s",core)
    l_format=core['format'] 
    core['template_file']='HP Daily WO List.html'
    core['user_id']=1
    data={}
    if ( 'transactions' not in core ):
        w_pd = pm_wo.getWOS(db, app1.logger, core)
        if ( not w_pd.empty ):
            h1= json.loads(w_pd.to_json(orient='table', double_precision=2))['data']
        #app1.logger.debug(" format: length:",len(h1))
            i=0
            while i < len(h1):
                #app1.logger.debug("history=>", i, "=>", h1[i])
                x = h1[i]
                x['tdate']=x['tdate'].split('T')[0]
                if ( x['status'] > 0 and x['owner'] == 'Scott LeCain'):
                    #app1.logger.debug("GOOD: ",ws_pd.at['2','co_value'])
                    x['status_l']=ws_pd.at[str(x['status']),'co_value']
                    x['priority_l']=wp_pd.at[str(x['priority']),'co_value']
                    i +=1
                else:
                    #app1.logger.debug("BAD: ", x)
                    garbage = h1.pop(i)            
        data['transactions'] = h1
    else:
        data['transactions'] = core['transactions']
                
    data['statement_date']=datetime.today().strftime('%d %b %Y')
    
    app1.logger.debug("pm_print.wo_reports:%s", data)

    if ( l_format == 'html'):
        data['h_logo']=app1.config['LOGO_HTML']
        #app1.logger.debug("pm_print.tenant_statement.7: HTML", data['h_logo'])
        rep =render_template(core['template_file'], data=data)
        mtype="text/html"
    else:
        #app1.logger.debug("pm_print.tenant_statement.8: PDF")
        data['h_logo']=app1.config['LOGO_PRINT'] 
        options = {
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'page-size': 'A4',
            'orientation' : 'Portrait',
            'footer-right': '[page]/[topage]'
        }
        
        rep1 =render_template(core['template_file'], data=data)
        #config = pdfkit.configuration(wkhtmltopdf="C:/ProgramData/Anaconda3/Lib/site-packages/wkhtmltopdf/")
        #config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
        config = pdfkit.configuration(wkhtmltopdf=app1.config['PRINT_SERVER'])
        if ( 'output_file' in core and core['output_file'] != ""  ):
            #app1.logger.debug("pm_print.tenant_statement.85: Output file=>",qj['output_file']);
            rep = pdfkit.from_string(rep1, core['output_file'], configuration=config, options=options)
        else:
            rep = pdfkit.from_string(rep1, False, configuration=config, options=options)        
            mtype="application/pdf"
    
    #app1.logger.debug("pm_print.tenant_statement.9: Generation complete");
    #response.headers['Content-Type'] = 'inline; filename=pktag.pdf'
    #response.headers['Content-Type'] = 'application/pdf'
    response = app1.response_class(
        response=rep,
        headers={'Content-Disposition':'inline; filename=tstmt.pdf', 'Content-Type':'application/pdf'},
        status=200,
        mimetype=mtype
    )          

    return response

####### tenant_statement
def tenant_statement(app1, db, qj):   

    app1.logger.debug("pm_print.tenant_statement: %s", qj)
    c_pd = ref_data.get_my_categories_pd(db, app1.logger)
    
    if ( 'template_file' not in qj ):
        qj['template_file']='HP Tenant Statement.html'
    data={}
    l_format="pdf"
    r ={}
    dt = datetime.today()
    l_ed=dt.strftime('%Y-%m-%d')
    l_period=60
    r['function']='pdf'
    r['status']='failure'

    if ('period' in qj):
        l_period=qj['period']
    
    G_sd = '2020-01-01'  # data calculation date
    dt = dt - timedelta(days=l_period)
    l_sd = dt.strftime('%Y-%m-%d')
    dt = dt.replace(day=1)
    
    if ('due_date' in qj):
        due_dt=qj['due_date']
    if ('format' in qj):
        l_format=qj['format']
    if ('start_date' in qj):
        l_sd=qj['start_date']
    if ('end_date' in qj):
        l_ed=qj['end_date']
    due_dt = l_ed
        
    app1.logger.debug("tenant_statement.3:%s [%s - %s] qj:%s",qj['tenant_id'],l_sd, l_ed, qj)
    O_t = PMTenant(qj['tenant_id'], qj, app1.logger, db)    
    data = O_t.getTInfo()
    dt1 = dt.strptime(data['lease_start_date'].split('T')[0],'%Y-%m-%d') - timedelta(days=60)
    l_lsd = dt1.strftime('%Y-%m-%d')
    
    O_t.updateFTS(db, G_sd, l_ed)
    c = O_t.getSTATS()
    data['lease_start_date']=data['lease_start_date'].split('T')[0]
    data['lease_end_date']=data['lease_end_date'].split('T')[0]
    data['move_in_date']=data['move_in_date'].split('T')[0]
    app1.logger.debug("Dates:G_sd=%s l_sd=%s l_lsd=%s [%s]",G_sd, l_sd, l_lsd, c)
    amount_due=0.0
    if ( not c.empty ):
        h1 = json.loads(c.to_json(orient='table', double_precision=2))['data']
        #app1.logger.debug(" format: length:",len(h1))
        i=0
        while i < len(h1):
            #app1.logger.debug("history=>[%s] %s", i,h1[i])
            x = h1[i]
            x['tdate']=x['tdate'].split('T')[0]
            if ( x['tdate'] > l_sd):
                #app1.logger.debug("GOOD: ", x)
                if ( x['credit'] > 0 ):
                    data['last_payment_date']=x['tdate'].split('T')[0]
                    data['last_payment']="{:.2f}".format(x['credit'])
                x['credit']="{:.2f}".format(x['credit'])
                x['debit']="{:.2f}".format(x['debit'])
                amount_due=x['balance']
                x['balance']="{:.2f}".format(x['balance'])
                x['category_l']=c_pd.at[x['category_id'],'name']
                i +=1
            else:
                data['carry_forward']="{:.2f}".format(x['balance'])
                data['carry_forward_date']=x['tdate'].split('T')[0]
                #app1.logger.debug("BAD: ", x)
                garbage = h1.pop(i)
            
        data['transactions']=h1
    data['rent']="{:.2f}".format(data['rent'])
    data['deposit']="{:.2f}".format(data['deposit'])
    if ( amount_due < 0 ):
        data['amount_due']="{:.2f}".format(abs(amount_due))
        data['due_date']=due_dt
        data['grace_period']='5 Days'
    else:
        data['amount_due']='No Payment Due'
        data['due_date']='NA'
        data['grace_period']='NA'
    data['statement_date']=datetime.today().strftime('%d %b %Y %H:%M:%S %Z')
    data['account'] = "TC."+str(data['tenancy_id'])+".P."+str(data['property_id'])+".T."+str(data['tenant_id'])
    
    
    # Company info
    c_pd = ref_data.get_company_info_pd(db, app1.logger)
    for ind in c_pd.index:
        if ( c_pd['label'][ind] == data['company']):
            data['company']=c_pd['name'][ind]
            data['company_address']=c_pd['m_address'][ind]
            data['company_address2']=c_pd['m_city'][ind]+"  "+c_pd['m_state'][ind]+" "+c_pd['m_zip'][ind]
    

    app1.logger.debug("pm_print.tenant_statement.4:Data=>%s",data)
    
    #app1.logger.debug("pm_print.tenant_statement.5: status=",data['status_l'], " priority:", data['priority_l'])

    headers={}
    headers['Content-Type'] = 'Content-Disposition: inline'
    
    if ( l_format == 'html'):
        data['h_logo']=app1.config['LOGO_HTML']
        #app1.logger.debug("pm_print.tenant_statement.7: HTML", data['h_logo'])
        rep =render_template('HP Tenant Statement.html', data=data)
        headers['Content-Type']='text/html'
        headers['Content-Type'] = 'filename=tstmt.html'
    else:
        #app1.logger.debug("pm_print.tenant_statement.8: PDF")
        data['h_logo']=app1.config['LOGO_PRINT'] 
        options = {
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'page-size': 'A4',
            'orientation' : 'Portrait',
            'footer-right': '[page]/[topage]'
        }
        
        rep1 =render_template(qj['template_file'], data=data)
        #config = pdfkit.configuration(wkhtmltopdf="C:/ProgramData/Anaconda3/Lib/site-packages/wkhtmltopdf/")
        #config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
        config = pdfkit.configuration(wkhtmltopdf=app1.config['PRINT_SERVER'])
        if ( 'output_file' in qj and qj['output_file'] != ""  ):
            #app1.logger.debug("pm_print.tenant_statement.85: Output file=>",qj['output_file']);
            rep = pdfkit.from_string(rep1, qj['output_file'], configuration=config, options=options)
            return data
        else:
            rep = pdfkit.from_string(rep1, False, configuration=config, options=options)        
            headers['Content-Type']='application/pdf'
            headers['Content-Type'] = 'filename=tstmt.pdf'
    
    #app1.logger.debug("pm_print.tenant_statement.9: Generation complete")
    
    response = app1.response_class(
        response=rep,
        headers=headers,
        status=200
    )          

    return response

####### Parking Tag PDF
def parkingTag(app1,db, qj):
    data={}
    l_format="pdf"
    r ={}
    r['function']='pdf'
    r['status']='failure'

    app1.logger.debug("parkingT::%s", qj)
    
    if ('format' in qj):
        l_format=qj['format']
    
    
    O_t = PMTenant(qj['tenant_id'], qj, app1.logger, db)
        
    data = O_t.getParkingTagInfo(int(qj['parking_permit_id']))
    
    data['h_logo']=app1.config['LOGO_PRINT']
    data['tenant_id']=qj['tenant_id']
    app1.logger.debug("parkingT.4:[%s] %s", l_format, data)
    data['label'] = data['label']+" "+data['city']+" " +data['state']+" " + data['zip']
    data['expiry']= datetime.strftime(data['expiry'],'%Y %b %d')
    if ( 'monthly' in data):
        data['monthly']="{:.2f}".format(data['monthly'])
    if ( 'setup_charge' in data):
        data['setup_charge']="{:.2f}".format(data['setup_charge'])
    if ( data['status'] < 0 ):
        mtype="text/json"
        r['message']="Parking tag is not active - not available"
        rep = r
    elif ( l_format == 'html'):
        app1.logger.debug("parkingT.7: HTML")
        data['h_logo']=app1.config['LOGO_HTML']
        rep =render_template('HP Parking Tag.html', data=data)
        mtype="text/html"
    else:
        app1.logger.debug("parkingT.8: PDF")
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
        }
        rep1 =render_template('HP Parking Tag.html', data=data)
        config = pdfkit.configuration(wkhtmltopdf=app1.config['PRINT_SERVER'])
        rep = pdfkit.from_string(rep1, False, configuration=config, options=options)    
        mtype="application/pdf"
    
    app1.logger.debug("parkingT.9: Generation complete");
    #response.headers['Content-Type'] = 'inline; filename=pktag.pdf'
    #response.headers['Content-Type'] = 'application/pdf'
    response = app1.response_class(
        response=rep,
        headers={'Content-Disposition':'inline; filename=pt.pdf', 'Content-Type':'application/pdf'},
        status=200,
        mimetype=mtype
    )        

    return response

####### Parking Tag PDF
def petPass(app1,db, qj):
    data={}
    l_format="pdf"
    r ={}
    r['function']='pdf'
    r['status']='failure'

    app1.logger.debug("petPass::%s", qj)
    
    if ('format' in qj):
        l_format=qj['format']
    
    
    O_t = PMTenant(qj['tenant_id'], qj, app1.logger, db)
        
    data = O_t.getPetTagInfo(int(qj['pet_id']))
    
    data['h_logo']=app1.config['LOGO_PRINT']
    data['tenant_id']=qj['tenant_id']
    app1.logger.debug("petPass.4:[%s] %s", l_format, data)
    data['label'] = data['label']+" "+data['city']+" " +data['state']+" " + data['zip']
    data['expiry']= datetime.strftime(data['expiry'],'%Y %b %d')
    if ( 'monthly' in data):
        data['monthly']="{:.2f}".format(data['monthly'])
    if ( 'setup_charge' in data):
        data['setup_charge']="{:.2f}".format(data['setup_charge'])
    if ( data['status'] < 0 ):
        mtype="text/json"
        r['message']="Pet pass is not active - not available"
        rep = r
    elif ( l_format == 'html'):
        app1.logger.debug("petPass.7: HTML")
        data['h_logo']=app1.config['LOGO_HTML']
        rep =render_template('HP Pet Pass.html', data=data)
        mtype="text/html"
    else:
        app1.logger.debug("petPass.8: PDF")
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
        }
        rep1 =render_template('HP Pet Pass.html', data=data)
        config = pdfkit.configuration(wkhtmltopdf=app1.config['PRINT_SERVER'])
        rep = pdfkit.from_string(rep1, False, configuration=config, options=options)    
        mtype="application/pdf"
    
    app1.logger.debug("petPass.9: Generation complete");
    #response.headers['Content-Type'] = 'inline; filename=pktag.pdf'
    #response.headers['Content-Type'] = 'application/pdf'
    response = app1.response_class(
        response=rep,
        headers={'Content-Disposition':'inline; filename=pt.pdf', 'Content-Type':'application/pdf'},
        status=200,
        mimetype=mtype
    )        

    return response
####### WO
def wo(app1, db, qj, action=''):
    data={}
    tenant = pd.DataFrame()
    rep = None
    l_format="pdf"
    r ={}
    r['function']='pdf'
    r['status']='failure'
    wos = ref_data.get_my_cores_pd(db, app1.logger, 'WO_STATUS')
    wos = wos.set_index('co_name')
    wop = ref_data.get_my_cores_pd(db,app1.logger, 'WO_PRIORITY')
    wop = wop.set_index('co_name')
    users = pm_user.getUsers_PD (db, app1.logger, None)

    app1.logger.debug("pm_print.wo::%s", qj)

    if ('format' in qj):
        l_format=qj['format']
    
    data = pm_wo.getWO(db, app1.logger, qj)
    app1.logger.debug("History:%s", data)
    if ( 'history' in data and data['history'] != '' ):
        history = json.loads(data['history'])
        h1 = history['data']
        #app1.logger.debug(" format:",h1)
        for x in h1:
            #app1.logger.debug("history=>", x, "=>", wos.at[str(x['status']),'co_value'])
            x['tdate']=x['tdate'].replace('T',' ').split('.')[0]
            #x['status_l']=wos.at[str(x['status']),'co_value']
            #x['priority_l']=wop.at[str(x['priority']),'co_value']
            #x['coordinator_l']=users.at[x['coordinator'],'first_name']+" " +users.at[x['coordinator'],'last_name']
        data['wo_history']=h1
    
    if ( data['tenant_id'] > 0 ):
        tenant = ref_data.get_my_tenants_pd2(db,app1.logger, data['tenant_id'])
    if ( not tenant.empty):
        app1.logger.debug("Tenant info: %s", tenant)
        data['tenant']=tenant.at[data['tenant_id'],'first_name']+" "+tenant.at[data['tenant_id'],'last_name']
        data['phone']=tenant.at[data['tenant_id'],'phone']
        data['email']=tenant.at[data['tenant_id'],'email']
    
    O_prop = PMProperty(data['property_id'], None, None ,app1.logger, db)
    p_data = O_prop.getPInfo('ALL')
    p_data['direction']=''
    #'first floor on right'
    k = {'label','city','direction','state','zip','p_status','p_type'} #,'direction','key_code'}
    #app1.logger.debug("pm_print.wo.4:PROPERTY ------------->", p_data)
    for x in k:
        if ( x in p_data ):
            data[x] = p_data[x]
        else:
            data[x] = ""
    #for x in data:
        #app1.logger.debug("pm_print.wo.4:Data=>", x, "->", data[x])
    
    data['status_l']=wos.at[str(data['status']),'co_value']
    data['priority_l']=wop.at[str(data['priority']),'co_value']
    data['coordinator_l']=users.at[data['coordinator'],'first_name']+" " +users.at[data['coordinator'],'last_name']
    data['createdby_l']=users.at[data['createdby'],'first_name']+" " +users.at[data['createdby'],'last_name']
                
    app1.logger.debug("pm_print.wo.5: status[%s] priority[%s]",data['status_l'], data['priority_l'])
    if ( l_format == 'html'):
        data['h_logo']=app1.config['LOGO_HTML']
        app1.logger.debug("pm_print.wo.7: HTML: %s", data['h_logo'])
        rep =render_template('HP WO.html', data=data)
        mtype="text/html"
    else:
        app1.logger.debug("pm_print.wo.8: PDF")
        data['h_logo']=app1.config['LOGO_PRINT']
        options = {
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'page-size': 'A4',
            'orientation' : 'Portrait',
            'footer-right': '[page]/[topage]'
        }
        rep1 =render_template('HP WO.html', data=data)
        config = pdfkit.configuration(wkhtmltopdf=app1.config['PRINT_SERVER'])
        rep = pdfkit.from_string(rep1, False, configuration=config, options=options)    
        mtype="application/pdf"
        #rep = pdfkit.from_string(rep1, "wo.pdf", configuration=config, options=options)    
        #mtype="text/json"
    
    app1.logger.debug("pm_print.wo.9: Generation complete");

    if ( action == 'HTML FILE'):
        data['message_html']=rep
        return data
    
    response = app1.response_class(
        response=rep,
        headers={'Content-Disposition':'inline; filename=wo.pdf', 'Content-Type':'application/pdf'},
        status=200,
        mimetype=mtype
    )        
    

    return response