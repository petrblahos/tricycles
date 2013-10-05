#!/usr/bin/env python
import datetime
import os.path

from mako.template import Template
from pyramid.response import Response
from pyramid.security import remember, forget, Authenticated, Everyone
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
<a href="${ request.route_url('logout') }">Logout</a><br/>
<hr/>
${ msg }
<hr/>
User ID: ${ identity if not identity is None else "--not-set--" }
</body></html>""")

class View(object):
    def __init__(self, request):
        self.request = request

    def response(self, msg, headers=[]):
        return Response(main_template.render(
                request=self.request,
                msg=msg,
                identity="IIII",
            ),
            headers=headers
        )

    @view_config(route_name="root", )
    def root_view(self):
        return self.response(["HOME"])

    @view_config(route_name="login", )
    def login_view(self):
        userid = self.request.params.get("userid")
        return self.response(["LOGGED IN", userid, ], headers=remember(self.request, userid))

    @view_config(route_name="logout", )
    def logout_view(self):
        self.request.response.delete_cookie("userid")
        return self.response(["LOGGED OUT", ], headers=forget(self.request, userid))

class DumbAuthenticationPolicy(object):
    def unauthenticated_userid(self, request):
        userid = request.cookies.get('userid')
        return userid

    authenticated_userid = unauthenticated_userid

    def effective_principals(self, request):
        principals = [Everyone]
        userid = self.unauthenticated_userid(request)
        if userid is not None:
            principals.append(Authenticated)
            principals.append(userid)
        return principals

    def remember(self, request, principal, **kw):
        return [
            ('Set-Cookie',
             'userid=%s' % str(principal))
            ]

    def forget(self, request):
        return [
            ('Set-Cookie',
             'userid=deleted; Expires=Thu, 01-Jan-1970 00:00:01 GMT')
            ]

class DumbAuthorizationPolicy(object):
    def permits(self, context, principals,
                permission):
        if permission == 'delete':
            return Authenticated in principals
        return False

if __name__ == '__main__':
    authn_policy = DumbAuthenticationPolicy()
    authz_policy = DumbAuthorizationPolicy()
    config = Configurator(
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
        )
    config.add_route('root', '')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)



