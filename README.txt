=================
Content Providers
=================

This package provides a framework to develop componentized Web GUI
applications. Instead of describing the content of a page using a single
template or static system of templates and METAL macros, content provider
objects can be created that are dynamically looked up based on the
setup/configuration of the application.

  >>> from zope.contentprovider import interfaces


Content Providers
-----------------

Content Providers is a term from the Java world that refers to components that
can provide HTML content. It means nothing more! How the content is found and
returned is totally up to the implementation. The Zope 3 touch to the concept
is that content providers are multi-adapters that are looked up by the
context, request (and thus the layer/skin), and view they are displayed in.

So let's create a simple content provider:

  >>> import zope.interface
  >>> import zope.component
  >>> from zope.publisher.interfaces import browser

  >>> class MessageBox(object):
  ...     zope.interface.implements(interfaces.IContentProvider)
  ...     zope.component.adapts(zope.interface.Interface,
  ...                           browser.IDefaultBrowserLayer,
  ...                           zope.interface.Interface)
  ...     message = u'My Message'
  ...
  ...     def __init__(self, context, request, view):
  ...         pass
  ...
  ...     def __call__(self):
  ...         return u'<div class="box">%s</div>' %self.message
  ...
  ...     def __repr__(self):
  ...         return 'MessageBox(%s)' %self.message.encode('utf-8')

The interface requires us to make the content provider callable. We can now
instantiate the content provider (manually) and render it:

  >>> box = MessageBox(None, None, None)
  >>> box()
  u'<div class="box">My Message</div>'

Since our content provider did not require the context, request or view to
create its HTML content, we were able to pass trivial dummy values into the
constructor.

I agree, this functionally does not seem very useful now. The constructor
seems useless and the returned content is totally static. However, we
implemented a contract for content providers that other code can rely
on. Content providers are (commonly) instantiated using the context, request
and view they appear in and are required to always generate its HTML using
those three components.


The TALES ``provider`` Expression
---------------------------------

The ``provider`` expression will look up the name of the content provider,
call it and return the HTML content. The first step, however, will be to
register our content provider with the component architecture:

  >>> zope.component.provideAdapter(MessageBox, name='mypage.MessageBox')

The content provider must be registered by name, since the TALES expression
uses the name to look up the provider at run time.

Let's now create a view using a page template:

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> templateFileName = os.path.join(temp_dir, 'template.pt')
  >>> open(templateFileName, 'w').write('''
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

As you can see, we exprect the ``provider`` expression to simply look up the
content provider and insert the HTML content at this place.

Next we register the template as a view (browser page) for all objects:

  >>> from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
  >>> FrontPage = SimpleViewClass(templateFileName, name='main.html')

  >>> zope.component.provideAdapter(
  ...     FrontPage,
  ...     (zope.interface.Interface, browser.IDefaultBrowserLayer),
  ...     zope.interface.Interface,
  ...     name='main.html')

Let's create a content object that can be viewed:

  >>> class Content(object):
  ...     zope.interface.implements(zope.interface.Interface)

  >>> content = Content()

Finally we look up the view and render it:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> view = zope.component.getMultiAdapter((content, request),
  ...                                       name='main.html')
  >>> print view().strip()
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


Failure to lookup a Content Provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Additional Data from TAL
~~~~~~~~~~~~~~~~~~~~~~~~


You might also want to look at the ``zope.viewlet`` package for a more
featureful API.