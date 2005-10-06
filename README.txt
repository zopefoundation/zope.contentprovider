========
Viewlets
========

This package provides a framework to develop componentized Web GUI
applications. Instead of describing the content of a page using a single
template or static system of templates and METAL macros, page regions can be
defined and are filled dynamically with content (viewlets) based on the setup
of the application.


Getting Started
---------------

Let's say we have simple two-column page. In the smaller left column, there
are boxes filled with various pieces of information, such as news, latest
software releases, etc. This content, however, generally changes depending on
the view and the object being viewed.


Regions
~~~~~~~

Instead of hard-coding the pieces of content in the left column in the page
template or using macros, we simply define a region for it. Regions are
interfaces that act as content placeholders. Here is a common setup:

  >>> import zope.interface
  >>> class ILeftColumn(zope.interface.Interface):
  ...     '''The left column of a Web site.'''

  >>> from zope.app.viewlet import interfaces
  >>> zope.interface.directlyProvides(ILeftColumn, interfaces.IRegion)

  >>> import zope.component
  >>> zope.component.provideUtility(ILeftColumn, interfaces.IRegion,
  ...                               'webpage.LeftColumn')

It is important that the region interface provides the ``IRegion``
interface and that it is registered as a utility providing
``IRegion``. If omitted, the framework will be unable to find the
region later.


Viewlet
~~~~~~~

Viewlets are snippets of content that can be placed into a region, such as the
one defined above. As the name suggests, viewlets are views, but they are
qualified not only by the context object and the request, but also the view
they appear in. Also, the viewlet must *provide* the region interface it is
filling; we will demonstrate a more advanced example later, where the purpose
of this requirement becomes clear.

Like regular views, viewlets can either use page templates to provide content
or provide a simple ``__call__`` method. For our first viewlet, let's develop
a more commonly used page-template-driven viewlet:

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()

  >>> viewletFileName = os.path.join(temp_dir, 'viewlet.pt')
  >>> open(viewletFileName, 'w').write('''
  ...         <div class="box">
  ...           <tal:block replace="viewlet/title" />
  ...         </div>
  ... ''')

  >>> class ViewletBase(object):
  ...     def title(self):
  ...         return 'Viewlet Title'

As you can see, the viewlet Python object is known as ``viewlet`` inside the
template, while the view object is still available as ``view``. Next we build
and register the viewlet using a special helper function:

  # Create the viewlet class
  >>> from zope.app.viewlet import viewlet
  >>> Viewlet = viewlet.SimpleViewletClass(
  ...     viewletFileName, bases=(ViewletBase,), name='viewlet')

  # Generate a viewlet checker
  >>> from zope.security.checker import NamesChecker, defineChecker
  >>> viewletChecker = NamesChecker(('__call__', 'weight', 'title',))
  >>> defineChecker(Viewlet, viewletChecker)

  # Register the viewlet with component architecture
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.app.publisher.interfaces.browser import IBrowserView
  >>> zope.component.provideAdapter(
  ...     Viewlet,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView),
  ...     ILeftColumn,
  ...     name='viewlet')

As you can see from the security checker registration, a viewlet provides also
a weight, which acts as a hint to determine the order in which the viewlets of
a region should be displayed. The view the viewlet is used in can also be
accessed via the ``view`` attribute of the viewlet class.


Creating the View
~~~~~~~~~~~~~~~~~

Now that we have a region with a viewlet registered for it, let's use it by
creating the front page of our Web Site:

  >>> templateFileName = os.path.join(temp_dir, 'template.pt')
  >>> open(templateFileName, 'w').write('''
  ... <html>
  ...   <body>
  ...     <h1>My Web Page</h1>
  ...     <div class="left-column">
  ...       <div class="column-item"
  ...            tal:repeat="viewlet viewlets:webpage.LeftColumn">
  ...         <tal:block replace="structure viewlet" />
  ...       </div>
  ...     </div>
  ...     <div class="main">
  ...       Content here
  ...     </div>
  ...   </body>
  ... </html>
  ... ''')

and registering it as a view (browser page) for all objects:

  >>> from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
  >>> FrontPage = SimpleViewClass(templateFileName, name='main.html')

  >>> zope.component.provideAdapter(
  ...     FrontPage,
  ...     (zope.interface.Interface, IDefaultBrowserLayer),
  ...     zope.interface.Interface,
  ...     name='main.html')

That is all of the setup. Let's now render the view.


Using the View
~~~~~~~~~~~~~~

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
        <div class="column-item">
  <BLANKLINE>
          <div class="box">
            Viewlet Title
          </div>
  <BLANKLINE>
        </div>
      </div>
      <div class="main">
        Content here
      </div>
    </body>
  </html>


