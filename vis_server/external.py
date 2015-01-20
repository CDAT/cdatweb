
# import this here to avoid repeating in every protocol
try:
    # recent versions
    from autobahn.wamp import register as _exportRpc

except ImportError:
    try:
        from autobahn.wamp import procedure as _exportRpc
    except ImportError:

        from autobahn.wamp import exportRpc as _exportRpc

exportRpc = _exportRpc
