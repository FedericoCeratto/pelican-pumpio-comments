#!/usr/bin/env python

"""
Microblogging client and commenting system.

Requirements:
    PyPump https://github.com/xray7224/PyPump

Usage: see README.rst


"""

# TODO post notes to be publicu

import anydbm
import sys
from argparse import ArgumentParser
from pelican import signals
from pelican.contents import Article, Page
from pypump import PyPump

DEFAULT_NOTICE_TPL = """{title}<br/>
Read the blog post <a href="{url}">here</a>"""

DB_FNAME = '.microblogging.db'
db = None
pump = None

__version__ = "0.1"

def initialize(pel):
    """Initialize plugin, setup db, connect to microblogging service
    """
    global db, pump
    webfinger = pel.settings.get('MICROBLOGGING_WEBFINGER', None)
    if not webfinger:
        print("Error: MICROBLOGGING_WEBFINGER must be defined")
        return

    db = anydbm.open(DB_FNAME, "c")

    # Check if the user changed configuration to use a new account
    if 'authentication:webfinger' in db \
        and webfinger != db['authentication:webfinger']:
        print("""
WARNING: the webfinger has been changed.
If you want to recreate all the microblog posts as a new user, delete %s
""" % DB_FNAME)
        return

    pump = connect(db, webfinger)


def finalize(*a):
    """Close database
    """
    global db
    if db:
        db.close()


def connect(db, webfinger):
    """Connect to the microblogging service, configure authentication
    if needed
    """
    if 'authentication:client_key' in db:
        pump = PyPump(
            webfinger,
            client_name='pelican',
            key=db['authentication:client_key'],
            secret=db['authentication:client_secret'],
            token=db['authentication:token_key'],
            token_secret=db['authentication:token_secret'],
        )
        return pump

    # Authenticate now and save auth data.
    pump = PyPump(
        webfinger,
        client_name='pelican',
    )

    client_key, client_secret, expire_time = pump.get_registration()
    token_key, token_secret = pump.get_token()

    print 'Saving authentication data'
    db['authentication:webfinger'] = webfinger
    db['authentication:client_key'] = client_key
    db['authentication:client_secret'] = client_secret
    db['authentication:token_key'] = token_key
    db['authentication:token_secret'] = token_secret
    return pump


def post_microblog_notice(title=None, url=None, tpl=DEFAULT_NOTICE_TPL):
    """Post a notice on the microblogging service
    """
    n = pump.Note(tpl.format(title=title, url=url))
    print "Posting %r" % n.content
    n.send()
    print "Posted as %r" % n.id
    return n.id.encode('utf-8')


def _micro_blog(instance):
    """Create microblogging embeddable
    Post a new notice if needed
    """
    global db, pump
    if not isinstance(instance, (Article, Page)):
        return

    if instance.status != u'published':
        return  # skip non-published items

    rel_url = instance.url
    rel_url = rel_url.encode('utf-8')
    url = "%s/%s" % (instance.get_siteurl(), rel_url)

    if rel_url not in db:
        # Newly created or published item: post a notice
        notice_tpl = instance.settings.get('MICROBLOGGING_NOTICE_TPL',
                                      DEFAULT_NOTICE_TPL)
        notice_url = post_microblog_notice(title=instance.title, url=url,
                                           tpl=notice_tpl)
        db["notice:%s" % rel_url] = notice_url

    else:
        notice_url = db["notice:%s" % rel_url]

    #TODO: fix this hack
    nickname = pump.nickname
    instance.microblog_url = notice_url.replace('/api/', "/%s/" % nickname)


def register():
    signals.initialized.connect(initialize)
    signals.content_object_init.connect(_micro_blog)
    signals.finalized.connect(finalize)


# The plugin can be run from the CLI or an interactive interpreter to
# easily access the "pump" object
# bpython -i microblogging/__init__.py
# >>> pump.Note('hi').send()

def _parse_args():
    ap = ArgumentParser()
    ap.add_argument('action', choices=['list-notices', 'del-notice',
                                       'show-auth', 'delete-database'])
    ap.add_argument('parameter', nargs='?', default=None)
    return ap.parse_args()


def _main():
    print("Microblogging plugin %s being run from CLI" % __version__)
    args = _parse_args()

    action = args.action
    if action == 'list-notices':
        db = anydbm.open(DB_FNAME, 'r')
        for k, v in sorted(db.items()):
            if k.startswith('notice:'):
                print("%-40s %s" % (k, v))

        db.close()

    elif action == 'show-auth':
        db = anydbm.open(DB_FNAME, 'r')
        for k, v in sorted(db.items()):
            if k.startswith('authentication:'):
                print("%-40s %s" % (k, v))

        db.close()

    elif action == 'del-notice':
        if not args.parameter:
            print("An notice slug is required, see list-notices")
            sys.exit(1)

        notice_key = "notice:%s" % args.parameter
        db = anydbm.open(DB_FNAME, 'w')
        if notice_key not in db:
            print("Notice slug not found, see list-notices")
            sys.exit(1)

        del(db[notice_key])
        db.close()

    elif action == 'delete-database':
        print("\nWARNING: this action will delete all authentication data and"
              " the history of published notices.\nPress Ctrl-C to stop or "
              "Enter to continue.\n")
        raw_input()

        db = anydbm.open(DB_FNAME, 'w')
        db.clear()
        db.close()

if __name__ == '__main__':
    _main()