Class-driven Viewlets
~~~~~~~~~~~~~~~~~~~~~

Let's now have a look into the steps involved to create a viewlet class from
scratch. We also want to ensure that this viewlet always displays second and
not before the first one. Here is a most simple implementation:

  >>> from zope.app.publisher.browser import BrowserView
  >>> class InfoViewlet(BrowserView):
  ...     zope.interface.implements(interfaces.IViewlet, ILeftColumn)
  ...     weight = 1
  ...
  ...     def __init__(self, context, request, view):
  ...         super(InfoViewlet, self).__init__(context, request)
  ...         self.view = view
  ...
  ...     def __call__(self):
  ...         return u'<h3>Some Information.</h3>'

  >>> defineChecker(InfoViewlet, viewletChecker)

  >>> zope.component.provideAdapter(
  ...     InfoViewlet,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView),
  ...     ILeftColumn,
  ...     name='infoViewlet')


Note that you would commonly not state in the class itself that it
implements a particular region, since it is usually done by the ZCML
directive, which is introduced in `directives.zcml`.

When we now render the view, the content of our info viewlet appears as well:

  >>> print view().strip()
  <html>
    <body>
      <h1>My Web Page</h1>
      <div class="left-column">
        <div class="column-item">
  <BLANKLINE>
          <div class="box">
            Viewlet Title
          </div>
  <BLANKLINE>
        </div>
        <div class="column-item">
          <h3>Some Information.</h3>
        </div>
      </div>
      <div class="main">
        Content here
      </div>
    </body>
  </html>


Changing the Weight
~~~~~~~~~~~~~~~~~~~

Let's ensure that the weight really affects the order of the viewlets. If we
change the weights around,

  >>> InfoViewlet.weight = 0
  >>> Viewlet._weight = 1

the order of the left column in the page template should change:

  >>> print view().strip()
  <html>
    <body>
      <h1>My Web Page</h1>
      <div class="left-column">
        <div class="column-item">
          <h3>Some Information.</h3>
        </div>
        <div class="column-item">
  <BLANKLINE>
          <div class="box">
            Viewlet Title
          </div>
  <BLANKLINE>
        </div>
      </div>
      <div class="main">
        Content here
      </div>
    </body>
  </html>


Looking Up a Viewlet by Name
----------------------------

In some cases you want to be able to look up a particular viewlet for a region,
given a context and a view. For this use case, you can simply use a second
TALES namespace called ``viewlet`` that selects the viewlet using the
expression ``<path to region>/<viewlet name>``.

Since everything else is already set up, we can simply register a new view:

  >>> template2FileName = os.path.join(temp_dir, 'template2.pt')
  >>> open(template2FileName, 'w').write('''
  ... <html>
  ...   <body>
  ...     <h1>My Web Page - Take 2</h1>
  ...     <div class="left-column">
  ...       <div class="column-item">
  ...         <tal:block
  ...           replace="structure viewlet:webpage.LeftColumn/viewlet" />
  ...       </div>
  ...     </div>
  ...   </body>
  ... </html>
  ... ''')

  >>> SecondPage = SimpleViewClass(template2FileName, name='second.html')
  >>> zope.component.provideAdapter(
  ...     SecondPage,
  ...     (zope.interface.Interface, IDefaultBrowserLayer),
  ...     ILeftColumn,
  ...     name='second.html')

  >>> view = zope.component.getMultiAdapter((content, request),
  ...                                       name='second.html')
  >>> print view().strip()
  <html>
    <body>
      <h1>My Web Page - Take 2</h1>
      <div class="left-column">
        <div class="column-item">
  <BLANKLINE>
          <div class="box">
            Viewlet Title
          </div>
  <BLANKLINE>
        </div>
      </div>
    </body>
  </html>

Note that this namespace returns the rendered viewlet and not the viewlet
view, like the ``viewlets`` TALES namespace.


Region Schemas
--------------

In some use cases you want to be able to provide variables to a viewlet that
cannot be accessed via the view class or the context object. They are usually
variables that are defined by the view template. Since we do not just want all
of the view's template variables to be available (because it would be implicit
and not all viewlets must be called from within page templates), we must
specify the variables that the environment of the viewlet provides in the slot
interface as fields.

