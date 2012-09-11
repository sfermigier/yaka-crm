from base import IntegrationTestCase


class TestAuth(IntegrationTestCase):

  init_data = True

  # Tests start here
  def test_home_redirects_to_login(self):
    response = self.client.get("/")
    assert response.status_code == 401
    assert response.location == "http://localhost/login"

  def XXXtest_login_logout(self):
    response = self.client.get("/login")
    assert response.status_code == 200

    d = dict(email="frog@example.com", password="toto")
    response = self.client.post("/login", data=d)
    assert response.status_code == 200
