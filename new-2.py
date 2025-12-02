"""
Playwright script to navigate to Cisco Meraki API documentation,
click on the schema definition, and take a screenshot of it.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python screenshot_schema.py
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


async def capture_schema_screenshot():
    """
    Navigate to the Meraki API documentation page, click on schema definition,
    and capture a screenshot of the entire schema.
    """
    async with async_playwright() as p:
        # Launch browser - set headless=False to see the browser in action
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        url = "https://developer.cisco.com/meraki/api-v1/create-organization-action-batch/"

        print(f"Navigating to: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except PlaywrightTimeout:
            print("Page load timed out, continuing anyway...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Wait for the page content to fully render
        print("Waiting for page to fully render...")
        await page.wait_for_timeout(5000)

        # Take an initial screenshot of the page
        print("Taking initial screenshot...")
        await page.screenshot(path="initial_page.png", full_page=True)

        # Scroll down to find the schema definition section
        print("Scrolling to find schema definition...")
        
        # Common selectors for schema definition in Cisco DevNet API docs
        schema_selectors = [
            # DevNet specific selectors
            "text=Schema Definition",
            "button:has-text('Schema')",
            "[data-testid='schema-toggle']",
            "summary:has-text('Schema')",
            ".schema-definition",
            "[class*='schema-toggle']",
            "[class*='schema-definition']",
            
            # Generic API doc patterns
            "details:has-text('Schema')",
            "[aria-label*='Schema']",
            "text=Response Schema",
            "text=Request Schema",
            
            # Expandable/collapsible patterns
            "[class*='expand']:has-text('Schema')",
            "[class*='collapse']:has-text('Schema')",
            ".toggle-schema",
            
            # Response section patterns
            "[class*='response'] summary",
            "[class*='response-schema']",
        ]

        schema_found = False
        
        # First, scroll down the page to make schema visible
        for scroll_position in range(0, 5000, 500):
            await page.evaluate(f"window.scrollTo(0, {scroll_position})")
            await page.wait_for_timeout(300)
            
            # Check for schema definition at each scroll position
            for selector in schema_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        print(f"Found schema element with selector: {selector}")
                        
                        # Scroll element into view
                        await element.scroll_into_view_if_needed()
                        await page.wait_for_timeout(500)
                        
                        # Click to expand if it's a toggle/expandable element
                        tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                        is_expanded = await element.get_attribute("aria-expanded")
                        
                        if tag_name in ["button", "summary", "details"] or is_expanded == "false":
                            print("Clicking to expand schema...")
                            await element.click()
                            await page.wait_for_timeout(2000)
                        
                        schema_found = True
                        break
                except Exception as e:
                    continue
            
            if schema_found:
                break

        # If schema not found with specific selectors, try text-based search
        if not schema_found:
            print("Trying text-based search for 'Schema'...")
            
            # Look for any clickable element containing "Schema"
            clickable_elements = await page.query_selector_all("button, summary, a, [role='button']")
            
            for element in clickable_elements:
                try:
                    text = await element.inner_text()
                    if text and "schema" in text.lower():
                        print(f"Found clickable schema element: {text[:50]}...")
                        await element.scroll_into_view_if_needed()
                        await page.wait_for_timeout(500)
                        await element.click()
                        await page.wait_for_timeout(2000)
                        schema_found = True
                        break
                except:
                    continue

        # Additional wait for any animations to complete
        await page.wait_for_timeout(2000)

        # Now try to find the expanded schema content
        print("Looking for expanded schema content...")
        
        schema_content_selectors = [
            "[class*='schema-content']",
            "[class*='schema-body']",
            "[class*='model-container']",
            ".json-schema",
            "[class*='response-schema']",
            "pre:has-text('type')",
            "[class*='properties']",
            "details[open]",
        ]

        schema_container = None
        
        for selector in schema_content_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    schema_container = element
                    print(f"Found schema content with selector: {selector}")
                    break
            except:
                continue

        # Take full page screenshot with schema expanded
        print("Taking full page screenshot with schema expanded...")
        await page.screenshot(path="schema_fullpage.png", full_page=True)

        # If we found a specific schema container, screenshot just that
        if schema_container:
            print("Taking screenshot of schema definition section...")
            
            # Get bounding box to check size
            bounding_box = await schema_container.bounding_box()
            if bounding_box:
                print(f"Schema container size: {bounding_box['width']}x{bounding_box['height']}")
            
            await schema_container.screenshot(path="schema_definition.png")
            print("Schema definition screenshot saved: schema_definition.png")
        else:
            print("Could not find specific schema container, using full page screenshot")
            
            # Try to screenshot the main content area instead
            main_content = await page.query_selector("main, [role='main'], .main-content, article")
            if main_content:
                await main_content.screenshot(path="schema_definition.png")
                print("Main content screenshot saved: schema_definition.png")

        # Also capture a viewport screenshot centered on the schema
        print("Taking viewport screenshot...")
        await page.screenshot(path="schema_viewport.png")

        print("\n" + "="*50)
        print("Screenshots saved:")
        print("  - initial_page.png (initial page state)")
        print("  - schema_fullpage.png (full page with schema)")
        print("  - schema_definition.png (schema definition section)")
        print("  - schema_viewport.png (current viewport)")
        print("="*50)

        await browser.close()


async def capture_schema_screenshot_alternative():
    """
    Alternative approach using a more aggressive method to find and capture schema.
    This version uses JavaScript evaluation to find schema elements.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        url = "https://developer.cisco.com/meraki/api-v1/create-organization-action-batch/"

        print(f"Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Use JavaScript to find and click all schema-related expandable elements
        print("Using JavaScript to find and expand schema elements...")
        
        await page.evaluate("""
            () => {
                // Find all elements that might be schema toggles
                const schemaPatterns = ['schema', 'Schema', 'SCHEMA'];
                const clickableElements = document.querySelectorAll('button, summary, [role="button"], details');
                
                clickableElements.forEach(el => {
                    const text = el.textContent || el.innerText || '';
                    if (schemaPatterns.some(pattern => text.includes(pattern))) {
                        // If it's a details element, set it to open
                        if (el.tagName.toLowerCase() === 'details') {
                            el.open = true;
                        } else {
                            // Try to click it
                            el.click();
                        }
                    }
                });
                
                // Also expand any collapsed sections that might contain schema
                document.querySelectorAll('details').forEach(details => {
                    if (!details.open) {
                        const text = details.textContent || '';
                        if (schemaPatterns.some(pattern => text.toLowerCase().includes(pattern.toLowerCase()))) {
                            details.open = true;
                        }
                    }
                });
            }
        """)

        await page.wait_for_timeout(3000)

        # Scroll to make sure schema is in view
        await page.evaluate("""
            () => {
                const schemaElement = document.querySelector('[class*="schema"], [id*="schema"]');
                if (schemaElement) {
                    schemaElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        """)

        await page.wait_for_timeout(2000)

        # Take screenshots
        print("Taking screenshots...")
        await page.screenshot(path="schema_fullpage_alt.png", full_page=True)
        await page.screenshot(path="schema_viewport_alt.png")

        print("Alternative screenshots saved!")
        await browser.close()


if __name__ == "__main__":
    print("Running main capture method...")
    asyncio.run(capture_schema_screenshot())
    
    print("\nRunning alternative capture method...")
    asyncio.run(capture_schema_screenshot_alternative())
