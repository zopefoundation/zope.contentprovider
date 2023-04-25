===================================
 The TALES ``provider`` Expression
===================================

.. testsetup::

    from zope.component import eventtesting
    from zope.testing import cleanup, renormalizing

    cleanup.setUp()
    eventtesting.setUp()

    __file__ = 'tales.rst'

    from zope.browserpage.metaconfigure import registerType
    from zope.contentprovider import tales
    registerType('provider', tales.TALESProviderExpression)

.. testcleanup::

    cleanup.tearDown()

The ``provider`` expression will look up the name of the content provider,
call it and return the HTML content. The first step, however, will be to
register our content provider with the component architecture:


  >>> import zope.interface
  >>> import zope.component
  >>> from zope.contentprovider import interfaces
  >>> from zope.publisher.interfaces import browser
  >>> from zope.contentprovider.provider import ContentProviderBase

  >>> class MessageBox(ContentProviderBase):
  ...     message = u'My Message'
  ...
  ...     def render(self):
  ...         return u'<div class="box">%s</div>' % self.message
  ...
  ...     def __repr__(self):
  ...         return '<MessageBox object at %x>' % id(self)

  >>> zope.component.provideAdapter(MessageBox,
  ...                               provides=interfaces.IContentProvider,
  ...                               name='mypage.MessageBox')

The content provider must be registered by name, since the TALES expression
uses the name to look up the provider at run time.

Let's now create a view using a page template:

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp(prefix="test-zopecontentprovider-")
  >>> templateFileName = os.path.join(temp_dir, 'template.pt')
  >>> with open(templateFileName, 'w') as file:
  ...     _ = file.write('''
  ... <html>
  ...   <body>
  ...     <h1>My Web Page</h1>
  ...     <div class="left-column">
  ...       <tal:block replace="structure provider:mypage.MessageBox" />
  ...     </div>
  ...     <div class="main">
  ...       Content here
  ...     </div>
  ...   </body>
  ... </html>
  ... ''')

As you can see, we expect the ``provider`` expression to simply look up the
content provider and insert the HTML content at this place.

Next we register the template as a view (browser page) for all objects:

  >>> from zope.browserpage.simpleviewclass import SimpleViewClass
  >>> FrontPage = SimpleViewClass(templateFileName, name='main.html')

  >>> zope.component.provideAdapter(
  ...     FrontPage,
  ...     (zope.interface.Interface, browser.IDefaultBrowserLayer),
  ...     zope.interface.Interface,
  ...     name='main.html')

Let's create a content object that can be viewed:

  >>> @zope.interface.implementer(zope.interface.Interface)
  ... class Content(object):
  ...     pass

  >>> content = Content()

Finally we look up the view and render it. Note that a
`.BeforeUpdateEvent` is fired - this event should always be fired before
any content provider is updated.

  >>> from zope.publisher.browser import TestRequest
  >>> events = []
  >>> zope.component.provideHandler(events.append, (None, ))
  >>> request = TestRequest()

  >>> view = zope.component.getMultiAdapter((content, request),
  ...                                       name='main.html')
  >>> print(view().strip())
  <html>
    <body>
      <h1>My Web Page</h1>
      <div class="left-column">
        <div class="box">My Message</div>
      </div>
      <div class="main">
        Content here
      </div>
    </body>
  </html>

  >>> events
  [<zope.contentprovider.interfaces.BeforeUpdateEvent object at ...>]

The event holds the provider and the request.

  >>> events[0].request
  <zope.publisher.browser.TestRequest instance URL=http://127.0.0.1>
  >>> events[0].object
  <MessageBox object at ...>

Failure to Find a Content Provider
==================================

If the name is not found, an error is raised. To demonstrate this behavior
let's create another template:

  >>> errorFileName = os.path.join(temp_dir, 'error.pt')
  >>> with open(errorFileName, 'w') as file:
  ...     _ = file.write('''
  ... <html>
  ...   <body>
  ...     <tal:block replace="structure provider:mypage.UnknownName" />
  ...   </body>
  ... </html>
  ... ''')

  >>> ErrorPage = SimpleViewClass(errorFileName, name='error.html')
  >>> zope.component.provideAdapter(
  ...     ErrorPage,
  ...     (zope.interface.Interface, browser.IDefaultBrowserLayer),
  ...     zope.interface.Interface,
  ...     name='main.html')

  >>> errorview = zope.component.getMultiAdapter((content, request),
  ...                                            name='main.html')
  >>> print(errorview())
  Traceback (most recent call last):
  ...
  ContentProviderLookupError: mypage.UnknownName


Additional Data from TAL
========================

