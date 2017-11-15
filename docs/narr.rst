===================
 Content Providers
===================

.. currentmodule:: zope.contentprovider.interfaces

"Content Provider" is a term from the Java world that refers to components that
can provide HTML content. It means nothing more! How the content is found and
returned is totally up to the implementation. The Zope 3 touch to the concept
is that content providers are multi-adapters that are looked up by the
context, request (and thus the layer/skin), and view they are displayed in.

The second important concept of content providers are their two-phase
rendering design. In the first phase the state of the content provider is
prepared and, if applicable, any data the provider is responsible for is
updated.

  >>> from zope.contentprovider import interfaces

So let's create a simple content provider:

  >>> import zope.interface
  >>> import zope.component
  >>> from zope.publisher.interfaces import browser

  >>> @zope.interface.implementer(interfaces.IContentProvider)
  ... @zope.component.adapter(zope.interface.Interface,
  ...                         browser.IDefaultBrowserLayer,
  ...                         zope.interface.Interface)
  ... class MessageBox(object):
  ...     message = u'My Message'
  ...
  ...     def __init__(self, context, request, view):
  ...         self.__parent__ = view
  ...
  ...     def update(self):
  ...         pass
  ...
  ...     def render(self):
  ...         return u'<div class="box">%s</div>' % self.message
  ...
  ...     def __repr__(self):
  ...         return '<MessageBox object at %x>' % id(self)

The ``update()`` method is executed during phase one. Since no state needs to
be calculated and no data is modified by this simple content provider, it is
an empty implementation. The ``render()`` method implements phase 2 of the
process. We can now instantiate the content provider (manually) and render it:

  >>> box = MessageBox(None, None, None)
  >>> print(box.render())
  <div class="box">My Message</div>

Since our content provider did not require the context, request or view to
create its HTML content, we were able to pass trivial dummy values into the
constructor. Also note that the provider must have a parent (using the
``__parent__`` attribute) specified at all times. The parent must be the view
the provider appears in.

I agree, this functionally does not seem very useful now. The constructor and
the ``update()`` method seem useless and the returned content is totally
static. However, we implemented a contract for content providers that other
code can rely on. Content providers are (commonly) instantiated using the
context, request and view they appear in and are required to always generate
its HTML using those three components.


Two-Phased Content Providers
============================

Let's now have a look at a content provider that actively uses the two-phase
rendering process. The simpler scenario is the case where the content provider
updates a content component without affecting anything else. So let's create a
content component to be updated,

  >>> class Article(object):
  ...     title = u'initial'
  >>> article = Article()

and the content provider that is updating the title:

  >>> @zope.interface.implementer(interfaces.IContentProvider)
  ... @zope.component.adapter(zope.interface.Interface,
  ...                         browser.IDefaultBrowserLayer,
  ...                         zope.interface.Interface)
  ... class ChangeTitle(object):
  ...     fieldName = 'ChangeTitle.title'
  ...
  ...     def __init__(self, context, request, view):
  ...         self.__parent__ = view
  ...         self.context, self.request = context, request
  ...
  ...     def update(self):
  ...         if self.fieldName in self.request:
  ...             self.context.title = self.request[self.fieldName]
  ...
  ...     def render(self):
  ...         return u'<input name="%s" value="%s" />' % (self.fieldName,
  ...                                                     self.context.title)

Using a request, let's now instantiate the content provider and go through the
two-phase rendering process:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> changer = ChangeTitle(article, request, None)
  >>> changer.update()
  >>> print(changer.render())
  <input name="ChangeTitle.title" value="initial" />

Let's now enter a new title and render the provider:

  >>> request = TestRequest(form={'ChangeTitle.title': u'new title'})
  >>> changer = ChangeTitle(article, request, None)
  >>> changer.update()
  >>> print(changer.render())
  <input name="ChangeTitle.title" value="new title" />
  >>> print(article.title)
  new title

So this was easy. Let's now look at a case where one content provider's update
influences the content of another. Let's say we have a content provider that
displays the article's title:

  >>> @zope.interface.implementer(interfaces.IContentProvider)
  ... @zope.component.adapter(zope.interface.Interface,
  ...                         browser.IDefaultBrowserLayer,
  ...                         zope.interface.Interface)
  ... class ViewTitle(object):
  ...
  ...     def __init__(self, context, request, view):
  ...         self.context, self.__parent__ = context, view
  ...
  ...     def update(self):
  ...         pass
  ...
  ...     def render(self):
  ...         return u'<h1>Title: %s</h1>' % self.context.title

Let's now say that the ``ShowTitle`` content provider is shown on a page
*before* the ``ChangeTitle`` content provider. If we do the full rendering
process for each provider in sequence, we get the wrong result:

  >>> request = TestRequest(form={'ChangeTitle.title': u'newer title'})

  >>> viewer = ViewTitle(article, request, None)
  >>> viewer.update()
  >>> print(viewer.render())
  <h1>Title: new title</h1>

  >>> changer = ChangeTitle(article, request, None)
  >>> changer.update()
  >>> print(changer.render())
  <input name="ChangeTitle.title" value="newer title" />

So the correct way of doing this is to first complete phase 1 (update) for all
providers, before executing phase 2 (render):

  >>> request = TestRequest(form={'ChangeTitle.title': u'newest title'})

  >>> viewer = ViewTitle(article, request, None)
  >>> changer = ChangeTitle(article, request, None)

  >>> viewer.update()
  >>> changer.update()

  >>> print(viewer.render())
  <h1>Title: newest title</h1>

  >>> print(changer.render())
  <input name="ChangeTitle.title" value="newest title" />


``UpdateNotCalled`` Errors
==========================

Since calling `~IContentProvider.update` before any other method that
mutates the provider or any other data is so important to the correct
functioning of the API, the developer has the choice to raise the
:exc:`UpdateNotCalled` error, if any method is called before
``update()`` (with exception of the constructor):

  >>> @zope.interface.implementer(interfaces.IContentProvider)
  ... @zope.component.adapter(zope.interface.Interface,
  ...                         browser.IDefaultBrowserLayer,
  ...                         zope.interface.Interface)
  ... class InfoBox(object):
  ...
  ...     def __init__(self, context, request, view):
  ...         self.__parent__ = view
  ...         self.__updated = False
  ...
  ...     def update(self):
  ...         self.__updated = True
  ...
  ...     def render(self):
  ...         if not self.__updated:
  ...             raise interfaces.UpdateNotCalled
  ...         return u'<div>Some information</div>'

  >>> info = InfoBox(None, None, None)

  >>> info.render()
  Traceback (most recent call last):
  ...
  UpdateNotCalled: ``update()`` was not called yet.

  >>> info.update()

  >>> print(info.render())
  <div>Some information</div>


zope.contentprovider.interfaces
===============================

.. automodule:: zope.contentprovider.interfaces


.. _zope.viewlet: https://zopeviewlet.readthedocs.io
