import types
import sys
import traceback

from paraview.web import protocols as pv_protocols
from autobahn.wamp import exportRpc

import protocol
import functools


#//////////////////////////////////////////////////////////////////////////////
#
# Helper function to bind RPC
#
#//////////////////////////////////////////////////////////////////////////////
def bindRpc(cls, ns, name, mctor):
  fullName = name
  rpcName = name

  if ns is not None:
    rpcName = ns + ':' + name
    fullName = '__' + ns + '_' + name

  rpc = types.MethodType(exportRpc(rpcName)(mctor(fullName)), None, cls)
  setattr(cls, fullName, rpc)

#//////////////////////////////////////////////////////////////////////////////
#
# Helper function to add mapped RPC
# UVisProtocol, "_plots", "plot", rpc)
#//////////////////////////////////////////////////////////////////////////////
def addMappedRpc(cls, objs, ns, call):
  call_lc = call[0].lower() + call[1:]

  def createRpc(call):
    def dispatchRpc(self, i, *args, **kwargs):
      c = getattr(self, objs)
      if i in c:
        return getattr(c[i], call_lc)(*args, **kwargs)
    return dispatchRpc

  bindRpc(cls, ns, call, createRpc)

#//////////////////////////////////////////////////////////////////////////////
#
# Decorator used to expose RPC endpoints
#//////////////////////////////////////////////////////////////////////////////
class export(object):
    def __init__(self, *pargs, **kwargs):

        # No args
        if len(pargs) == 1 and not kwargs and callable(pargs[0]):
            self.f = pargs[0]
            self.name = self.f.__name__
        else:
            # We support name as position or named argument
            if len(pargs) == 1 and len(kwargs) == 0:
                self.name = pargs[0]
            elif len(kwargs) == 1 and 'name' in kwargs and len(pargs) == 0:
                self.name = kwargs['name']
            else:
                raise ValueError("Invalid arguments to decorator")

        self._registerRpc()

    def _registerRpc(self):
        addMappedRpc(protocol.UVisProtocol, "_plots", "plot", self.name)
        print "registering %s" % (self.name)

    def __call__(self, *pargs, **kwargs):
        if len(pargs) == 1 and not kwargs and callable(pargs[0]):
            return pargs[0]
        else:
            return self.f(*pargs, **kwargs)

    def __get__(self, instance, type=None):

        return functools.partial(self.__call__, instance)
