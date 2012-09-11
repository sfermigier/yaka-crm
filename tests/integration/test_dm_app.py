from os.path import join, dirname
import re
from io import StringIO
from werkzeug.datastructures import FileStorage

from base import IntegrationTestCase
from nose.tools import eq_, ok_
from util import DataLoader

from yaka.core.extensions import db

from yaka_crm.apps.dm import create_file


ROOT = "/dm/"

class TestViews(IntegrationTestCase):

  init_data = True
  no_login = True

  @staticmethod
  def uid_from_url(url):
    return int(url[len("http://localhost" + ROOT):])

  # Actual tests start here
  def test_home(self):
    response = self.client.get(ROOT)
    self.assert_200(response)

  def test_create_file(self):
    fs = FileStorage(stream=self.open_file("rammstein.pdf"),
                     filename="rammstein.pdf", content_type="application/pdf")
    with self.app.test_request_context('/dm/dummy'):
      self.app.preprocess_request()
      f = create_file(fs)
      ok_("rammstein" in f.text.lower())
      eq_("English", f.language)

  def test_preview(self):
    loader = DataLoader()
    loader.load_users()
    loader.load_files()
    db.session.commit()

    response = self.client.get(ROOT)
    self.assert_200(response)

    data = response.data
    for m in re.findall(ROOT + "([0-9]+)", data):
      id = int(m)
      response = self.client.get(ROOT + "%d/preview?size=500" % id)
      self.assert_200(response)

  def test_upload_text(self):
    CONTENT = u'my file contents'
    NAME = u'hello world.txt'
    data = {
      'file': (StringIO(CONTENT), NAME, 'text/plain'),
      'action': 'upload',
    }
    response = self.client.post(ROOT, data=data)
    self.assert_302(response)

    id = self.uid_from_url(response.location)

    response = self.client.get(ROOT + "%d" % id)
    self.assert_200(response)

    response = self.client.get(ROOT)
    self.assert_200(response)
    ok_(NAME in response.data)
    ok_((ROOT + "%d" % id) in response.data)

    response = self.client.get(ROOT + "%d/download" % id)
    self.assert_200(response)
    eq_(response.headers['Content-Type'], 'text/plain')
    eq_(response.data, CONTENT)

    response = self.client.post(ROOT + "%d/delete" % id)
    self.assert_302(response)

    response = self.client.get(ROOT + "%d" % id)
    self.assert_404(response)

  def test_upload_pdf(self):
    NAME = u"onepage.pdf"
    data = {
      'file': (self.open_file(NAME), NAME, 'application/pdf'),
      'action': 'upload',
    }
    response = self.client.post(ROOT, data=data)
    self.assert_302(response)

    id = self.uid_from_url(response.location)
    response = self.client.get(ROOT + "%d" % id)
    self.assert_200(response)

    response = self.client.get(ROOT)
    self.assert_200(response)
    ok_(NAME in response.data)
    ok_((ROOT + "%d" % id) in response.data)

    response = self.client.get(ROOT + "%d/download" % id)
    self.assert_200(response)
    eq_(response.headers['Content-Type'], 'application/pdf')
    ok_(response.data)

    response = self.client.get(ROOT + "%d/preview?size=500" % id)
    self.assert_200(response)
    eq_(response.headers['Content-Type'], 'image/jpeg')

    response = self.client.post(ROOT + "%d/delete" % id)
    self.assert_302(response)

    response = self.client.get(ROOT + "%d" % id)
    self.assert_404(response)

  @staticmethod
  def open_file(filename):
    path = join(dirname(__file__), "..", "dummy_files", filename)
    return open(path)
