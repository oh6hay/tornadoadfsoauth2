#!/usr/bin/env python3

import time, json, sys
import logging
from db import db
import base64
import json

from hashlib import sha256
def sha(x):
    return sha256(str(x).encode('ascii')).hexdigest()

def session2tuple(sessionkey):
    session = json.loads(base64.b64decode(str(sessionkey).split('.')[1]+'======'))
    exp = session['exp'] if 'exp' in session else 0
    nbf = session['nbf'] if 'nbf' in session else 0
    iat = session['iat'] if 'iat' in session else 0
    upn = session['upn'] if 'upn' in session else ''
    winaccountname = session['winaccountname'] if 'winaccountname' in session else ''
    return exp, nbf, iat, upn, winaccountname


class SessionCache:
    def __init__(self):
        self.sessions = {}

    def add_session(self, key, session):
        exp, nbf, iat, upn, winaccountname = session2tuple(key)
        self.sessions[key] = (sha(key), exp, nbf, iat, upn, winaccountname)
        #db.add_session(key, exp, nbf, iat, upn, winaccountname)

    def remove_session(self, key):
        if key in self.sessions:
            del self.sessions[key]
        #db.remove_session(key)

    def check_session(self, key):
        #return db.check_session(key)
        if key in self.sessions:
            s = self.sessions[key]
            if s[0] == sha(key) and s[1] > time.time():
                logging.debug('all is good, session is fine')
                return True
            else:
                logging.debug('keys match: %s time ok: %s'%(str(s[0] == sha(key)), str(s[1] > time.time())))
        else:
            logging.debug('fuck off. key not found')
        return False

    def get_username(self, key):
        try:
            exp, iat, nbf, upn, winaccountname = db.get_session(key)
            return winaccountname
        except:
            return None
            
sessions = SessionCache()


if __name__=='__main__':
    s = SessionCache.Instance()
    s.unserialize()
    print(json.dumps(s.sessions, indent=True, sort_keys=True))
