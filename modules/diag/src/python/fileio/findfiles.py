#!/usr/local/uvcdat/1.3.1/bin/python

# The user provides some minimal specification of the data he wants analyzed.
# Our goal here is to find all the data files which comprise that data.

import hashlib, pickle, operator, os, functools, sys, re
import pprint
from metrics.frontend.version import version
from metrics.fileio.filetable import *

# Datafile Filters: Make one class for each atomic operation, e.g. check that it
# is a file (as opposed to directory, etc.), check the file extension,
# various other filename checks; check the file type (from its contents).
# The __call__() method applies the filter to a single candidate file.
# You will be able to combine filters by constructing an 'and','or',
# or 'not' object.

class basic_filter:
    def __call__( self, filen ):
        return True
    def __repr__( self ):
        return self.__class__.__name__

class basic_binary_filter(basic_filter):
    def __init__( self, f1, f2 ):
        self._f1 = f1
        self._f2 = f2
    def __repr__( self ):
        return basic_filter.__repr__(self)+'('+self._f1.__repr__()+','+self._f2.__repr__()+')'

# If we were to decide to require that all datafiles functions put nothing but files
# into the files variable, then the following filter would be pointless:
class f_isfile(basic_filter):
    def __call__( self, filen ):
        return os.path.isfile(filen)

class f_nc(basic_filter):
    """filter for *.nc files"""
    def __call__( self, filen ):
        return os.path.splitext(filen).lower()=='nc'

class f_startswith(basic_filter):
    """requires name to start with a specified string"""
    def __init__( self, startstring ):
        self._startstring = startstring
    def __call__( self, filen ):
        return filen.find(self._startstring)==0
    def __repr__( self ):
        return basic_filter.__repr__(self)+'("'+self._startstring+'")'

class f_and(basic_binary_filter):
    def __call__( self, filen ):
        return self._f1(filen) and self._f2(filen)
    def __repr__( self ):
        return self._f1.__repr__()+' and '+self._f2.__repr__()

class f_or(basic_binary_filter):
    def __call__( self, filen ):
        return self._f1(filen) or self._f2(filen)
    def __repr__( self ):
        return self._f1.__repr__()+' or '+self._f2.__repr__()

# Thus a filter for "is a real file, with a .nc extension" is:
#       f = f_and( f_nc(), f_isfile() )
# Or we could do that in a class by:
class f_ncfile(f_and):
    def __init__(self):
        return f_and.__init__( f_nc(), f_isfile() )


# Datafiles, the core of this module.
# Other datafiles classes may have different __init__ methods, and maybe
# even a __call__ or other methods.  For example, we may be able to automatically
# identify these directories on a machine-dependent basis (implemented
# with a mixin maybe) given portable specifications like a CMIP5
# dataset id.  And we may want to filter the directory as well
# as the file.
# But a simple dirtree_datafiles() will be enough for most users' needs.

class basic_datafiles:
    def __init__(self):
        self.files = []  # Not _files; this may be referenced from outside the class.
    def __repr__(self):
        return self.files.__repr__()
    def short_name(self):
        return ''
    def long_name(self):
        return self.__class__.__name__
    def check_filesepc(self):
        """the basic_datafiles version of this method does nothing.  See the dirtree_datafiles
        version to see what it is supposed to do."""
        return True

