#!/usr/local/uvcdat/1.3.1/bin/python

# Functions callable from the UV-CDAT GUI.

import hashlib, os, pickle, sys, os
from metrics import *
from metrics.fileio.filetable import *
from metrics.fileio.findfiles import *
from metrics.computation.reductions import *
from metrics.amwg import *
from metrics.amwg.derivations.vertical import *
from metrics.amwg.plot_data import plotspec, derived_var
from metrics.frontend.version import version
from metrics.amwg.derivations import *
from metrics.diagnostic_groups import *
from pprint import pprint
import cProfile
import json
import vcs
import os.path
import shutil
vcsx = False

import time

#vcsx=vcs.init()   # This belongs in one of the GUI files, e.g.diagnosticsDockWidget.py
                  # The GUI probably will have already called vcs.init().
                  # Then, here,  'from foo.bar import vcsx'
# ---------------- code to compute plot in another process, not specific to UV-CDAT:

from multiprocessing import Process, Semaphore, Pipe

def _plotdata_run( child_conn, sema,
                   plotspec, filetable1, filetable2, varname, seasonname, ts, aux=None):
    global vcsx
    vcsx = False # temporary kludge
    sema.acquire()
    ps = plotspec( filetable1, filetable2, varname, seasonname, aux )
    if ps is None:
        results = None
    else:
        results = ps.compute()
        json_results=[ rr.write_plot_data(writer="JSON string") for rr in results ]
        full_json = '['+','.join(json_results)+']'
        outpath=os.environ['HOME']+'/tmp/diagout/' + str(ts) 
        f=open(outpath,mode='w')
        f.write(full_json)
        f.close()
    print "jfp _plotdata_run results=",results
    sema.release()
    #child_conn.send(results)
    return results

def plotdata_run( plotspec, filetable1, filetable2, varname, seasonname, aux=None ):
    """Inputs:
    plotspec is a plot_spec class to be instantiated
    filetable1 is the model data file table
    fileteable2 is the obs or reference model data file table
    varname is a string representing the variable to be plotted
    seasonname is a string representing the season for climatology to be presented
    aux is an auxiliary option, if any

    This function will spawn another process and return it as p, an instance of
    multiprocessing.Process.  This p will create a plotspec object and run its compute() method.
    To check the status of p, call plotdata_status(p) to get a semaphore value (>0 means done).
    To get the computed value, call plotdata_results(p).
    """
    sema = Semaphore()
    parent_conn, child_conn = Pipe()
    ts= time.time()
    p = Process( target=_plotdata_run,
                 args=(child_conn, sema,
                       plotspec, filetable1, filetable2, varname, seasonname, ts, aux) )
    p.start()
    p.sema = sema
    p.parent_conn = parent_conn
    return ts

def plotdata_status( p ):
    return p.sema.get_value()

def plotdata_results( p ):
    return p.parent_conn.recv()

# ----------------

def setup_filetable( search_path, cache_path, ftid=None, search_filter=None ):
    print "jfp in setup_filetable, search_path=",search_path," search_filter=",search_filter
    #try:
    datafiles = dirtree_datafiles( search_path, search_filter )
    return datafiles.setup_filetable( cache_path, ftid )
    #except Exception, err:
    #    print "=== EXCEPTION in setup_filetable ===", err
    #    return None

def clear_filetable( search_path, cache_path, search_filter=None ):
    """obsolete; Deletes (clears) the cached file table created by the corresponding call of setup_filetable"""
    search_path = os.path.abspath(search_path)
    cache_path = os.path.abspath(cache_path)
    csum = hashlib.md5(search_path+cache_path).hexdigest()  #later will have to add search_filter
    cachefilename = csum+'.cache'
    cachefile=os.path.normpath( cache_path+'/'+cachefilename )

    if os.path.isfile(cache_path):
        os.remove(cache_path)

