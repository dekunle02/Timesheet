import codecs
import re
from datetime import date
from database import db
from database.models import User, TimeSheet
from pathlib import Path
import pdfkit

TEMPLATE_DIRECTORY = Path(__file__).parents[0] / 'template.html'
today = str(date.today().strftime('%d-%m-%Y'))

OUTPUT_FILENAME = 'timesheet'
OUT_DIR = Path(__file__).parents[1] / 'out'
OUT_PNG = OUT_DIR / (OUTPUT_FILENAME + '.png')
OUT_HTML = OUT_DIR / (OUTPUT_FILENAME + '.html')

LOGO_DIR = Path(__file__).parents[1] / 'res' / 'nes_logo.jpg'
SIGNATURE_DIRECTORY = Path(__file__).parents[1] / 'database' / 'signature.jpg'

BOOTSTRAP_DIR = Path(__file__).parents[1] / 'res' / 'bootstrap.css'
STYLES_DIR = Path(__file__).parents[1] / 'res' / 'styles.css'

CSS_DIR = (
    BOOTSTRAP_DIR,
    STYLES_DIR
)

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def obtain_sheet() -> str:
    with codecs.open(str(TEMPLATE_DIRECTORY), 'r') as f:
        return f.read()


def obtain_bio() -> User:
    return db.get_user()


def write_css_n_images(text: str, css_dir=CSS_DIR, logo_dir=LOGO_DIR, signature_dir=SIGNATURE_DIRECTORY,
                       timesheet=None) -> str:
    css_import: str = ''
    for css_dir in css_dir:
        css_import += f"<link rel='stylesheet' href='file://{css_dir}'>\n"
    text = text.replace('XXCSSXX', css_import)
    text = text.replace('XXLOGOXX', 'file://' + str(logo_dir))
    text = text.replace('XXSIGNATUREXX', 'file://' + str(signature_dir))
    return text


def write_bio(text: str, timesheet: TimeSheet) -> str:
    bio: dict = timesheet.data['bio']
    replace_dic = {
        'XXFIRST_NAMEXX': bio['first_name'],
        'XXLAST_NAMEXX': bio['last_name'],
        'XXHOSPITALXX': bio['hospital_name']
    }
    return replace_all(text, replace_dic)

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


def write_hours(text: str, timesheet: TimeSheet) -> str:
    table_data = timesheet.data['table_data']
    entries = table_data['entries']
    entry_strings = ""
    last_date = ''
    for entry in entries:
        entry_weekday = WEEKDAYS[entry['date'].weekday()]
        entry_date = entry['date'].strftime('%d-%m-%Y')
        entry_string = f"<tr>\n" \
                       f"<th scope='row'>{entry_weekday}</th>\n" \
                       f"<td>{entry_date}</td>\n" \
                       f"<td>{entry['start_time']}</td>\n" \
                       f"<td>{entry['end_time']}</td>\n" \
                       f"<td>{entry['hours']}</td>\n" \
                       f"</tr>\n"
        entry_strings += entry_string
        last_date = entry_date
    
    template_dic = {
        'XXENTRIESXX': entry_strings,
        'XXTOTAL_WEEK_HOURSXX': table_data['total_hours']
    }
    text = replace_all(text, template_dic).replace('XXTODAY_DATEXX', last_date)
    return text


def clean_tags(text: str, timesheet=None) -> str:
    pattern = r"(?:XX)(.*?)(?:XX)"
    while re.findall(pattern, text):
        text = re.sub(pattern, "", text)
    return text


def replace_all(text: str, dic: dict) -> str:
    for k, v in dic.items():
        text = text.replace(k, str(v))
    return text


def compose(timesheet: TimeSheet, text: str, *args):
    for arg in args:
        text = arg(text=text, timesheet=timesheet)
    return text


def produce(timesheet: TimeSheet):
    text = obtain_sheet()
    composition = compose(timesheet, text,
                          write_css_n_images, write_bio, write_disturbances, write_hours, clean_tags)

    if not OUT_DIR.exists():
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        
    with codecs.open(str(OUT_HTML), 'w') as f:
        f.write(composition)
    