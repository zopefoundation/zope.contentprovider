##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Content provider tests

$Id$
"""
__docformat__ = 'restructuredtext'
import os.path
import unittest
from zope.component import eventtesting
from zope.testing import doctest, cleanup
from zope.testing.doctest import DocFileSuite

counter = 0
mtime_func = None

def setUp(test):
    cleanup.setUp()
    eventtesting.setUp()

    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

    # Make sure we are always reloading page template files ;-)
    global mtime_func
    mtime_func = os.path.getmtime
    def number(x):
        global counter
        counter += 1
        return counter
    os.path.getmtime = number


def tearDown(test):
    cleanup.tearDown()
    os.path.getmtime = mtime_func
    global counter
    counter = 0

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
