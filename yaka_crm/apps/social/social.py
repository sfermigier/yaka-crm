from datetime import datetime, timedelta
from os.path import join, dirname

from flask import Blueprint, render_template, redirect, g, make_response, request
#from flaskext.babel import lazy_gettext as _
from flask.ext.babel import gettext as _

from yaka.core import signals
from yaka.core.subjects import User, Group
from yaka.core.util import get_params
from yaka.core.extensions import db, mail
from yaka.services.image import crop_and_resize
from yaka.web.frontend import BreadCrumbs

from .content import Message, TagApplication
from .util import Env

__all__ = ['social']

ROOT = '/social'
social = Blueprint("social", __name__, url_prefix=ROOT)


def make_bread_crumbs(path="", label=None):
  bread_crumbs = BreadCrumbs([("/", "Home"), ("/social/", "Social")])
  if label:
    return bread_crumbs + (path, label)
  else:
    return bread_crumbs


@social.before_request
def before_request():
  g.groups = g.user.groups
  g.groups.sort(lambda x, y: cmp(x.name, y.name))


@social.route("/")
def home():
  e = Env()
  e.bread_crumbs = make_bread_crumbs()

  #group_ids = [None] + [ group.id for group in g.user.groups ]

  messages = Message.query.filter(Message.group_id==None).all()
  for group in g.user.groups:
    messages += Message.query.filter(Message.group_id==group.id).all()
  messages.sort(lambda x, y: -cmp(x.id, y.id))
  e.messages = messages

  # Alternate technique
  #  group_ids = [ group.id for group in g.user.groups ]
  #  messages = Message.query.filter(Message.group_id.in_(group_ids)) \
  #      .order_by(Message.created_at) \
  #      .limit(20).all()

  e.groups = Group.query.order_by(Group.name).all()

  e.latest_visitors = User.query.order_by(User.last_active.desc()).limit(15).all()
  one_minute_ago = (datetime.utcnow()-timedelta(0, 60))
  e.active_visitors_count = User.query.filter(User.last_active > one_minute_ago).count()

  tag_applications = TagApplication.query.filter()

  #select = tagging.select()
  #print str(select)
  #top_tags = db.engine.execute(select)

  return render_template("social/home.html", **e)


@social.route("/stream/<stream_name>")
def stream(stream_name):
  pass


@social.route("/", methods=['POST'])
def share():
  d = get_params(Message.__editable__)
  message = Message(**d)
  db.session.add(message)

  tags = message.tags
  values = [ {'tag': tag, 'message_id': message.id} for tag in tags ]
  #db.engine.execute(tagging.insert(), values)

  db.session.commit()
  signals.entity_created.send(message)

  return redirect(ROOT)


@social.route("/private/")
def private():
  return "Not done yet."


@social.route("/private/", methods=['POST'])
def private_post():
  """Post a private message."""
  return "Not done yet."


@social.route("/<users_or_groups>/<int:id>/mugshot")
def mugshot(users_or_groups, id):
  size = int(request.args.get('s', 0))
  if size > 500:
    raise Exception("Error, size = %d" % size)

  if users_or_groups == "users":
    subject = User.query.get(id)
    photo = subject.photo
    if not photo:
      photo = get_default_picture("user")
  else:
    subject = Group.query.get(id)
    photo = subject.photo
    if not photo:
      photo = get_default_picture("group")

  if size:
    photo = crop_and_resize(photo, size)

  response = make_response(photo)
  response.headers['content-type'] = 'image/jpeg'
  return response


def get_default_picture(type):
  path = join(dirname(__file__), "..", "..", "static", "images", "user-%s.png" % type)
  photo = open(path).read()
  return photo