class uvc_plotspec():
    """This is a simplified version of the plotspec class, intended for the UV-CDAT GUI.
    Once it stabilizes, I may replace the plotspec class with this one.
    The plots will be of the type specified by presentation.  The data will be the
    variable(s) supplied, and their axes.  Optionally one may specify a list of labels
    for the variables, and a title for the whole plot."""
    # re prsentation (plottype): Yxvsx is a line plot, for Y=Y(X).  It can have one or several lines.
    # Isofill is a contour plot.  To make it polar, set projection=polar.  I'll
    # probably communicate that by passing a name "Isofill_polar".
    def __init__( self, vars, presentation, labels=[], title=''):
        type = presentation
        if vcsx:   # temporary kludge, presently need to know whether preparing VCS plots
            if presentation=="Yxvsx":
                self.presentation = vcsx.createyxvsx()
                type="Yxvsx"
            elif presentation == "Isofill":
                self.presentation = vcsx.createisofill()
            elif presentation == "Vector":
                self.presentation = vcsx.createvector()
            elif presentation == "Boxfill":
                self.presentation = vcsx.createboxfill()
            elif presentation == "Isoline":
                self.presentation = vcsx.createisoline()
            else:
                print "ERROR, uvc_plotspec doesn't recognize presentation",presentation
                self.presentation = "Isofill"  # try to go on
        else:
            self.presentation = presentation
        ## elif presentation == "":
        ##     self.resentation = vcsx.create
        self.vars = vars
        self.labels = labels
        self.title = title
        self.type = type
    def __repr__(self):
        return ("uvc_plotspec %s: %s\n" % (self.presentation,self.title))
    def _json(self,*args,**kwargs):
        """returns a JSON serialization of this object"""
        vars_json_list = [ v.dumps() for v in self.vars ]
        vars_json = json.dumps(vars_json_list)
        return {'vars':vars_json, 'presentation':self.presentation, 'type':self.type,\
                    'labels':self.labels, 'title':self.title }
    def write_plot_data( self, writer="" ):
        # This is just experimental code, so far.
        if writer=="" or writer=="NetCDF" or writer=="NetCDF file":
            writer = "NetCDF file"
        elif writer=="JSON string":
            pass
        elif writer=="JSON file":
            pass
        else:
            print "WARNING: write_plot_data cannot recognize writer name",writer,\
                ", will write a NetCDF file."
            writer = "NetCDF file"

        if len(self.title)<=0:
            fname = 'foo'
        else:
            fname = self.title.strip()+'.nc'
        filename = os.path.join(writer,fname)
        print "output to",filename

        if writer=="NetCDF file":
            writer = cdms2.open( filename, 'w' )    # later, choose a better name and a path!
        elif writer=="JSON file":
            print "ERROR: JSON file not implemented yet"
        elif writer=="JSON string":
            return json.dumps(self,cls=DiagsEncoder)

        for zax in self.vars:
            writer.write( zax )

        writer.close()

class DiagsEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'_json'):
            return obj._json()
        else:
            return super(DiagsEncoder,self).default(obj)

def get_plot_data( plot_set, filetable1, filetable2, variable, season ):
    """returns a list of uvc_plotspec objects to be plotted.  The plot_set is a string from
    1,2,3,4,4a,5,...,16.  Usually filetable1 indexes model data and filetable2 obs data,  but
    anything generated by setup_filetable() is ok.  The variable is a string - it can be a data
    variable from the indexed data sets, or a derived variable.  The season is a 3-letter code,
    e.g. 'DJF','ANN','MAR'.
    This is DEPRECATED and AMWG-specific.  It is better to call a method obtained by a call
    of the list_diagnostic_sets() method of BasicDiagnosticGroup and its children such as AMWG."""
    print "WARNING - deprecated function get_plot_data() has been called."
    return _get_plot_data( plot_set, filetable1, filetable2, variable, season)

