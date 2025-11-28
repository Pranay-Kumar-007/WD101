from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# Initialize Firefox driver
driver = webdriver.Firefox(service=Service("C:\\WebDrivers\\geckodriver.exe"))
driver.maximize_window()

try:
    # Navigate to the URL
    print("Loading page...")
    driver.get("https://developer.cisco.com/meraki/api-v1/create-organization-action-batch/")
    wait = WebDriverWait(driver, 30)

    # Wait for and switch to the API documentation iframe
    print("Switching to iframe...")
    iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
    driver.switch_to.frame(iframe)
    time.sleep(1)  # Give iframe content time to load

    # Try multiple possible selectors for the scrollable container
    scroll_div = None
    possible_selectors = [
        "div.ps > div",
        "div.ps",
        "div[class*='scroll']",
        "div.api-content",
        "body"
    ]
    
    for selector in possible_selectors:
        try:
            scroll_div = driver.find_element(By.CSS_SELECTOR, selector)
            print(f"Found scrollable element: {selector}")
            break
        except NoSuchElementException:
            continue
    
    if not scroll_div:
        scroll_div = driver.find_element(By.TAG_NAME, "body")
        print("Using body as fallback scroll element")

    # Scroll to find Schema Definition button
    print("Searching for Schema Definition button...")
    schema_button = None
    max_scrolls = 50
    scroll_increment = 300
    
    for scroll_attempt in range(max_scrolls):
        try:
            # Try to find the button
            schema_button = driver.find_element(
                By.XPATH, "//button[contains(text(), 'Schema Definition') or contains(@aria-label, 'Schema Definition')]"
            )
            
            # Check if button is in viewport
            if schema_button.is_displayed():
                print(f"Found Schema Definition button after {scroll_attempt} scrolls")
                # Scroll button into view smoothly
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                    schema_button
                )
                time.sleep(0.5)
                break
        except NoSuchElementException:
            pass
        
        # Scroll down incrementally
        current_scroll = driver.execute_script("return arguments[0].scrollTop;", scroll_div)
        driver.execute_script(f"arguments[0].scrollTop = {current_scroll + scroll_increment};", scroll_div)
        time.sleep(0.3)
        
        # Check if we've reached the bottom
        new_scroll = driver.execute_script("return arguments[0].scrollTop;", scroll_div)
        if new_scroll == current_scroll:
            print("Reached bottom of page")
            break

    if not schema_button:
        raise Exception("Could not find Schema Definition button after scrolling entire page!")

    # Click the Schema Definition button to expand accordion
    print("Clicking Schema Definition button...")
    try:
        schema_button.click()
    except:
        # If regular click fails, try JavaScript click
        driver.execute_script("arguments[0].click();", schema_button)
    
    time.sleep(1)

    # Wait for the accordion content to expand and become visible
    print("Waiting for schema content to expand...")
    schema_content = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".accordion-body, div[class*='accordion'] div[class*='body']"))
    )
    
    # Additional wait to ensure content is fully rendered
    time.sleep(1.5)
    
    # Scroll the schema content into view if needed
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", 
        schema_content
    )
    time.sleep(0.5)

    # Take screenshot of the schema section
    print("Taking screenshot...")
    screenshot_path = "schema_definition.png"
    schema_content.screenshot(screenshot_path)
    print(f"✓ Screenshot saved successfully: {screenshot_path}")

except TimeoutException as e:
    print(f"Timeout error: {e}")
    driver.save_screenshot("error_timeout.png")
    print("Error screenshot saved: error_timeout.png")
    
except Exception as e:
    print(f"An error occurred: {e}")
    driver.save_screenshot("error_general.png")
    print("Error screenshot saved: error_general.png")
    
finally:
    print("Closing browser...")
    time.sleep(2)
    driver.quit()
    print("Done!")