import cgi
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
import random
import urllib
import os
from google.appengine.ext.webapp import template
from urlparse import urlparse
import sys

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
		self.code = str(random.randint(0,9))
		while self.checkCode():
			self.code += self.CodeFrom[random.randint(0, len(self.CodeFrom) - 1)]
	def build(self):
		self.makeCode()
		info = UrlData(url = self.url, code = self.code)
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
class UrlHandler(webapp.RequestHandler):
	def get(self, parm = ""):
		url = ""
		code = ""
		if parm == 'create.html':
                        parm = self.request.get('url')
		if len(parm) > 0:
                        if parm.lower().startswith('http'):
                                #hostname = hostnameGet(parm)
                                #if blacklisted(hostname) == 1:
                                #        code = "blacklisted"
                                #else:
                                code = getCode(parm)
                        else:
                                url = getUrl(parm)
                                if len(url) > 0:
                                        url = urllib.unquote_plus(url)
                                        #print "Status: 301"
                                        #print "Location: " + url
                                        self.response.headers.add_header("Window-target", "_top")
                                        self.response.out.write("<html><head><META HTTP-EQUIV=\"Refresh\" CONTENT=\"0;URL=" + url + "\"><META HTTP-EQUIV=\"Window-target\" CONTENT=\"_top\"><script type='text/javascript'>top.location.href='" + url + "';</script></head><body></body></html>")
                                        return
                                        #sys.exit(1)

                url = urllib.unquote_plus(parm)
                disp_url = url
                if len(disp_url) > 40:
                        disp_url = disp_url[0:40] + '...'
                template_values = {
                'code': code,
                'url': url,
                'disp_url': disp_url
                }
                if len(code) == 0:
                        path = os.path.join(os.path.dirname(__file__), 'index.html')
                else:
                        path = os.path.join(os.path.dirname(__file__), 'create.html')

                self.response.out.write(template.render(path, template_values))

def hostnameGet(url):
    return urlparse(url)[1]

def main():

  #Used for normal request.
  application = webapp.WSGIApplication([('/', UrlHandler)],
                                       debug=True)
  #Enable url rewrite /{url or code}.
  application = webapp.WSGIApplication([('/(.*)', UrlHandler)],
                                       debug=True)

  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
