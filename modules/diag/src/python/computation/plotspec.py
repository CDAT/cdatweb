#!/usr/local/uvcdat/1.3.1/bin/python

# general-purpose classes used in computing data for plots

class derived_var:
    def __init__( self, vid, inputs=[], outputs=['output'], func=(lambda: None) ):
        self._vid = vid
        self._inputs = inputs
        self._outputs = outputs
        self._func = func
    def derive( self, vardict ):
        # error from checking this way!... if None in [ vardict[inp] for inp in self._inputs ]:
        dictvals = [ vardict.get(inp,None) for inp in self._inputs ]
        nonevals = [nn for nn in dictvals if nn is None]
        if len(nonevals)>0:
            return None
        output = apply( self._func, [ vardict[inp] for inp in self._inputs ] )
        if type(output) is tuple or type(tuple) is list:
            for o in output:
                o._vid  = self._vid
        elif output is not None:
            output._vid = self._vid
        return output

class plotspec:
    def __init__(
        self, vid,
        xvars=[], xfunc=None, x1vars=[], x1func=None,
        x2vars=[], x2func=None, x3vars=[], x3func=None,
        yvars=[], yfunc=None, y1vars=[], y1func=None,
        y2vars=[], y2func=None, y3vars=[], y3func=None,
        yavars=[], yafunc=None, ya1vars=[], ya1func=None,
        zvars=[], zfunc=None, zrangevars=[], zrangefunc=None, plottype='table'
        ):
        """Initialize a plotspec (plot specification).  Inputs are an id and plot type,
        and lists of x,y,z variables (as keys in the plotvars dictionary), functions to
        transform these variables to the quanitity plotted, and a plot type (a string).
        A recommended range in z can be computed by applying zrangefunc to zrangevars;
        the normal use of this feature is to make two plots compatible.  Alternate graph
        axes may be specified - e.g. ya to substitute for y in a plot, or ya1 as an addition
        to y in the plot.
        """
        if xfunc==None:
            if len(xvars)==0:
                xfunc = (lambda: None)
            else:
                xfunc = (lambda x: x)
        if x1func==None:
            if len(x1vars)==0:
                x1func = (lambda: None)
            else:
                x1func = (lambda x: x)
        if x2func==None:
            if len(x2vars)==0:
                x2func = (lambda: None)
            else:
                x2func = (lambda x: x)
        if x3func==None:
            if len(x3vars)==0:
                x3func = (lambda: None)
            else:
                x3func = (lambda x: x)
        if yfunc==None:
            if len(yvars)==0:
                yfunc = (lambda: None)
            else:
                yfunc = (lambda y: y)
        if y1func==None:
            if len(y1vars)==0:
                y1func = (lambda: None)
            else:
                y1func = (lambda y: y)
        if y2func==None:
            if len(y2vars)==0:
                y2func = (lambda: None)
            else:
                y2func = (lambda y: y)
        if y3func==None:
            if len(y3vars)==0:
                y3func = (lambda: None)
            else:
                y3func = (lambda y: y)
        if yafunc==None:
            if len(yavars)==0:
                yafunc = (lambda: None)
            else:
                yafunc = (lambda ya: ya)
        if ya1func==None:
            if len(ya1vars)==0:
                ya1func = (lambda: None)
            else:
                ya1func = (lambda ya: ya)
        if zfunc==None:
            if len(zvars)==0:
                zfunc = (lambda: None)
            else:
                zfunc = (lambda z: z)
        if zrangefunc==None:
            zrangefunc = (lambda: None)
        self._id = vid
        self.xfunc = xfunc
        self.xvars = xvars
        self.x1func = x1func
        self.x1vars = x1vars
        self.x2func = x2func
        self.x2vars = x2vars
        self.x3func = x3func
        self.x3vars = x3vars
        self.yfunc = yfunc
        self.yvars = yvars
        self.y1func = y1func
        self.y1vars = y1vars
        self.y2func = y2func
        self.y2vars = y2vars
        self.y3func = y3func
        self.y3vars = y3vars
        self.yafunc = yafunc
        self.yavars = yavars
        self.ya1func = ya1func
        self.ya1vars = ya1vars
        self.zfunc = zfunc
        self.zvars = zvars
        self.zrangevars = zrangevars
        self.zrangefunc = zrangefunc
        self.plottype = plottype
    def __repr__(self):
        return "plotspec _id=%s xvars=%s xfunc=%s yvars=%s yfunc=%s zvars=%s zfunc=%s" %\
            (self._id,self.xvars,self.xfunc.__name__,self.yvars,self.yfunc.__name__,\
                 self.zvars,self.zfunc.__name__)
    
