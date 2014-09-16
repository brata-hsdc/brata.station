import unittest
from sve.conf import SveConfig
from sve.main import Sve

# ------------------------------------------------------------------------------
class SveTestCase(unittest.TestCase):

   def setUp(self):

      self.config = SveConfig()

   def test_init(self):

      target = Sve(self.config)

   def test_start(self):

      target = Sve(self.config)
      target.start()

if __name__ == '__main__':
    unittest.main()
