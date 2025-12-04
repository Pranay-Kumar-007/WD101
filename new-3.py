"""
Selenium script to navigate to Cisco Meraki API documentation,
click on the schema definition, and take a screenshot of it.

This is a more generic version with multiple fallback approaches.

Requirements:
    pip install selenium webdriver-manager

Usage:
    python screenshot_schema_selenium.py
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    ElementNotInteractableException
)
from webdriver_manager.chrome import ChromeDriverManager


class SchemaScreenshotCapture:
    """Class to handle schema screenshot capture with multiple strategies."""
    
    def __init__(self, headless=True):
        """Initialize the WebDriver with specified options."""
        self.chrome_options = Options()
        
        if headless:
            self.chrome_options.add_argument("--headless")
        
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-setuid-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = None
        self.wait = None
    
    def start_driver(self):
        """Start the Chrome WebDriver."""
        print("Starting Chrome WebDriver...")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        return self.driver
    
    def stop_driver(self):
        """Stop the Chrome WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def navigate_to_page(self, url):
        """Navigate to the specified URL and wait for load."""
        print(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(5)  # Wait for JavaScript to render
    
    def take_screenshot(self, filename):
        """Take a screenshot and save it."""
        self.driver.save_screenshot(filename)
        print(f"Screenshot saved: {filename}")
    
    def take_full_page_screenshot(self, filename):
        """Take a full page screenshot by resizing the window."""
        # Get the total height of the page
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        total_width = self.driver.execute_script("return document.body.scrollWidth")
        
        # Set window size to capture full page
        self.driver.set_window_size(max(1920, total_width), total_height)
        time.sleep(1)
        
        self.driver.save_screenshot(filename)
        print(f"Full page screenshot saved: {filename}")
        
        # Reset window size
        self.driver.set_window_size(1920, 1080)
    
    def scroll_to_element(self, element):
        """Scroll an element into view."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
            element
        )
        time.sleep(0.5)
    
    def click_element(self, element):
        """Click an element with fallback strategies."""
        try:
            element.click()
            return True
        except ElementClickInterceptedException:
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except:
                pass
        except ElementNotInteractableException:
            try:
                ActionChains(self.driver).move_to_element(element).click().perform()
                return True
            except:
                pass
        return False
    
    def find_schema_element_by_selectors(self):
        """Find schema element using various selector strategies."""
        
        # List of (By type, selector, description) tuples
        selectors = [
            # Text-based XPath
            (By.XPATH, "//*[contains(text(), 'Schema Definition')]", "Schema Definition text"),
            (By.XPATH, "//*[contains(text(), 'Response Schema')]", "Response Schema text"),
            (By.XPATH, "//summary[contains(., 'Schema')]", "Summary with Schema"),
            (By.XPATH, "//button[contains(., 'Schema')]", "Button with Schema"),
            
            # Class-based CSS selectors
            (By.CSS_SELECTOR, "[class*='schema-toggle']", "schema-toggle class"),
            (By.CSS_SELECTOR, "[class*='schema-definition']", "schema-definition class"),
            (By.CSS_SELECTOR, "[class*='schema'] summary", "schema class summary"),
            (By.CSS_SELECTOR, "[class*='schema'] button", "schema class button"),
            
            # Generic expandable elements
            (By.CSS_SELECTOR, "details summary", "details summary"),
            (By.CSS_SELECTOR, "[aria-expanded='false']", "collapsed aria element"),
        ]
        
        for by, selector, description in selectors:
            try:
                elements = self.driver.find_elements(by, selector)
                for element in elements:
                    try:
                        if element.is_displayed():
                            text = element.text.lower()
                            if 'schema' in text or description.startswith('schema'):
                                print(f"  Found: {description} - '{text[:30]}...'")
                                return element
                    except StaleElementReferenceException:
                        continue
            except NoSuchElementException:
                continue
        
        return None
    
    def find_schema_element_by_javascript(self):
        """Find and click schema element using JavaScript."""
        
        result = self.driver.execute_script("""
            const allElements = document.querySelectorAll('button, summary, a, [role="button"]');
            
            for (const el of allElements) {
                const text = (el.textContent || '').toLowerCase();
                
                if (text.includes('schema definition') || 
                    text.includes('response schema') ||
                    (text.includes('schema') && text.length < 50)) {
                    
                    el.scrollIntoView({ behavior: 'instant', block: 'center' });
                    return {
                        found: true,
                        tag: el.tagName,
                        text: text.substring(0, 50)
                    };
                }
            }
            
            return { found: false };
        """)
        
        if result.get('found'):
            print(f"  JavaScript found: {result.get('tag')} - '{result.get('text')}'")
            # Now find and return the actual element
            elements = self.driver.find_elements(By.XPATH, 
                f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'schema')]"
            )
            for el in elements:
                if el.is_displayed() and el.tag_name.lower() in ['button', 'summary', 'a']:
                    return el
        
        return None
    
    def expand_all_schema_nodes(self):
        """Expand all collapsed schema nodes using JavaScript."""
        
        self.driver.execute_script("""
            // Expand all details elements
            document.querySelectorAll('details').forEach(d => {
                d.open = true;
            });
            
            // Click elements with aria-expanded="false"
            document.querySelectorAll('[aria-expanded="false"]').forEach(el => {
                try { el.click(); } catch(e) {}
            });
            
            // Expand any collapsed elements
            document.querySelectorAll('.collapsed, [class*="collapse"]').forEach(el => {
                try { el.click(); } catch(e) {}
            });
        """)
        
        time.sleep(1)
        print("  Expanded all schema nodes")
    
    def find_schema_container(self):
        """Find the schema container element for targeted screenshot."""
        
        container_selectors = [
            "[class*='schema-content']",
            "[class*='schema-definition']",
            "[class*='schema-body']",
            "[class*='model-container']",
            "[class*='response-schema']",
            "details[open]",
            "[class*='schema']",
        ]
        
        for selector in container_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        size = element.size
                        if size['height'] > 100 and size['width'] > 100:
                            print(f"  Found container: {selector} ({size['width']}x{size['height']})")
                            return element
            except:
                continue
        
        return None
    
    def capture_schema(self, url):
        """Main method to capture schema screenshot."""
        
        try:
            self.start_driver()
            
            # Step 1: Navigate to page
            print("\n[Step 1] Navigating to page...")
            self.navigate_to_page(url)
            
            # Step 2: Take initial screenshot
            print("\n[Step 2] Taking initial screenshot...")
            self.take_screenshot("01_initial_page.png")
            
            # Step 3: Scroll through page to load all content
            print("\n[Step 3] Scrolling through page...")
            for pos in range(0, 5000, 500):
                self.driver.execute_script(f"window.scrollTo(0, {pos})")
                time.sleep(0.2)
            
            # Step 4: Find schema element
            print("\n[Step 4] Finding schema element...")
            schema_element = self.find_schema_element_by_selectors()
            
            if not schema_element:
                print("  Trying JavaScript approach...")
                schema_element = self.find_schema_element_by_javascript()
            
            # Step 5: Click to expand schema
            if schema_element:
                print("\n[Step 5] Clicking schema element...")
                self.scroll_to_element(schema_element)
                if self.click_element(schema_element):
                    print("  Schema element clicked")
                    time.sleep(2)
            else:
                print("\n[Step 5] Schema element not found, expanding all details...")
                self.expand_all_schema_nodes()
            
            # Step 6: Take post-click screenshot
            print("\n[Step 6] Taking post-click screenshot...")
            self.take_screenshot("02_after_schema_click.png")
            
            # Step 7: Expand all nested nodes
            print("\n[Step 7] Expanding all nested schema nodes...")
            self.expand_all_schema_nodes()
            time.sleep(2)
            
            # Step 8: Take full page screenshot
            print("\n[Step 8] Taking full page screenshot...")
            self.take_full_page_screenshot("03_schema_fullpage.png")
            
            # Step 9: Find and screenshot schema container
            print("\n[Step 9] Finding schema container...")
            container = self.find_schema_container()
            
            if container:
                self.scroll_to_element(container)
                container.screenshot("04_schema_definition.png")
                print("  Schema container screenshot saved")
            else:
                print("  Container not found, using viewport screenshot")
            
            # Step 10: Take viewport screenshot
            print("\n[Step 10] Taking viewport screenshot...")
            self.take_screenshot("05_schema_viewport.png")
            
            # Print summary
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
            print(f"\nError: {e}")
            if self.driver:
                self.take_screenshot("error_screenshot.png")
            return False
            
        finally:
            self.stop_driver()


def main():
    """Main entry point."""
    print("=" * 60)
    print("Schema Screenshot Capture Tool (Selenium)")
    print("=" * 60)
    
    url = "https://developer.cisco.com/meraki/api-v1/create-organization-action-batch/"
    
    # Set headless=False to watch the browser in action
    capturer = SchemaScreenshotCapture(headless=True)
    success = capturer.capture_schema(url)
    
    if success:
        print("\nScript completed successfully!")
    else:
        print("\nScript completed with errors. Check error_screenshot.png")


if __name__ == "__main__":
    main()
