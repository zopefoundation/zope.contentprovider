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
"""content provider interfaces

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
    """Type interface for content provider regions.

    Region interfaces specify the environment variables that are available to
    the IContentProvider. How those variables are provided is up to the 
    implementation.
    """


class IContentProvider(zope.interface.Interface):
    """A piece of content to be shown on a page.

    Content provider are objects that can fill the region specified in a 
    page, most often page templates. They are selected by the context, request 
    and view. All content providers of a particular region must also provide
    the corresponding region interface.
    """

    weight = zope.schema.Int(
        title=_(u'weight'),
        description=_(u"""
            Key for sorting content providers if the content provider
            manager is supporting this sort mechanism."""),
        required=False,
        default=0)

    def __call__(*args, **kw):
        """ Return the content provided by this content provider.
        """


class IContentProviderManager(zope.interface.Interface):
    """An object that provides access to the content providers.

    The content providers are of a particular context, request and view configuration
    are accessible via a particular manager instance. content providers are looked up
    by the region they appear in and the name of the content provider.
    """

    context = zope.interface.Attribute(
        'The context of the view the provider manager adapts to.')

    view = zope.interface.Attribute(
        'The view the provider manager adapts to.')

    request = zope.interface.Attribute(
        'The request the provider manager adapts to.')

    region = zope.interface.Attribute(
        'An interface providing IRegion that specifies the region the '
        'provider manager is responsible for.')

    def values(region):
        """Get all available content providers of the given region.

        This method is responsible for sorting the providers as well.
        """

    def __getitem__(self, name, region):
        """Get a particular content provider of a region selected by name."""


class ITALESProvidersExpression(interfaces.ITALESExpression):
    """TAL namespace for getting a list of content providers.

    To call content providers in a view use the the following syntax in a page
    template::

      <tal:block repeat="content providers:path.to.my.IRegion">
        <tal:block replace="structure content" />
      </tal:block>

    where ``path.to.my.IRegion`` is a region object that provides
    ``contentprovider.interfaces.IRegion``.
    """


class ITALESProviderExpression(interfaces.ITALESExpression):
    """TAL namespace for getting a single content provider.

    To call a named content provider in a view use the the following syntax
    in a page template::

      <tal:block replace="structure provider:path.to.my.IRegion/name" />

    where ``path.to.my.IRegion`` is a region object that provides
    ``contentprovider.interfaces.IRegion`` and ``name`` is the name of the page
    template.
    """
