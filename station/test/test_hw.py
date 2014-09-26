import unittest
from station.hw import Led
from station.hw import VibrationMotor

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

      # TODO
      #output = pibrella.output.e
      #self.assertEqual(0, output.read())
      self.Target.turnOn()
      #self.assertEqual(1, output.read())


   # ---------------------------------------------------------------------------
   def test_turnOff(self):

      # TODO
      #output = pibrella.output.f
      #self.assertEqual(0, output.read())
      self.Target.turnOff()
      #self.assertEqual(1, output.read())


   # ---------------------------------------------------------------------------
   def test_setFlashing(self):

      # TODO
      self.Target.setFlashing()
      # TODO


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

      # TODO
      self.Target.start()
      # TODO


   # ---------------------------------------------------------------------------
   def test_stop(self):

      # TODO
      self.Target.stop()
      # TODO


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
