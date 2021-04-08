#!/usr/bin/env python3

import datetime, sys, os

def log(message, deeper=False, skipframe=False):
    debug = os.getenv('OAUTH2DEBUG', False)
    if not debug:
        return
    if not message:
        return
    import inspect
    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    func = inspect.currentframe().f_back.f_code
    if deeper:
        func = inspect.currentframe().f_back.f_back.f_code
    # Dump the message + the name of this function to the log.
    if skipframe:
        sys.stderr.write("%s [tornadoadfsoauth2] %s\n" % (
            str(datetime.datetime.utcnow()),
            message.strip()
        ))
    else:
        sys.stderr.write("%s [tornadoadfsoauth2] %s:%i %s: %s\n" % (
            str(datetime.datetime.utcnow()),
            func.co_filename, 
            func.co_firstlineno,
            func.co_name, 
            message.strip()
        ))
