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
"""Provider tales expression registrations

$Id$
"""
__docformat__ = 'restructuredtext'
import zope.interface
import zope.component
from zope.component.interfaces import ISiteManager
from zope.tales import expressions

from zope.interface.declarations import providedBy
from zope.contentprovider import interfaces, manager


def getRegion(str):
    """Get a region from the string.

    This function will create the dummy region implementation as well.
    """
    region = zope.component.queryUtility(interfaces.IRegion, name=str)
    if region is None:
        raise interfaces.ViewletRegionLookupError(
            'Viewlet region interface not found.', str)
    return region


def getRegionFieldData(region, context):
    """Get a dictionary of values for the region fields."""
    data = {}
    for name, field in zope.schema.getFields(region).items():
        data[name] = context.vars.get(name, field.default)
    return data


class TALESProvidersExpression(expressions.StringExpr):
    """Collect content provider via a TAL namespace."""

    zope.interface.implements(interfaces.ITALESProvidersExpression)

    def __call__(self, econtext):
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # get the region from the expression
        region = getRegion(self._s)

        cpManager = None
        res = []
        iface = interfaces.IContentProviderManager
        objs = (context, request, view)
        # we have to use the lookup method because region is an interface!
        lookup = ISiteManager(context).adapters.lookup
        cpManagerClass = lookup(map(providedBy, objs)+[region], iface, name='')
        if cpManagerClass is not None:
            cpManager = cpManagerClass(context, request, view, region)
            
        if cpManager is None:
            cpManager = manager.DefaultContentProviderManager(
                context, request, view, region)

        providers = cpManager.values()
        #providers = cpManager.values()

        # Insert the data gotten from the context
        data = getRegionFieldData(region, econtext)
        for provider in providers:
            provider.__dict__.update(data)

        return providers


class TALESProviderExpression(expressions.StringExpr):
    """Collects a single content provider via a TAL namespace."""

    zope.interface.implements(interfaces.ITALESProviderExpression)

    def __init__(self, name, expr, engine):
        if not '/' in expr:
            raise KeyError('Use `iface/viewletname` for defining the viewlet.')

        parts = expr.split('/')
        if len(parts) > 2:
            raise KeyError("Do not use more then one / for defining iface/key.")

        # get interface from key
        self._iface = parts[0]
        self._name = parts[1]

    def __call__(self, econtext):
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # get the region from the expression
        region = getRegion(self._iface)

        # Find the content provider
        cpManager = None
        res = []
        iface = interfaces.IContentProviderManager
        objs = (context, request, view)
        # we have to use the lookup method because region is an interface!
        lookup = ISiteManager(context).adapters.lookup
        cpManagerClass = lookup(map(providedBy, objs)+[region], iface, name='')
        if cpManagerClass is not None:
            cpManager = cpManagerClass(context, request, view, region)
            
        if cpManager is None:
            cpManager = manager.DefaultContentProviderManager(
                context, request, view, region)

        provider = cpManager.__getitem__(self._name)
        #provider = cpManager[self._name]

        # Insert the data gotten from the context
        data = getRegionFieldData(region, econtext)
        provider.__dict__.update(data)

        return provider()
