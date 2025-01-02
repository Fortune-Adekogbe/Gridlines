from datetime import datetime, date, timedelta
from tqdm.auto import tqdm
import time
from db_setup import *
from selenium_setup import *
from bs4 import BeautifulSoup

def get_grid_data(date_):
    date_str = str(date_).replace('-', '/')

    # change date to day of interest
    element = driver.find_element(By.XPATH, '//*[@id="MainContent_txtReadingDate"]')

    driver.execute_script("""
        arguments[0].removeAttribute('readonly');
        arguments[0].value = arguments[1];
    """, element, date_str)

    # Click "get generation" button
    button = driver.find_element(By.XPATH, '//*[@id="MainContent_btnGetReadings"]')
    driver.execute_script("arguments[0].click();", button)

    wait = WebDriverWait(driver, 2)

    # Get date on website
    website_date = driver.find_element(By.CSS_SELECTOR, 'span[id="MainContent_lblReadingDate"]').text
    website_date = datetime.strptime(website_date, '%Y/%m/%d').date()
    # print(date_str, website_date)

    grid_data = dict() # storage for grid data

    try:
        # get table
        grid_table = wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'table')))
        inner_html = driver.execute_script("return arguments[0].innerHTML;", grid_table)
        soup = BeautifulSoup(inner_html, "html.parser")

        # separate header and rows
        header, *body = soup.find_all('tr')

        _, _, *keys = [i.text for i in header.find_all('th')]

        for genco in body:
            try:
                _, company, *hour_data = [i.text for i in genco.find_all('td')]
                if not company:
                    company = 'Hour Total'
            except ValueError:
                ...

            
            grid_data[company] = dict(zip(keys, hour_data))
    except:
        pass

    return str(website_date), grid_data

def write_to_mongo(the_date, data):
    filter = {"date": the_date}
    update = {"$set": data}
    result = db.gridmoments.update_one(filter, update)

    if (result.matched_count) == 0:
        data = {
            "date": the_date,
            'metadata': {'source': 'niggrid.org'},
            **data
        }
        result = db.gridmoments.insert_one(data)
    return result

url = "https://niggrid.org/GenerationProfile2"

driver.get(url)
driver.maximize_window()

curr_date = date.today() # - timedelta(days=1)

REWIND = False
if REWIND:
    start_of_time = datetime.strptime("2017/11/03", '%Y/%m/%d').date()

    total_iterations = (curr_date - start_of_time).days
    progress_bar = tqdm(total=total_iterations, desc="Scraping...")

    while curr_date >= start_of_time:
        try:
            the_date, grid_data = get_grid_data(curr_date)
            write_to_mongo(the_date, grid_data)
        except Exception as e:
            with open('failed.txt', 'a') as f:
                f.write(str(curr_date) +"\t"+ str(e))

        curr_date -= timedelta(days=1)
        if curr_date.day == 31:
            time.sleep(42)
        progress_bar.update(1)
else:
    try:
        the_date, grid_data = get_grid_data(curr_date)
        print(the_date)
        print(len(grid_data.keys()))
        print(sorted(grid_data.keys()))
        write_to_mongo(the_date, grid_data)
    except Exception as e:
        print("No Data. Probable Grid Failure.")
        print(e)
# Close the driver
driver.quit()