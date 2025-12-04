from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def main():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Step 1: Open the Cisco Meraki API documentation page
        print("Opening Cisco Meraki API documentation page...")
        driver.get("https://developer.cisco.com/meraki/api-v1/")
        time.sleep(2)
        
        # Step 2: Click on the search breadcrumb element
        print("Clicking on the search breadcrumb...")
        search_breadcrumb = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.doc-breadcrumb__search.gradual-border"))
        )
        search_breadcrumb.click()
        time.sleep(1)
        
        # Step 3: Click on the search input field and enter text
        print("Clicking on the search input field...")
        search_input = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.search__bar__input"))
        )
        search_input.click()
        time.sleep(0.5)
        
        # Optional: Enter search text if needed (you can modify this)
        # For now, just pressing Enter to show results
        print("Pressing Enter to show results...")
        search_input.send_keys(Keys.RETURN)
        time.sleep(2)
        
        # Step 4: Click on the first result
        print("Clicking on the first search result...")
        first_result = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.search-name-container"))
        )
        first_result.click()
        time.sleep(2)
        
        # Step 5: Scroll down to find schema definition
        print("Scrolling down to find schema definition...")
        
        # Try to find the schema definition element
        # Common selectors for schema definitions (you may need to adjust)
        schema_selectors = [
            "div.schema-definition",
            "button[aria-label*='Schema']",
            "button:contains('Schema')",
            "a[href*='schema']",
            ".schema",
            "[id*='schema']"
        ]
        
        schema_element = None
        for selector in schema_selectors:
            try:
                # Scroll down gradually to find the element
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                schema_element = driver.find_element(By.CSS_SELECTOR, selector)
                if schema_element:
                    print(f"Found schema element with selector: {selector}")
                    break
            except:
                continue
        
        # If still not found, try scrolling and searching by text
        if not schema_element:
            print("Trying to find schema definition by scrolling and searching...")
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(0.5)
                
                try:
                    # Try to find any element containing "schema" text
                    schema_element = driver.find_element(By.XPATH, 
                        "//*[contains(translate(text(), 'SCHEMA', 'schema'), 'schema definition') or " +
                        "contains(translate(text(), 'SCHEMA', 'schema'), 'schema')]")
                    if schema_element:
                        print("Found schema element by text search")
                        break
                except:
                    pass
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        
        # Step 6: Click on the schema definition
        if schema_element:
            print("Clicking on schema definition...")
            driver.execute_script("arguments[0].scrollIntoView(true);", schema_element)
            time.sleep(1)
            schema_element.click()
            time.sleep(2)
            
            # Step 7: Take screenshot
            print("Taking screenshot of schema definition...")
            screenshot_path = "/mnt/user-data/outputs/schema_definition_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
        else:
            print("Could not find schema definition element. Taking full page screenshot...")
            screenshot_path = "/mnt/user-data/outputs/full_page_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
        
        print("Automation completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Take screenshot of error state
        driver.save_screenshot("/mnt/user-data/outputs/error_screenshot.png")
        
    finally:
        # Keep browser open for a few seconds before closing
        time.sleep(3)
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()