Let's say in your view you want to display a list of objects and you would
like to allow various columns that are controlled by viewlets:

  >>> class ObjectItems(object):
  ...
  ...     def objectInfo(self):
  ...         return [{'name': 'README.txt', 'size': '1.2kB'},
  ...                 {'name': 'logo.png', 'size': '100 x 100'}]

  >>> contentsFileName = os.path.join(temp_dir, 'items.pt')
  >>> open(contentsFileName, 'w').write('''
  ... <html>
  ...   <body>
  ...     <h1>Contents</h1>
  ...     <table>
  ...       <tr tal:repeat="item view/objectInfo">
  ...         <td tal:repeat="column viewlets:webpage.ObjectInfoColumn"
  ...             tal:content="structure column" />
  ...       </tr>
  ...     </table>
  ...   </body>
  ... </html>
  ... ''')

  >>> Contents = SimpleViewClass(contentsFileName, bases=(ObjectItems,),
  ...                            name='contents.html')

  >>> zope.component.provideAdapter(
  ...     Contents,
  ...     (zope.interface.Interface, IDefaultBrowserLayer),
  ...     zope.interface.Interface,
  ...     name='contents.html')

As you can see from the page template code, in order for the viewlets to be
of any use, they need access to the ``item`` variable as defined in the page
template. Thus, the region definition will state that the viewlet must have
access to a variable called ``item`` that contains the value of ``item`` in
the page template:

  >>> import zope.schema
  >>> class IObjectInfoColumn(zope.interface.Interface):
  ...     '''Place holder for the columns of a contents view.'''
  ...
  ...     item = zope.schema.Dict(
  ...         title=u'Object info dictionary',
  ...         required=True)

  >>> zope.interface.directlyProvides(
  ...     IObjectInfoColumn, interfaces.IRegion)

  >>> zope.component.provideUtility(
  ...     IObjectInfoColumn, interfaces.IRegion,
  ...     'webpage.ObjectInfoColumn')


Next we implement two very simple viewlets, one displaying the name

  >>> class NameColumnViewlet(BrowserView):
  ...     zope.interface.implements(interfaces.IViewlet, IObjectInfoColumn)
  ...     weight = 0
  ...
  ...     def __init__(self, context, request, view):
  ...         super(NameColumnViewlet, self).__init__(context, request)
  ...         self.view = view
  ...
  ...     def __call__(self):
  ...         return '<b>' + self.item['name'] + '</b>'

  >>> defineChecker(NameColumnViewlet, viewletChecker)

  >>> zope.component.provideAdapter(
  ...     NameColumnViewlet,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView),
  ...     IObjectInfoColumn,
  ...     name='name')

... and the other displaying the size of the of objects in the list:

  >>> class SizeColumnViewlet(BrowserView):
  ...     zope.interface.implements(interfaces.IViewlet, IObjectInfoColumn)
  ...     weight = 1
  ...
  ...     def __init__(self, context, request, view):
  ...         super(SizeColumnViewlet, self).__init__(context, request)
  ...         self.view = view
  ...
  ...     def __call__(self):
  ...         return self.item['size']

  >>> defineChecker(SizeColumnViewlet, viewletChecker)

  >>> zope.component.provideAdapter(
  ...     SizeColumnViewlet,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView),
  ...     IObjectInfoColumn,
  ...     name='size')


Now let's have a look at the resulting view:

  >>> view = zope.component.getMultiAdapter(
  ...     (content, request), name='contents.html')
  >>> print view().strip()
  <html>
    <body>
      <h1>Contents</h1>
      <table>
        <tr>
          <td><b>README.txt</b></td>
          <td>1.2kB</td>
        </tr>
        <tr>
          <td><b>logo.png</b></td>
          <td>100 x 100</td>
        </tr>
      </table>
    </body>
  </html>


Viewlet Managers
----------------

Until now we have always asserted that the viewlets returned by the TALES
namespaces ``viewlets`` and ``viewlet`` always find the viewlets in the
component architecture and then return them ordered by weight. This, however,
is just the default policy. We could also register an alternative policy that
has different rules on looking up, filtering and sorting the viewlets. The
objects that implement those policies are known as viewlet managers.

Viewlet managers are usually implemented as adapters from the context, request
and view to the ``IViewletManager`` interface. They must implement two
methods. The first one is ``getViewlets(region)``, which returns a list of
viewlets for the specified region. The region argument is the region
interface. The second method is ``getViewlet(name, region)``, which allows you
to look up a specific viewlet by name and region.


The Default Viewlet Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's first have a close look at the default view manager, whose functionality
we took for granted until now. Initializing the manager

  >>> from zope.app.viewlet import manager
  >>> defaultManager = manager.DefaultViewletManager(
  ...     content, request, FrontPage(content, request))

