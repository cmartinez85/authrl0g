import os

username = os.environ.get('HRLOG_USERNAME')
password = os.environ.get('HRLOG_PASSWORD')
url = "https://app.hrlog.es/admin/login"

afternoon_shift_weeks = [
    18,

]

afternoon_shift = {
    'checkin': ["16:00"] ,
    'checkout': ["23:59"]
}

main_shift = {
    'checkin': ["09:00","14:00"] ,
    'checkout': ["13:00","18:30"]
}

interval_seconds = int(os.environ.get('TRACK_INTERVAL','600'))
working_flag = 'Estás trabajando'