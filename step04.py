#!/usr/bin/env python
from collections import defaultdict
import datetime
import hashlib
import logging
import random
import time

from mako.template import Template
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPBadRequest
from waitress import serve

main_template = Template("""<html><head>
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
</head><body>
<h1>TRICYCLES</h1>
<a href="${ request.route_url('root') }">HOME</a><br/>
<hr/>
<a href="${ request.route_url('login', _query={'userid': 'john'}) }">Login as john</a><br/>
<a href="${ request.route_url('login', _query={'userid': 'bob'}) }">Login as bob</a><br/>
<hr/>
<a href="${ request.route_url('passwd') }">Change Password</a><br/>
<a href="${ request.route_url('logout') }">Logout</a><br/>
<hr/>
${ msg }
<hr/>
User ID: ${ identity if not identity is None else "--not-set--" }
</body></html>""")

def calculate_digest(secret, userid, usersalt, timestamp, ip):
    m = hashlib.sha1()
    m.update(str(secret))
    m.update(str(userid))
    m.update(str(usersalt))
    m.update(str(timestamp))
    m.update(str(ip))
    return m.hexdigest()

class View(object):
    SECRET = "verysecretstring"
    USER_SALT = defaultdict(lambda : str(random.randint(1000000, 9999999)))
    def _encode_cookie(self, userid):
        ip = ""
        ts = int(time.time())
        digest = calculate_digest(self.SECRET, userid, self.USER_SALT[userid], ts, ip)
        return "%s-%s-%s" % (digest, ts, userid)

    def _decode_cookie(self):
        cookie = self.request.cookies.get("userid", None)
        if not cookie:
            return None
        # try to extract a userid and timestamp from the cookie
        try:
            (digest, ts, userid) = cookie.split("-", 2)
            logging.info("cookie splitted up:%s-%s-%s" % (digest, ts, userid, ))
        except:
            logging.error("BAD COOKIE FORMAT:%s|" % cookie)
            response = HTTPBadRequest()
            response.delete_cookie("userid")
            raise response
        ip = ""
        d2 = calculate_digest(self.SECRET, userid, self.USER_SALT[userid], ts, ip)
        if d2==digest:
            return userid
        logging.error("bad digest")
        response = HTTPBadRequest()
        response.delete_cookie("userid")
        raise response

    def __init__(self, request):
        self.request = request
        self.identity = self._decode_cookie()

    def response(self, msg):
        return Response(main_template.render(
                request=self.request,
                msg=msg,
                identity=self.identity
            ))

    @view_config(route_name="root", )
    def root_view(self):
        return self.response(["HOME"])

    @view_config(route_name="login", )
    def login_view(self):
        userid = self.request.params.get("userid")
        response = self.response(["LOGGED IN", userid ])
        response.set_cookie("userid", self._encode_cookie(userid), httponly=1)    # session - cleared with browser exit
        return response

    @view_config(route_name="logout", )
    def logout_view(self):
        response = self.response(["LOGGED OUT" ])
        response.delete_cookie("userid")
        return response

    @view_config(route_name="passwd")
    def passwd_view(self):
        # When the user changes the password, we generate a new random string
        # and "store it into the database with the password".
        del self.USER_SALT[self.identity]
        # Then we re-generate the cookie, otherwise we will be logged out.
        response = self.response(["PASSWORD CHANGED", self.identity ])
        response.set_cookie("userid", self._encode_cookie(self.identity), httponly=1)    # session - cleared with browser exit
        return response

if __name__ == '__main__':
    config = Configurator()
    config.add_route('root', '')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('passwd', '/password')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)

