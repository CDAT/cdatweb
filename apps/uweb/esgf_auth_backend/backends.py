import os
import cdms2

from myproxy_logon import myproxy_logon, GetException

from fcntl import flock, LOCK_EX, LOCK_UN
from django.contrib.auth.models import User
from django.conf import settings
if not settings.configured:
    settings.configure()

class ESGF_Auth_Backend:
    """
    Custom backend to log-in with an ESGF OpenID. Saves a certificate + private
    key as settings.proxy_cert_dir/username/username.pem
    and create .httprc if not already created as settings.proxy_cert_dir/username/.httprc
    (eg: /esgserver/proxycerts/jsmith/jsmith.pem)
    """
    def authenticate(self, username=None, password=None, peernode=None):
        try:
            cert_path=os.path.join(settings.PROXY_CERT_DIR,username)
            if not os.path.exists(cert_path):
                try:
                    os.makedirs(cert_path)
                except:
                    pass
            myproxy_logon(peernode,
                    username,
                    password,
                    os.path.join(cert_path,username + '.pem').encode("UTF-8"),
                    lifetime=43200,
                    port=settings.ESGF_PORT
                    )
        except GetException as e:
            # myproxy_logon failed, so return None instead of a User
            #
            # TODO: When Django 1.6 comes out, this should be changed to:
            #
            #     raise PermissionDenied
            #
            # This will prevent the possibility of someone listing multiple
            # authentication backends in their settings.py, thus allowing an
            # attacker to authenticate as any user simply by using the default
            # password assigned to all users created by this auth backend.
            return None
        # if we make it here, the username and password were good
        # output .httprc file if .httprc is not found
        try:
            cdms2.setHttprcDirectory(cert_path)
            filepath=os.path.join(settings.PROXY_CERT_DIR,username,".daprc")
            if not os.path.exists(filepath):
                dodsrc_cache_root=os.path.join(cert_path,".dods_cache")
                dodsrc_curl_ssl_certificate=os.path.join(cert_path,"%s.pem"%username)
                dodsrc_curl_ssl_key=os.path.join(cert_path,"%s.pem"%username)
                dodsrc_curl_ssl_capath=os.path.join(os.environ["HOME"],".esg","certificates")
                daprc_text=""
                daprc_text+="USE_CACHE=0\n"
                daprc_text+="MAX_CACHE_SIZE=20\n"
                daprc_text+="MAX_CACHED_OBJ=5\n"
                daprc_text+="IGNORE_EXPIRES=0\n"
                daprc_text+="CACHE_ROOT=%s/\n"%dodsrc_cache_root
                daprc_text+="DEFAULT_EXPIRES=86400\n"
                daprc_text+="ALWAYS_VALIDATE=0\n"
                daprc_text+="DEFLATE=0\n"
                daprc_text+="VALIDATE_SSL=1\n"
                daprc_text+="CURL.COOKIEJAR=.dods_cookies\n"
                daprc_text+="CURL.SSL.VALIDATE=1\n"
                daprc_text+="CURL.SSL.CERTIFICATE=%s\n"%dodsrc_curl_ssl_certificate
                daprc_text+="CURL.SSL.KEY=%s\n"%dodsrc_curl_ssl_key
                daprc_text+="CURL.SSL.CAPATH=%s\n"%dodsrc_curl_ssl_capath
                outfile=open(filepath, 'w')
                flock(outfile, LOCK_EX)
                outfile.write(daprc_text)
                flock(outfile, LOCK_UN)
                outfile.close()
        except Exception as e:
            print "Unable to locate .daprc\n"
            return None
        # if we make it here, the username and password were good
        # (myproxy_logon throws GetException if login fails)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Create a new user. Note that we can set password
            # to anything, because unless another authentication backend is
            # listed in settings.py's AUTHENTICATION_BACKENDS, this password
            # will never be seen.
            user = User(username=username,
                        password='password is not used, ESGF handles authentication for us')
            user.is_staff = False
            user.is_superuser = False
            user.save()
        return user
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
