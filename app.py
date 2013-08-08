import webapp2
from paste import httpserver

from webapp2_extras import jinja2


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, _template, **context):
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)


class HomeHandler(BaseHandler):
    def get(self):
        context = {'message': 'Hello, World!'}
        self.render_template('layout.html', **context)


application = webapp2.WSGIApplication([
    (r'/', HomeHandler),
], debug=True)


def main():
    httpserver.serve(application, host='127.0.0.1:8080')
    application.run()

if __name__ == '__main__':
    main()