# To profile, replace (by name changes) the above get_plot_data() with the following one:
def profiled_get_plot_data( plot_set, filetable1, filetable2, variable, season ):
    """returns a list of uvc_plotspec objects to be plotted.  The plot_set is a string from
    1,2,3,4,4a,5,...,16.  Usually filetable1 indexes model data and filetable2 obs data,  but
    anything generated by setup_filetable() is ok.  The variable is a string - it can be a data
    variable from the indexed data sets, or a derived variable.  The season is a 3-letter code,
    e.g. 'DJF','ANN','MAR'."""
    args = [ plot_set, filetable1, filetable2, variable, season ]
    prof = cProfile.Profile()
    returnme = prof.runcall( _get_plot_data, *args )
    prof.print_stats()   # use dump_stats(filename) to print to file
    return returnme

def _get_plot_data( plot_set, filetable1, filetable2, variable, season ):
    """the real _get_plot_data() function; get_plot_data() is a simple wrapper around this"""
    if season=='ANN':
        # cdutil.times.getMonthIndex() (called by climatology()) doesn't recognize 'ANN'
        season='JFMAMJJASOND'
    plot_set = plot_set.strip()
    from metrics.amwg.amwg import plot_set2, plot_set3, plot_set4, plot_set5
    if plot_set=='2':
        return plot_set2( filetable1, filetable2, variable )
    if plot_set=='3':
        return plot_set3( filetable1, filetable2, variable, season )
    elif plot_set=='4':
        return plot_set4( filetable1, filetable2, variable, season )
    elif plot_set=='5':
        return plot_set5( filetable1, filetable2, variable, season )
    else:
        print "ERROR, plot set",plot_set," not implemented yet!"
        return None

class basic_one_line_plot( plotspec ):
    def __init__( self, yvar, xvar=None ):
        # xvar, yvar should be the actual x,y of the plot.
        # xvar, yvar should already have been reduced to 1-D variables.
        # Normally y=y(x), x is the axis of y.
        if xvar is None:
            xvar = yvar.getAxisList()[0]
        plotspec.__init__( self, xvars=[xvar], yvars=[yvar],
                           vid = yvar.id+" line plot", plottype='Yxvsx' )

class basic_two_line_plot( plotspec ):
    def __init__( self, y1var, y2var, x1var=None, x2var=None ):
        """x?var, y?var should be the actual x,y of the plots.
        x?var, y?var should already have been reduced to 1-D variables.
        Normally y?=y(x?), x? is the axis of y?."""
        plotspec.__init__( self, y1vars=[y1var], y2vars=[y2var],
                           vid = y1var.variableid+y2var.variableid+" line plot", plottype='Yxvsx' )

class one_line_diff_plot( plotspec ):
    def __init__( self, y1var, y2var, vid ):
        """y?var should be the actual y of the plots.
        y?var should already have been reduced to 1-D variables.
        y?=y(x?), x? is the axis of y?."""
        plotspec.__init__( self,
            xvars=[y1var,y2var], xfunc = latvar_min,
            yvars=[y1var,y2var],
            yfunc=aminusb_1ax,   # aminusb_1ax(y1,y2)=y1-y2; each y has 1 axis, use min axis
            vid=vid,
            plottype='Yxvsx' )

class contour_plot( plotspec ):
    def __init__( self, zvar, xvar=None, yvar=None, ya1var=None,
                  xfunc=None, yfunc=None, ya1func=None ):
        """ zvar is the variable to be plotted.  xvar,yvar are the x,y of the plot,
        normally the axes of zvar.  If you don't specify, a x=lon,y=lat plot will be preferred.
        xvar, yvar, zvar should already have been reduced; x,y to 1-D and z to 2-D."""
        if xvar is None:
            xvar = zvar
        if yvar is None:
            yvar = zvar
        if ya1var is None:
            ya1var = zvar
        if xfunc==None: xfunc=lonvar
        if yfunc==None: yfunc=latvar
        vid = ''
        if hasattr(zvar,'vid'): vid = zvar.vid
        if hasattr(zvar,'id'): vid = zvar.id
        plotspec.__init__(
            self, vid+'_contour', xvars=[xvar], xfunc=xfunc,
            yvars=[yvar], yfunc=yfunc, ya1vars=[ya1var], ya1func=ya1func,
            zvars=[zvar], plottype='Isofill' )

