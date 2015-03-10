
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

Optionally you can specify a notice template, for example::

  MICROBLOGGING_NOTICE_TPL="""{title}<br/>{content}<br/><a href="{url}">{slug}</a>"""

Add the following to your theme's templates/article.html, after {{ article.content }}::

  <iframe id="comments" src="{{article.microblog_url}}"></iframe>

Also add the following to the main css, usually static/css/main.css::

  iframe#comments {
    margin-top: 2em;
    border: 0;
    width: 100%;
    height: 40em;
  }

On the first run it will ask for authentication.

Managing the plugin
-------------------

Authentication data and a list of published notices is stored in a tiny file-based database.
You can run the plugin from command line as::
  ./pelican-pumpio-comments/pumpio_comments.py <action> <parameter>
  
show-auth
  Show authentication data
  
list-notices
  List known published notices
  
del-notice <notice_name>
  Delete a notice from the database. If the original post is still present, the next time Pelican is run a new notice will be published.
  
delete-database
  Flush the whole database: authentication and notices. Useful if you want to move to a new microblogging account.






