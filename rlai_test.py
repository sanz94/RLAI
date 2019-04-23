import unittest 
from rlai import Reinforcement
class testCases(unittest.TestCase):

    def testAccuracyRlai(self):
        #Test if hour when max people in room is 7pm ie 19hr for 14 feb 2019
        r = Reinforcement('2019-02-14.csv', True)
        sen_files = r.get_sensor_original_file()
        r.parse_file(sen_files)
        out = r.q_learning()
        self.assertEqual(out, "19")

    def testInvalidFile(self):
        #Test if system exit with code 1 on invalid file name
        with self.assertRaises(SystemExit) as context:
            r = Reinforcement("Badfile123.txt", False)
            r.get_sensor_original_file()
        self.assertEqual(context.exception.code, 1)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)