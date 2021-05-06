from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config
import datetime
from time import sleep
import pytz

def get_week_of_year() -> int:
    return datetime.datetime.now().isocalendar()[1]

def get_status(session: webdriver) -> str:
    try:
        status = session.find_element_by_id('texto-estado-fichaje')
        print(status.text)
        return status.text
    except Exception as e: 
        print(f'Unable to get status: {e}')
        exit(1)

def get_shift(afternoon_shift_weeks) -> dict:
    print(f'we are in the week: {get_week_of_year()}')
    if get_week_of_year() in afternoon_shift_weeks:
        print("Afternoon shift detected")
        timetable = config.afternoon_shift
    else:
        print("Main shift detected")
        timetable = config.main_shift
    return timetable

def login(url: str, username: str, password: str) -> webdriver:
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_prefs = {}
        chrome_options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(800, 600)
        print(f'Opening {url}...')
        driver.get(url)
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'username')))
        user = driver.find_element_by_id("username")
        print(f'Inserting user {username}')
        user.send_keys(username)
        passw = driver.find_element_by_id("password")
        passw.send_keys(password)
        passw.send_keys(Keys.ENTER)
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'div-fichaje-action')))
        print("Login succeded")
        return driver
    except Exception as e:
        print(f'Unable to login on HRLOG: {e}')
        exit(1)

def should_i_track(status: str,shift: dict,now: str, interval_seconds: int) -> bool:
    FMT="%H:%M"
    if status == config.working_flag:
        timetable = shift['checkout']
    else:
        print(f'Status detected: {status}')
        timetable = shift['checkin']
    for hour in timetable:
        print(f'Examining {hour} - {now}')
        print(abs(datetime.datetime.strptime(now,FMT) - datetime.datetime.strptime(hour,FMT)).total_seconds()) 
        if abs(datetime.datetime.strptime(now,FMT) - datetime.datetime.strptime(hour,FMT)).total_seconds() < datetime.timedelta(days=0,seconds=interval_seconds).total_seconds():
            return True
    return False

def track_time(session: webdriver) -> None:
    try:
        st = session.find_element_by_id('div-fichaje-action')
        print(st.text)
        st.click()
        print('waiting to save track info')
        sleep(10)
        print("Time tracked")
    except Exception as e:
        print(f'Unable to submit track info:{e}')
    finally:
        session.quit()

def main():
    session = login(config.url,
    config.username,
    config.password)
    status = get_status(session)
    shift = get_shift(config.afternoon_shift_weeks)
    tz = pytz.timezone('Europe/Madrid')
    now = datetime.datetime.now(tz).strftime("%H:%M")
    if should_i_track(status, shift, now, config.interval_seconds):
        print('I have to track my time')
        track_time(session)
    else:
        print("Everything is OK")

if __name__ == "__main__":
    main()

