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
"""Content provider interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
from zope.tales import interfaces
from zope.app.publisher.interfaces import browser


class IContentProvider(browser.IBrowserView):
    """A piece of content to be shown on a page.

    Objects implementing this interface are providing HTML content when they
    are called. It is up to the implementation to decide how to lookup
    necessary data to complete the job.

    Content Providers are discriminated by three components: the context, the
    request and the view. This allows great control over the selection of the
    provider.
    """

    view = zope.interface.Attribute(
        """The View

        The view is the third discriminator of the content provider. It allows
        that the content can be controlled for different views.
        """)

    def __call__(*args, **kw):
        """ Return the content provided by this content provider.
        """

class IContentProviderType(zope.interface.interfaces.IInterface):
    """Type interface for content provider types (interfaces derived from
       IContentProvider).
    """

class ITALNamespaceData(zope.interface.interfaces.IInterface):
    """A type interface that marks an interface as a TAL data specification.

    All fields specified in an interface that provides `ITALNamespaceData`
    will be looked up in the TAL context and stored on the content provider. A
    content provider can have multiple interfaces that are of this type.
    """

class ContentProviderLookupError(zope.component.ComponentLookupError):
    """No content provider was found."""


class ITALESProviderExpression(interfaces.ITALESExpression):
    """Return the HTML content of the named provider.

    To call a content provider in a view use the the following syntax in a page
    template::

      <tal:block replace="structure provider:provider.name">

    The content provider is looked up by the (context, request, view) objects
    and the name (`provider.name`).
    """
