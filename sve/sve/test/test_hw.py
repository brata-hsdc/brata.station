import unittest
from sve.hw import Led
from sve.hw import VibrationMotor

# ------------------------------------------------------------------------------
class LedTestCase(unittest.TestCase):

   # ---------------------------------------------------------------------------
   def setUp(self):

      self.Target = Led('three')


   # ---------------------------------------------------------------------------
   def test_init(self):

      name = 'four'
      target = Led(name)
      self.assertEqual(name, target.Name)


   # ---------------------------------------------------------------------------
   def test_turnOn(self):

      self.Target.turnOn()


   # ---------------------------------------------------------------------------
   def test_turnOff(self):

      self.Target.turnOff()


   # ---------------------------------------------------------------------------
   def test_setFlashing(self):

      self.Target.setFlashing()


# ------------------------------------------------------------------------------
class VibrationMotorTestCase(unittest.TestCase):

   # ---------------------------------------------------------------------------
   def setUp(self):

      self.Target = VibrationMotor('two')


   # ---------------------------------------------------------------------------
   def test_init(self):

      name = 'one'
      target = VibrationMotor(name)
      self.assertEqual(name, target.Name)


   # ---------------------------------------------------------------------------
   def test_start(self):

      self.Target.start()


   # ---------------------------------------------------------------------------
   def test_stop(self):

      self.Target.stop()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