class dirtree_datafiles( basic_datafiles ):
    def __init__( self, root, filt=basic_filter() ):
        """Finds all the data files in the directory tree below root.
        root can be a string representing a directory, or a list
        of such strings.
        The second argument is an optional filter, of type basic_filter."""
        if root==None:
            self._root = None
            self._filt = None
            self.files = []
            return None
        root = os.path.expanduser(root)
        root = os.path.abspath(root)
        if filt==None: filt=basic_filter()
        if type(filt)==str and filt.find('filt=')==0:   # really we need to use getopt to parse args
            filt = eval(filt[5:])
        self._root = root
        self._filt = filt
        self.files = []
        basic_datafiles.__init__(self)
        if type(root)==list:
            pass
        elif type(root)==str:
            root = [root]
        else:
            raise Error("don't understand root directory %s"%root)
        for r in root:
            self._getdatafiles(r,filt)
        self.files.sort()  # improves consistency between runs
    def _getdatafiles( self, root, filt ):
        """returns all data files under a single root directory"""
        if os.path.isfile(root):
            self.files += [root]
        for dirpath,dirname,filenames in os.walk(root):
            dirpath = os.path.expanduser(dirpath)
            dirpath = os.path.abspath(dirpath)
            self.files += [ os.path.join(dirpath,f) for f in filenames if filt(f) ]
        return self.files
    def short_name(self):
        return os.path.basename(str(self._root))
    def long_name(self):
        return ' '.join( [ self.__class__.__name__, str(self._root), str(self._filt) ] )
    def check_filespec( self ):
        """method to determine whether the file specification used to build this object is useful,
        and help improve it if it's not.
        There are three possible return values:
            - True if the file specification unambiguously defines useful data
            - None if the file specification defines no useful data
            - a dict if the file specification defines useful data but with ambiguities.  For example,
            the specification may be simply a directory which contains two sets of obs data, and both
            contain surface temperatures throughout the world.  The dict can be used to determine a menu
            for resolving the ambiguities.
            - If the output be a dict, each key will be a string, normally a dataset name.  Each value
            will be a filter which narrows down the filter used to construct this object enough to
            resolve the ambiguity.
            Normally this filter will constrain the filenames so each file belongs to the selected
            dataset.
            - If the output be a dict and one of its values be chosen, this can be used as the
            search_filter argument for a call of setup_filetable."""
        famdict = { f:extract_filefamilyname(f) for f in self.files }
        families = list(set([ famdict[f] for f in self.files if famdict[f] is not None]))
        families.sort(key=len)  # a shorter name is more likely to be what we want
        if len(families)==1: return True
        if len(families)==0: return None
        # Ambiguous file specification!  Make a menu out of it.
        famdict = {}
        for fam in families:
            famdict[fam] = f_and( self._filt, f_startswith(fam) )
        return famdict
    def setup_filetable( self, cache_path, ftid=None ):
        """Returns a file table (an index which says where you can find a variable) for files in the
        supplied search path, satisfying the optional filter.  It will be useful if you provide a name
        for the file table, the string ftid.  For example, this may appear in names of variables to be
        plotted.  This function will cache the file table and
        use it if possible.  If the cache be stale, call clear_filetable()."""
        if ftid is None:
            ftid = self.short_name()

        cache_path = os.path.expanduser(cache_path)
        cache_path = os.path.abspath(cache_path)
        datafile_ls = [ f+'size'+str(os.path.getsize(f))+'mtime'+str(os.path.getmtime(f))\
                            for f in self.files ]
        search_string = ' '.join(
            [self.long_name(),cache_path,version,';'.join(datafile_ls)] )
        csum = hashlib.md5(search_string).hexdigest()
        cachefilename = csum+'.cache'
        cachefile=os.path.normpath( cache_path+'/'+cachefilename )

        if os.path.isfile(cachefile):
            f = open(cachefile,'rb')
            try:
                filetable = pickle.load(f)
                cached=True
            except:
                cached=False
            f.close()
        else:
            cached=False
        if cached==False:
            filetable = basic_filetable( self, ftid )
            f = open(cachefile,'wb')
            pickle.dump( filetable, f )
            f.close()
        return filetable
    def clear_filetable( self, cache_path ):
        """Deletes (clears) the cached file table created by the corresponding call of setup_filetable"""
        cache_path = os.path.expanduser(cache_path)
        cache_path = os.path.abspath(cache_path)
        # >>> problem with this: if the file is absent we definitely want to get rid of
        # >>> the cached filetable, but we can't compute datafile_ls!!!! >>>>>>
        datafile_ls = [ f+'size'+str(os.path.getsize(f))+'mtime'+str(os.path.getmtime(f))\
                            for f in self.files ]
        search_string = ' '.join(
            [self.long_name(),cache_path,version,';'.join(datafile_ls)] )
        csum = hashlib.md5(search_string).hexdigest()
        cachefilename = csum+'.cache'
        cachefile=os.path.normpath( cache_path+'/'+cachefilename )

        if os.path.isfile(cache_path):
            os.remove(cache_path)



def extract_filefamilyname( filename ):
        """
        From a filename, extracts the first part of the filename as the possible
        name of a family of files; e.g. from 'ts_Amon_bcc-csm1-1_amip_r1i1p1_197901-200812.nc'
        extract and return 'ts_Amon_bcc-csm1-1_amip_r1i1p1'.    Or from
        'b30.009.cam2.h0.0600-01.nc' extract and return 'b30.009.cam2.h0'.  Or from
        'CRU_JJA_climo.nc', extract and return 'CRU'.
        """
        # The algorithm is:
        # 1. Look for '_SSS_climo.nc' (at end) where SSS are letters (really SSS is one
        #   (of the 17 standard season codes, but I'm not checking that carefully).
        #   This is a climatology file.  Return the rest of the name.
        # 2. Look for '_nnn-nnn.nc' (at end) where nnn is any number>0 of digits.  This is a CMIP5
        # time-split file.  Return the rest of the name.
        # 3. Look for '.nnn-nnn.nc' (at end) where nnn is any number>0 of digits.  This is a CCSM
        # history tape file.  Return the rest of the name.
        # I surely will have to adjust this algorithm as I encounter more files.
        fn = os.path.basename(filename)
        matchobject = re.search( r"\.nc$", fn )
        if matchobject is None:
            return None
        matchobject = re.search( r"_\w\w\w_climo\.nc$", fn )
        if matchobject is not None:  # climatology file, e.g. CRU_JJA_climo.nc
            return fn[0:matchobject.start()] # e.g. CRU
        matchobject = re.search( r"_\d\d_climo\.nc$", fn )
        if matchobject is not None:  # climatology file, e.g. CRU_11_climo.nc
            return fn[0:matchobject.start()] # e.g. CRU
        matchobject = re.search( r"_\d\d*-\d\d*\.nc$", fn )
        if matchobject is not None: # CMIP5 file eg ts_Amon_bcc-csm1-1_amip_r1i1p1_197901-200812.nc
            return fn[0:matchobject.start()] # e.g. ts_Amon_bcc-csm1-1_amip_r1i1p1
        matchobject = re.search( r"\.\d\d*-\d\d*\.nc$", fn )
        if matchobject is not None: # CAM file eg b30.009.cam2.h0.0600-01.nc
            return fn[0:matchobject.start()] # e.g. b30.009.cam2.h0
        return fn

if __name__ == '__main__':
    if len( sys.argv ) == 2:
        datafiles = dirtree_datafiles( sys.argv[1] )
    elif len( sys.argv ) == 3:    # see above about needing to use the getopt library
        datafiles = dirtree_datafiles( sys.argv[1], sys.argv[2] )
    else:
        print "usage: findfiles.py root  or  findfiles.py root filt=filter"

