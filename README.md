# ADFS Oauth2 authentication for tornadoweb

This module provides an ADFS-Oauth2 authentication mixin to a web
application built on the Tornadoweb framework.

# Known issues

This project was quickly extracted from some other project. The code
may look a bit odd at places. Cleanup PRs are appreciated.

# Setup

First, install by

```
pip3 install .
```

Provide the following environment variables (with sample values):

```
export adfs_client_id='[redacted]'
export adfs_sharedsecret='[redacted]'
export adfs_oauth_authorize_url='https://adfs.yourdomain.tld/adfs/oauth2/authorize'
export adfs_oauth_access_token_url='https://adfs.yourdomain.tld/adfs/oauth2/token'
export adfs_keys_url='https://adfs.yourdomain.tld/adfs/discovery/keys'
export adfs_redirect_uri='http://yourwebapp.domain/auth/'
export adfs_logout_uri='https://adfs.yourdomain.tld/adfs/oauth2/logout'
```

Then configure your web app like in the simplified example below

```
from tornadoadfsoauth2.auth import AuthHandler

class LogoutHandler(BaseHandler):
    def get(self):
        log('GET /logout')
        sessions.remove_session(self.get_current_user())
        self.clear_all_cookies()
        self.redirect(os.environ.get('adfs_logout_uri', 'http://127.0.0.1/'))

def make_app():
    return tornado.web.Application([
        (r"/", WhateverHandler),
        (r"/logout/", LogoutHandler),
        (r"/auth/(.*)", AuthHandler)
    ], cookie_secret='yourass',
                                   login_url='/auth/')
```

You can also implement your own `BaseHandler` that provides some
shorthand to check the current user, here's part of mine,

```
from tornadoadfsoauth2.session import sessions
import tornado.web, sys, base64

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        try:
            raw = self.get_secure_cookie('session')
            if not raw:
                log("No session cookie set")
                return None
            c = raw.decode('utf-8')
            if c and sessions.check_session(c):
                return c
            else:
                log('check_session NOK for %s'%str(c))
                return None
        except:
            raise

    def get_current_username(self):
        return sessions.get_username(self.get_current_user())
```

Now you can add the `@tornado.web.authenticated` decorator to methods
you want to only allow for authenticated users, like this.

```
class SomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company, path, args):
        pass
```

Also now if you want to allow an AD user `john` to perform specific
actions, you can check for `self.get_current_username() == 'john'`.
