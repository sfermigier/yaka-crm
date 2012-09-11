from base import IntegrationTestCase
from tests.integration.util import DataLoader

from yaka_crm.apps.crm.entities import Contact
from yaka.services import indexing


class TestSearch(IntegrationTestCase):

  init_data = True
  no_login = True

  def setUp(self):
    self.index = indexing.get_service()
    self.index.start()
    IntegrationTestCase.setUp(self)

  def tearDown(self):
    IntegrationTestCase.tearDown(self)
    self.index.stop()

  def test_contacts_are_indexed(self):
    contact = Contact(first_name="John", last_name="Test User", email="test@example.com")
    self.session.add(contact)
    self.session.commit()

    # Check 3 different APIs
    search_result = list(Contact.search_query(u"john").all())
    assert 1 == len(search_result)
    assert contact == search_result[0]

    search_result = list(Contact.search_query.search(u"john"))
    assert 1 == len(search_result)
    assert contact == search_result[0][1]
    assert contact.id, int(search_result[0][0]['id'])

    search_result = list(self.index.search(u"john"))
    assert 1 == len(search_result)
    assert contact == search_result[0][1]
    assert contact.id == int(search_result[0][0]['id'])

  def test_basic_search(self):
    # Note: there a guy named "Paul Dupont" in the test data
    response = self.client.get("/search/?q=dupont")
    self.assert_200(response)
    assert "Paul" in response.data

  def test_live_search(self):
    response = self.client.get("/search/live?q=dupont")
    self.assert_200(response)
    assert "Paul" in response.data

  def test_document_search(self):
    loader = DataLoader()
    loader.load_users()
    loader.load_files()
    loader.commit()

    response = self.client.get("/search/docs?q=rammstein")
    self.assert_200(response)
    print response.data
    assert "Wikipedia" in response.data
