import cdms2
from fcntl import flock, LOCK_EX, LOCK_UN
import os
import sys
import tempfile,tarfile
import subprocess
from util.sanitize import sanitize_filename
import time
import cdms2

from django.conf import settings
if not settings.configured:
    settings.configure()
    
def download_file(filename, varlist, proxy_cert):
    outfilename="/tmp/" + str(time.time())
    myvarlist=varlist.split(',')
    if len(myvarlist)>0 and myvarlist[0] != '':
        try:
            f=cdms2.open(filename)
            fout=cdms2.open(outfilename,'w')
            for var in myvarlist:
                myvar=str(var)
                fout.write(f(myvar,time=slice(0,1)))
            fout.close()
            f.close()
            return outfilename
        except Exception as e:
            print e
            return None
    else:
        try:
            wget_url="http://pcmdi9.llnl.gov/esg-search/wget?url="+filename
            print wget_url
            with open(outfilename,'w') as outfile:
                flock(outfile,LOCK_EX)
                cmd="wget --certificate %s -t 2 -T 10 --private-key %s -O %s %s"%(proxy_cert,proxy_cert,outfilename,wget_url) 
                output=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
                time.sleep(.1)
                flock(outfile,LOCK_UN)
            outfile.close()
            return outfilename
        except Exception as e:
            return None