class contour_diff_plot( plotspec ):
    def __init__( self, z1var, z2var, plotid, x1var=None, x2var=None, y1var=None, y2var=None,
                   ya1var=None,  ya2var=None, xfunc=None, yfunc=None, ya1func=None ):
        """We will plot the difference of the two z variables, z1var-z2var.
        See the notes on contour_plot"""
        if x1var is None:
            x1var = z1var
        if y1var is None:
            y1var = z1var
        if ya1var is None:
            ya1var = z1var
        if x2var is None:
            x2var = z2var
        if y2var is None:
            y2var = z2var
        if ya2var is None:
            ya2var = z2var
        if xfunc==None: xfunc=lonvar_min
        if yfunc==None: yfunc=latvar_min
        plotspec.__init__(
            self, plotid, xvars=[x1var,x2var], xfunc=xfunc,
            yvars=[y1var,y2var], yfunc=yfunc, ya1vars=[ya1var,ya2var], ya1func=ya1func,
            zvars=[z1var,z2var], zfunc=aminusb_2ax, plottype='Isofill' )


class plot_spec(object):
    # ...I made this a new-style class so we can call __subclasses__ .
    package=BasicDiagnosticGroup  # Note that this is a class not an object.
    def __repr__( self ):
        if hasattr( self, 'plotall_id' ):
            return self.__class__.__name__+'('+self.plotall_id+')'
        else:
            return self.__class__.__name__+' object'
    def __init__(self, seasonid='ANN', *args ):
        if seasonid=='ANN' or seasonid is None:
            # cdutil.times.getMonthIndex() (called by climatology()) doesn't recognize 'ANN'
            self._seasonid='JFMAMJJASOND'
        else:
            self._seasonid=seasonid
        self.reduced_variables = {}
        self.derived_variables = {}
        self.variable_values = {}
        self.single_plotspecs = {}
        self.composite_plotspecs = {}
        self.plotspec_values = {}
        self.computation_planned = False
    def plan_computation( self, seasonid):
        pass
    def _build_label( self, vars, p ):
        yls = []
        for y in vars:
            if type(y) is tuple:
                yl = getattr(y[0],'_vid',None)
            else:
                yl = getattr(y,'_vid',None)
            if yl is not None:
                yls.append( yl )
        new_id = '_'.join(yls)
        if new_id is None or new_id.strip()=="": new_id = p+'_2'
        return new_id
    def compute(self):
        return self.results()
    def results(self):
        return self._results()
