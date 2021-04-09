#!/usr/bin/env python3

import base64, json, time
import jwt
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
import logging

def verify(t, key, tenant_id):
    parts = t.split('.')
    part0 = json.loads(base64.b64decode(parts[0] + '====='))
    logging.debug('part0:'+str(base64.b64decode(parts[0] + '=====')))
    part1 = json.loads(base64.b64decode(parts[1] + '====='))
    logging.debug('part1:'+str(base64.b64decode(parts[1] + '=====')))
    sig = parts[2]

    nbf = None
    exp = None
    if 'nbf' in part1:
        nbf = int(part1['nbf'])
    if 'exp' in part1:
        exp = int(part1['exp'])
    now = time.time()

    alg = part0['alg']

    # actually verify
    PEMSTART = "-----BEGIN CERTIFICATE-----\n"
    PEMEND = "\n-----END CERTIFICATE-----\n"
    pem = str.encode(PEMSTART + key + PEMEND, 'utf-8')
    cert_obj = load_pem_x509_certificate(pem, default_backend())
    public_key = cert_obj.public_key()
    decoded = jwt.decode(t, public_key, algorithms=['RS256'], audience=tenant_id)

    if nbf and exp:
        if decoded != None and nbf < now < exp and decoded['aud'] == tenant_id:
            logging.debug('OK nbf=%d exp=%d'%(nbf,exp))
            return decoded
        else:
            logging.debug('NOK nbf=%d exp=%d'%(nbf,exp))
            return None
    elif exp:
        if decoded != None and now < exp and decoded['aud'] == tenant_id:
            logging.debug('OK exp=%d'%exp)
            return decoded
        else:
            logging.debug('NOK exp=%d'%exp)
            return None
    else:
        logging.debug('verify, nbf and exp missing, decoded="%s"'%str(decoded))
        return decoded if decoded != None and decoded['aud'] == tenant_id else None
        
if __name__=='__main__':
    verify(open(sys.argv[1],'r').read())
