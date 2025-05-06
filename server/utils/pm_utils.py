# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 22:38:40 2020

@author: ppare
"""

import pandas as pd


# Properties
def dict2Html(d):
    
    html = ""
    
    for x in d:
        #print(x, " value:", d[x])
        html += "<tr><td>"+str(x)+"</td><td>"
        if ( d[x] != None):
            html += str(d[x]) +"</td></tr>"
        else:
            html += "&nbsp;</td></tr>"
    html = "<table>" + html + "</table>"
    return html

def highlight_max(data, color='yellow'):
    '''
    highlight the maximum in a Series or DataFrame
    '''
    attr = 'background-color: {}'.format(color)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data.max()
        return [attr if v else '' for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data.max().max()
        return pd.DataFrame(np.where(is_max, attr, ''),
                            index=data.index, columns=data.columns)
        
def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color



