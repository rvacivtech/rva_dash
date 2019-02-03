import logging, time
from datetime import datetime, timedelta, date
from configparser import ConfigParser

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from sqlalchemy.sql import text

from utilities.connections import create_engine
from app.models import Crime

config = ConfigParser()
config.read('config.ini')
DATABASE = config.get('environment', 'db_name')


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('scrape_crime.log')
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Crime_Scraper:
    def __init__(self, start_date='12/31/2018', end_date='12/31/2018'):
        self.start_date = start_date
        self.end_date = end_date
        self.browser = self.get_browser()

    def get_browser(self):
        options = Options()
        options.set_headless(True)
        browser = webdriver.Firefox(options=options)
        logger.info('Headless Firefox browser initialized.')
        return browser


    def query_crime_data_by_date(self):
        # start_date and end_date are strings formatted mm/dd/yyyy

        logger.info(f'Attempting to get crime date from {self.start_date} to {self.end_date}.')
        self.browser.get('http://eservices.ci.richmond.va.us/applications/crimeinfo/index.asp')

        start_date_elem = self.browser.find_element_by_name('txtBeginDate')
        start_date_elem.clear()
        start_date_elem.send_keys(self.start_date)
        end_date_elem = self.browser.find_element_by_name('txtEndDate')
        end_date_elem.clear()
        end_date_elem.send_keys(self.end_date)
        submit_elem = self.browser.find_element_by_name('cmdGetInfo')
        submit_elem.click()

        all_outer_links = self.get_all_details_links()
        number_of_outer_links = len(all_outer_links)
        
        try:
            crime_data, skipped_link_indexes = self.loop_through_all_outer_links(number_of_outer_links)
            crime_data += self.loop_through_skipped_links(skipped_link_indexes)
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
            self.browser.quit()

        logger.info(f'Successfully scraped {len(crime_data)} crime records.')
        return crime_data


    def loop_through_all_outer_links(self, number_of_outer_links, timeout_delay=15):
        # Handler for process_outer_link function to ensure all links for neighborhoods are scraped
        crime_data = []
        skipped_link_indexes = []
        for outer_index in range(number_of_outer_links):
            crime_datum, skipped_link_index = self.process_outer_link(outer_index)
            crime_data += crime_datum
            skipped_link_indexes += skipped_link_index
            logger.info(f'Successfully scraped {len(crime_data)} records.')
            logger.info(f'Skipped {len(skipped_link_indexes)} records.')
        return (crime_data, skipped_link_indexes)


    def loop_through_skipped_links(self, skipped_link_indexes, timeout_delay=15):
        # Occassionally scraper can't find outer link that should be there.  This function allows program to skip missing link and retry at end.
        crime_data = []
        for outer_index in skipped_link_indexes:
            crime_data += self.process_outer_link(outer_index)[0]
            logger.info(f'Successfully scraped {len(crime_data)} skipped records.')
        return crime_data


    def process_outer_link(self, outer_index, timeout_delay=20):
        # Handler for loop_through_inner_links function.  Scrapes name of neighborhood.
        crime_data = []
        skipped_link_index = []
        all_outer_links = self.get_all_details_links()
        this_outer_link = all_outer_links[outer_index]
        this_outer_link.click() 

        inner_page_element_selector = 'body > form > table:nth-child(21) > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(1) > td > table > tbody > tr > td:nth-child(3) > a > img'
        try:
            WebDriverWait(self.browser, timeout_delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, inner_page_element_selector)))
        except TimeoutException:
            skipped_link_index = [outer_index]
            return (crime_data, skipped_link_index)
        neighborhood_css_selector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                    '> table:nth-child(1) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td.fntSmallBlack')
        neighborhood = WebDriverWait(self.browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, neighborhood_css_selector))).text[15:]
        logger.info(f'Scraping crime data for neighborhood: {neighborhood}.')
        all_inner_links = self.get_all_details_links()
        number_of_inner_links = len(all_inner_links)
        crime_data += self.loop_through_inner_links(number_of_inner_links, neighborhood)    
        self.browser.back()
        return (crime_data, skipped_link_index)


    def loop_through_inner_links(self, number_of_inner_links, neighborhood, timeout_delay=15):
        # This function scrapes required data and passes the data back up through the handlers.
        crime_data=[]
        for inner_index in range(number_of_inner_links):
            all_inner_links = self.get_all_details_links()
            this_inner_link = all_inner_links[inner_index]
            WebDriverWait(self.browser, timeout_delay).until(EC.visibility_of(this_inner_link))
            this_inner_link.click() 
            incident_number_css_selector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                            '> table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td:nth-child(2) > font')
            try:
                incident_number = 'N/A'
                incident_number = WebDriverWait(self.browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, incident_number_css_selector))).text
            except TimeoutException:
                pass
            address_css_selector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                    '> table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > font')
            try:
                address = 'N/A'
                address = WebDriverWait(self.browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, address_css_selector))).text
            except TimeoutException:
                pass
            description_css_selector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                        '> table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(3) > td:nth-child(2) > font')
            try:
                description = 'N/A'
                description = WebDriverWait(self.browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, description_css_selector))).text
            except TimeoutException:
                pass
            incident_date_css_delector = ('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td '
                                        '> table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td:nth-child(4) > font')
            try:
                incident_date = WebDriverWait(self.browser, timeout_delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, incident_date_css_delector))).text
                try:
                    parsed_incident_date = datetime.strptime(incident_date, '%m/%d/%Y %H:%M')
                except ValueError:
                    parsed_incident_date = datetime.strptime(self.start_date, '%m/%d/%Y')
            except TimeoutException:
                pass
            crime_datum = {'neighborhood':neighborhood, 'incident_number':incident_number, 'street_address':address, 'description':description, 'incident_date':parsed_incident_date, 'scraping_input_date':datetime.strptime(self.start_date, '%m/%d/%Y')}
            crime_data.append(crime_datum)
            logger.info(f'Just added {crime_datum} to list.')
            self.browser.back()    
        return crime_data


    def get_all_details_links(self):
        # This function finds all "DETAIL" links on a page.  These links appear on the initial search result, and down a level when looking by neighborhood.
        timeout_delay = 15
        link_list_css_selector = 'body > form > table:nth-child(21) > tbody > tr:nth-child(3) > td > table > tbody > tr > td.tdRptLayoutSubTot > a'
        link_list = WebDriverWait(self.browser, timeout_delay).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, link_list_css_selector)))
        logger.info(f'Found {len(link_list)} "DETAIL" links.')
        return link_list


