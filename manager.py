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
"""Viewlet implementation

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.security

from zope.viewlet import interfaces


class DefaultContentProviderManager(object):
    """The Default ContentProvider Manager

    This implementation looks up all viewlets from the adapter registry and
    sorts the viewlet list by weight. Viewlets that are not accessible in the
    context of this request will also be filtered.
    """
    zope.interface.implements(interfaces.IViewletManager)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view


    def values(self, region):
        """See zope.app.viewlet.interfaces.IViewletManager"""
        # Find all viewlets for this region
        viewlets = zope.component.getAdapters(
            (self.context, self.request, self.view), region)
        # Sort out all viewlets that cannot be accessed by the principal
        viewlets = [viewlet for name, viewlet in viewlets
                    if zope.security.canAccess(viewlet, '__call__')]
        # Sort the viewlets by weight.
        viewlets.sort(lambda x, y: cmp(x.weight, y.weight))

        return viewlets


    def __getitem__(self, name, region):
        """See zope.app.viewlet.interfaces.IViewletManager"""
        # Find the viewlet
        viewlet = zope.component.queryMultiAdapter(
            (self.context, self.request, self.view), region, name=name)

        # If the viewlet was not found, then raise a lookup error
        if viewlet is None:
            raise zope.component.interfaces.ComponentLookupError(
                'No viewlet with name `%s` found.' %name)

        # If the viewlet cannot be accessed, then raise an unauthorized error
        if not zope.security.canAccess(viewlet, '__call__'):
            raise zope.security.interfaces.Unauthorized(
                'You are not authorized to access the viewlet '
                'called `%s`.' %name)

        # Return the rendered viewlet.
        return viewlet
