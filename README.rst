
What
----
A plugin for Pelican to provide commenting for a static blog/website.

It encapsulates posts from http://pump.io/ or https://identi.ca/ in an iframe.

Why
---

* Pump.io is fully Open Source and provides spam filtering and "social network" features
* No need to run a dedicated service
* Quick to set up

How
---

Every time a new blog post is made public, the plugin will create a notice on the microblogging service
and embed it in the blog post.

Usage
-----

Configure your pelicanconf.py with::

  PLUGINS = ['pelican-pumpio-comments']
  MICROBLOGGING_WEBFINGER='<nickname>@identi.ca' 


Add the following to your theme's templates/article.html, after {{ article.content }}::

  <iframe id="comments" src="{{article.microblog_url}}"></iframe> 

On the first run it will ask for authentication.
