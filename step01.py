#!/usr/bin/env python
import datetime

from mako.template import Template
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
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
        self.identity = request.cookies.get("userid", None)

    def response(self, msg):
        return Response(main_template.render(
                request=self.request,
                msg=msg,
                identity=self.identity
            ))

    @view_config(route_name="root")
    def root_view(self):
        return self.response(["HOME"])

    @view_config(route_name="login")
    def login_view(self):
        userid = self.request.params.get("userid")
        response = self.response(["LOGGED IN", userid ])
        response.set_cookie("userid", str(userid))
        #response.set_cookie("userid", str(userid), secure=1)    # secure flag
        #response.set_cookie("userid", str(userid), max_age=600) # 600 seconds - survives browser restart
        return response


    @view_config(route_name="logout")
    def logout_view(self):
        response = self.response(["LOGGED OUT" ])
        response.delete_cookie("userid")
        #response.set_cookie("userid", "", max_age=-1)
        return response

if __name__ == '__main__':
    config = Configurator()
    config.add_route('root', '')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)

