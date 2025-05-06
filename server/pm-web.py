#!flask/bin/python
import sys, os, platform
#print(sys.path)
from flask import Flask, jsonify, request, json, make_response,send_from_directory
from flask_cors import CORS, cross_origin
from flask import render_template, send_file
from locale import LC_ALL
from locale import setlocale
from logging import FileHandler
from logging import Formatter
import logging

import pandas as pd
from datetime import datetime
import ref_data, pm_update, pm_search,pm_company
import analysis.pm_analysis, pm_application, pm_investor
from analysis.pm_cashflow import PMCashflow
import pm_tx, pm_wo, pm_user, utils.pm_print, pm_sd, pm_vendor, pm_tranche, pm_message
import utils.pm_mail, utils.pm_utils, utils.pm_file, utils.pm_conf, utils.pm_db
from utils.pm_db import PMDB
from pm_category import PMCategory
import components.pm_property
from components.pm_property import PMProperty
from components.pm_tenant import PMTenant
from components.pm_tenancy import PMTenancy
import pm_tenant_admin
from pm_tranche import PMTranche

from werkzeug.utils import secure_filename


#app = Flask(__name__)
app = Flask(__name__, static_url_path="/files", static_folder="files")
#app = Flask(__name__, static_url_path="/files", static_folder="C:/Users/ppare/Development/HC/files")
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})
#
#CORS(app,resources={r"*": {"origins": "*" }})
#
global CONFIG
CONFIG={}
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
O_db = PMDB
O_cat = PMCategory
O_prop = PMProperty
O_pmcf = PMCashflow

O_dates={}
O_dates['tdate'] = datetime.today().strftime('%Y-%m-%d')
O_dates['year'] = datetime.today().strftime('%Y')
O_dates['month'] = datetime.today().strftime('%m')

#
@app.route("/info",methods=['GET', 'OPTIONS'])
def info():
    return "Hi : You have reached Himalaya Properties"
#    
@app.route("/",methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost')
def main():
    return render_template('index.html')

@app.route("/pimages/<name>",methods=['GET','POST', 'OPTIONS'])
@cross_origin(origin='localhost')
def main2(name):
    name = name.replace('|','/')
    app.logger.info("main2:%s", name)
    try:
        #return send_file(file_path, attachment_filename=file_name, mimetype=mimeT)
        return send_from_directory(CONFIG['upload_folder'], name)
    except Exception as e:
        return str(e)

@app.route("/files/<name>",methods=['GET','POST', 'OPTIONS'])
@cross_origin(origin='localhost')
def main3(name):
    app.logger.info("main2:%s", name)
    if ( name == 'pa_lease'):
        return send_from_directory('static', 'hp_ra.pdf')
    else:
        return render_template('error.html')

@app.route("/templates/<name>",methods=['GET','POST', 'OPTIONS'])
@cross_origin(origin='localhost')
def main4(name):
    dt={}
    dt['tenant']={}
    dt['property']={}
    dt['propertyW']={}
    dt['no field']='NO'
    return render_template(name, data=dt)

@app.route("/publicx", methods=['GET','OPTIONS', 'POST'])
@cross_origin(origin='localhost')
def publicX():
    qj={}
    mtype='text/json'
    query=""
    r ={}

    app.logger.debug("publicX: Headers=%s",request.headers)
    if ( request.method == "POST" ):
        app.logger.info("publicX.2:POST:%s", request.get_data(parse_form_data=True))        
        #qj = json.loads(request.form)
        for x in request.form:
            qj[x] = request.form[x]
    else:
        qj = request.args
        app.logger.info("publicX.2:GET:%s", qj)
    
    app.logger.info("publicX:data:%s",qj)
    if ( qj['requestor'] == 'wo-public' ):
        r = pm_wo.createWEBWO(app, O_db, qj)
    elif ( qj['requestor'] == 'tenant_application_fetch' ):
        r = pm_application.getTenancyApplication(app, O_db,qj)
    elif ( qj['requestor'] == 'tenant_application'):
        r = pm_application.createTenancyApplication(app, O_db,qj)
    else:
        r['message']='Unknown request'
        r['status']='Failure'
        r['code']=-1
        
    rep = json.dumps(r)
    
    app.logger.debug("publicX::%s",rep);
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

@app.route("/pdftstmt",methods=['GET','POST', 'OPTIONS'])
@cross_origin(origin='localhost')    
def tstmtPDF():   
    mtype='text/json'
    qj = {}
    r ={}
    query=""
    r['function']='pdf'
    r['status']='failure'
    
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.warn("tstmtPDF: Header verification failed")
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        query = request.data
        qj = json.loads(query)
    else:
        qj['tenant_id'] = request.args.get('tenant_id')
        qj['start_date'] = request.args.get('start_date')
        qj['end_date'] = request.args.get('end_date')
    
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    if ( qj ):
        response = utils.pm_print.tenant_statement(app,O_db, qj)  
    else:
        response = r
        
    return response

@app.route("/pdfpt",methods=['GET','POST', 'OPTIONS'])
@cross_origin(origin='localhost')    
def ptPDF():   
    mtype='text/json'
    qj = {}
    r ={}
    query=""
    r['function']='pdf'
    r['status']='failure'
    
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if (  vh['code'] != 0 ):
        app.logger.warn("ptPDF: Header verification failed")
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        query = request.data
        qj = json.loads(query)
    else:
        qj['tenant_id'] = request.args.get("tenant_id")
        qj['type'] = request.args.get("type")
        if ( qj['type'] == 'PARKING'):
            qj['parking_permit_id'] = request.args.get("parking_permit_id")
        elif ( qj['type'] == 'PET'):
            qj['pet_id'] = request.args.get("pet_id")
    
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    app.logger.info("pm-web.ptPDF:%s", qj)
    
    if ( qj['type'] == 'PARKING'):
        response = utils.pm_print.parkingTag(app,O_db, qj)  
    elif ( qj['type'] == 'PET'):
        response = utils.pm_print.petPass(app,O_db, qj)  
    else:
        response = r
        
    return response

@app.route("/pdfwo",methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origin='localhost')    
def woPDF():   
    mtype='text/json'
    r ={}
    qj={}
    query={}
    r['function']='pdf'
    r['status']='failure'
    
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.warn("woPDF: Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
        qj = json.loads(query)
    else:
        qj['wo_id'] = request.args.get("wo_id")
        
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    app.logger.debug("woPDF:%s", qj)
    if ( qj ):
        response = utils.pm_print.wo(app,O_db, qj)  
    else:
        response = r
    
    return response
@app.route("/gpdf",methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origin='localhost')    
def getPDF():   
    mtype='text/json'
    r ={}
    qj={}
    query={}
    r['function']='pdf'
    r['status']='failure'
    
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.warn("getPDF: Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
        qj = json.loads(query)
    else:
        qj['tx_id'] = request.args.get("tx_id")
        qj['tr_id'] = request.args.get("tr_id")
        qj['type'] = request.args.get("type")
        
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    app.logger.debug("getPDF:%s", qj)
    if ( qj ):
        response = utils.pm_print.createPDF(app,O_db, qj)  
    else:
        response = r
    
    return response

@app.route("/genreport",methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origin='localhost')    
def genReport():   
    mtype='text/json'
    r ={}
    qj={}
    query={}
    r['function']='pdf'
    r['status']='failure'
    
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.info("genReport: Header verification failed: %s",vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    
    if ( request.method == "POST"):
        query = request.data
        qj = json.loads(query)
    else:
        qj['report'] = request.args.get("report")
        
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']

    app.logger.debug("genReport:%s", qj)
    if ( qj ):
        response = utils.pm_print.wo(app,O_db, qj)  
    else:
        response = r
    
    return response
 
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'HP Error': '404: Not found'}), 404)
############# search #################
def rehashFileName(filename, dn):
    fname=""
    timestamp = datetime.today().strftime('%Y%m%d_%H%M%S')
    if ( '.' in filename):
        t =  filename.rsplit('.')
        app.logger.debug("rehashFileName:%s Ext:%s", filename, t)
        if t[1].lower() in ALLOWED_EXTENSIONS:
            fname = dn + "_" + timestamp + "." + t[1].lower()
    
    return fname
def rehashFileFormat(filename):
    fname=""
    if ( '.' in filename):
        t =  filename.rsplit('.')
        app.logger.debug("rehashFileFormat:%s", t)
        if t[1] in ALLOWED_EXTENSIONS:
            fname = t[1]
        else:
            fname='pdf'
    
    return fname

@app.route("/fu", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')    
def fileUpload():
    r ={}
    core={}

    r['function']='fu'
    r['status']='failure'
    
    if request.method == 'POST':
        for x in request.form:
            core[x] = request.form[x]
        
        app.logger.debug("fu.1=%s",core)
        app.logger.debug("fu.2=%s",request.files)
        # check if the post request has the file part
        if 'fileKey' not in request.files:
            app.logger.info('No file part')
            r['message']= "[fileKey]:No File Found"
        file = request.files['fileKey']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            app.logger.info('No selected file')
            r['message']= "[filename]:No Filename"
        else:
            filename = secure_filename(file.filename)
            fname = rehashFileName(filename, core['doc_name'])
            if ( 'doc_format' not in core ):
                core['doc_format'] = rehashFileFormat(filename)
                
            app.logger.debug("fileUpload.4:file name=%s", fname)
            # doc path should be: tenant id, wo id etc.
            d_path = os.path.join(core['key_type'] , core['key_value']).lower() + "/" + fname
            #d_path= O_dates['year'] + O_dates['month'] +"/"+ fname
            #core['doc_path'] = d_path
            
            core['doc_path'] = d_path
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], d_path)
            app.logger.debug("fileUpload.5:save folder=%s", save_path)
            
            if not os.path.exists(os.path.dirname(save_path)):
                try:
                    os.makedirs(os.path.dirname(save_path))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            else:
                app.logger.debug("fileUpload.55: save path exists:%s", save_path)
            #core['doc_path'] = os.path.join(d_path, fname)
            
            app.logger.debug("fileUpload.6:save path=%s", save_path)
            
            file.save(save_path)
            r['status']='success'
            r['message']='['+filename+']File Saved'
            app.logger.info("fileUpload.7: saved: %s", core['doc_path'])
            
    if (r['status'] == 'success' ):
        utils.pm_file.updateFiles(O_db, app.logger, core)
    rep = json.dumps(r)
    mtype='text/json'
    
    app.logger.debug("fu::%s",rep);
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )       
    
    return response