we can now get a list of viewlets:

  >>> defaultManager.getViewlets(ILeftColumn)
  [<InfoViewlet object at ...>,
   <zope.app.viewlet.viewlet.SimpleViewletClass from ...viewlet.pt object ...>]

The default manager also filters out all viewlets for which the current user
is not authorized. So, if I create a viewlet that has no security
declarations, then it is ignored:

  >>> class UnauthorizedViewlet(Viewlet):
  ...     pass

  # Register the access to a permission that does not exist.
  >>> unauthorizedChecker = NamesChecker(('__call__', 'weight', 'title',),
  ...                                    permission_id='Unauthorized')
  >>> defineChecker(UnauthorizedViewlet, unauthorizedChecker)

  >>> zope.component.provideAdapter(
  ...     UnauthorizedViewlet,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView),
  ...     ILeftColumn,
  ...     name='unauthorized')

  >>> len(defaultManager.getViewlets(ILeftColumn))
  2

Also, when you try to look up the unauthorized viewlet by name you will get an
exception telling you that you have insufficient priviledges to access the
viewlet:

  >>> defaultManager.getViewlet('unauthorized', ILeftColumn)
  Traceback (most recent call last):
  ...
  Unauthorized: You are not authorized to access the viewlet
                called `unauthorized`.

When looking for a particular viewlet, you also get an exception, if none is
found:

  >>> defaultManager.getViewlet('unknown', ILeftColumn)
  Traceback (most recent call last):
  ...
  ComponentLookupError: 'No viewlet with name `unknown` found.'


An Alternative Viewlet Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's now imagine that we would like to allow the user to choose the columns
for the contents view. Here it would not be enough to implement a condition as
part of the viewlet class, since the TD tag appearance is not controlled by
the viewlet itself. In those cases it is best to implement a custom viewlet
manager that only returns the viewlets that are specified in an option:

  >>> showColumns = ['name', 'size']

So our custom viewlet manager could look something like this:

  >>> class ContentsViewletManager(manager.DefaultViewletManager):
  ...
  ...     def getViewlets(self, region):
  ...         viewlets = zope.component.getAdapters(
  ...             (self.context, self.request, self.view), region)
  ...         viewlets = [(name, viewlet) for name, viewlet in viewlets
  ...                     if name in showColumns]
  ...         viewlets.sort(lambda x, y: cmp(showColumns.index(x[0]),
  ...                                        showColumns.index(y[0])))
  ...         return [viewlet for name, viewlet in viewlets]

We just have to register it as an adapter:

  >>> zope.component.provideAdapter(
  ...     ContentsViewletManager,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView),
  ...     interfaces.IViewletManager)

  >>> view = zope.component.getMultiAdapter(
  ...     (content, request), name='contents.html')
  >>> print view().strip()
  <html>
    <body>
      <h1>Contents</h1>
      <table>
        <tr>
          <td><b>README.txt</b></td>
          <td>1.2kB</td>
        </tr>
        <tr>
          <td><b>logo.png</b></td>
          <td>100 x 100</td>
        </tr>
      </table>
    </body>
  </html>

But if I turn the order around,

  >>> showColumns = ['size', 'name']

it will provide the columns in a different order as well:

  >>> print view().strip()
  <html>
    <body>
      <h1>Contents</h1>
      <table>
        <tr>
          <td>1.2kB</td>
          <td><b>README.txt</b></td>
        </tr>
        <tr>
          <td>100 x 100</td>
          <td><b>logo.png</b></td>
        </tr>
      </table>
    </body>
  </html>

On the other hand, it is as easy to remove a column:

  >>> showColumns = ['name']
  >>> print view().strip()
  <html>
    <body>
      <h1>Contents</h1>
      <table>
        <tr>
          <td><b>README.txt</b></td>
        </tr>
        <tr>
          <td><b>logo.png</b></td>
        </tr>
      </table>
    </body>
  </html>


UML Diagram
-----------

                      _________
                     |         |
                     | Context |
                     |_________|
                          ^
                          |
                          |*
                      ____|____
                     |         |
                     |   View  |
                     |_________|
                          |
                          |
                          |* a view is composed of regions
                      ____v____
                     |         |
                     |  Region |
                     |_________|
                          |
                          |
                          |* a region contains a list of viewlets
                      ____v____
                     |         |
                     | Viewlet |
                     |_________|

Natively, Zope 3 allows us to associate one or more views to a given
object. Those views are either registered for the provided interfaces of the
object or the object itself. In a view, usually a template, one can define
zero or more view regions. Upon rendering time, those view regions are populated
with the viewlets that have been assigned to the region.


Cleanup
-------

  >>> import shutil
  >>> shutil.rmtree(temp_dir)

