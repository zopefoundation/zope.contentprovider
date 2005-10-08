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

import zope.component
import zope.interface
import zope.schema
from zope.tales import expressions

from zope.contentprovider import interfaces


def addTALNamespaceData(provider, context):
    """Add the requested TAL attributes to the provider"""
    data = {}

    for interface in zope.interface.providedBy(provider):
        if interfaces.ITALNamespaceData.providedBy(interface):
            for name, field in zope.schema.getFields(interface).items():
                data[name] = context.vars.get(name, field.default)

    provider.__dict__.update(data)


class TALESProviderExpression(expressions.StringExpr):
    """Collect content provider via a TAL namespace."""

    zope.interface.implements(interfaces.ITALESProviderExpression)

    def __call__(self, econtext):
        name = super(TALESProviderExpression, self).__call__(econtext)
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # Try to look up the provider.
        provider = zope.component.queryMultiAdapter(
            (context, request, view), interfaces.IContentProviderManager, name)

        # Provide a useful error message, if the provider was not found.
        if provider is None:
            raise interfaces.ContentProviderLookupError(name)

        # Insert the data gotten from the context
        addTALNamespaceData(provider, econtext)

        return provider
