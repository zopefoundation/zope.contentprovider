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
"""Viewlet metadconfigure

$Id$
"""
__docformat__ = 'restructuredtext'

import os

from zope.security import checker

from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface, classImplements
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.app.component.interface import provideInterface
from zope.app.component import metaconfigure
from zope.app.publisher.browser import viewmeta
from zope.app.publisher.interfaces.browser import IBrowserView

from zope.app.viewlet import viewlet, interfaces


def viewletDirective(_context, name, permission, region,
                     for_=Interface, layer=IDefaultBrowserLayer,
                     view=IBrowserView,
                     class_=None, template=None, attribute='__call__', weight=0,
                     allowed_interface=None, allowed_attributes=None):

    required = {}

    # Get the permission; mainly to correctly handle CheckerPublic.
    permission = viewmeta._handle_permission(_context, permission)

    # Either the class or template must be specified.
    if not (class_ or template):
        raise ConfigurationError("Must specify a class or template")

    # Make sure that all the non-default attribute specifications are correct.
    if attribute != '__call__':
        if template:
            raise ConfigurationError(
                "Attribute and template cannot be used together.")

        # Note: The previous logic forbids this condition to evere occur.
        if not class_:
            raise ConfigurationError(
                "A class must be provided if attribute is used")

    # Make sure that the template exists and that all low-level API methods
    # have the right permission.
    if template:
        template = os.path.abspath(str(_context.path(template)))
        if not os.path.isfile(template):
            raise ConfigurationError("No such file", template)
        required['__getitem__'] = permission

    # Make sure the has the right form, if specified.
    if class_:
        if attribute != '__call__':
            if not hasattr(class_, attribute):
                raise ConfigurationError(
                    "The provided class doesn't have the specified attribute "
                    )
        if template:
            # Create a new class for the viewlet template and class.
            new_class = viewlet.SimpleViewletClass(
                template, bases=(class_, ), weight=weight)
        else:
            if not hasattr(class_, 'browserDefault'):
                cdict = {
                    'browserDefault':
                    lambda self, request: (getattr(self, attribute), ())
                    }
            else:
                cdict = {}

            cdict['_weight'] = weight
            cdict['__name__'] = name
            cdict['__page_attribute__'] = attribute
            new_class = type(class_.__name__,
                             (class_, viewlet.SimpleAttributeViewlet), cdict)

        if hasattr(class_, '__implements__'):
            classImplements(new_class, IBrowserPublisher)

    else:
        # Create a new class for the viewlet template alone.
        new_class = viewlet.SimpleViewletClass(
            template, name=name, weight=weight)

    # Make sure the new class implements the region
    classImplements(new_class, region)

    for attr_name in (attribute, 'browserDefault', '__call__',
                      'publishTraverse', 'weight'):
        required[attr_name] = permission

    viewmeta._handle_allowed_interface(
        _context, allowed_interface, permission, required)
    viewmeta._handle_allowed_attributes(
        _context, allowed_interface, permission, required)

    viewmeta._handle_for(_context, for_)
    metaconfigure.interface(_context, view)
    metaconfigure.interface(_context, region, interfaces.IRegion)

    checker.defineChecker(new_class, checker.Checker(required))

    # register viewlet
    _context.action(
        discriminator = ('viewlet', for_, layer, view, region, name),
        callable = metaconfigure.handler,
        args = ('provideAdapter',
                (for_, layer, view), region, name, new_class,
                 _context.info),)
