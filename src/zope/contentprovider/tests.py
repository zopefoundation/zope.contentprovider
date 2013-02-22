##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""
import doctest
import os.path
import re
import unittest

from zope.component import eventtesting
from zope.testing import cleanup, renormalizing

counter = 0
mtime_func = None

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    # Python 3 adds module name to exceptions.
    (re.compile("zope.contentprovider.interfaces.UpdateNotCalled"),
     r"UpdateNotCalled"),
    (re.compile("zope.contentprovider.interfaces.ContentProviderLookupError"),
     r"ContentProviderLookupError"),
    ])


def setUp(test):
    cleanup.setUp()
    eventtesting.setUp()

    from zope.browserpage.metaconfigure import registerType
    from zope.contentprovider import tales
    registerType('provider', tales.TALESProviderExpression)

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
        doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                checker=checker,
                globs = {'__file__': os.path.join(
                        os.path.dirname(__file__), 'README.txt')}
            ),
        ))
