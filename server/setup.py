# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 23:36:20 2020

@author: ppare
"""
from distutils.core import setup

setup(name='hc-server',
      version='1.0',
      description='Python Distribution Utilities',
      author='Paresh Patel',
      author_email='paresh@acudatascience.com',
      url='https://www.himalayaproperties.org',
      packages=['distutils', 'distutils.command'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: API',
          'Environment :: Web Environment',
          'Intended Audience :: End Users , Browsers',
          'Intended Audience :: Property Managers',
          'License :: OSI Approved :: Restricted - private use only for a fee',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Communications :: Email',
          'Topic :: Office/Business',
          'Topic :: Software Development :: Bug Tracking',
          ],
      )