The ``provider`` expression allows also for transferring data from the TAL
context into the content provider. This is accomplished by having the content
provider implement an interface that specifies the attributes and provides
`~zope.contentprovider.interfaces.ITALNamespaceData`:

  >>> import zope.schema
  >>> class IMessageText(zope.interface.Interface):
  ...     message = zope.schema.Text(title=u'Text of the message box')

  >>> zope.interface.directlyProvides(IMessageText,
  ...                                 interfaces.ITALNamespaceData)

Now the message box can receive its text from the TAL environment:

  >>> @zope.interface.implementer(IMessageText)
  ... class DynamicMessageBox(MessageBox):
  ...     pass

  >>> zope.component.provideAdapter(
  ...     DynamicMessageBox, provides=interfaces.IContentProvider,
  ...     name='mypage.DynamicMessageBox')

We are now updating our original template to provide the message text:

  >>> with open(templateFileName, 'w') as file:
  ...     _ = file.write('''
  ... <html>
  ...   <body>
  ...     <h1>My Web Page</h1>
  ...     <div class="left-column">
  ...       <tal:block define="message string:Hello World!"
  ...                  replace="structure provider:mypage.DynamicMessageBox" />
  ...       <tal:block define="message string:Hello World again!"
  ...                  replace="structure provider:mypage.DynamicMessageBox" />
  ...     </div>
  ...     <div class="main">
  ...       Content here
  ...     </div>
  ...   </body>
  ... </html>
  ... ''')

Let's make sure the template will be reloaded from disk

  >>> FrontPage.index.__func__._v_last_read = 0

Now we should get two message boxes with different text:

  >>> print(view().strip())
  <html>
    <body>
      <h1>My Web Page</h1>
      <div class="left-column">
        <div class="box">Hello World!</div>
        <div class="box">Hello World again!</div>
      </div>
      <div class="main">
        Content here
      </div>
    </body>
  </html>

Finally, a content provider can also implement several
`~zope.contentprovider.interfaces.ITALNamespaceData`:

  >>> class IMessageType(zope.interface.Interface):
  ...     type = zope.schema.TextLine(title=u'The type of the message box')

  >>> zope.interface.directlyProvides(IMessageType,
  ...                                 interfaces.ITALNamespaceData)

We'll change our message box content provider implementation a bit, so the new
information is used:

  >>> @zope.interface.implementer(IMessageType)
  ... class BetterDynamicMessageBox(DynamicMessageBox):
  ...     type = None
  ...
  ...     def render(self):
  ...         return u'<div class="box,%s">%s</div>' % (self.type, self.message)

  >>> zope.component.provideAdapter(
  ...     BetterDynamicMessageBox, provides=interfaces.IContentProvider,
  ...     name='mypage.MessageBox')

Of course, we also have to make our template a little bit more dynamic as
well:

  >>> with open(templateFileName, 'w') as file:
  ...     _ = file.write('''
  ... <html>
  ...   <body>
  ...     <h1>My Web Page</h1>
  ...     <div class="left-column">
  ...       <tal:block define="message string:Hello World!;
  ...                          type string:error"
  ...                  replace="structure provider:mypage.MessageBox" />
  ...       <tal:block define="message string:Hello World again!;
  ...                          type string:warning"
  ...                  replace="structure provider:mypage.MessageBox" />
  ...     </div>
  ...     <div class="main">
  ...       Content here
  ...     </div>
  ...   </body>
  ... </html>
  ... ''')
  >>> FrontPage.index.__func__._v_last_read = 0

Now we should get two message boxes with different text and types:

  >>> print(view().strip())
  <html>
    <body>
      <h1>My Web Page</h1>
      <div class="left-column">
        <div class="box,error">Hello World!</div>
        <div class="box,warning">Hello World again!</div>
      </div>
      <div class="main">
        Content here
      </div>
    </body>
  </html>

ILocation
=========

If our content provider implements
:class:`zope.location.interfaces.ILocation`, then it will have its
``__name__`` set to the name that was used to invoke it.


  >>> from zope.location.interfaces import ILocation
  >>> @zope.interface.implementer(ILocation)
  ... class LocationDynamicMessageBox(BetterDynamicMessageBox):
  ...
  ...     def render(self):
  ...         return u'<div class="box">%s</div>' % (self.__name__,)

  >>> zope.component.provideAdapter(
  ...     LocationDynamicMessageBox, provides=interfaces.IContentProvider,
  ...     name='mypage.MessageBox')

  >>> print(view().strip())
  <html>
    <body>
      <h1>My Web Page</h1>
      <div class="left-column">
        <div class="box">mypage.MessageBox</div>
        <div class="box">mypage.MessageBox</div>
      </div>
      <div class="main">
        Content here
      </div>
    </body>
  </html>

.. testcleanup::

  import shutil
  shutil.rmtree(temp_dir)


zope.contentprovider.tales
==========================

.. automodule:: zope.contentprovider.tales
