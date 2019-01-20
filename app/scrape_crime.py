import logging
from datetime import datetime, timedelta
from configparser import ConfigParser

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from sqlalchemy.sql import text

from utilities.connections import create_engine
from app.models import insert_many_crime_records

config = ConfigParser()
config.read('config.ini')
DATABASE = config.get('environment', 'db_name')


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('scrape_crime.log')
# handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)



def get_browser():
    options = Options()
    options.set_headless(True)
    browser = webdriver.Firefox(options=options)
    # browser.implicitly_wait(10)
    logger.info('Headless Firefox browser initialized.')
    return browser


def query_crime_data_by_date(browser, start_date='12/31/2018', end_date='12/31/2018'):
    # start_date and end_date are strings formatted mm/dd/yyyy

    logger.info(f'Attempting to get crime date from {start_date} to {end_date}.')
    browser.get('http://eservices.ci.richmond.va.us/applications/crimeinfo/index.asp')

    start_date_elem = browser.find_element_by_name('txtBeginDate')
    start_date_elem.clear()
    start_date_elem.send_keys(start_date)
    end_date_elem = browser.find_element_by_name('txtEndDate')
    end_date_elem.clear()
    end_date_elem.send_keys(end_date)
    submit_elem = browser.find_element_by_name('cmdGetInfo')
    submit_elem.click()

    all_outer_links = get_all_details_links(browser)
    number_of_outer_links = len(all_outer_links)
    
    try:
        crime_data, skipped_link_indexes = loop_through_all_outer_links(browser, number_of_outer_links)
        crime_data += loop_through_skipped_links(browser, skipped_link_indexes)
    except TimeoutException as e:
        logger.error(f'Failed to scrape crime data due to TimeoutException.')
        raise TimeoutException(e)
    except WebDriverException as e:
        logger.error(f'Failed to scrape crime data due to error page on source website.')
        raise WebDriverException(e)
    except Exception as e:
        logger.error(f'Failed to scrape crime data due to {e}.')
        raise Exception(e)
    finally:
        browser.quit()

    logger.info(f'Successfully scraped {len(crime_data)} crime records.')
    return crime_data


def loop_through_all_outer_links(browser, number_of_outer_links, timeout_delay=15):
    crime_data = []
    skipped_link_indexes = []
    for outer_index in range(number_of_outer_links):
        crime_datum, skipped_link_index = process_outer_link(browser, outer_index)
        crime_data += crime_datum
        skipped_link_indexes += skipped_link_index
        logger.info(f'Successfully scraped {len(crime_data)} records.')
        logger.info(f'Skipped {len(skipped_link_indexes)} records.')
    return (crime_data, skipped_link_indexes)


def loop_through_skipped_links(browser, skipped_link_indexes, timeout_delay=15):
    crime_data = []
    for outer_index in skipped_link_indexes:
        crime_data += process_outer_link(browser, outer_index)[0]
        logger.info(f'Successfully scraped {len(crime_data)} skipped records.')
    return crime_data


def process_outer_link(browser, outer_index, timeout_delay=20):
    crime_data = []
    skipped_link_index = []
    all_outer_links = get_all_details_links(browser)
    this_outer_link = all_outer_links[outer_index]
    this_outer_link.click() 

    inner_page_element_selector = 'body > form > table:nth-child(21) > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(1) > td > table > tbody > tr > td:nth-child(3) > a > img'
    try:
        WebDriverWait(browser, timeout_delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, inner_page_element_selector)))
    except TimeoutException:
        skipped_link_index = [outer_index]
        return (crime_data, skipped_link_index)
    neighborhood_css_selector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                '> table:nth-child(1) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td.fntSmallBlack')
    neighborhood = WebDriverWait(browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, neighborhood_css_selector))).text[15:]
    logger.info(f'Scraping crime data for neighborhood: {neighborhood}.')
    all_inner_links = get_all_details_links(browser)
    number_of_inner_links = len(all_inner_links)
    crime_data += loop_through_inner_links(browser, number_of_inner_links, neighborhood)    
    browser.back()
    return (crime_data, skipped_link_index)


def loop_through_inner_links(browser, number_of_inner_links, neighborhood, timeout_delay=15):
    crime_data=[]
    for inner_index in range(number_of_inner_links):
        all_inner_links = get_all_details_links(browser)
        this_inner_link = all_inner_links[inner_index]
        WebDriverWait(browser, timeout_delay).until(EC.visibility_of(this_inner_link))
        this_inner_link.click() 
        incident_number_css_selector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                        '> table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td:nth-child(2) > font')
        try:
            incident_number = WebDriverWait(browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, incident_number_css_selector))).text
        except TimeoutException:
            pass
        address_css_selector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                '> table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > font')
        try:
            address = WebDriverWait(browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, address_css_selector))).text
        except TimeoutException:
            pass
        description_css_selector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                    '> table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(3) > td:nth-child(2) > font')
        try:
            description = WebDriverWait(browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, description_css_selector))).text
        except TimeoutException:
            pass
        incident_date_css_delector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                    '> table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td:nth-child(4) > font')
        try:
            incident_date = WebDriverWait(browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, incident_date_css_delector))).text
        except TimeoutException:
            pass
        crime_datum = {'neighborhood':neighborhood, 'incident_number':incident_number, 'street_address':address, 'description':description, 'incident_date':incident_date}
        crime_data.append(crime_datum)
        logger.info(f'Just added {crime_datum} to list.')
        browser.back()    
    return crime_data


def get_all_details_links(browser):
    timeout_delay = 15
    link_list_css_selector = 'body > form > table:nth-child(21) > tbody > tr:nth-child(3) > td > table > tbody > tr > td.tdRptLayoutSubTot > a'
    # link_list = browser.find_elements_by_css_selector(link_list_css_selector)
    link_list = WebDriverWait(browser, timeout_delay).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, link_list_css_selector)))
    logger.info(f'Found {len(link_list)} "DETAIL" links.')
    return link_list


def save_crime_data_to_db(crime_data, connection_name=DATABASE):
    try:
        logger.info(f'Attempting to insert {len(crime_data)} crime record(s) into {connection_name} database.')
        insert_many_crime_records(crime_data)
        logger.info('Successfully inserted record(s).')
    except Exception as e:
        logger.error(f'Failed to insert crime record(s) into database: {e}')
        raise Exception(e)
    return None


def save_crime_for_single_day(crime_date, connection_name=DATABASE):
    browser = get_browser()
    crime_data = query_crime_data_by_date(browser=browser, start_date=crime_date, end_date=crime_date)
    save_crime_data_to_db(connection_name, crime_data)
    return None


def save_crime_for_number_of_days(start_date, number_of_days, connection_name=DATABASE):
    for _ in range(number_of_days):
        save_crime_for_single_day(connection_name=connection_name, crime_date=start_date)
        parsed_date = datetime.strptime(start_date, '%m/%d/%Y')
        next_day = parsed_date + timedelta(days=1)
        start_date = next_day.strftime('%m/%d/%Y')
    return None







