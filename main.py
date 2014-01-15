import os

import webapp2
import jinja2

from google.appengine.ext import ndb
from google.appengine.api import users

import parse

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                                'template')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


SAMPLE_PROGRAM = """\
# Lines that start with "#" are comments.
# Every program is a list, each step starting with a "- "
# Every step starts with a duration like "5m" or "1m30s" or "15s".
# A step can have two parts, divided by a slash, like:
#
#  10m easy/zI
#
# To repeat a list group, use <qty>x, and indent the list underneath.
#
# Here's an example:

- 5m warm up/zII
- 5x:
  - 15s super-hard/zIV
  - 1m15s easy/zI
- 5x:
  - 30s super-hard/zIV
  - 30s easy/zI
- 10m cool down/zII'
"""

def template_file(filename):
    """Return absolute path to template file."""
    return JINJA_ENVIRONMENT.get_template(filename)


class HandlerMixin(object):
    """Extra func mixin for handlers."""

    def template_dict(self, dflt=None):
        """Create a template dict with some globally-applicable context
        variables populated."""
        if not dflt:
            dflt = dict()
        if users.get_current_user():
            dflt['user'] = users.get_current_user()
            dflt['session_url'] = users.create_logout_url(self.request.uri)
        else:
            dflt['session_url'] = users.create_login_url(self.request.uri)
        return dflt


class Program(ndb.Model):
    """A workout program consisting of several stages of varying intensity."""
    owner = ndb.StringProperty()
    desc = ndb.StringProperty(verbose_name='Description')
    added = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    program_code = ndb.TextProperty(verbose_name='Program Definition')
    
class MainHandler(webapp2.RequestHandler, HandlerMixin):
    def get(self):
        programs_q = Program.query(Program.owner==users.get_current_user().user_id())
        programs = programs_q.fetch(100)
        template_values = self.template_dict({
            'programs': programs,
        })

        template = template_file('index.html')
        self.response.out.write(template.render(template_values))


class ProgramHandler(webapp2.RequestHandler, HandlerMixin):
    def get(self, program_id=None):
        template_values = self.template_dict()
        if program_id:
            program = Program.get_by_id(int(program_id))
            template_values['id'] = program.key.id()
            template_values['desc'] = program.desc
            template_values['code'] = program.program_code
        else:
            template_values['id'] = ''
            template_values['desc'] = 'New program'
            template_values['code'] = SAMPLE_PROGRAM
        template = template_file('program.html')
        self.response.out.write(template.render(template_values))

    def post(self, program_id=None):
        owner = users.get_current_user().user_id()
        if program_id:
            program = Program.get_by_id(int(program_id))
        else:
            program = Program()
        program.owner = owner
        program.desc = self.request.POST['desc']
        if 'program_code' in self.request.POST:
            program.program_code = self.request.POST['program_code']
        program.put()
        self.redirect('/')


class ProgramRunHandler(webapp2.RequestHandler, HandlerMixin):
    def get(self, program_id=None):
        program = Program.get_by_id(int(program_id))
        rendered = parse.flatten(parse.parse_workout(program.program_code))
        template_values = {
            'json': rendered
        }
        template = template_file('program_run.html')
        self.response.out.write(template.render(template_values))


application = webapp2.WSGIApplication(
    [('/program/(\w+)/run', ProgramRunHandler),
     ('/program/(\w+)?', ProgramHandler),
     ('/', MainHandler),
     ],
    debug=True)
