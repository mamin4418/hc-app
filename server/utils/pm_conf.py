# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 14:26:13 2019

@author: ppare
"""

import json


def read_conf_from_file(config_file, os_name):
    cf = {}

    config_data = {}
    print("pm_conf:1=", config_file, os_name)
    
    with open(config_file) as f:
        config_data = json.load(f)
    
    if ( os_name in config_data):
        cf=config_data[os_name]
    else:
        cf=config_data['windows']
        
    print("pm_conf:2=", cf)
    
    return cf