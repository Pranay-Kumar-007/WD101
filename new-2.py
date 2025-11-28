from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Firefox(service=Service("C:\\WebDrivers\\geckodriver.exe"))
driver.maximize_window()

try:
    driver.get("https://developer.cisco.com/meraki/api-v1/create-organization-action-batch/")
    wait = WebDriverWait(driver, 30)

    # Switch to the main API documentation iframe
    iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
    driver.switch_to.frame(iframe)

    # Locate the scrollable center panel
    scroll_div = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.ps > div"))  # Scrollable area inside PerfectScrollbar container
    )

    # Scroll step by step until Schema Definition button appears
    schema_button = None
    for _ in range(30):  # up to 30 scroll attempts
        try:
            schema_button = driver.find_element(
                By.XPATH, "//button[contains(., 'Schema Definition')]"
            )
            if schema_button.is_displayed():
                break
        except:
            pass
        
        driver.execute_script("arguments[0].scrollTop += 200;", scroll_div)
        time.sleep(0.4)

    if not schema_button:
        raise Exception("Could not find Schema Definition after scrolling!")

    # Click the accordion button
    schema_button.click()

    # Wait for content expansion
    schema_content = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".accordion-body"))
    )
    time.sleep(1)

    # Screenshot ONLY the schema section
    schema_content.screenshot("schema_definition.png")
    print("Screenshot saved: schema_definition.png")

finally:
    time.sleep(2)
    driver.quit()