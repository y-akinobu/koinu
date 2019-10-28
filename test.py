import unittest
from main import app

class NLPTestCase(unittest.TestCase):

  def setUp(self):
    self.app = app.test_client()

  def test_get_nlp(self):
    rs = self.app.get('/api/nlp/色は檸檬')
    assert rs.status_code == 405
  
  def test_post_nlp(self):
    rs = self.app.post('/api/nlp/色は檸檬')
    print(rs.get_json())
    assert rs.data


if __name__ == '__main__':
  unittest.main()
