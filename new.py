"""
Playwright script specifically designed for Cisco DevNet/Meraki API documentation.
Navigates to the API page, clicks on the Schema Definition toggle, and captures a screenshot.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python cisco_schema_screenshot.py
"""

import asyncio
from playwright.async_api import async_playwright


async def capture_cisco_schema():
    """
    Navigate to Cisco Meraki API documentation and capture the schema definition.
    
    The Cisco DevNet API documentation typically has:
    - A "Schema Definition" collapsible section in the response area
    - Schema is shown as a tree structure with expandable nodes
    """
    async with async_playwright() as p:
        # Launch browser (set headless=False to watch the automation)
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1200},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()

        url = "https://developer.cisco.com/meraki/api-v1/create-organization-action-batch/"
        
        print(f"[1/8] Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Wait for the page to fully load - DevNet pages can be slow
        print("[2/8] Waiting for page to fully load...")
        await page.wait_for_timeout(5000)
        
        # Wait for main content to be present
        try:
            await page.wait_for_selector("main, article, [class*='content']", timeout=10000)
            print("[3/8] Main content loaded")
        except:
            print("[3/8] Main content selector not found, continuing...")

        # Take initial screenshot
        await page.screenshot(path="01_initial_page.png", full_page=True)
        print("[4/8] Initial screenshot saved")

        # Scroll down to the response section where schema typically is
        print("[5/8] Scrolling to find Schema Definition...")
        
        # Scroll through the page to find schema
        found_schema = False
        
        # Try to find "Schema Definition" or similar text
        schema_locators = [
            page.get_by_text("Schema Definition", exact=False),
            page.get_by_text("Response Schema", exact=False),
            page.get_by_text("Schema", exact=True),
            page.locator("text=Schema").first,
            page.locator("[class*='schema']").first,
            page.locator("summary:has-text('Schema')").first,
            page.locator("button:has-text('Schema')").first,
        ]
        
        for locator in schema_locators:
            try:
                # Check if element exists and is visible
                count = await locator.count()
                if count > 0:
                    element = locator.first
                    if await element.is_visible():
                        print(f"    Found schema element!")
                        
                        # Scroll into view
                        await element.scroll_into_view_if_needed()
                        await page.wait_for_timeout(1000)
                        
                        # Click to expand
                        await element.click()
                        print("    Clicked to expand schema")
                        await page.wait_for_timeout(2000)
                        
                        found_schema = True
                        break
            except Exception as e:
                continue
        
        if not found_schema:
            print("    Schema not found with locators, trying scroll and JavaScript approach...")
            
            # Scroll down and use JavaScript to find schema
            for i in range(10):
                await page.evaluate(f"window.scrollTo(0, {i * 400})")
                await page.wait_for_timeout(300)
            
            # JavaScript approach to find and click schema
            result = await page.evaluate("""
                () => {
                    // Find all elements that might be schema toggles
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
                }
            """)
            
            if result.get('clicked'):
                print(f"    JavaScript found and clicked: {result.get('element')} - {result.get('text')}")
                found_schema = True

        # Wait for schema to expand
        await page.wait_for_timeout(3000)
        
        # Take screenshot after clicking
        await page.screenshot(path="02_after_schema_click.png", full_page=True)
        print("[6/8] Post-click screenshot saved")

        # Try to find and expand all schema nodes for complete view
        print("[7/8] Expanding all schema nodes...")
        
        await page.evaluate("""
            () => {
                // Expand all collapsed schema nodes
                document.querySelectorAll('details:not([open])').forEach(d => {
                    d.open = true;
                });
                
                // Click any expand buttons
                document.querySelectorAll('[aria-expanded="false"], .collapsed, [class*="expand"]').forEach(el => {
                    try { el.click(); } catch(e) {}
                });
            }
        """)
        
        await page.wait_for_timeout(2000)

        # Find the schema container and take a targeted screenshot
        print("[8/8] Taking final screenshots...")
        
        # Take full page screenshot
        await page.screenshot(path="03_schema_fullpage.png", full_page=True)
        
        # Try to find the schema container for a targeted screenshot
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
                container = await page.query_selector(selector)
                if container and await container.is_visible():
                    bbox = await container.bounding_box()
                    if bbox and bbox['height'] > 100:  # Make sure it's substantial
                        await container.screenshot(path="04_schema_definition.png")
                        print(f"    Schema container screenshot saved (selector: {selector})")
                        break
            except:
                continue

        # Take viewport screenshot
        await page.screenshot(path="05_schema_viewport.png")

        print("\n" + "=" * 60)
        print("SCREENSHOTS SAVED:")
        print("  01_initial_page.png      - Initial page state")
        print("  02_after_schema_click.png - After clicking Schema Definition")
        print("  03_schema_fullpage.png   - Full page with expanded schema")
        print("  04_schema_definition.png - Schema definition section only")
        print("  05_schema_viewport.png   - Current viewport")
        print("=" * 60)

        await browser.close()
        
        return True


if __name__ == "__main__":
    print("Starting Cisco DevNet Schema Screenshot Tool")
    print("=" * 60)
    
    success = asyncio.run(capture_cisco_schema())
    
    if success:
        print("\nScript completed successfully!")
    else:
        print("\nScript completed with some issues. Check the screenshots.")
