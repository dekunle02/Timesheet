import codecs
import re
from datetime import date
from database.models import User, TimeSheet
from pathlib import Path
import pdfkit

# confirm signature and user first
TEMPLATE_DIRECTORY = 'template.html'
TEMP_DIRECTORY = 'temp.html'
today = str(date.today())
OUT_DIRECTORY = Path(__file__).parents[1] / 'out' / (today + '.pdf')


def compose(timesheet: TimeSheet):
    with codecs.open(TEMPLATE_DIRECTORY, 'r') as f:
        template_string = f.read()
        template_string = compose_bio(timesheet, template_string)
        template_string = compose_timesheet(timesheet, template_string)
        template_string = compose_disturbances(timesheet, template_string)
        template_string = compose_date(template_string)
        make_temp(clean_timesheet(template_string))
        produce()


def produce():
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    options = {
        "enable-local-file-access": None,
        "page-size": 'A5',
        'margin-top': '0in',
        'margin-right': '0in',
        'margin-bottom': '0in',
        'margin-left': '0in'
    }
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    css = ['styles.css', 'bootstrap.css']

    pdfkit.from_file(TEMP_DIRECTORY, OUT_DIRECTORY, options=options, configuration=config, css=css)


def make_temp(text):
    with codecs.open(TEMP_DIRECTORY, 'w') as f:
        f.write(text)


def compose_bio(timesheet: TimeSheet, template: str) -> str:
    bio = timesheet.data['bio']
    replace_dic = {
        'XXFIRST_NAMEXX': bio['first_name'],
        'XXLAST_NAMEXX': bio['last_name'],
        'XXHOSPITALXX': bio['hospital_name']
    }
    return replace_all(template, replace_dic)


def compose_date(template: str) -> str:
    today = str(date.today().strftime('%d-%m-%Y'))
    return template.replace('XXTODAY_DATEXX', today)


def compose_disturbances(timesheet: TimeSheet, template: str) -> str:
    disturbances = timesheet.data['night_disturbances']
    counter = 1
    template_dic = {}
    for disturbance in disturbances:
        template_dic[f'XXDIST_DATE_{counter}XX'] = disturbance['date']
        template_dic[f'XXDIST_TIME_{counter}XX'] = disturbance['time']
        template_dic[f'XXDIST_DURATION_{counter}XX'] = disturbance['duration']
        template_dic[f'XXDIST_REASON_{counter}XX'] = disturbance['reason']
        counter += 1

    template = replace_all(template, template_dic)
    return template


def compose_timesheet(timesheet: TimeSheet, template: str) -> str:
    table_data = timesheet.data['table_data']
    entries = table_data['entries']
    template_dic = {}

    for entry in entries:
        entry_id = entry['id']
        template_dic[f'XXDAY_{entry_id}_DATEXX'] = entry['date']
        template_dic[f'XXDAY_{entry_id}_STARTXX'] = entry['start_time']
        template_dic[f'XXDAY_{entry_id}_ENDXX'] = entry['end_time']
        template_dic[f'XXDAY_{entry_id}_TOTALXX'] = entry['hours']

    template_dic['XXTOTAL_WEEK_HOURSXX'] = table_data['total_hours']
    template = replace_all(template, template_dic)

    return template


def clean_timesheet(text: str) -> str:
    pattern = r"(?:XX)(.*?)(?:XX)"
    while re.findall(pattern, text):
        text = re.sub(pattern, "", text)
    return text


def replace_all(text: str, dic: dict) -> str:
    for k, v in dic.items():
        text = text.replace(k, str(v))
    return text


if __name__ == '__main__':
    sample_user = User(first_name="Samad", last_name="Adeleke", hospital_name="Nuffield")
    start_date = '25/10/2021'
    end_date = '1/11/2021'
    start_time = '13:00'
    end_time = '13:00'

    t = TimeSheet(sample_user, start_date, start_time, end_date, end_time)
    compose(t)
