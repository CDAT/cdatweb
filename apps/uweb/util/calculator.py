import MV2, genutil,cdms2,vcs,cdutil,numpy,os
import time

from django.conf import settings
if not settings.configured:
        settings.configure()

def eval_cdat_cmd(cmd, myfile, myselectedvar, mynewvar):
    cert_path=os.path.join(settings.PROXY_CERT_DIR,"448000")
    cdms2.setHttprcDirectory(cert_path)
    outfilename="/tmp/" + str(time.time())
    fout=cdms2.open(outfilename,'w')
    f=cdms2.open(myfile)
    c=cmd.replace(myselectedvar,"f(\'"+myselectedvar+"\',time=slice(0,1))")
    b=eval(c)
    fout.write(b,id=mynewvar) 
    fout.close()
    f.close()
    return outfilename
