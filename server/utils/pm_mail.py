# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 21:23:32 2020

@author: ppare
"""
import flask
from flask import json, render_template
from datetime import timedelta, datetime
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email.utils import formataddr
from email.header import Header
from email import encoders 
import re
import utils.pm_print as pm_print
   
sender_address = 'SET SENDER ADDRESS HERE'
sender_pass = 'SET PASSWORD HERE'
smtp_server='smtp.gmail.com'
smtp_port=587
pdf_logo = 'file:///C:/Users/ppare/Development/HC/files/HC-3.png'
html_logo = './files/HC-3.png'

def sendWONotification(app, db, core):
    app.logger.debug("pm_mail:sendWONotification:%s", core)

def sendApplicationNotification(app, O_db, core):
    app.logger.debug("pm_mail:sendApplicationNotification:%s", core)
    

def sendUserSignUpNotification(app, core):
    app.logger.debug("pm_mail:sendUserSignUpNotification:%s", core)
    
def passwordResetEmail(app, qj):
    core={}
    app.logger.debug("pm_mail.passwordResetMail.0:%s", qj)
    
    

def sendMail(app, qj):
    app.logger.info("pm_mail.sendMail.0:%s", qj)
   

def sendMailWAttachment(app, qj):
    app.logger.info("pm_mail.sendMailWAttachment.0:%s", qj)
    

def verifyEmailAddress(app, addressToVerify):
    #regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
    regex = r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
    
    ret = 0
    if ( addressToVerify == None ):
        return -1
    #app.logger.debug("verifyEmailAddress: verifying: %s", addressToVerify)
    # Syntax check
    match = re.match(regex, addressToVerify.lower().rstrip())
    if match == None:
        print('Bad Syntax')
        ret = -1
    
    app.logger.debug("verifyEmailAddress: verifying:[%s][%s]",ret,addressToVerify)
    return ret