def save_crime_data_to_db(crime_data, connection_name=DATABASE):
    try:
        logger.info(f'Attempting to insert {len(crime_data)} crime record(s) into {connection_name} database.')
        crime = Crime()
        crime.insert_many_crime_records(crime_data)
        logger.info('Successfully inserted record(s).')
    except Exception as e:
        logger.error(f'Failed to insert crime record(s) into database: {e}')
        raise Exception(e)
    return None


def save_crime_for_single_day(crime_date, connection_name=DATABASE):
    scraper = Crime_Scraper(start_date=crime_date, end_date=crime_date)
    crime_data = scraper.query_crime_data_by_date()
    save_crime_data_to_db(crime_data, connection_name)
    return None


def save_crime_for_number_of_days(start_date, number_of_days, connection_name=DATABASE):
    for _ in range(number_of_days):
        save_crime_for_single_day(connection_name=connection_name, crime_date=start_date)
        parsed_date = datetime.strptime(start_date, '%m/%d/%Y')
        next_day = parsed_date + timedelta(days=1)
        start_date = next_day.strftime('%m/%d/%Y')
    return None


def update_db_with_latest_crime_records(connection_name=DATABASE):
    days_to_process = True 
    while days_to_process:
        try:
            crime = Crime()
            last_date = crime.get_last_scraping_input_date()[0].date()
            start_date = last_date + timedelta(days=1)
            end_date = date.today()
            logger.info(f'Most recent date in DB is {last_date}. Attempting to scrape data from {start_date} to {end_date}.')
            delta = end_date - start_date
            days_to_process = delta.days
            start_date_string = start_date.strftime('%m/%d/%Y')
            save_crime_for_number_of_days(start_date=start_date_string, number_of_days=days_to_process, connection_name=connection_name)
        except WebDriverException:
            logger.error('Encountered WebDriverException. Restarting...')
            time.sleep(30)
    return None





