from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def get_browser():
    options = Options()
    options.set_headless(True)
    browser = webdriver.Firefox(options=options)
    browser.implicitly_wait(20)
    return browser


def query_crime_data_by_date(browser, start_date='12/01/2018', end_date='12/31/2018'):
    # start_date and end_date are strings formatted mm/dd/yyyy

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
    

    crime_data = []
    try:
        for outer_index in range(number_of_outer_links):
            all_outer_links = get_all_details_links(browser)
            this_outer_link = all_outer_links[outer_index]
            this_outer_link.click() 

            neighborhood = browser.find_element_by_css_selector('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td > table:nth-child(1) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td.fntSmallBlack').text[15:]
            all_inner_links = get_all_details_links(browser)
            number_of_inner_links = len(all_inner_links)
            for inner_index in range(number_of_inner_links):
                all_inner_links = get_all_details_links(browser)
                this_inner_link = all_inner_links[inner_index]
                this_inner_link.click() 
                incident_number = browser.find_element_by_css_selector('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td > table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td:nth-child(2) > font').text 
                address = browser.find_element_by_css_selector('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td > table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > font').text 
                description = browser.find_element_by_css_selector('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td > table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(3) > td:nth-child(2) > font').text 
                incident_date = browser.find_element_by_css_selector('body > form > table:nth-child(21) > tbody > tr:nth-child(2) > td > table:nth-child(2) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td:nth-child(4) > font').text
                crime_datum = {'neighborhood':neighborhood, 'indcident_number':incident_number, 'address':address, 'description':description, 'incident_date':incident_date}
                crime_data.append(crime_datum)
                print(description)
                browser.back()        
            browser.back()
    except Exception as e:
        print('outer list length is {}'.format(number_of_outer_links))
        print(f'Last clicked {outer_index + 1} outer link and {inner_index + 1} inner link.  Collected {len(crime_data)} records.')
        raise Exception(e)

    print('outer list length is {}'.format(number_of_outer_links))
    return crime_data


def get_all_details_links(browser):
    link_list = browser.find_elements_by_css_selector('body > form > table:nth-child(21) > tbody > tr:nth-child(3) > td > table > tbody > tr > td.tdRptLayoutSubTot > a')
    return link_list