@app.route("/fd", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')    
def fileDelete():
    query = ""
    r ={}
    qj = {}
    r['function']='fu'
    r['status']='failure'
    mtype='text/json'
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.warn("filesGet: Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
    app.logger.info("fileDelete::%s", query)
    
    if ( query ):
        qj = json.loads(query)
        
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    ret = utils.pm_file.deleteFiles(O_db, app.logger, qj)
    
    if ( ret > 1 ):
        r['status']='Success'
        r['doc_id']=ret
        rep = json.dumps(r)
        mtype='text/json'
    else:
        r['status']='Failure'
        r['tenant_id']='-1'
        rep = json.dumps(r)
        mtype='text/json'
        
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response
## Send file to client
@app.route("/fg", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')    
def return_file():
    qj = {}
    
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.warn("filesGet: Header verification failed: %s",vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        query = request.data
        qj = json.loads(query)
    else:
        query = request.args.get('query')
        qj = json.loads(query)
        l_format = request.args.get("format")
    qj['user_id']=vh['user_id']
    qp = qj["params"]
    mimeT='application/'+qp['doc_format']
    app.logger.debug("return_file:user1:%s [%s]%s", vh, mimeT, qj)
    
    if ( 'key_type' in qp and qp['key_type'] == 'INVESTOR'):
        qp['user_id']=vh['user_id']
        ret = pm_investor.verifyFile(O_db, app.logger, qp)
        app.logger.debug("return_file:user2:%s", ret)
        if ( ret != 1 ):
            return()
            r ={}
            r['function']='fl'
            r['status']='failure'
            rep = json.dumps(r)
            mtype='text/json'
            
            return( app.response_class(
                response=rep,
                status=200,
                mimetype=mtype
            ) )
    
    file_name = qp['doc_name']
    file_path = CONFIG['upload_folder'] + "/" + qp['doc_path']
    app.logger.debug("return_file:%s [%s]", file_path, file_name)

    pm_user.updateUsage(O_db, app.logger, vh, qj)
    
    try:
        return send_file(file_path, attachment_filename=file_name, mimetype=mimeT)
    except Exception as e:
        return str(e)
    
@app.route("/fl", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')                 
def filesGet():
    query = ""
    qj={}
    l_format = 'json'
    mtype='text/json'  
    
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.warn("filesGet: Header verification failed: %s",vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
        qj = json.loads(query)
    else:
        query = request.args.get('query')
        qj = json.loads(query)
        l_format = request.args.get("format")
        
    qj['params']['user_id']=vh['user_id']
    qj['params']['updatedby']=vh['Updatedby']
    app.logger.debug("filesGet:%s",qj)
    ret = utils.pm_file.getDocuments(O_db, app.logger, qj['params'])
    
    if ( ret.empty != True ):
        if ( l_format == 'html' ):
            rep = ret.to_html()
            mtype = 'text/html'            
        else:
            rep = ret.to_json(orient='table')
            mtype='text/json'
    else:
        r ={}
        r['function']='fl'
        r['status']='failure'
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
        
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    pm_user.updateUsage(O_db, app.logger, vh, qj)                 

    return response
############# Notices #################
@app.route("/notices", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')    
def notices():
    l_format='json'
    query = request.args.get("query")
    app.logger.debug("notices::%s",query)
    r ={}
    r['code']='1'
    qj = json.loads(query)['params']


    if ( qj['report'] == 'RENTAL' ):
        r = pm_message.get_message(O_db, app, qj)
    elif ( qj['report'] == 'HP' ):
        r = pm_message.get_message(O_db, app, qj)

    
    if ( l_format == 'html' ):
        rep = r
        mtype = 'text/html'            
    else:
        rep = json.dumps(r)
        mtype='text/json'
        
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

############# search #################
@app.route("/search", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')    
def search():
        
    l_format = 'json'
    mtype='text/json'
    query=""
    s=""

    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("search:%s  format: %s", query, l_format)
    if ( query ):
        qj = json.loads(query)
        if ( 'search' in qj['params']):
            try:
                s = qj['params']['search']
            except ValueError:
                app.logger.warn("No Search string, no data will be fetched")
        
    app.logger.debug("search:: data:%s",s)

    ret = pm_search.searchMe(O_db, app.logger, s, vh['user_id'])
    
    if ( ret.empty != True ):
        if ( l_format == 'html' ):
            rep = ret.to_html()
            mtype = 'text/html'            
        else:
            rep = ret.to_json(orient='table')
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
        
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

## pm_investor ----------------------------
@app.route("/investor/<action>",methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origin='localhost')    
def investor(action):

    rep= None
    qj = {}
    l_format = 'json'
    mtype='text/json'
    query=""

    app.logger.info("pm_web.investor::%s", action)

    #query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
    else:
        query = request.args.get("query")
    app.logger.info("investor::%s",query);
    
    if ( query ):
        qj = json.loads(query)
    
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    app.logger.info("investor:%s",qj)

    if ( action in 'info'  ):
        ret = pm_investor.getInvestor(O_db, app.logger, qj)
        rep = json.dumps(ret)
    elif ( action == 'list'):
        ret = pm_investor.getInvestors(O_db, app.logger, qj)
        rep = ret.to_json(orient='table')
    elif ( action == 'gtx'):
        ret = pm_investor.getITX(O_db, app.logger, qj)
        rep = json.dumps(ret)
    elif ( action == 'gtxs'):
        ret = pm_investor.getITXS(O_db, app.logger, qj)
        rep = ret.to_json(orient='table')
    elif ( action == 'utx'):
        ret = pm_investor.updateITX(O_db, app.logger, qj)
        rep = json.dumps(ret)
    elif ( action == 'update'):
        ret = pm_investor.updateInvestor(O_db, app.logger, qj)
        rep = json.dumps(ret)
    else:
        r ={}
        r['status']='Failure'
        r['message']='Request failed'
        r['investor_id']='-1'
        r['code']=1
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
    app.logger.debug("Investor Response: %s", rep)    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response 

## pm_applications ----------------------------
@app.route("/applications/<action>",methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origin='localhost')    
def applications(action):

    rep= None
    qj = {}
    l_format = 'json'
    mtype='text/json'
    query=""

    app.logger.info("pm_web.applications::%s", action)

    #query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
    else:
        query = request.args.get("query")
    app.logger.info("applications::%s",query);
    
    if ( query ):
        qj = json.loads(query)
    
    qj['params']['user_id']=vh['user_id']
    qj['params']['updatedby']=vh['Updatedby']

    app.logger.info("applications:%s",qj)

    if ( action in 'info'  ):
        ret = pm_application.getTenancyApplication(app, O_db, qj['params'])
        rep = json.dumps(ret)
    elif ( action == 'list'):
        ret = pm_application.getTenancyApplications(app, O_db, qj['params'])
        rep = ret.to_json(orient='table')
    elif ( action == 'update'):
        ret = pm_application.updateTenancyApplication(app, O_db, qj['params'])
        rep = json.dumps(ret)
    else:
        r ={}
        r['status']='Failure'
        r['message']='Request failed'
        r['tenancy_app_id']='-1'
        r['code']=1
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
    #app.logger.debug("applications Response: %s", rep)    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    pm_user.updateUsage(O_db, app.logger, vh, qj)          

    return response 

    
################ Update #######################
@app.route("/pu", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def updateP():

    qf=""
    qj = None
    l_format = 'json'
    mtype='text/json'
    query=""

    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
    app.logger.debug("updateP::%s",query);
    
    if ( query ):
        qj = json.loads(query)
      
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    app.logger.debug("updateP::qf:%s Data:%s", qf,qj)

    ret = pm_update.updateProperty(O_db, app.logger, qj)
    
    if ( ret > 1 ):
        O_t = PMProperty(ret, None, None, app.logger, O_db)
        
        c = O_t.getPInfo('ALL')
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = ret
            mtype = 'text/html'            
        else:
            rep = json.dumps(ret)
            mtype='text/json'
        
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response
#################
@app.route("/tenancyu", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def updateTC():
    qf=""
    qj = None
    l_format = 'json'
    mtype='text/json'
    query=""

    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        query = request.data
    
    if ( query ):
        qj = json.loads(query)
    
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    app.logger.info("updateTC::%s",qj)
    
    ret = pm_update.updateTenancy(O_db, app.logger, qj)
    app.logger.debug("updateTC.3:%s", ret)
    if ( ret > 1 ):
        app.logger.debug("updateTC.4:: fetching new tenancy info")
        O_t = PMTenancy(O_db, app.logger, ret, -1, -1)
        
        c = O_t.getTenancyInfo()
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = ret
            mtype = 'text/html'            
        else:
            rep = json.dumps(ret)
            mtype='text/json'
    
    app.logger.debug("updateT::%s",rep);
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

@app.route("/tenantu", methods=['POST','PUT'])
@cross_origin(origin='localhost')
def updateT():
    qf=""
    qj={}
    mtype='text/json'
    query=""

    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        app.logger.debug("RR:%s",request.get_data(parse_form_data=True))
        query = request.data
        
        app.logger.debug("tenantu.2:POST:%s", query)
        if ( query ):
            qj = json.loads(query)   
        #qj = json.loads(request.form)
        for x in request.form:
            qj[x] = request.form[x]

    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    
    app.logger.info("updateT::%s",qj)
    
    ret = pm_update.updateTenant(O_db, app.logger, qj)

    rep = json.dumps(ret)
    
    app.logger.info("updateT::%s",rep);
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

@app.route("/tenanta", methods=['POST','PUT'])
@cross_origin(origin='localhost')
def tenanta():
    qf=""
    qj={}
    mtype='text/json'
    query=""

    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("tenantadmin:Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        app.logger.debug("tenantadmin:%s",request.get_data(parse_form_data=True))
        query = request.data
        
        app.logger.debug("tenantadmin.2:POST:%s", query)
        if ( query ):
            qj = json.loads(query)   
        #qj = json.loads(request.form)
        for x in request.form:
            qj[x] = request.form[x]

    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    
    app.logger.info("tenantadmin::%s",qj)
    
    ret = pm_tenant_admin.tenantAdmin(O_db, app, qj)

    if ( ret == 0 ):
        r ={}
        r['status']='NOP'
        r['message']='No Action Taken by server'
        r['code']=0
        r['tenant_id']=qj['tenant_id']
        rep = json.dumps(r)
    elif ( ret > 1 ):
        r ={}
        r['status']='Success'
        r['code']=0
        r['tenant_id']=ret
        rep = json.dumps(r)
    else:
        r ={}
        r['status']='Failure'
        r['code']=ret
        r['message']='Server side error'
        rep = json.dumps(r)
    
    app.logger.info("updateT::%s",rep);
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )                                  
    return response

@app.route("/ustx", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def updateSTX():
    qf=""
    qj={}
    l_format = 'json'
    mtype='text/json'
    query=""
    # http://127.0.0.1:5000/utx?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
    app.logger.info(query)
    if ( query ):
        qj = json.loads(query)
        if ( 'qualifier' in qj):
            try:
                qf = qj['qualifier']
            except ValueError:
                app.logger.warn("No qualifier, must use default")           
    
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby'] 
    app.logger.info("updateSTX::%s", qj)   
    ret = pm_sd.updateSTX(O_db, app.logger, qj)
    
    O_t = PMTenant(qj['tenant_id'], qj , app.logger, O_db)
    sd = O_t.updateSD(O_db, None, None) 
    
    if ( ret != "-1" ):        
        r = {}
        r['status']='Success'
        r['stx_id']=ret
        r['status_code']=ret
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'
        else:
            rep = json.dumps(r)
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = ret
            mtype = 'text/html'            
        else:
            rep = json.dumps(ret)
            mtype='text/json'
         
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

@app.route("/utx", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def updateTX():
    qf=""
    qj={}
    l_format = 'json'
    mtype='text/json'
    query=""
    # http://127.0.0.1:5000/utx?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.info("updateT: Header verification failed")
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        query = request.data
    app.logger.info(query)
    if ( query ):
        qj = json.loads(query)
        app.logger.info(qj)
        if ( 'qualifier' in qj):
            try:
                qf = qj['qualifier']
            except ValueError:
                app.logger.info("No qualifier, must use default")           
    app.logger.info("updateTX::qf:" + qf)   

    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']

    ret = pm_tx.updateTX(O_db, app.logger, qj)
    
    if ( ret != "-1" ):        
        r = {}
        r['status']='Success'
        r['tx_id']=ret
        r['status_code']=ret
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'
        else:
            rep = json.dumps(r)
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = ret
            mtype = 'text/html'            
        else:
            rep = json.dumps(ret)
            mtype='text/json'
         
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

@app.route("/utr", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def updateTR():
    qf=""
    l_format = 'json'
    mtype='text/json'
    query=""
    # http://127.0.0.1:5000/utx?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        query = request.data
    app.logger.info(query)
    if ( query ):
        qj = json.loads(query)
        if ( 'qualifier' in qj):
            try:
                qf = qj['qualifier']
            except ValueError:
                app.logger.warn("No qualifier, must use default")           
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']  
    app.logger.info("updateTR::%s", qj)  
    ret = pm_tx.updateTR(O_db, app.logger, qj)
    
    if ( ret > 0 ):        
        r = {}
        r['status']='Success'
        r['code']=0
        r['tr_id']=ret
        r['status_code']=ret
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'
        else:
            rep = json.dumps(r)
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['code']=1
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = ret
            mtype = 'text/html'            
        else:
            rep = json.dumps(ret)
            mtype='text/json'
         
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response
######## Transactions
@app.route("/gtx", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getTX():
    p = {}
    l_format = 'json'
    mtype='text/json'
    query=""
    tr_id=-1
    tx_id=-1
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("getTX:%s  Format:%s", query, l_format)
    if ( query ):
        qj = json.loads(query)
        qj['params']['user_id'] = vh['user_id']
        
        if ( 'tr_id' in qj['params']):
            try:
                tr_id = int(qj['params']['tr_id'])
            except ValueError:
                app.logger.warn("No tr_id, no data will be fetched")
        if ( 'tx_id' in qj['params']):
            try:
                tx_id = int(qj['params']['tx_id'])
            except ValueError:
                app.logger.warn("No tx_id, no data will be fetched")          
    app.logger.info("getTX::TX:%s  TR:%s", tx_id, tr_id)
    if ( tr_id > 0 ):
        p = pm_tx.getTX(O_db,app.logger, 'TR',tr_id)  
    elif( tx_id > 0):
        p = pm_tx.getTX(O_db,app.logger, 'TX',tx_id)    

    app.logger.info("getTX::Reply:%s", p)
    if ( p ):
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(p)
            mtype = 'text/html'            
        else:
            rep = json.dumps(p)
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['tr_id']=tr_id
        r['tx_id']=tx_id
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'     
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    pm_user.updateUsage(O_db, app.logger, vh, qj)       
    return response

@app.route("/gtxs", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getTXS():
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    query=""
    # http://127.0.0.1:5000/gtxs?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    
    query = request.args.get("query")
    l_format = request.args.get("format")
    
    
    if ( query ):
        qj = json.loads(query)
    qj['params']['user_id']=vh['user_id']
    qj['params']['updatedby']=vh['Updatedby']
    app.logger.info("getTXS::%s QJ:%s", l_format, qj)    
    if ( 'tx_type' in qj['params'] and qj['params']['tx_type'] == 'TR'):
        p = pm_tx.getTRS(O_db, app.logger, qj['params'])
    elif ( 'tx_type' in qj['params'] and qj['params']['tx_type'] == 'STX'):
        p = pm_sd.getSTXS(O_db, app.logger, qj['params'])
    else:
        p = pm_tx.getTXS(O_db, app.logger, qj['params'])

    app.logger.info("getTXS.2:%s", p.size)
    if ( not p.empty ):
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
    
    #app.logger.info("updateT::"+rep);
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    pm_user.updateUsage(O_db, app.logger, vh, qj)                      
    return response

@app.route("/gtxsdups", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getTXSDUPS():
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    query=""
    # http://127.0.0.1:5000/gtxs?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    
    query = request.args.get("query")
    
    if ( query ):
        qj = json.loads(query)['params']
    qj['user_id']=vh['user_id']
    app.logger.info("getTXS::%s QJ:%s", l_format, qj)    
    p = pm_tx.getTXSDUPS(O_db, app.logger, qj)

    app.logger.info("getTXS.2:%s", p.size)
    if ( not p.empty ):
        rep = p.to_json(orient='table')
        mtype='text/json'
    else:
        r ={}
        r['status']='Success'
        r['code']='0'
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
    
    #app.logger.info("updateT::"+rep);
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

######## SD Transactions
@app.route("/gstx", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getSTX():
    p = {}
    l_format = 'json'
    mtype='text/json'
    query=""
    tr_id=-1
    tx_id=-1
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    
    query = request.args.get("query")
    l_format = request.args.get("format")
    
    if ( query ):
        qj = json.loads(query)['params']
        qj['user_id'] = vh['user_id']
        app.logger.info("getTX:2:", qj)
        if ( 'stx_id' in qj):
            try:
                stx_id = int(qj['stx_id'])
            except ValueError:
                app.logger.info("No stx_id, no data will be fetched")        
    app.logger.info("getTX:QJ:%s", qj)
    if ( stx_id > 0 ):
        p = pm_sd.getSTX(O_db,app.logger,'STX',stx_id)    
    if ( p ):
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(p)
            mtype = 'text/html'            
        else:
            rep = json.dumps(p)
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['tr_id']=tr_id
        r['tx_id']=tx_id
        r['stx_id']=stx_id
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'     
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

@app.route("/gstxs", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getSTXS():
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    query=""
    qj = {}
    t_id=-1
    l_sd=None
    l_ed=None
    # http://127.0.0.1:5000/gstxs?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)

    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    
    query = request.args.get("query")
    l_format = request.args.get("format")
         
    app.logger.debug("getSTXS::%s %s", l_format, query)
    if ( query ):
        qj = json.loads(query)['params']
        qj['user_id']=vh['user_id']
        if ( 'updatedby' not in qj):
            qj['updatedby']=vh['Updatedby']
        t_id = qj['tenant_id']
        if ( 'start_date' in qj):
            try:
                l_sd = qj['start_date']
            except ValueError:
                app.logger.info("No start_date, will return all data")

        if ( 'end_date' in qj):
            try:
                l_ed = qj['end_date']
            except ValueError:
                app.logger.info("No end_date, will return all date")
        O_tenant = PMTenant(t_id, qj, app.logger, O_db)
        sd = O_tenant.updateSD(O_db, l_sd, l_ed)
        p = O_tenant.getSDH()

        
    app.logger.debug("getSTXS.2:%s  %s", p.size, p)
    if ( not p.empty ):
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
    
    app.logger.debug("updateT:%s",rep);
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response
########### Users ########################
@app.route("/lo", methods=['POST','PUT'])
@cross_origin(origin='localhost')
def logoutUser():
    qj = None
    l_format = 'json'
    mtype='text/json'
    login=""
    
    if ( request.method == "POST"):   
        app.logger.debug("logoutUser:%s",request.get_data(parse_form_data=True))
        query = request.data
        
        app.logger.info("logout.2:POST:%s", query)
        qj = json.loads(query)       
    
    app.logger.info("logoutUser: %s QJ: %s", query, qj)
    if ( 'login' in qj):
        try:
            login = qj['login']
        except ValueError:
            app.logger.info("logoutUser:No login, verification will failure")
            
    app.logger.info("logoutUser.3:Get User: %s", login)
    if ( login != None and login != "" ):

        c = pm_user.logoutUser(O_db, app.logger, qj)
        
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:
        r =qj
        r['status']='Failure'
        r['code']=1
        r['message']='No User ID found'
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'
        else:
            rep = json.dumps(r)
            mtype='text/json'
       
    app.logger.info("logoutUser.10: response:%s", rep)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response 
    
@app.route("/vu", methods=['POST','PUT'])
@cross_origin(origin='localhost')
def verifyUser():
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    qj=None
    query=""
    login=""
    # http://127.0.0.1:5000/gtxs?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    if ( request.method == "POST"):   
        app.logger.debug("vu:%s",request.get_data(parse_form_data=True))
        query = request.data
        
        app.logger.info("vu.2:POST:%s", query)
        qj = json.loads(query)       
    
    app.logger.info("vu?%s  QJ:%s", query, qj)
    
    if ( 'login' in qj):
        try:
            login = qj['login']
        except ValueError:
            app.logger.error("No login, verification will failure")
            
    app.logger.debug("verifyUser.3:Get User:%s", login)
    if ( login != None and login != "" ):

        c = pm_user.verifyUser(O_db, app.logger, qj)
        
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:
        r =qj
        r['status']='Failure'
        r['code']=1
        r['message']='No User ID found'
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'
        else:
            rep = json.dumps(r)
            mtype='text/json'
       
    
    app.logger.info("verifyUser.10: response:%s", rep)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response 

@app.route("/gu", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getUser():
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    qj=None
    query=""
    rep={}
    u_id=-1
    # http://127.0.0.1:5000/gtxs?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("gu?%s %s", query, l_format)
    if ( query ):
        qj = json.loads(query)
   
        if ( 'user_id' in qj['params']):
            try:
                u_id = qj['params']['user_id']
            except ValueError:
                app.logger.info("No user id, will return all properties")
            
    app.logger.info("Get User:%s", u_id)
    if ( u_id > 0 ):

        c = pm_user.getUser(O_db, app.logger, qj['params'])
        
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:
        p = pm_user.getUsers_PD(O_db, app.logger, qj)
        
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
       
    #app.logger.debug("User info:%s", rep)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response 

@app.route("/su", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def saveUser():
    l_format = 'json'
    mtype='text/json'
    qj=None
    query=""
    rep={}
    u_id=-1

    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        query = request.data
    app.logger.info("saveUser:%s", query)
    if ( query ):
        qj = json.loads(query)
        if ( 'format' in qj ):
            l_format=qj['format']
        app.logger.info("saveUser:", qj)
        if ( 'user_id' in qj):
            u_id = qj['user_id']
            
    app.logger.info("saveUser.3:%s", u_id)
    if ( u_id > 0 ):
        c = pm_user.saveUser(O_db, app.logger, qj)
        
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:
        r =qj
        r['status']='Failure'
        r['code']=1
        r['message']='No User ID found'
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'
        else:
            rep = json.dumps(r)
            mtype='text/json'
       
    app.logger.debug("User info:%s", rep)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response 
    
@app.route("/rup", methods=['POST','PUT'])
@cross_origin(origin='localhost')
def resetPass():
    mtype='text/json'
    qj=None
    query=""
    rep={}
    vh = request.headers
    app.logger.info("resetPass: Header:%s", vh)
    
    if ( request.method == "POST"):
        query = request.data
    app.logger.info("resetPass:%s", query)
    if ( query ):
        qj = json.loads(query)
            
    app.logger.info("resetPass.3:%s", qj)
    c = pm_user.updatePassword(O_db, app.logger, qj)
    
    if ( c['code'] == 0):
        utils.pm_mail.passwordResetEmail(app, c)
        
    rep = json.dumps(c)
    mtype='text/json'
    
    app.logger.debug("resetPass: User info:%s", rep)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response 
@app.route("/signup", methods=['POST','PUT'])
@cross_origin(origin='localhost')
def userSignUp():
    mtype='text/json'
    qj=None
    query=""
    rep={}
    vh = request.headers
    app.logger.info("userSignUp: Header:%s", vh)
    
    if ( request.method == "POST"):
        query = request.data
    app.logger.info("userSignUp:%s", query)
    if ( query ):
        qj = json.loads(query)
            
    app.logger.info("userSignUp.3:%s", qj)
    n = qj['name'].split(' ')
    if ( len(n) > 1 ):
        qj['first_name']=n[0]
        qj['last_name']=n[1]
    else:
        qj['first_name']=qj['name']
        qj['last_name']=''
    c = {}
    c['code']=0
    c['message']="Request submitted"
    c['status']="success"
    
    utils.pm_mail.sendUserSignUpNotification(app, qj)
        
    rep = json.dumps(c)
    mtype='text/json'
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response 

@app.route("/askq", methods=['POST','PUT'])
@cross_origin(origin='localhost')
def userAskQ():
    mtype='text/json'
    qj=None
    query=""
    rep={}
    vh = request.headers
    app.logger.info("userAskQ: Header:%s", vh)
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
    app.logger.info("userAskQ:%s", query)
    if ( query ):
        qj = json.loads(query)
            
  
    c['code']=0
    c['message']="Request submitted"
    c['status']="success"
    
    #utils.pm_mail.sendUserSignUpNotification(app, qj)
        
    rep = json.dumps(c)
    mtype='text/json'
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response 
########### Work orders ########################
@app.route("/gwo", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getWO():
    p = {}
    l_format = 'json'
    mtype='text/json'
    qj = None
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("getWO.2::%s %s", l_format, query)
    if ( query ):
        qj = json.loads(query)
    
    qj['params']['user_id']=vh['user_id']
    qj['params']['updatedby']=vh['Updatedby']
        
    app.logger.info("getWO.3:%s", qj)
    p = pm_wo.getWO(O_db, app.logger, qj['params'])
    if ( p ):
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(p)
            mtype = 'text/html'            
        else:
            rep = json.dumps(p)
            mtype='text/json'
    else:
        r = qj['params']
        r['status']='Failure'
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'     
            
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

@app.route("/gwos", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getWOS():
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    qj=None
    query=""
    # http://127.0.0.1:5000/gtxs?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("getWOS::%s %s", l_format, query)
    if ( query ):
        qj = json.loads(query)
    
    qj['params']['user_id']=vh['user_id']
    qj['params']['updatedby']=vh['Updatedby']
    
    p = pm_wo.getWOS(O_db, app.logger, qj['params'])
    app.logger.debug("getWOS.2::%s", p.size)
    if ( p.empty != True ):
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
    else:
        r =qj['params']
        r['status']='Failure'
        r['status_code']=-1
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
    
    #app.logger.debug("getWOS:%s",rep);
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response
@app.route("/gwoh", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getWOH():
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    qj=None
    query=""
    # http://127.0.0.1:5000/gtxs?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("getWOH::%s %s", l_format, query)
    if ( query ):
        qj = json.loads(query)
    
    qj['params']['user_id']=vh['user_id']
    qj['params']['updatedby']=vh['Updatedby']
    p = pm_wo.getWOH(O_db, app.logger, qj['params'])
    app.logger.info("getWOH.2::%s", p.size)
    if ( p.empty != True ):
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
    else:
        r =qj['params']
        r['status']='Failure'
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
    
    app.logger.debug("getWOH:%s",rep);
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

@app.route("/uwo", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def updateWO():
    l_format = 'json'
    mtype='text/json'
    query=""
    qj={}
    # http://127.0.0.1:5000/utx?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    
    if ( request.method == "POST"):
        query = request.data
       
    app.logger.info("updateWO:%s", query)
    if ( query ):
        qj = json.loads(query)
        qj['user_id']=vh['user_id']
        qj['login']=vh['Login']
        qj['updatedby']=vh['Updatedby']
        app.logger.info("updateWO:%s", qj)
        
    ret = pm_wo.updateWO(app, O_db,qj)
    
    if ( ret > 0 ):        
        r = {}
        r['status']='Success'
        r['wo_id']=ret
        r['status_code']=0
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'
        else:
            rep = json.dumps(r)
            mtype='text/json'
    else:
        r ={}
        r['status']='Failure'
        r['status_code']=-1
        r['wo_id']=-1
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
    app.logger.info("updateWO:[%s] %s",ret, rep)
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response
############# update communication history
@app.route("/uchistory", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def updateCHistory():
    l_format = 'json'
    mtype='text/json'
    query=""
    qj={}
    # http://127.0.0.1:5000/utx?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    
    if ( request.method == "POST"):
        query = request.data
       
    app.logger.info("updateCHistory:%s", query)
    if ( query ):
        qj = json.loads(query)
        qj['user_id']=vh['user_id']
        qj['login']=vh['Login']
        qj['updatedby']=vh['Updatedby']
    app.logger.info("updateCHistory:%s", qj)
    
    ret = pm_update.updateHistory(O_db, app.logger, qj)
    
    if ( ret != "-1" ):        
        r = {}
        r['status']='Success'
        r['wo_id']=ret
        r['status_code']=ret
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(r)
            mtype = 'text/html'
        else:
            rep = json.dumps(r)
            mtype='text/json'
        
    else:
        r ={}
        r['status']='Failure'
        r['tenant_id']='-1'
        if ( l_format == 'html' ):
            rep = ret
            mtype = 'text/html'            
        else:
            rep = json.dumps(ret)
            mtype='text/json'
         
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response
############# Analysis Functions
@app.route("/get_u_tenancy", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getUL():
    r ={}
    r['function']='get_u_tenancy'
    r['status']='success'
    r['message']='No Data Found'
    
    l_format = 'json'
    mtype='text/json'
    rep=""
    # 127.0.0.1:5000/p?query={%22params%22:{%22id%22:%22123%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("getUL?%s  %s", query, l_format)
    if ( query ):
        qj = json.loads(query)
     
    p = analysis.pm_analysis.get_upcoming_tenancy(O_db, app.logger, qj['params'])
    if ( p.empty != True ):
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'    
    else:
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'

    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        

    return response
    
@app.route("/analysis", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getAnalysis():
    r ={}
    r['function']='analysis'
    r['action']='deliquencies'
    r['status']='success'
    r['message']='No Data Found'
    
    l_format = 'json'
    mtype='text/json'
    rep=""
    # 127.0.0.1:5000/p?query={%22params%22:{%22id%22:%22123%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("getUL?%s  %s", query, l_format)
    if ( query ):
        qj = json.loads(query)
    qj1 = qj['params'] 
    qj1['user_id']=vh['user_id']
    qj1['login']=vh['Login']
    qj1['updatedby']=vh['Updatedby']
    p = analysis.pm_analysis.get_deliquencies(O_db, app.logger, qj1)
    if ( p.empty != True ):
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'    
    else:
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'

    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        

    return response

############# Time series
@app.route("/ts", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getTS():
    
    l_format = 'json'
    mtype='text/json'
    rep=""
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("ts?%s %s", query,l_format)
    if ( query ):
        qj = json.loads(query)
     
    p = analysis.pm_analysis.getTS(O_db, app.logger, qj['params'])
    
    if ( l_format == 'html' ):
        rep = p.to_html()
        mtype = 'text/html'            
    else:
        rep = p.to_json(orient='table')
        mtype='text/json'
       
    app.logger.debug("getTS info:%s", mtype)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           

    return response 
    
#################
@app.route("/core", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getCores():
    
    l_format = 'json'
    mtype='text/json'
    co_type=""
    rep=""

    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("cores?%s %s", query, l_format)
    if ( query ):
        qj = json.loads(query)
        if ( 'co_type' in qj['params']):
            try:
                co_type=qj['params']['co_type']
            except ValueError:
                app.logger.info("No co_type will return all cores")
    app.logger.info("cores2:%s", qj)
    if ( co_type != "" ):
        p = ref_data.get_my_cores_pd(O_db, app.logger, co_type)
        
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
    else:
        p = ref_data.get_my_cores_pd(O_db,app.logger, '')
        
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
       
    app.logger.debug("getCores info:%s", mtype)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response
    
########### Vendors 
@app.route("/vendor", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def getVendor():
    qj = {}
    l_format = 'json'
    mtype='text/json'
    v_type="ALL"
    v_id=-1
    rep=""
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    # 127.0.0.1:5000/p?query={%22params%22:{%22id%22:%22123%22}}
    # read the posted values from the UI
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("vendors?%s %s", query, l_format)
    if ( query ):
        qj = json.loads(query)
        if ( 'vendor_id' in qj['params']):
            try:
                v_id=int(qj['params']['vendor_id'])
            except ValueError:
                app.logger.warn("No vendor id will return all vendors")
        if ( 'type' in qj['params']):
            try:
                v_type=qj['params']['type']
            except ValueError:
                app.logger.warn("No type will return all vendors")
    app.logger.info("vendors:%s", qj)
    
    p = pm_vendor.get_my_vendors_pd(O_db,app.logger, v_type, v_id)
    
    if ( l_format == 'html' ):
        rep = p.to_html()
        mtype = 'text/html'            
    else:
        rep = p.to_json(orient='table')
        mtype='text/json'
       
    #app.logger.debug("getCores info:%s", rep)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    pm_user.updateUsage(O_db, app.logger, vh, qj)               

    return response

@app.route("/vendoru", methods=['POST','PUT'])
@cross_origin(origin='localhost')
def updateVendor():
    qf=""
    qj={}
    mtype='text/json'
    query=""
    x={}

    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    if ( request.method == "POST"):
        app.logger.debug("updateVendor:%s",request.get_data(parse_form_data=True))
        query = request.data
        
        app.logger.debug("updateVendor.2:POST:%s", query)
        if ( query ):
            qj = json.loads(query)   
        #qj = json.loads(request.form)
        for x in request.form:
            qj[x] = request.form[x]

    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    
    app.logger.info("updateVendor::%s",qj)
    
    ret = pm_vendor.updateVendor(O_db, app.logger, qj)

    rep = json.dumps(ret)
    
    app.logger.info("updateVendor::%s",rep);
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response

@app.route("/vendortx", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def vendorTransactions():
    qj=[]
    v_id=0
    l_format = 'json'
    mtype='text/json'
    # 127.0.0.1:5000/vendortx?query={%22params%22:{%22id%22:%221408%20vernon%20street%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    query = request.args.get("query")  
    l_format = request.args.get("format")
    app.logger.info("vendor::Query:%s", query)
    if ( query ):
        qj = json.loads(query)
        v_id = qj['params']['vendor_id']
    
    app.logger.info("vendorransactions2: %s",qj)
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    
    if v_id:
        # pid, cid, d1, d2, logger, db)
        c = pm_vendor.get_vendor_tx_pd(O_db, app.logger, qj['params'])
       
        if ( l_format == 'html' ):
            #c = c.style.applymap(pm_utils.color_negative_red).apply(pm_utils.highlight_max)
            #rep = c.to_html()
            rep = (
                    c.style \
                    .applymap(pm_utils.color_negative_red, subset=['debit', 'amount']) \
                    .set_properties(**{'font-size': '9pt', 'font-family': 'Calibri'}) \
                    .bar(subset=['credit', 'amount'], color='lightblue') \
                    .render()
                )
            mtype = 'text/html'
        else:
            rep = c.to_json(orient='table')
            mtype='text/json'       
    else: 
        r ={}
        r['status']='FAILED'
        r['code']='1'       
        r['message']='Vendor ID missing'      
        rep = json.dumps(r)
    
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    
    return response

###################### Property ############################
@app.route("/pcommercial", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def propertyV():
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    rep=""
    user_id=-1;
    
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.info("property: Header verification failed - IGNORED")
    else:
        user_id=vh['user_id']
    
    app.logger.info("/pv?")
    
    query = request.args.get("query")
    p_id=-1
    s_id='ALL'
    core={}
    core['status'] = 'RENT READY'

    if ( query ):
        qj = json.loads(query)
        if ( 'property_id' in qj['params']):
            p_id = int(qj['params']['property_id'])
        if ( 'state' in qj['params']):
            core['state'] = qj['params']['state']
        if ( 'status' in qj['params']):
            core['status'] = qj['params']['status']

    app.logger.info("pcommercial:%s %s %s", query, p_id, core)
    if ( p_id > 0 ):
        O_prop = PMProperty(p_id, None, None ,app.logger, O_db)
        c = O_prop.getPCInfo()
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:
        
        app.logger.info("pcommercial:%s %s", p_id, core)
        p = components.pm_property.get_my_properties_com_pd(O_db, app.logger, core, user_id)
    
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response

@app.route("/p", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def property():
    c = {}
    qj={}
    l_status=""
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    p_id=0
    t_id=-1
    l_sd=""
    l_ed=""
    rep=""
    l_info="ALL"
    l_grp=""
    user_id=-1;
    
    # 127.0.0.1:5000/p?query={%22params%22:{%22id%22:%22123%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    user_id=vh['user_id']
    
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("P?%s %s", query, l_format)
    if ( query ):
        qj = json.loads(query)
   
        if ( 'property_id' in qj['params']):
            try:
                p_id = qj['params']['property_id']
            except ValueError:
                app.logger.warn("No property id, will return all properties")
        if ( 'tenant_id' in qj['params']):
            try:
                t_id = qj['params']['tenant_id']
            except ValueError:
                app.logger.warn("No tenant id")
            
        if ( 'status' in qj['params']):   
            try:
                l_status = qj['params']['status']
            except ValueError:
                app.logger.warn("No status, will return all properties")
        if ( 'info' in qj['params']):   
            try:
                l_info = qj['params']['info']
            except ValueError:
                app.logger.warn("No info, will return all data")
    
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    app.logger.info("property:qj:[%s] %s", l_info, qj)
    if ( t_id > 0 ):
        O_t = PMTenant(t_id, qj , app.logger, O_db)
        p_id = O_t.getPropertyId()

    if ( p_id != 0 ):

        O_prop = PMProperty(p_id, l_sd, l_ed ,app.logger, O_db)

        c = O_prop.getPInfo(l_info)

        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
            
        app.logger.debug("Property info========: %s", rep)
    else:
        p = ref_data.get_my_properties_pd(O_db,app.logger, qj, qj['user_id'])
        
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
       
    
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response


@app.route("/pi/<action>", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')    
def propertyInspection(action):

    rep= None
    qj = {}
    l_format = 'json'
    mtype='text/json'
    query=""

    app.logger.info("pm_web.propertyInspection::%s", action)

    #query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("propertyInspection: Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
    else:
        query = request.args.get("query")
    app.logger.info("investor::%s",query);
    
    if ( query ):
        qj = json.loads(query)
    
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    app.logger.info("propertyInspection:%s",qj)

    if ( action in 'info'  ):
        ret = pm_property_insp.get_my_pi(O_db, app.logger, qj)
        rep = json.dumps(ret)
    elif ( action == 'list'):
        ret = pm_property_insp.get_my_pi_pd(O_db, app.logger, qj)
        rep = ret.to_json(orient='table')
    elif ( action == 'update'):
        ret = pm_property_insp.updatePI(O_db, app.logger, qj)
        rep = json.dumps(ret)
    else:
        r ={}
        r['status']='Failure'
        r['message']='Request failed'
        r['investor_id']='-1'
        r['code']=1
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
    app.logger.debug("propertyInspection Response: %s", rep)    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )           
    return response

@app.route("/ptr", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def propertyTransactions():
    c = pd.DataFrame()
    qj=[]
    p_id=0
    l_sd=""
    l_ed=""
    l_format = 'json'
    mtype='text/json'
    # 127.0.0.1:5000/ptr?query={%22params%22:{%22id%22:%221408%20vernon%20street%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    query = request.args.get("query")  
    l_format = request.args.get("format")
    app.logger.info("property::Query:%s", query)
    if ( query ):
        qj = json.loads(query)
   
        if ( 'property_id' in qj['params']):
            try:
                p_id = qj['params']['property_id']
            except ValueError:
                app.logger.info("No property id, must specify property id")        
        if ( 'start_date' in qj['params']):
            try:
                l_sd = qj['params']['start_date']
            except ValueError:
                app.logger.info("No start_date, will return all data")

        if ( 'end_date' in qj['params']):
            try:
                l_ed = qj['params']['end_date']
            except ValueError:
                app.logger.info("No end_date, will return all date")
    
    app.logger.info("propertyTransactions2:p_id:%s l_sd:%s l_ed:%s", p_id, l_sd,l_ed)
    qj['user_id']=vh['user_id']
    qj['updatedby']=vh['Updatedby']
    
    if p_id:
        # pid, cid, d1, d2, logger, db)
        O_prop = PMProperty(p_id, l_sd, l_ed, app.logger, O_db)
       
        O_prop.updateFTS(O_db)
        c = O_prop.getTS()
        
        if ( l_format == 'html' ):
            #c = c.style.applymap(pm_utils.color_negative_red).apply(pm_utils.highlight_max)
            #rep = c.to_html()
            rep = (
                    c.style \
                    .applymap(pm_utils.color_negative_red, subset=['debit', 'amount']) \
                    .set_properties(**{'font-size': '9pt', 'font-family': 'Calibri'}) \
                    .bar(subset=['credit', 'amount'], color='lightblue') \
                    .render()
                )
            mtype = 'text/html'
        else:
            rep = c.to_json(orient='table')
            mtype='text/json'       
    else: 
        return ("No Property found for: "+ query)
    
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    
    return response

@app.route("/pcf", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def propertyCF():
    c = pd.DataFrame()
    p_id=""
    c_id=""
    l_sd=""
    l_ed=""
    l_llc = ""
    l_grp = ""
    l_format = 'json'
    mtype='text/json'
    # http://127.0.0.1:5000/pcf?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")  
    l_format = request.args.get("format")
    app.logger.info("property::Query:%s", query)
    if ( query ):
        qj = json.loads(query)
   
        if ( 'property_id' in qj['params']):
            try:
                p_id = qj['params']['property_id']
            except ValueError:
                app.logger.warn("No property id, must specify property id")   
        if ( 'start_date' in qj['params']):
            try:
                l_sd = qj['params']['start_date']
            except ValueError:
                app.logger.warn("No start_date, will return all data")

        if ( 'end_date' in qj['params']):
            try:
                l_ed = qj['params']['end_date']
            except ValueError:
                app.logger.warn("No end_date, will return all date")
    
    if (p_id != "" ):
        O_prop = PMProperty(p_id, l_sd, l_ed, app.logger, O_db)
        app.logger.debug("property info: %s", id)
    
        O_prop.updateFTS(O_db)
        c = O_prop.getSTATS()
        
        if ( l_format == 'html' ):
            rep = c.to_html()
            mtype = 'text/html'
        else:
            rep = c.to_json(orient='table')
            mtype='text/json' 
    else:    
        return ("No data found for: "+ query)
           
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    
    return response

 
@app.route("/pcfa", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def propertyCFA():
    c = pd.DataFrame()
    p_id=""
    l_sd=""
    l_ed=""
    l_pd = "MONTHLY"
    l_format = 'json'
    mtype='text/json'
    # http://127.0.0.1:5000/pcfa?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")  
    l_format = request.args.get("format")
    app.logger.info("property::Query:%s", query)
    if ( query ):
        qj = json.loads(query)
   
        if ( 'property_id' in qj['params']):
            try:
                p_id = qj['params']['property_id']
            except ValueError:
                app.logger.warn("No property id, must specify property id")
        if ( 'period' in qj['params']):
            try:
                l_pd = qj['params']['period']
            except ValueError:
                app.logger.warn("No period, will return MONTHLY data")        
        if ( 'start_date' in qj['params']):
            try:
                l_sd = qj['params']['start_date']
            except ValueError:
                app.logger.warn("No start_date, will return all data")

        if ( 'end_date' in qj['params']):
            try:
                l_ed = qj['params']['end_date']
            except ValueError:
                app.logger.warn("No end_date, will return all date")
    
    if (p_id != "" or l_llc != ""):
        O_prop = PMProperty(p_id, l_sd, l_ed, app.logger, O_db)
        app.logger.debug("property info: %s", id)
    
        O_prop.updateFTS(O_db)
        c = O_prop.getCF()

        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:    
        return ("No data found for: "+ query)
           
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    
    return response
     
@app.route("/parking", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def parking_lot():
    c_pd = pd.DataFrame()
    rep = ""
    
    l_format = 'json'
    mtype='text/json'
    # http://127.0.0.1:5000/pcfa?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")  
    l_format = request.args.get("format")
    app.logger.info("property::Query:%s", query)
    if ( query ):
        qj = json.loads(query)
   
        c_pd = ref_data.get_parking_lot_pd(O_db,app.logger,qj);
      
        if ( l_format == 'html' ):
            rep = c_pd.to_html()
            mtype = 'text/html'            
        else:
            rep = c_pd.to_json(orient='table')
            mtype='text/json'

    else:    
        r = {}
        r['status']='Failure'
        r['message']='Request failed'
        r['code']=1
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'
           
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    
    return response

################## Tenants ##########################
@app.route("/tenantv", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def tenantV():
    # used for public wo page
    p = pd.DataFrame()
    l_format = 'json'
    mtype='text/json'
    rep=""
    user_id=-1;
    
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.info("tenantV: Header verification failed - IGNORED: %s", vh)
    else:
        user_id=vh['user_id']
    
    app.logger.info("/tenantv?")    
    p = ref_data.get_my_tenants_names_pd(O_db, app.logger,'', -1)
    
    if ( l_format == 'html' ):
        rep = p.to_html()
        mtype = 'text/html'            
    else:
        rep = p.to_json(orient='table')
        mtype='text/json'
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response

@app.route("/tenant", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def tenant():
    c = {}
    l_format = 'json'
    mtype='text/json'
    t_id=-1
    l_info='ALL'
    sta=""
    qj = {}
    rep=""
    user_id=-1
    # 127.0.0.1:5000/p?query={%22params%22:{%22id%22:%22123%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    else:
        user_id=vh['user_id']
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("tenant? %s format: %s", query, l_format)
    if ( query ):
        qj = json.loads(query)['params']
        if ( 'tenant_id' in qj):
            try:
                t_id = int(qj['tenant_id'])
            except ValueError:
                app.logger.warn("No tenant id, will return all tenants")
        if ( 'info' in qj):
            try:
                l_info = qj['info']
            except ValueError:
                app.logger.warn("No info, will return all info")
    qj['user_id']=user_id
    qj['navigation']=vh['navigation']
    if ( t_id > 0 ):
        app.logger.debug("tenant::%s", t_id)
        O_t = PMTenant(t_id, qj , app.logger, O_db)
        c = O_t.getTInfo(l_info)
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:
        if ( 'report' in qj and qj['report'] == 'TENANT-PETS' ):
            p = ref_data.get_my_tenants_pet_pd(O_db,app.logger, qj, user_id)
        elif ( 'report' in qj and qj['report'] == 'TENANT-VEHICLES' ):
            p = ref_data.get_my_tenants_vehicle_pd(O_db,app.logger, qj, user_id)
        elif ( 'report' in qj and qj['report'] == 'TENANT-SEARCH' ):
            p = ref_data.search_my_tenants_pd(O_db,app.logger, qj)
        else:
            p = ref_data.get_my_tenants_pd(O_db,app.logger, qj, user_id)
        
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
    pm_user.updateUsage(O_db, app.logger, vh, qj)
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                       
    return response

#################################################################
@app.route("/tenancy", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def tenancy():
    c = {}
    qj = {}
    llc=""
    grp=""
    l_format = 'json'
    mtype='text/json'
    t_id=-1
    tc_id=-1
    p_id=-1
    user_id=-1
    rep=""
    # 127.0.0.1:5000/p?query={%22params%22:{%22id%22:%22123%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.info("tenant: Header verification failed")
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    else:
        user_id=vh['user_id']
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("tenancy?%s format:%s", query, l_format)
    if ( query ):
        qj = json.loads(query)
        if ( 'tenant_id' in qj['params']):
            try:
                t_id=int( qj['params']['tenant_id'])
            except ValueError:
                app.logger.warn("No tenant id, will return all tenancy")
        if ( 'property_id' in qj['params']):
            try:
                p_id = int(qj['params']['property_id'])
            except ValueError:
                app.logger.warn("No property id, will return all tenancy")
        if ( 'tenancy_id' in qj['params']):
            try:
                tc_id = int(qj['params']['tenancy_id'])
            except ValueError:
                app.logger.warn("No tenancy id, will return all tenancy")     

    if ( t_id > 0 or tc_id > 0 or p_id > 0 ):
        app.logger.debug("tenant:%s", t_id)
        O_t = PMTenancy(O_db, app.logger,tc_id,t_id, p_id)
        c = O_t.getTenancyInfo()
        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(c)
            mtype = 'text/html'
        else:
            rep = json.dumps(c)
            mtype='text/json'
    else:
        app.logger.info("QJ:%s", qj)
        cj = qj['params']
        cj['user_id']=user_id
        p = ref_data.get_my_tenancy_pd(O_db,app.logger, cj)
        
        if ( l_format == 'html' ):
            rep = p.to_html()
            mtype = 'text/html'            
        else:
            rep = p.to_json(orient='table')
            mtype='text/json'
       
    app.logger.debug("Tenancy info:%s",rep)
    pm_user.updateUsage(O_db, app.logger, vh, qj)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    if ( 1):  # c or p:
        return response
    else: 
        return ("No Tenant found for: "+ t_id)
###############
@app.route("/tenant_tx", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def tenantTX():
    c = pd.DataFrame()
    qj={};
    t_id=""
    l_sd=""
    l_ed=""
    l_format = 'json'
    mtype='text/json'
    # http://127.0.0.1:5000/pcf?query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    query = request.args.get("query")  
    l_format = request.args.get("format")
    app.logger.info("tenantTX::Query:%s | %s", query, vh)
    
    if ( query ):
        qj = json.loads(query)
   
        if ( 'tenant_id' in qj['params']):
            try:
                t_id = qj['params']['tenant_id']
            except ValueError:
                app.logger.warn("No property id, must specify property id")
        if ( 'start_date' in qj['params']):
            try:
                l_sd = qj['params']['start_date']
            except ValueError:
                app.logger.warn("No start_date, will return all data")

        if ( 'end_date' in qj['params']):
            try:
                l_ed = qj['params']['end_date']
            except ValueError:
                app.logger.warn("No end_date, will return all date")
    
    pm_user.updateUsage(O_db, app.logger, vh, qj['params'])
    if (t_id != "" ):
        O_prop = PMTenant(t_id, qj['params'], app.logger, O_db)
        app.logger.info("tenantTX info: %s", t_id)
    
        O_prop.updateFTS(O_db, l_sd, l_ed)
        c = O_prop.getSTATS()

        if ( l_format == 'html' ):
            rep = c.to_html()
            mtype = 'text/html'
        else:
            rep = c.to_json(orient='table')
            mtype='text/json' 
    else:    
        return ("tenantTX: No data found for: "+ query)
           
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    
    return response

#################################################################
@app.route("/company/<action>", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def company(action):
    c = {}
    l_format = 'json'
    mtype='text/json'
    
    user_id=-1
    rep=""
    # 127.0.0.1:5000/p?query={%22params%22:{%22id%22:%22123%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    else:
        user_id=vh['user_id']
    query = request.args.get("query")
    l_format = request.args.get("format")
    app.logger.info("pm_web.company:%s Format:%s", query, l_format)
    if ( query ):
        qj = json.loads(query)
    qj['user_id']=user_id
    
    app.logger.debug("company info:%s %s", rep, action)
    if ( action in 'info'  ):
        O_t = PMTranche(O_db, app.logger, qj['params']['tranche_id'], qj['params'])
        ret = O_t.getTInfo()
        rep = json.dumps(ret)
    elif ( action == 'list'):
        c = pm_company.getCompanies(O_db, app.logger, qj)
        pm_user.updateUsage(O_db, app.logger, vh, qj['params'])    
        rep = c.to_json(orient='table')
    else:
        c = pm_company.getCompanies(O_db, app.logger, qj)
        pm_user.updateUsage(O_db, app.logger, vh, qj['params'])    
        if ( l_format == 'html' ):
            rep = c.to_html()
            mtype = 'text/html'
        else:
            rep = c.to_json(orient='table')
            mtype='text/json'
    
    pm_user.updateUsage(O_db, app.logger, vh, qj)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
    return response

## pm_tranche ----------------------------
@app.route("/tranche/<action>",methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origin='localhost')    
def tranche(action):

    rep= None
    qj = {}
    l_format = 'json'
    mtype='text/json'
    query=""

    app.logger.info("pm_web.tranche::%s", action)

    #query={%22params%22:{%22id%22:%2220%22,%22group%22:%22WAL%22,%22start_date%22:%222018-10-01%22,%22end_date%22:%222019-12-31%22}}&format=html
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed:%s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    if ( request.method == "POST"):
        query = request.data
    else:
        query = request.args.get("query")
    app.logger.info("tranche::%s",query);
    
    if ( query ):
        qj = json.loads(query)

    app.logger.info("pm_web.tranche:%s", qj)

    qj['params']['user_id']=vh['user_id']
    qj['params']['updatedby']=vh['Updatedby']
    app.logger.info("tranche[%s]:%s",action,qj)

    if ( action in 'info'  ):
        O_t = PMTranche(O_db, app.logger, qj['params']['tranche_id'], qj['params'])
        ret = O_t.getTInfo()
        rep = json.dumps(ret)
    elif ( action == 'list'):
        ret = pm_tranche.getTrancheList(O_db, app.logger, qj['params'])
        rep = ret.to_json(orient='table')
    elif ( action == 'loanlist'):
        ret = pm_tranche.getLoanList(O_db, app.logger, qj['params'])
        rep = ret.to_json(orient='table')
    elif ( action == 'update'):
        ret = pm_tranche.updateTranche(O_db, app.logger, qj['params'])
        rep = json.dumps(ret)
    elif ( action == 'gltx'):
        ret = pm_tranche.getLTTX(O_db, app.logger, qj['params'])
        rep = json.dumps(ret)
    elif ( action == 'gltxs'):
        ret = pm_tranche.getLTTXS(O_db, app.logger, qj['params'])
        rep = json.dumps(ret)
    elif ( action == 'ultx'):
        ret = pm_tranche.updateLTTX(O_db, app.logger, qj['params'])
        rep = json.dumps(ret)
    elif ( action == 'analytics'):
        ret = pm_tranche.getTrancheAnalytics(O_db, app.logger, qj['params'])
        rep = ret.to_json(orient='table')
    else:
        r ={}
        r['status']='Failure'
        r['message']='Request failed'
        r['tranche_id']='-1'
        r['code']=1
        if ( l_format == 'html' ):
            rep = r
            mtype = 'text/html'            
        else:
            rep = json.dumps(r)
            mtype='text/json'

    pm_user.updateUsage(O_db, app.logger, vh, qj)
    app.logger.debug("Tranche Response: %s", rep)    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        
                           
    return response 

@app.route("/tranche_tx", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def tranche_tx():
    c = {}
    l_format = 'json'
    mtype='text/json'
    
    user_id=-1
    rep=""
    # 127.0.0.1:5000/p?query={%22params%22:{%22id%22:%22123%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    else:
        user_id=vh['user_id']
    query = request.args.get("query")
    l_format = request.args.get("format")
    
    if ( query ):
        qj = json.loads(query)
    qj['params']['user_id']=user_id
    app.logger.info("pm_web.tranche:%s", qj)
    if ( 'tranche_id' in qj['params']):
        
        O_t = PMTranche(O_db, app.logger, qj['params']['tranche_id'], qj['params'])
        
        O_t.updateTS(O_db)
        c = O_t.getTS()
        app.logger.info("pm_web.tranche2:%s", c)
        #st = O_cat.getSTATS('amount')
        x={}
        if( c is None ):
            x['code']=1
            x['data']=''
            x['message']='No data found'
            x['success']='OK'
            
        else:
            x = c.to_json(orient='table')
        
        app.logger.info("pm_web.tranche3:%s", x)

        if ( l_format == 'html' ):
            rep = pm_utils.dict2Html(x)
            mtype = 'text/html'
        else:
            rep = x
            mtype='text/json'
    else:
        c['code']=-1;
        c['message']="No tranche ID"
        if ( l_format == 'html' ):
            rep = c.to_html()
            mtype = 'text/html'
        else:
            rep = c.to_json(orient='table')
            mtype='text/json'
    
    app.logger.debug("tranche info:%s", rep)
    
    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )        

    pm_user.updateUsage(O_db, app.logger, vh, qj)
    return response

################## Category Functions
@app.route("/c", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def categoryList():
    c_id=""
    l_type = ""
    l_format="json"
    mtype='text/json'
    qj = {}
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")
    if ( query ):
        qj = json.loads(query)

    l_format = request.args.get("format")
    l_type = request.args.get("type")
    app.logger.info("c?%s %s %s", query, l_format, l_type)
    
    c = ref_data.get_my_categories_pd(O_db,app.logger, l_type)
    
    if ( c.empty ):
        r ={}
        r['status']='FAILED'
        r['code']='1'       
        r['message']='Categories could nto be fetched'      
        rep = json.dumps(r)
    else:
        if ( l_format == 'html' ):
            rep = c.to_html()
            mtype = 'text/html'            
        else:
            rep = c.to_json(orient='table')
            mtype='text/json'

    response = app.response_class(
        response=rep,
        status=200,
        mimetype=mtype
    )                          
    pm_user.updateUsage(O_db, app.logger, vh, qj)
    return response

@app.route("/ctr", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def categoryTransactions():
    c = pd.DataFrame()
    # 127.0.0.1:5000/ctr?query={%22params%22:{%22id%22:%228%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")
    qj = json.loads(query)
    c_id = 0
    l_company=""
    p_id=-1
    t_id=-1
    l_sd = ""
    l_ed = ""
    app.logger.debug("Category info: %s", query)
    if ( query):
        if ( 'category_id' in qj['params']):
            try:
                c_id = qj['params']['category_id']
            except ValueError:
                app.logger.info("No property id, will return all data")
        if ( 'company_id' in qj['params']):
            try:
                l_company = qj['params']['company_id']
            except ValueError:
                app.logger.info("No start_date, will return all data")
        if ( 'start_date' in qj['params']):
            try:
                l_sd = qj['params']['start_date']
            except ValueError:
                app.logger.info("No start_date, will return all data")
        if ( 'end_date' in qj['params']):
            try:
                l_ed = qj['params']['end_date']
            except ValueError:
                app.logger.info("No end_date, will return till date")
        if ( 'property_id' in qj['params']):
            try:
                p_id = int(qj['params']['property_id'])
            except ValueError:
                app.logger.info("No property_id, will return all properties")
        if ( 'tenant_id' in qj['params']):
            try:
                t_id = int(qj['params']['tenant_id'])
            except ValueError:
                app.logger.info("No tenant_id, will return all tenant")
    
    if ( c_id > -1 ):
        O_cat = PMCategory(O_db, c_id,l_sd, l_ed, app.logger)
    app.logger.debug("Category info: LLC[%s] P[%s] T[%s]", l_company, p_id, t_id)
    if ( p_id > 0 ):
        O_cat.updateFTS(O_db, p_id)
    elif( t_id > 0 ):
        O_cat.updateFTS2(O_db, t_id)
    else:
        O_cat.updateFTS3(O_db, l_company)
    c = O_cat.getTS()
    #st = O_cat.getSTATS('amount')
    x={}
    if( c is None ):
        x['code']=1
        x['data']=''
        x['message']='No data found'
        x['success']='OK'
        
    else:
        x = c.to_json(orient='table')
    
    app.logger.info(x)
    #x.add["stats"]=st;
    #x += c.to_json(path_or_buf=None, orient='table', date_format=None, double_precision=10, force_ascii=True, date_unit='ms', default_handler=None, lines=False, compression='infer', index=True)
    
    response = app.response_class(
        response=x,
        status=200,
        mimetype='application/json'
    )        
    
    return response
    

    #return render_template("country-list.html", country=country)
@app.route("/ccf", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def categoryCF():
    c = pd.DataFrame()
    # 127.0.0.1:5000/ccf?query={%22params%22:{%22start date%22:%222019-04-01%22, %22end date%22:%222019-04-30%22}}
    c_id=""
    l_sd=""
    l_ed=""
    l_format = 'json'
    mtype='text/json'
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response
    query = request.args.get("query")  
    l_format = request.args.get("format")
    app.logger.info("tenantTX::Query:%s", query)
    if ( query ):
        qj = json.loads(query)
   
        if ( 'category_id' in qj['params']):
            try:
                c_id = qj['params']['category_id']
            except ValueError:
                app.logger.info("No category id, must specify category id")
        if ( 'start_date' in qj['params']):
            try:
                l_sd = qj['params']['start_date']
            except ValueError:
                app.logger.info("No start_date, must specify start_date")
        if ( 'end_date' in qj['params']):
            try:
                c_id = qj['params']['end_date']
            except ValueError:
                app.logger.info("No end_date, must specify end_date")                
    
    O_cat = PMCategory(c_id, None, None, l_sd, l_ed, None)
    app.logger.info("Category info: %s l_sd:%s l_ed:%s l_format:%s", c_id, l_sd, l_ed, l_format)
    O_cat.updateTS(O_db)
    c = O_cat.getTS()
    if ( l_format == 'html' ):
        x = c.to_html()
        mtype = 'text/html'
    else:
        x = c.to_json(orient='table')
        mtype='text/json'
    
    response = app.response_class(
        response=x,
        status=200,
        mimetype=mtype
    )        
    if c.count:
        return response
    else: 
        return ("No transactions found for: "+ c_id)

@app.route("/pmcf", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def pmCF():
    c = pd.DataFrame()
    t_dict = {}
    l_format = 'json'
    mtype='text/json'
    r_type=""
    option = 1
    # 127.0.0.1:5000/pmcf?format=json&query={%22params%22:{%22start date%22:%222019-01-01%22, %22end date%22:%222019-08-31%22, %22company%22:%22AHPA%22}}
    # read the posted values from the UI
    vh = pm_user.verifyRequest(O_db, app.logger, request.headers)
    if ( vh['code'] != 0 ):
        app.logger.error("Header verification failed: %s", vh)
        rep = json.dumps(vh)
        response = app.response_class(
            response=rep,
            status=200,
            mimetype=mtype
        )        
        return response

    query = request.args.get("query")
    
    l_format = request.args.get("format")
        
    if ( query != ''):
        app.logger.info("pmCF:"+str(query))
        qj = json.loads(query)
        if ( 'report' in qj['params']):   
            try:
                r_type = qj['params']['report']
            except ValueError:
                app.logger.info("No report, will return all data")

    #l_format = 'html'
    if (qj['params']):
        O_pmcf = PMCashflow(app.logger,O_db, qj['params'])
    app.logger.debug("PMCF info:%s", r_type)
    if ( r_type == "TAX" ):
        O_pmcf.updateTaxTS(O_db)
        c = O_pmcf.getTS()
    elif( r_type == "PCF" ):
        O_pmcf.updatePCF(O_db)
        c = O_pmcf.getTS()    
        option = 1
    elif( r_type == "PROJECT" ):
        O_pmcf.updateProjectTS(O_db)
        c = O_pmcf.getTS()    
        option = 1
    else:
        O_pmcf.updateTS(O_db)
        c = O_pmcf.getTS()
    
    if ( l_format == 'html'):
        if ( option == 2 ):
            x = pm_utils.dict2Html(t_dict)
        else:
            x = c.to_html()
        mtype = 'text/html'
    else:
        if ( option == 2 ):
            x = json.dumps(t_dict)
        else:
            x = c.to_json(orient='table')
        mtype='text/json'
        
    response = app.response_class(
        response=x,
        status=200,
        mimetype=mtype
    )        

    return response
################### payments
@app.route("/payment", methods=['POST','PUT','GET'])
@cross_origin(origin='localhost')
def payment():
    t_dict = {}
    l_format = 'json'
    mtype='text/json'
    idt=""
    idv=-1
    c_id=-1

    # 127.0.0.1:5000/payment?format=json&query={%22params%22:{%22start date%22:%222019-01-01%22, %22end date%22:%222019-08-31%22, %22company%22:%22AHPA%22}}
    # read the posted values from the UI
    
    query = request.args.get("query")
    
    l_format = request.args.get("format")
        
    if ( query != ''):
        app.logger.info("payments:%s",query)
        qj = json.loads(query)
        if ( 'company_id' in qj['params']):   
            c_id = qj['params']['company_id']
        if ( 'id_value' in qj['params']):   
            idv = qj['params']['id_value']
        if ( 'id_type' in qj['params']):   
            idt = qj['params']['id_type']
            
    app.logger.info("Payments:%s", qj)
    if (qj['params']):
        t_dict = pm_company.getCompany(O_db, app.logger, qj['params'])
        
    if ( l_format == 'html'):
        x = pm_utils.dict2Html(t_dict)
        mtype = 'text/html'
    else:
        x = json.dumps(t_dict)
        mtype='text/json'
        
    response = app.response_class(
        response=x,
        status=200,
        mimetype=mtype
    )        

    return response

#        
## 0.0.0.0 implies localhos
if __name__ == "__main__":
#   app.run(host='0.0.0.0',threaded=True)  
    server_port = 7000
    config_type = platform.system().lower()        
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-m')
    parser.add_argument('-c')
    args = parser.parse_args()
    mode = "dev"
    hc_config = "NA"
    foo = args.c
    if ( foo != None ):
        hc_config = foo
    if ( hc_config == 'NA'):
        hc_config ="./files/pm-conf.json"

    foo = args.m
    if ( foo != None ):
        mode = foo
        config_type += "-" + mode
    else:
        mode = ""
    hc_home = os.environ.get('HC_HOME','NA')
    
    today =  datetime.today()
    ts=today.strftime('%Y%m%d%H%M')  

    CONFIG = utils.pm_conf.read_conf_from_file(hc_config, config_type)

    if ( 'allowed_extensions' in CONFIG ):
        ALLOWED_EXTENSIONS = CONFIG["allowed_extensions"]
    app.config['UPLOAD_FOLDER'] = CONFIG["upload_folder"]
    app.config['LOGO_PRINT'] = CONFIG["logo_print"]    
    app.config['LOGO_HTML'] = CONFIG["logo_html"]    
    app.config['PRINT_SERVER'] = CONFIG["print_server"]    
    app.config['LOG_DIR'] = CONFIG["log_dir"]
    app.config['LOG_FILE'] = CONFIG["log_file"]
    app.config['HP_SUPPORT_EMAIL'] = 'support@himalayaproperties.org'

    log_dir = CONFIG["log_dir"]
    server_port = CONFIG["server_port"]
    LOG_FILE = log_dir + '/'+ CONFIG["log_file"].replace('TS',ts)
    LOG_FORMAT = "%(thread)d|%(levelname)s|%(asctime)s|%(filename)s|%(funcName)s|L:%(lineno)d|%(message)s"

    file_handler = logging.FileHandler(filename=LOG_FILE)
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    app.logger = logging
    #app.logger.basicConfig(format=LOG_FORMAT, filename=LOG_FILE,level=logging.DEBUG)
    #app.logger.basicConfig(format=LOG_FORMAT, level=logging.DEBUG, stream=sys.stdout)
    app.logger.basicConfig(format=LOG_FORMAT, level=logging.DEBUG, handlers=handlers)

    app.logger.info("========= HP Server started ==========")
    app.logger.info("OS: %s  Platform:%s Config:%s", os.name, platform.system(), hc_config)    
   

    O_db = PMDB(
        CONFIG["db"]["host"],
        int(CONFIG["db"]["port"]),
        CONFIG["db"]["user"],
        CONFIG["db"]["pass"],
        CONFIG["db"]["schema"],
        app.logger
    )
#    # TODO make debug mode configurable

    app.run(host='0.0.0.0',port=server_port, threaded=True, debug=True)
#    app.run()
#   
#
#
