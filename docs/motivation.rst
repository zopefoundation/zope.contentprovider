=============================
 Motivation and Design Goals
=============================

Before diving into the features of this package let me take up a few bytes of
text to explain the use cases that drove us to develop this package (also
others) and how the API documented below fulfills/solves those use cases. When
we started developing Zope 3, it was from a desire to decentralize
functionality and thus the complexity of the Python code. And we were
successful! The component architecture is a marvelous piece of software that
hopefully will allow us to build scalable solutions for a very long
time. However, when it comes to user interface design, in this case
specifically HTML pages, we have failed to provide the features and patterns
of assembling a page from configured components.

Looking up views for a particular content component and a request just simply
does not work by itself. The content inside the page is still monolithic. One
attempt to solve this problem are METAL macros, which allow you to insert
other TAL snippets into your main template. But macros have two shortcomings.
For one there is a "hard-coded" one-to-one mapping between a slot and the
macro that fills that slot, which makes it impossible to register several
macros for a given location. The second problem is that macros are not views
in their own right; thus they cannot provide functionality that is independent
of the main template's view.

A second approach to modular UI design are rendering pipes. Rendering pipes
have the great advantage that they can reach all regions of the page during
every step of the rendering process. For example, if we have a widget in the
middle of the page that requires some additional Javascript, then it is easy
for a rendering unit to insert the Javascript file link in the HTML header of
the page. This type of use case is very hard to solve using page
templates. However, pipes are not the answer to componentized user interface,
since they cannot simply deal with registering random content for a given page
region. In fact, I propose that pipelines are orthogonal to content providers,
the concept introduced below. A pipeline framework could easily use
functionality provided by this and other packages to provide component-driven
UI design.

So our goal is clear: Bring the pluggability of the component architecture
into page templates and user interface design. Zope is commonly known to
reinvent the wheel, develop its own terminology and misuse other's terms. For
example, the Plone community has a very different understanding of what a
"portlet" is compared to the commonly accepted meaning in the corporate world,
which derives its definition from JSR 168. Therefore an additional use case of
the design of this package was to stick with common terms and use them in
their original meaning -- well, given a little extra twist.

The most basic user interface component in the Web application Java world is
the "content provider" [1]_. A content provider is simply responsible for
providing HTML content for a page. This is equivalent to a view that does not
provide a full page, but just a snippet, much like widgets or macros. Once
there is a way to configure those content providers, we need a way to
insert them into our page templates. In our implementation this is
accomplished using a new TALES namespace that allows to insert content
providers by name. But how, you might wonder, does this provide a
componentized user interface? On the Zope 3 level, each content provider is
registered as a presentation component discriminated by the context, request
and view it will appear in. Thus different content providers will be picked
for different configurations.

Okay, that's pretty much everything there is to say about content
providers. What, we are done? Hold on, what about defining regions of
pages and filling them configured UI snippets. The short answer is:
See the `zope.viewlet`_ package. But let me also give you the long
answer. This and the other packages were developed using real world
use cases. While doing this, we noticed that not every project would
need, for example, all the features of a portlet, but would still
profit from lower-level features. Thus we decided to declare clear
boundaries of functionality and providing each level in a different
package. This particular package is only meant to provide the
interface between the content provider world and page templates.

.. [1] Note that this is a bit different from the role named content provider,
       which refers to a service that provides content; the content provider
       we are talking about here are the software components the service would
       provide to an application.

.. _zope.viewlet: https://zopeviewlet.readthedocs.io/
