from base import IntegrationTestCase

from yaka_crm.apps.crm.entities import *

from datetime import datetime, timedelta


class TestModels(IntegrationTestCase):

  # Utility
  def check_editable(self, object):
    if hasattr(object, '__editable__'):
      for k in object.__editable__:
        assert hasattr(object, k), "Property '%s' of object %s is not " \
                                   "editable" % (k, object)

  # Tests start here
  def test_account(self):
    account = Account(name="John SARL")
    self.check_editable(account)

    self.session.add(account)
    self.session.commit()

    assert datetime.utcnow() - account.created_at < timedelta(1)

  def test_contact(self):
    contact = Contact(first_name="John", last_name="Test User", email="test@example.com")
    self.check_editable(contact)

    account = Account(name="John SARL")
    contact.account = account

    self.session.add(account)
    self.session.add(contact)
    self.session.commit()

    assert datetime.utcnow() - contact.created_at < timedelta(1)
