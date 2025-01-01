from datetime import datetime, date, timedelta
from tqdm.auto import tqdm
import time
from db_setup import *
from selenium_setup import *

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

    # Identify the custom scrollable container
    scroll_container = driver.find_element(By.XPATH, '//*[@id="form1"]/div[3]/div[2]')  # Replace with the correct selector

    grid_data = dict() # storage for grid data

    # get column names in grid table outside loop logic because of ridiculous javascript
    header = wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'table'))).find_element(By.TAG_NAME, 'tr')
    _, _, *keys = [i.text for i in header.find_elements(By.TAG_NAME, 'th')]

    # define scrolling logic
    last_scroll_position = 0
    while True:
        # Scroll down by a fixed amount
        driver.execute_script("arguments[0].scrollTop += 600;", scroll_container)

        try:
            # get table in view
            grid_table = wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'table')))

            body = grid_table.find_elements(By.TAG_NAME, 'tr') # get table rows

            # Check if header is in view
            if len(body[0].find_elements(By.TAG_NAME, 'th')) == 27:
                _, *body = body

            for genco in body:
                try:
                    _, company, *hour_data = [i.text for i in genco.find_elements(By.TAG_NAME, 'td')]
                    # print([_, company, *hour_data])
                    # Skip rows that are not in view
                    if len(hour_data) < 24:
                        continue
                    if not company:
                        company = 'Hour Total'
                except ValueError:
                    ...

                
                grid_data[company] = dict(zip(keys, hour_data))
        except:
            pass

        # Check the new scroll position
        new_scroll_position = driver.execute_script("return arguments[0].scrollTop;", scroll_container)
        if new_scroll_position == last_scroll_position:  # Stop if no new content loads
            break
        last_scroll_position = new_scroll_position

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