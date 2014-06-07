import os
import jinja2
import webapp2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
  loader = jinja2.FileSystemLoader(template_dir),
  autoescape = True
)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))

class Posts(db.Model):
  subject = db.StringProperty(required = True)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)

class NewPost(Handler):
  def render_form(self, subject = "", content = "", error = ""):
    self.render("newpost.html", subject = subject, content = content, error = error)

  def get(self):
    self.render_form()

  def post(self):
    subject = self.request.get("subject") 
    content = self.request.get("content")

    if subject and content:
      a = Posts(subject = subject, content = content)
      a.put()
      self.redirect("/" + str(a.key().id()))
    else:
      error = "Need to enter both a subject and some content"
      self.render_form(subject, content, error)

class MainPage(Handler):

  def get(self):
    posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC")
    self.render('posts.html', posts = posts)

class GetPost(Handler):

  def get(self, post_id):
    post_id = int(post_id)
    blog_post = Posts.get_by_id(post_id)
    self.render('post.html', blog_post = blog_post)

app = webapp2.WSGIApplication(
  [
    ('/', MainPage),
    ('/newpost', NewPost),
    (r'/(\d+)', GetPost), 
  ],
  debug = True
)