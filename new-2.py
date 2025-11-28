from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time

service = Service("C:\\WebDrivers\\geckodriver.exe")  # update path!
driver = webdriver.Firefox(service=service)
driver.maximize_window()

try:
    driver.get("https://developer.cisco.com/meraki/api-v1/create-organization-action-batch/")
    wait = WebDriverWait(driver, 30)

    # 🔹 Wait for the iframe that contains the API content
    iframe = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
    )
    driver.switch_to.frame(iframe)

    # 🔹 Wait for Schema Definition button to be clickable
    schema_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Schema Definition')]"))
    )

    # 🔹 Scroll into view or Firefox may say it's not clickable
    driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth'});", schema_button)
    time.sleep(1)

    # 🔹 Click Schema Definition accordion
    schema_button.click()

    # 🔹 Wait for definition content to appear
    schema_content = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".accordion-body"))
    )

    # Wait for animation
    time.sleep(2)

    # Full page screenshot for safety
    driver.save_screenshot("schema_definition.png")
    print("Screenshot saved: schema_definition.png")

finally:
    time.sleep(2)
    driver.quit()