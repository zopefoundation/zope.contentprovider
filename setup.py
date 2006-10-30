##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for zope.contentprovider package

$Id$
"""

import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.contentprovider',
      version='3.4-dev',
      url='http://svn.zope.org/zope.contentprovider',
      license='ZPL 2.1',
      description='Zope contentprovider',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="This package provides a framework to"
                       "develop componentized Web GUI applications."
                       "Instead of describing the content of a page"
                       "using a single template or static system of"
                       "templates and METAL macros, content provider"
                       "objects are dynamically looked up based on"
                       "the setup/configuration of the application.",

      packages=['zope',
                'zope.contentprovider'],
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing',
                       'zope.security',
                       'zope.app.pagetemplate',
                       'zope.app.testing'],
      install_requires=['zope.interface',
                        'zope.component',
                        'zope.publisher',
                        'zope.schema',
                        'zope.tales'],
      include_package_data = True,

      zip_safe = False,
      )
