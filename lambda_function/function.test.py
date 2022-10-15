import unittest

function = __import__('function')
handler = function.lambda_handler

class TestFunction(unittest.TestCase):
  def test_function(self):
    event = {}
    context = {}
    result = handler(event, context)
    self.fail("bad test. current result: " + str(result))

if __name__ == '__main__':
    unittest.main()