import webapp2
from google.appengine.ext import db
import random
import urllib
from webapp2_extras import jinja2


class UrlData(db.Model):
    url = db.StringProperty()
    code = db.StringProperty()


class newUrl:
    CodeFrom = "abcdefghijklmnopqrstuvwxyz1234567890"

    def __init__(self, url):
        self.url = url

    def checkCode(self):
        if len(self.code) < 3:
            return 1
        back = UrlData.gql("WHERE code = :1 LIMIT 1", self.code)
        return back.count(1) > 0

    def makeCode(self):
        self.code = str(random.randint(0, 9))
        while self.checkCode():
            self.code += self.CodeFrom[
                random.randint(0, len(self.CodeFrom) - 1)]

    def build(self):
        self.makeCode()
        info = UrlData(url=self.url, code=self.code)
        info.put()
        return self.code


def getCode(url):
    # get the code for the url
    data = UrlData.gql("WHERE url = :1 LIMIT 1", url)
    if data.count(1) > 0:
        return data.fetch(1)[0].code
    else:
        u = newUrl(url)
        return u.build()


def getUrl(code):
    # get the url from the code
    data = UrlData.gql("WHERE code = :1 LIMIT 1", code)
    url = ""
    for urls in data:
        url = urls.url
    return url


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, _template, **template_args):
        rv = self.jinja2.render_template(_template, **template_args)
        self.response.write(rv)


class URLHandler(BaseHandler):
    def get(self, parm=""):
        url = ""
        code = ""
        disp_url = url
        template_args = {
            'code': code,
            'url': url,
            'disp_url': disp_url
        }
        if parm == 'create.html':
            parm = self.request.get('url')
        if len(parm) > 0:
            if parm.lower().startswith('http'):
                code = getCode(parm)
            else:
                url = getUrl(parm)
                if len(url) > 0:
                    url = urllib.unquote_plus(url)
                    return

        url = urllib.unquote_plus(parm)
        disp_url = url
        if len(disp_url) > 40:
            disp_url = disp_url[0:40] + '...'

        if len(code) == 0:
            self.render_template('index.html', **template_args)
        else:
            self.render_template('create.html', **template_args)


application = webapp2.WSGIApplication([
    (r'/', URLHandler),
], debug=True)


def main():
    application.run()

if __name__ == '__main__':
    main()
