import codecs
import re
from datetime import date
from database.models import User, TimeSheet
from pathlib import Path
import pdfkit
import base64

TEMPLATE_DIRECTORY = Path(__file__).parents[0] / 'template.html'

today = str(date.today().strftime('%d-%m-%Y'))
OUT_PDF = Path(__file__).parents[1] / 'out' / (today + '.pdf')
OUT_HTML = Path(__file__).parents[1] / 'out' / (today + '.html')

LOGO_DIR = Path(__file__).parents[1] / 'res' / 'nes_logo.jpg'
SIGNATURE_DIRECTORY = Path(__file__).parents[1] / 'database' / 'signature.jpg'

BOOTSTRAP_DIR = Path(__file__).parents[1] / 'res' / 'bootstrap.css'
STYLES_DIR = Path(__file__).parents[1] / 'res' / 'styles.css'

CSS_DIRS = [
    BOOTSTRAP_DIR,
    STYLES_DIR
]


def compose(timesheet: TimeSheet, *args):
    text = obtain_sheet()
    for arg in args:
        text = arg(text, timesheet)
    return text


def obtain_sheet() -> str:
    with codecs.open(str(TEMPLATE_DIRECTORY), 'r') as f:
        return f.read()


def get_image_file_as_base64_data(path):
    with open(path, 'rb') as image_file:
        return base64.b64encode(image_file.read())


def write_css_n_images(text: str, *args) -> str:
    css_import: str = ''
    for css_dir in CSS_DIRS:
        css_import += f"<link rel='stylesheet' href='file://{css_dir}'>\n"
    return text.replace('XXCSSXX', css_import) \
        .replace('XXLOGOXX', 'file://' + str(LOGO_DIR)) \
        .replace('XXSIGNATUREXX', 'file://' + str(SIGNATURE_DIRECTORY))


def write_bio(text: str, timesheet: TimeSheet) -> str:
    bio: dict = timesheet.data['bio']
    replace_dic = {
        'XXFIRST_NAMEXX': bio['first_name'],
        'XXLAST_NAMEXX': bio['last_name'],
        'XXHOSPITALXX': bio['hospital_name']
    }
    return replace_all(text, replace_dic)


def write_date(text: str, *args) -> str:
    return text.replace('XXTODAY_DATEXX', today)


def write_disturbances(text: str, timesheet: TimeSheet) -> str:
    disturbances = timesheet.data['night_disturbances']
    counter = 1
    template_dic = {}
    for disturbance in disturbances:
        template_dic[f'XXDIST_DATE_{counter}XX'] = disturbance['date']
        template_dic[f'XXDIST_TIME_{counter}XX'] = disturbance['time']
        template_dic[f'XXDIST_DURATION_{counter}XX'] = disturbance['duration']
        template_dic[f'XXDIST_REASON_{counter}XX'] = disturbance['reason']
        counter += 1

    text = replace_all(text, template_dic)
    return text


def write_hours(text: str, timesheet: TimeSheet, ) -> str:
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
    text = replace_all(text, template_dic)
    return text


def clean_tags(text: str, *args) -> str:
    pattern = r"(?:XX)(.*?)(?:XX)"
    while re.findall(pattern, text):
        text = re.sub(pattern, "", text)
    return text


def replace_all(text: str, dic: dict) -> str:
    for k, v in dic.items():
        text = text.replace(k, str(v))
    return text


def produce(timesheet: TimeSheet):
    composition = compose(timesheet,
                          write_css_n_images, write_bio, write_date, write_disturbances, write_hours, clean_tags)

    with codecs.open(str(OUT_HTML), 'w') as f:
        f.write(composition)

    options = {
        "enable-local-file-access": None,
        "page-size": 'A4',
        'margin-top': '0in',
        'margin-right': '0in',
        'margin-bottom': '0in',
        'margin-left': '0in',
        'orientation': 'landscape'
    }
    css = [str(BOOTSTRAP_DIR), str(STYLES_DIR)]
    pdfkit.from_file(str(OUT_HTML), str(OUT_PDF), options=options, css=css)


if __name__ == '__main__':
    sample_user = User(first_name="Samad", last_name="Adeleke", hospital_name="Nuffield")
    start_date = '25/10/2021'
    end_date = '1/11/2021'
    start_time = '13:00'
    end_time = '13:00'

    t = TimeSheet(sample_user, start_date, start_time, end_date, end_time)
    produce(t)
