import time
import pandas as pd
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Get user input
car_name = input("Enter Car: ")
zipcode = input("Enter Zipcode: ")

# Initialize car details dict
car_details = defaultdict(list)

#Create scraping function for the first website
def carmax(driver):
    driver.get('https://www.carmax.com/cars')

    #Get zipcode popup
    zipcode_popup = driver.find_element(By.XPATH, '//span[@id="header-my-store-button-text"]')
    zipcode_popup.click()

    # Get zipcode input and input zipcode
    zipcode_input = driver.find_element(By.ID, 'header-store-search-form-input')
    zipcode_input.send_keys(zipcode)
    zipcode_input.send_keys(Keys.RETURN)

    # Get car input and search for car
    search_input = driver.find_element(By.ID, 'header-inventory-search')
    search_input.send_keys(car_name)
    search_input.send_keys(Keys.RETURN)

    # Get cars
    car_text_field = driver.find_elements(By.CLASS_NAME, "sc--car-tile--content")
    for car in car_text_field:
        # Get car year and make
        car_year = car.find_element(By.CLASS_NAME, 'sc--make-model-info--year-make')
        car_make = car.find_element(By.CLASS_NAME, 'sc--make-model-info--model-trim')

        # Get car price and miles
        car_price = car.find_element(By.CLASS_NAME, 'sc--price-miles-info--price')
        car_miles = car.find_element(By.CLASS_NAME, 'sc--price-miles-info--miles')

        # Get car links
        car_link = car.find_element(By.XPATH, '//a[@href]')

        # combine details
        car_name_details = car_year.text + " " + car_make.text
        car_sub_details = car_price.text.replace("*","")
        car_details['CarMax Name'].append(car_name_details)
        car_details['CarMax Price'].append(car_sub_details)
        #car_details['Carmax Links'].append(car_link.get_attribute('href'))
    

def driveway(driver):
    driver.get('https://www.driveway.com/shop')

    driver.maximize_window()


    zipcode_popup = driver.find_element(By.XPATH, '//*[@id="srp-location-btn"]')
    zipcode_popup.click()

    zipcode_input = driver.find_element(By.XPATH, '//*[@id="zip-code"]')
    zipcode_input.send_keys(zipcode)
    zipcode_input.send_keys(Keys.RETURN)

    zipcode_button = driver.find_element(By.CSS_SELECTOR, 'body > div.MuiPopover-root.MuiModal-root.mui-jp7szo > div.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation8.MuiPopover-paper.mui-128to16 > div > form > button')
    zipcode_button.click()

    search_input = driver.find_element(By.XPATH, '//*[@id="search-field"]')
    search_input.send_keys(car_name)
    search_input.send_keys(Keys.RETURN)

    car_text_field = driver.find_elements(By.CSS_SELECTOR, '[data-testid="result-grid-item"]')
    print(len(car_text_field))

    driver.implicitly_wait(4)

    for i, car in enumerate(car_text_field):
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end', inline: 'nearest'});", car)
        try:
            #Get year and car make
            car_year = car.find_element(By.CSS_SELECTOR, '[data-testid="vehicle-card-year"]')
            car_model = car.find_element(By.CSS_SELECTOR, '[data-testid="vehicle-card-make-model"]')
            car_make = car.find_element(By.CSS_SELECTOR, '[data-testid="vehicle-card-trim"]')
            car_details_col1 = car_year.text + " " + car_model.text + " " + car_make.text
            car_details['Driveway Name'].append(car_details_col1)
        except:
            print(f"Card {i} not found")
            continue
        
        #Get Car Price
        try:
            car_price = car.find_element(By.CSS_SELECTOR, '[data-testid="vehicle-card-price"]')
            car_details['Driveway Price'].append(car_price.text)
        except:
            print(f"price {i} not found")
            continue

        
        
        
    
def main():
    # Intialize web driver
    options = Options()
    #options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

    driver.implicitly_wait(10)
    carmax(driver)
    driveway(driver)
    driver.quit

main()

# Determine the maximum length among the arrays
max_length = max(len(car_details['CarMax Name']), len(car_details['CarMax Price']), len(car_details['Driveway Name']), len(car_details['Driveway Price']))

# Fill the arrays with None to match the maximum length
car_details['CarMax Name'] += [None] * (max_length - len(car_details['CarMax Name']))
car_details['CarMax Price'] += [None] * (max_length - len(car_details['CarMax Price']))
car_details['Driveway Name'] += [None] * (max_length - len(car_details['Driveway Name']))
car_details['Driveway Price'] += [None] * (max_length - len(car_details['Driveway Price']))

df = pd.DataFrame(car_details)
df.to_csv("CarDetails.csv", index=False)