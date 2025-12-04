"""
Selenium script specifically designed for Cisco DevNet/Meraki API documentation.
Navigates to the API page, clicks on the Schema Definition toggle, and captures a screenshot.

Requirements:
    pip install selenium webdriver-manager

Usage:
    python cisco_schema_selenium.py
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager


def capture_cisco_schema():
    """
    Navigate to Cisco Meraki API documentation and capture the schema definition.
    
    The Cisco DevNet API documentation typically has:
    - A "Schema Definition" collapsible section in the response area
    - Schema is shown as a tree structure with expandable nodes
    """
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Remove this line to see the browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Initialize the driver
    print("[1/8] Initializing Chrome WebDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://developer.cisco.com/meraki/api-v1/create-organization-action-batch/"
        
        print(f"[2/8] Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        print("[3/8] Waiting for page to fully load...")
        time.sleep(5)
        
        # Wait for main content
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            print("    Main content loaded")
        except TimeoutException:
            print("    Main content selector not found, continuing...")
        
        # Take initial screenshot
        driver.save_screenshot("01_initial_page.png")
        print("[4/8] Initial screenshot saved")
        
        # Scroll down to find Schema Definition
        print("[5/8] Scrolling to find Schema Definition...")
        
        found_schema = False
        schema_element = None
        
        # Different strategies to find schema definition
        schema_locator_strategies = [
            # XPath strategies
            (By.XPATH, "//*[contains(text(), 'Schema Definition')]"),
            (By.XPATH, "//*[contains(text(), 'Response Schema')]"),
            (By.XPATH, "//summary[contains(text(), 'Schema')]"),
            (By.XPATH, "//button[contains(text(), 'Schema')]"),
            (By.XPATH, "//*[contains(@class, 'schema')]//summary"),
            (By.XPATH, "//*[contains(@class, 'schema-definition')]"),
            
            # CSS Selector strategies
            (By.CSS_SELECTOR, "[class*='schema-toggle']"),
            (By.CSS_SELECTOR, "[class*='schema-definition']"),
            (By.CSS_SELECTOR, "summary"),
            (By.CSS_SELECTOR, "details summary"),
        ]
        
        # First, scroll through the page
        for scroll_pos in range(0, 5000, 500):
            driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
            time.sleep(0.3)
        
        # Now try to find schema element
        for by, locator in schema_locator_strategies:
            try:
                elements = driver.find_elements(by, locator)
                for element in elements:
                    try:
                        text = element.text.lower()
                        if 'schema' in text:
                            print(f"    Found schema element: '{text[:50]}...'")
                            schema_element = element
                            found_schema = True
                            break
                    except StaleElementReferenceException:
                        continue
                
                if found_schema:
                    break
            except NoSuchElementException:
                continue
        
        # If found, scroll to it and click
        if schema_element:
            print("    Scrolling to schema element...")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", schema_element)
            time.sleep(1)
            
            print("    Clicking to expand schema...")
            try:
                schema_element.click()
            except ElementClickInterceptedException:
                # Try JavaScript click if regular click is intercepted
                driver.execute_script("arguments[0].click();", schema_element)
            
            time.sleep(2)
        else:
            print("    Schema not found with locators, trying JavaScript approach...")
            
            # JavaScript approach to find and click schema
            result = driver.execute_script("""
                const allElements = document.querySelectorAll('*');
                let clicked = false;
                
                for (const el of allElements) {
                    const text = (el.textContent || '').toLowerCase();
                    const className = (el.className || '').toString().toLowerCase();
                    
                    if ((text.includes('schema definition') || 
                         text.includes('response schema') ||
                         className.includes('schema')) &&
                        (el.tagName === 'BUTTON' || 
                         el.tagName === 'SUMMARY' || 
                         el.tagName === 'A' ||
                         el.getAttribute('role') === 'button')) {
                        
                        el.scrollIntoView({ behavior: 'instant', block: 'center' });
                        el.click();
                        clicked = true;
                        return { clicked: true, element: el.tagName, text: text.substring(0, 50) };
                    }
                }
                
                // Also try to expand all details elements that might contain schema
                document.querySelectorAll('details').forEach(d => {
                    const text = (d.textContent || '').toLowerCase();
                    if (text.includes('schema')) {
                        d.open = true;
                    }
                });
                
                return { clicked: clicked, element: null, text: null };
            """)
            
            if result and result.get('clicked'):
                print(f"    JavaScript found and clicked: {result.get('element')} - {result.get('text')}")
                found_schema = True
        
        # Wait for schema to expand
        time.sleep(3)
        
        # Take screenshot after clicking
        driver.save_screenshot("02_after_schema_click.png")
        print("[6/8] Post-click screenshot saved")
        
        # Expand all schema nodes
        print("[7/8] Expanding all schema nodes...")
        
        driver.execute_script("""
            // Expand all collapsed schema nodes
            document.querySelectorAll('details:not([open])').forEach(d => {
                d.open = true;
            });
            
            // Click any expand buttons
            document.querySelectorAll('[aria-expanded="false"], .collapsed, [class*="expand"]').forEach(el => {
                try { el.click(); } catch(e) {}
            });
        """)
        
        time.sleep(2)
        
        # Take final screenshots
        print("[8/8] Taking final screenshots...")
        
        # Full page screenshot (Selenium doesn't have built-in full page, so we need to resize)
        # Get the full page height
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, total_height)
        time.sleep(1)
        
        driver.save_screenshot("03_schema_fullpage.png")
        
        # Reset window size
        driver.set_window_size(1920, 1200)
        
        # Try to find and screenshot just the schema container
        schema_container_selectors = [
            "[class*='schema-content']",
            "[class*='schema-definition']",
            "[class*='model-']",
            "[class*='response-body']",
            "details[open]",
            "[class*='schema']",
        ]
        
        for selector in schema_container_selectors:
            try:
                container = driver.find_element(By.CSS_SELECTOR, selector)
                if container.is_displayed():
                    # Scroll to container
                    driver.execute_script("arguments[0].scrollIntoView({block: 'start'});", container)
                    time.sleep(0.5)
                    container.screenshot("04_schema_definition.png")
                    print(f"    Schema container screenshot saved (selector: {selector})")
                    break
            except (NoSuchElementException, Exception):
                continue
        
        # Viewport screenshot
        driver.save_screenshot("05_schema_viewport.png")
        
        print("\n" + "=" * 60)
        print("SCREENSHOTS SAVED:")
        print("  01_initial_page.png      - Initial page state")
        print("  02_after_schema_click.png - After clicking Schema Definition")
        print("  03_schema_fullpage.png   - Full page with expanded schema")
        print("  04_schema_definition.png - Schema definition section only")
        print("  05_schema_viewport.png   - Current viewport")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"Error occurred: {e}")
        driver.save_screenshot("error_screenshot.png")
        return False
        
    finally:
        driver.quit()


if __name__ == "__main__":
    print("Starting Cisco DevNet Schema Screenshot Tool (Selenium)")
    print("=" * 60)
    
    success = capture_cisco_schema()
    
    if success:
        print("\nScript completed successfully!")
    else:
        print("\nScript completed with some issues. Check the screenshots.")
