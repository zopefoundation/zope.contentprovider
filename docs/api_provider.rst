=======================
 Provided Base Classes
=======================

The `zope.contentprovider.provider` module provides an useful base
class for implementing content providers. It has all boilerplate code
and it's only required to override the ``render`` method to make it
work:

  >>> from zope.contentprovider import interfaces
  >>> from zope.contentprovider.provider import ContentProviderBase

  >>> class MyProvider(ContentProviderBase):
  ...     def render(self, *args, **kwargs):
  ...         return 'Hi there'

  >>> provider = MyProvider(None, None, None)
  >>> interfaces.IContentProvider.providedBy(provider)
  True

  >>> provider.update()
  >>> print(provider.render())
  Hi there

Note that it can't be used as is, without providing the ``render`` method:

  >>> bad = ContentProviderBase(None, None, None)
  >>> bad.update()
  >>> print(bad.render())
  Traceback (most recent call last):
  ...
  NotImplementedError: ``render`` method must be implemented by subclass

You can add the update logic into the ``update`` method as with any content
provider and you can implement more complex rendering patterns, based on
templates, using this ContentProviderBase class as a base.

You might also want to look at the `zope.viewlet`_ package for a more
featureful API.

.. _zope.viewlet: https://zopeviewlet.readthedocs.io

zope.contentprovider.provider
=============================

.. automodule:: zope.contentprovider.provider
