
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users

import jinja2
import os
import time


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

class Blogentry(ndb.Model):
    """docstring for Blogentry"""
    comment = ndb.StringProperty()
    username = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
        

class Handler(webapp2.RequestHandler):
    def write(self, **kw):
        self.response.out.write(**kw)

    def render_str(self, template, **params):
        print "in render_str"
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        print "in render"
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def get(self):
        global errors
        user = users.get_current_user()

        if user:
            # self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
            # self.response.write('Hello, ' + user.nickname())
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout' + " (" + user.nickname() + ")"
        else:
            # self.redirect(users.create_login_url(self.request.uri))
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login (Optional)'

        query = Blogentry.query().order(-Blogentry.date)
        be_list = query.fetch()

        errors = self.request.get('errors')
        template_values = {
            'errors' : errors,
            'user' : user,
            'entries' : be_list,
            'url' : url,
            'url_linktext' : url_linktext
        }
        
        
        # self.render("blog_comments.html", entries = be_list)
        # self.render("blog_comments.html", template_values = template_values)
        t2 = jinja_env.get_template("blog_comments.html")
        self.response.write(t2.render(template_values))

class AddHandler(Handler):
    def post(self):
        current_comment = self.request.get('content')
        user = users.get_current_user()
        if user:
            current_user = user.nickname()
        else:
            current_user = "Anonymous"
        if current_comment == "":
            errors = "Empty comment submitted!"
            redirect_url = "/?errors=" + errors
            self.redirect(redirect_url)
        else:    
            be = Blogentry(comment = current_comment, username = current_user)
            be.put()
            time.sleep(.1)
            self.redirect("/")
		
				
app = webapp2.WSGIApplication([("/", MainPage),
                               ("/addblogentry", AddHandler)

                              ])