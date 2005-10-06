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
"""Viewlet tales expression registrations

$Id$
"""
__docformat__ = 'restructuredtext'
import zope.interface
import zope.component
from zope.tales import expressions

from zope.app.viewlet import interfaces, manager


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


class TALESViewletsExpression(expressions.StringExpr):
    """Collect viewlets via a TAL namespace called `viewlets`."""

    zope.interface.implements(interfaces.ITALESViewletsExpression)

    def __call__(self, econtext):
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # get the region from the expression
        region = getRegion(self._s)

        # Find the viewlets
        viewletManager = zope.component.queryMultiAdapter(
            (context, request, view), interfaces.IViewletManager)
        if viewletManager is None:
            viewletManager = manager.DefaultViewletManager(
                context, request, view)

        viewlets = viewletManager.getViewlets(region)

        # Insert the data gotten from the context
        data = getRegionFieldData(region, econtext)
        for viewlet in viewlets:
            viewlet.__dict__.update(data)

        return viewlets


class TALESViewletExpression(expressions.StringExpr):
    """Collects a single viewlet via a TAL namespace called viewlet."""

    zope.interface.implements(interfaces.ITALESViewletExpression)

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

        # Find the viewlets
        viewletManager = zope.component.queryMultiAdapter(
            (context, request, view), interfaces.IViewletManager)
        if viewletManager is None:
            viewletManager = manager.DefaultViewletManager(
                context, request, view)

        viewlet = viewletManager.getViewlet(self._name, region)

        # Insert the data gotten from the context
        data = getRegionFieldData(region, econtext)
        viewlet.__dict__.update(data)

        return viewlet()
