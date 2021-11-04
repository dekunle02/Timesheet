import unittest
from database.models import User, NightDisturbance, TimeSheet
from template import composer

"""
Things to test
1. Test that composer can parse an html string with a template and user obj
2. That composer can output html
3. That composer can output a pdf
"""


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        user = User(first_name='A', last_name='B', hospital_name='C')
        night_disturbances = [
            NightDisturbance(date='1', time='1', duration='1', reason='1'),
        ]

        self.timesheet = TimeSheet(
            user=user,
            start_date='1/1/2021',
            number_of_days=1,
            start_time='12:00',
            end_time='15:00'
        )

        for disturbace in night_disturbances:
            self.timesheet.add_night_disturbance(disturbace)

        self.css_dir = ['c']
        self.logo_dir = 'l'
        self.signature_dir = 's'

    def test_parsers(self):
        """replaces the text with the bio information of a user"""
        text = "XXFIRST_NAMEXX.XXLAST_NAMEXX.XXHOSPITALXX." \
               "XXCSSXX.XXLOGOXX.XXSIGNATUREXX." \
               "XXDIST_DATE_1XX.XXDIST_TIME_1XX.XXDIST_DURATION_1XX.XXDIST_REASON_1XX." \
               ""
        expected_result = 'A.B.C.' \
                          "<link rel='stylesheet' href='file://c'>\n" \
                          ".file://l.file://s." \
                          '1.1.1.1.'
        result = composer.write_bio(text, self.timesheet)
        result = composer.write_css_n_images(result,
                                             css_dir=self.css_dir,
                                             logo_dir=self.logo_dir,
                                             signature_dir=self.signature_dir)
        result = composer.write_disturbances(result, self.timesheet)
        self.assertEqual(result, expected_result)

    def test_date_parsers(self):
        """This tests the autocreation of rows for each shifts"""
        text = "XXDAY_1_DATEXX.XXDAY_1_STARTXX.XXDAY_1_ENDXX.XXDAY_1_TOTALXX" \
               "XXDAY_2_DATEXX.XXDAY_2_STARTXX.XXDAY_2_ENDXX.XXDAY_2_TOTALXX" \
               ".XXTOTAL_WEEK_HOURSXX."
        expected_result = "01-01-2021.12:00.00:00.12.0" \
                          "01-02-2021.00:00.15:00.15.0" \
                          ".27.0."
        result = composer.write_hours(text, self.timesheet)
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
