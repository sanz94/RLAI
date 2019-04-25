import unittest 
from rlai import Reinforcement
from datetime import datetime
class RLAITest(unittest.TestCase):

    def testAccuracyRlai(self):
        #Test if hour when max people in room is 7pm ie 19hr for 14 feb 2019
        r = Reinforcement('2019-02-14.csv', True)
        sen_files = r.get_sensor_original_file()
        r.parse_file(sen_files)
        out = r.q_learning()
        self.assertEqual(out, "19")
    
    def testNoDataPresentRlai(self):
        #Test if no data present for selected date
        r = Reinforcement('2019-02-21.csv', False)
        sen_files = r.get_sensor_original_file()
        result = r.parse_file(sen_files)
        self.assertEqual(result, False)

    def testDataPresent(self):
        #Test if data present for selected date
        r = Reinforcement('2019-02-14.csv', False)
        sen_files = r.get_sensor_original_file()
        result = r.parse_file(sen_files)
        self.assertEqual(result, True)

    def testInvalidFile(self):
        #Test if system exit with code 1 on invalid file name
        with self.assertRaises(SystemExit) as context:
            r = Reinforcement("Badfile123.txt", False)
            r.get_sensor_original_file()
        self.assertEqual(context.exception.code, 1)
    
    def testValidFile(self):
        #Test if valid file is read and return
        r = Reinforcement("2019-02-14.csv", False)
        result = r.get_sensor_original_file()
        self.assertEqual("2019-02-14.csv",result.name)

    def testCalcPeakTimeMethod(self):
        r = Reinforcement('2019-02-14.csv', True)
        sen_files = r.get_sensor_original_file()
        r.parse_file(sen_files)
        time = r.calc_peak_time(r.humiditydict['2019-02-14.csv'])
        expectedDate=datetime(2019, 2, 14, 19, 47, 1)
        self.assertEqual(time,expectedDate)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)