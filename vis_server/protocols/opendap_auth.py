#!/usr/bin/env python

import os

from pyesgf import logon as _logon


def logon(openid, password, pth=None):
    """Log on to ESGF and store credentials at the given path."""
    if pth is None:
        pth = os.curdir

    pth = os.path.abspath(pth)
    esg = os.path.join(pth, '.esg')
    dods = os.path.join(pth, '.dodsrc')

    success = False

    try:
        lm = _logon.LogonManager(
            esgf_dir=esg,
            dap_config=dods
        )

        lm.logon_with_openid(
            openid,
            interactive=False,
            bootstrap=True,
            password=password
        )

        success = lm.is_logged_on()
    except Exception:
        pass

    return success
