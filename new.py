from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time

# Path to your ChromeDriver
driver_path = "chromedriver.exe"

# Create WebDriver
driver = webdriver.Chrome(service=Service(driver_path))
driver.maximize_window()

try:
    # Step 1: Open the page
    driver.get("https://developer.cisco.com/meraki/api-v1/create-organization-action-batch/")

    wait = WebDriverWait(driver, 15)
    
    # Step 2: Scroll to Schema Definition accordion (if not in view)
    schema_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(., 'Schema Definition')]")
    ))
    
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", schema_button)
    time.sleep(1)

    # Step 3: Click to expand the schema definition
    schema_button.click()
    
    # Step 4: Wait for content to appear
    schema_content = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'accordion-body')]"))
    )

    # Optional: scroll into view fully
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});", schema_content)

    time.sleep(2)  # Allow UI animation to finish

    # Step 5: Take screenshot
    screenshot_path = "schema_definition.png"
    schema_content.screenshot(screenshot_path)

    print(f"Screenshot saved: {screenshot_path}")

finally:
    time.sleep(2)
    driver.quit()