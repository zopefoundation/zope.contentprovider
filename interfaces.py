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
"""Viewlet interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.schema
from zope.tales import interfaces

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.publisher.interfaces.browser import IBrowserView


class RegionLookupError(zope.component.ComponentLookupError):
    """Region object not found."""


class IRegion(zope.interface.interfaces.IInterface):
    """Type interface for viewlet regions.

    Region interfaces specify the environment variables that are available to
    the IContentProvider. How those variables are provided is up to the 
    implementation.
    """


class IContentProvider(IBrowserView):
    """A piece of content of a page.

    Content provider are objects that can fill the region specified in a 
    page, most often page templates. They are selected by the context, request 
    and view. All viewlets of a particular region must also provide the region
    interface.
    """

    view = zope.interface.Attribute(
        'The view the viewlet is used in.')

    weight = zope.schema.Int(
        title=_(u'weight'),
        description=_(u"""
            Key for sorting viewlets if the viewlet collector is supporting
            this sort mechanism."""),
        required=False,
        default=0)


class IContentProviderManager(zope.interface.Interface):
    """An object that provides access to the viewlets.

    The viewlets are of a particular context, request and view configuration
    are accessible via a particular manager instance. Viewlets are looked up
    by the region they appear in and the name of the viewlet.
    """

    context = zope.interface.Attribute(
        'The context of the view the viewlet appears in.')

    view = zope.interface.Attribute(
        'The view the viewlet is used in.')

    request = zope.interface.Attribute(
        'The request of the view the viewlet is used in.')

# TODO: implement dummy object providing the region or lookup hook
#    region = zope.interface.Attribute(
#        'The request of the view the viewlet is used in.')

    def values(region):
        """Get all available viewlets of the given region.

        This method is responsible for sorting the viewlets as well.
        """

    def __getitem__(self, name, region):
        """Get a particular viewlet of a region selected by name."""


class ITALESProvidersExpression(interfaces.ITALESExpression):
    """TAL namespace for getting a list of viewlets.

    To call viewlets in a view use the the following syntax in a page
    template::

      <tal:block repeat="viewlet viewlets:path.to.my.IRegion">
        <tal:block replace="structure viewlet" />
      </tal:block>

    where ``path.to.my.IRegion`` is a region object that provides
    ``viewlet.interfaces.IRegion``.
    """


class ITALESProviderExpression(interfaces.ITALESExpression):
    """TAL namespace for getting a single viewlet.

    To call a named viewlet in a view use the the following syntax in a page
    template::

      <tal:block replace="structure viewlet:path.to.my.IRegion/name" />

    where ``path.to.my.IRegion`` is a region object that provides
    ``viewlet.interfaces.IRegion`` and ``name`` is the name of the page
    template.
    """
