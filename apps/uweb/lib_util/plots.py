import cdms2
from fcntl import flock, LOCK_EX, LOCK_UN
import os
import sys
import vcs

from lib_util.sanitize import sanitize_filename

from django.conf import settings
if not settings.configured:
    settings.configure()

vcs_inst=None

def get_vcs_inst():
    global vcs_inst
    if not vcs_inst:
        vcs_inst=vcs.init()
    return vcs_inst

def save_plot(myVar,outfile,fromJson=False):
    vcs_instance=get_vcs_inst()
    print "CanvasID: ",vcs_instance.canvasid()
    if fromJson:
       myVar=cdms2.createVariable(myVar,fromJSON=True)
    vcs_instance.plot(myVar, bg=1)
    f=open(outfile,'w')
    flock(f, LOCK_EX)
    vcs_instance.png(outfile)
    flock(f,LOCK_UN)
    f.close()
    return

def getVar(in_file):
    try:
        data=cdms2.open(in_file)
        varlist=data.variables.keys()
    except Exception, e:
        return None
    return varlist

def boxfill(in_file, variable, in_selection, proxy_cert=None, lev1=None, lev2=None):
    '''
    Generates a boxfill plot of the selected variable.
    Writes a .png file to disk and returns the URL to it when it's done.
    '''
    ### determine the filename plot will have ###
    filename = "plot-boxfill_%s_%s_%s_%s_%s" % (in_file, variable, str(in_selection), lev1, lev2)
    filename = sanitize_filename(filename)
    filename += ".png"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    
    ### check to see if we've already created this file ###
    #if(os.path.isfile(filepath)):
    #    return settings.MEDIA_URL + filename
    
    ### if not, create the plot, write it to file, and return ###
    try:
        #######################################################################
        # Unidata is adding functionality to netcdf so that we will be able
        # to specify which .dodsrc (or .httprc) file it should read in order
        # to find where the certificate is located.
        # Once they're done with that, we'll need to make some changes to cdms2
        # but in the end, our cdms2 call will probably look something like:
        #
        # httprc_path = settings.PROXY_CERT_DIR + '/' + username + '.httprc')
        # data = cdms2.open(in_file, httprc=httprc_path)
        #######################################################################
        data = cdms2.open(in_file)
        ### check to see if we've already created this file ###
        if(os.path.isfile(filepath)):
            return settings.MEDIA_URL + filename
        selection = data(variable, **in_selection)
        canvas = vcs.init()
        plot = canvas.createboxfill()
        if lev1 is not None and lev2 is not None:
            plot.level_1 = lev1
            plot.level_2 = lev2
        canvas.clear()
        canvas.plot(selection, plot, bg=1)#, #ratio='autot') # plots in background
        
        with open(filepath, 'wb') as outfile:
            flock(outfile, LOCK_EX)
            canvas.png(filepath)
            flock(outfile, LOCK_UN)
        return settings.MEDIA_URL + filename
    except Exception as e:
        print type(e)
        print "An exception has occured in plots.boxfill()! The error was \"%s\"" % e
        return None
