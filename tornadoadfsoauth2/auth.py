#!/usr/bin/env python3

import tornado.web, tornado.auth
from tornado import escape
import urllib.parse
import asyncio
from tornadoadfsoauth2.verify import verify
from tornadoadfsoauth2.session import sessions
import logging

import os
client_id=os.environ.get('adfs_client_id')
tenant_id = 'microsoft:identityserver:' + client_id
sharedsecret=os.environ.get('adfs_sharedsecret')
OAUTH_AUTHORIZE_URL = os.environ.get('adfs_oauth_authorize_url')
OAUTH_ACCESS_TOKEN_URL = os.environ.get('adfs_oauth_access_token_url')
keys_url = os.environ.get('adfs_keys_url')
redirect_uri=os.environ.get('adfs_redirect_uri')


class AdfsMixin(tornado.auth.OAuth2Mixin):
    async def get_authenticated_user(self, redirect_uri, code):
        http = self.get_auth_http_client()
        body = urllib.parse.urlencode(
            {
                "redirect_uri": redirect_uri,
                "code": code,
                "client_id": client_id,
                "client_secret": sharedsecret,
                "grant_type": "authorization_code",
            }
        )

        logging.debug("Fetching token from %s"%self._OAUTH_ACCESS_TOKEN_URL)
        response = await http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=body,
        )
        return escape.json_decode(response.body)


class AuthHandler(tornado.web.RequestHandler,
                  AdfsMixin):
    def on_finish(self):
        ua = (self.request.headers['user-agent'] if 'user-agent' in self.request.headers else 'Unknown').replace('"','')
        logging.debug('%s "%s"'%(str(self._request_summary()), ua))
    
    def _oauth_consumer_token(self):
        return {'key': client_id,
                'secret': sharedsecret}
    
    async def get(self, args):
        self._OAUTH_AUTHORIZE_URL = OAUTH_AUTHORIZE_URL
        self._OAUTH_ACCESS_TOKEN_URL = OAUTH_ACCESS_TOKEN_URL
        logging.debug('GET /auth/')
        code = self.get_argument('code', None)
        error = self.get_argument('error', None)
        nxt = self.get_argument('next', '/')
        if error:
            logging.debug('/auth error, code="%s", error="%s"'%(str(code), str(error)))
            self.set_status(401)
            self.write(error)
            return
        if not code:
            logging.debug('/auth error, no code present, redirecting to %s'%redirect_uri)
            self.clear_all_cookies()
            self.authorize_redirect(client_id=client_id,client_secret=sharedsecret, redirect_uri=redirect_uri)
        else:
            result = await self.get_authenticated_user(redirect_uri,
                                                       code)
            http = self.get_auth_http_client()
            keys_response = await http.fetch(keys_url)
            keyinfo = escape.json_decode(keys_response.body)

            key = keyinfo['keys'][0]['x5c'][0]
            
            # verify magic
            decoded = verify(result['access_token'], key, tenant_id)
            if decoded:
                logging.debug('/auth OK')
                sessions.add_session(result['access_token'], decoded)
                self.set_secure_cookie('session', result['access_token'])
                self.redirect(nxt)
            else:
                logging.debug('/auth error, failed to validate token')
                self.set_status(401)
                self.write({'status': 'authentication failure'})


