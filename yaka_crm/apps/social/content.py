"""
Social content items: messages aka status updates, private messages, etc.
"""
import re

from sqlalchemy.orm.query import Query
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, LargeBinary

from yaka.core.subjects import User, Group
from yaka.core.entities import Entity, SEARCHABLE
from yaka.core.extensions import db

__all__ = ['Message', 'PrivateMessage']


class MessageQuery(Query):

  def by_creator(self, user):
    return self.filter(Message.creator_id==user.id)


class Message(Entity):
  """Message aka Status update aka Note.

  See: http://activitystrea.ms/head/activity-schema.html#note
  """
  __tablename__ = 'message'
  __editable__ = ['content']
  __exportable__ = __editable__ + ['id', 'created_at', 'updated_at', 'creator_id', 'owner_id']

  content = Column(UnicodeText, info=SEARCHABLE)
  # Nullable: if null, then message is public.
  group_id = Column(Integer, ForeignKey(Group.id))

  query = db.session.query_property(MessageQuery)

  @property
  def tags(self):
    return re.findall("#([^\W]+)(?u)", self.content)


# TODO: inheriting from Entity is overkill here
class TagApplication(Entity):
  __tablename__ = 'tag_application'

  tag = Column(UnicodeText, index=True)
  message_id = Column(Integer, ForeignKey('message.id'))


class PrivateMessage(Entity):
  """Private messages are like messages, except they are private."""

  __tablename__ = 'private_message'
  __editable__ = ['content', 'recipient_id']
  __exportable__ = __editable__ + ['id', 'created_at', 'updated_at', 'creator_id', 'owner_id']

  content = Column(UnicodeText, info=SEARCHABLE)
  recipient_id = Column(Integer, ForeignKey(User.id), nullable=False)


class Comment(Entity):

  __tablename__ = 'comment'
  __editable__ = ['content', 'message_id']
  __exportable__ = __editable__ + ['id', 'created_at', 'updated_at', 'creator_id', 'owner_id']

  content = Column(UnicodeText, info=SEARCHABLE)
  message_id = Column(Integer, ForeignKey(Message.id), nullable=False)


class Like(Entity):

  __tablename__ = 'like'
  __editable__ = ['content', 'message_id']
  __exportable__ = __editable__ + ['id', 'created_at', 'updated_at', 'creator_id', 'owner_id']

  content = Column(UnicodeText, info=SEARCHABLE)
  message_id = Column(Integer, ForeignKey(Message.id), nullable=False)


#class FeedEntry(db.Model):
#
#  __tablename__ = 'feedentry'


class Attachment(Entity):
  __tablename__ = 'attachment'

  content = Column(LargeBinary)
