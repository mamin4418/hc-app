 
import errno, os

import pandas as pd

from datetime import datetime

from dateutil.parser import parse

from mw_error_codes import err_code

import json

 

def getdirsize(folder):

    total_size = os.path.getsize(folder)

    for item in os.listdir(folder):

        itempath = os.path.join(folder, item)

        if os.path.isfile(itempath):

            total_size += os.path.getsize(itempath)

        elif os.path.isdir(itempath):

            total_size += getdirsize(itempath)

    return total_size

 
def dirtree_to_dict(db,logger,path):

    logger.debug("Get_directory_tree [%s]",path)

    try:

        d=dict()

        if os.path.isdir(path):

            d = {'name': os.path.basename(path)}

            d['modified_date'] = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')

            d['created_date'] = datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d %H:%M:%S')

            d['last_access'] = datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d %H:%M:%S')

            d['type'] = "directory"

            d['path'] = path

            d['children'] = [dirtree_to_dict(db,logger,os.path.join(path,x)) for x in os.listdir(path)]

            d['size'] = getdirsize(path)/1024

        else:

            len_filename = os.path.basename(path).split(".")

            if len(len_filename) >1 :

                d['name'] = os.path.basename(path)

                d['modified_date'] = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')

                d['created_date'] = datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d %H:%M:%S')

                d['last_access'] = datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d %H:%M:%S')

                d['type'] = "file"

                d['size'] =os.path.getsize(path)/1024

        return d

    except Exception as e:

        return {'status': "failure", 'error': err_code.get_vendor_information_tree_unexpected_error + str(e), 'data': None, 'code': 1}

 


 

 