# To profile, replace (by name changes) the above results() with the following one:
    def profiled_results(self):
        prof = cProfile.Profile()
        returnme = prof.runcall( self._results )
        prof.dump_stats('results_stats')
        return returnme
    def _results(self):
        for v in self.reduced_variables.keys():
            value = self.reduced_variables[v].reduce()
            self.variable_values[v] = value  # could be None
        postponed = []   # derived variables we won't do right away
        for v in self.derived_variables.keys():
            value = self.derived_variables[v].derive(self.variable_values)
            if value is None:
                # couldn't compute v - probably it depends on another derived variables which
                # hasn't been computed yet
                postponed.append(v)
            else:
                self.variable_values[v] = value
        for v in postponed:   # Finish up with derived variables
            value = self.derived_variables[v].derive(self.variable_values)
            self.variable_values[v] = value  # could be None
        varvals = self.variable_values
        for p,ps in self.single_plotspecs.iteritems():
            print "jfp preparing data for",ps._id
            xrv = [ varvals[k] for k in ps.xvars ]
            x1rv = [ varvals[k] for k in ps.x1vars ]
            x2rv = [ varvals[k] for k in ps.x2vars ]
            x3rv = [ varvals[k] for k in ps.x3vars ]
            yrv = [ varvals[k] for k in ps.yvars ]
            y1rv = [ varvals[k] for k in ps.y1vars ]
            y2rv = [ varvals[k] for k in ps.y2vars ]
            y3rv = [ varvals[k] for k in ps.y3vars ]
            yarv = [ varvals[k] for k in ps.yavars ]
            ya1rv = [ varvals[k] for k in ps.ya1vars ]
            zrv = [ varvals[k] for k in ps.zvars ]
            zrrv = [ varvals[k] for k in ps.zrangevars ]
            xax = apply( ps.xfunc, xrv )
            x1ax = apply( ps.x1func, x1rv )
            x2ax = apply( ps.x2func, x2rv )
            x3ax = apply( ps.x3func, x3rv )
            yax = apply( ps.yfunc, yrv )
            y1ax = apply( ps.y1func, y1rv )
            y2ax = apply( ps.y2func, y2rv )
            y3ax = apply( ps.y3func, y3rv )
            # not used yet yaax = apply( ps.yafunc, yarv )
            ya1ax = apply( ps.ya1func, ya1rv )
            zax = apply( ps.zfunc, zrv )
            # not used yet zr = apply( ps.zrangefunc, zrrv )
            vars = []
            # The x or x,y vars will hopefully appear as axes of the y or z
            # vars.  This needs more work; but for now we never want x vars here:
            xlab=""
            ylab=""
            zlab=""
            if xax is not None:
                xlab += ' '+xax.id
            if x1ax is not None:
                xlab += ' '+x1ax.id
            if x2ax is not None:
                xlab += ', '+x2ax.id
            if x3ax is not None:
                xlab += ', '+x3ax.id
            if yax is not None:
                vars.append( yax )
                new_id = self._build_label( yrv, p )
                yax.id = new_id
                ylab += ' '+yax.id
            if y1ax is not None:
                vars.append( y1ax )
                new_id = self._build_label( y1rv, p )
                y1ax.id = new_id
                ylab += ' '+y1ax.id
            if y2ax is not None:
                vars.append( y2ax )
                new_id = self._build_label( y2rv, p )
                y2ax.id = new_id
                ylab += ', '+y2ax.id
            if y3ax is not None:
                vars.append( y3ax )
                new_id = self._build_label( y3rv, p )
                y3ax.id = new_id
                ylab += ', '+y3ax.id
            if zax is not None:
                vars.append( zax )
                new_id = self._build_label( zrv, p )
                zax.id = new_id
                zlab += ' '+zax.id
            if vars==[]:
                self.plotspec_values[p] = None
                continue
            labels = [xlab,ylab,zlab]
            title = ' '.join(labels)+' '+self._seasonid  # do this better later
            self.plotspec_values[p] = uvc_plotspec( vars, self.plottype, labels, title )
        for p,ps in self.composite_plotspecs.iteritems():
            self.plotspec_values[p] = [ self.plotspec_values[sp] for sp in ps ]

        return self
        
class basic_plot_variable():
    """represents a variable to be plotted.  This need not be an actual data variable;
       it could be some derived quantity"""
    def __init__( self, name, plotset_name, package ):
        self.name = name
        self.plotset_name = plotset_name
        self.package = package
    @staticmethod
    def varoptions(*args,**kwargs):
        """returns a represention of options specific to this variable.  Example dict items:
         'vertical average':'vertavg'
         '300 mbar level value':300
        """
        return None
    
class basic_level_variable(basic_plot_variable):
    """represents a typical variable with a level axis, in a plot set which reduces the level
    axis."""
    @staticmethod
    def varoptions():
        """returns a represention of options specific to this variable.  That is, how should
        one reduce the level axis?  The default is to average along that axis.  But other options
        are to pick out the variable's value at some particular pressure level, e.g. 300 mb.
        """
        opts ={
            " default":"vertical average", " vertical average":"vertical average",
            "200 mbar":200, "300 mbar":300, "500 mbar":500, "850 mbar":850 }
        return opts
    
