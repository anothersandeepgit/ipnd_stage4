
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
        

class MainPage(webapp2.RequestHandler):
    def get(self):
        page2get = self.request.GET.getall('display_page')

        if page2get and page2get[0] == 'comments':
            global errors
            user = users.get_current_user()

            if user:
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Logout' + " (" + user.nickname() + ")"
            else:
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
            display_page = "blog_comments.html"
        else:
            template_values = {}
            display_page = "notes.html"
            
        t2 = jinja_env.get_template(display_page)
        self.response.write(t2.render(template_values))

class AddHandler(webapp2.RequestHandler):
    def post(self):
        current_comment = self.request.get('content')
        current_comment = current_comment.strip()
        user = users.get_current_user()

        if user:
            current_user = user.nickname()
        else:
            current_user = "Anonymous"

        if current_comment == "":
            errors = "Empty comment submitted!"
            redirect_url = "/?display_page=comments&errors=" + errors
        else:    
            be = Blogentry(comment = current_comment, username = current_user)
            be.put()
            delay = 0.1
            time.sleep(delay)
            redirect_url = "/?display_page=comments"

        self.redirect(redirect_url)
		
				
app = webapp2.WSGIApplication([("/", MainPage),
                               ("/addblogentry", AddHandler)
                              ])