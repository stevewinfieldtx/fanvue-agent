import asyncio
from playwright.async_api import async_playwright
from src.config import Config
import logging
import random

class FacebookBot:
    def __init__(self):
        self.email = Config.FACEBOOK_EMAIL
        self.password = Config.FACEBOOK_PASSWORD
        self.proxy_url = Config.PROXY_URL
        self.headless = False

    async def post_content(self, text, image_path=None):
        """
        Posts content to the user's Facebook feed.
        """
        logging.info("Posting to Facebook Feed...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless) # Add proxy if needed
            context = await browser.new_context()
            page = await context.new_page()
            try:
                await self.login(page)
                
                # Navigate to profile or home to post
                await page.click('div[aria-label="Create a post"], div[role="button"]:has-text("What\'s on your mind")')
                await asyncio.sleep(2)
                
                # Input text
                # Note: Facebook selectors change frequently. This is a best-guess.
                focused_element = await page.evaluate("document.activeElement")
                # We often need to click the text area
                await page.keyboard.type(text)
                
                # Upload image if provided
                if image_path:
                    # Logic to upload image (requires finding the file input)
                    # standard input[type=file] often hidden
                    pass
                
                await asyncio.sleep(2)
                # Click Post
                await page.click('div[aria-label="Post"]')
                logging.info("Facebook Post submitted.")
                
            except Exception as e:
                logging.error(f"Facebook Post Error: {e}")
            finally:
                await browser.close()

    async def run_engagement_cycle(self):
        """
        Runs the daily engagement cycle:
        1. Login
        2. Check specific groups ( Asian Dating, Single Men, etc.)
        3. Like/Comment on relevant posts.
        """
        logging.info("Starting Facebook Engagement Cycle...")
        
        # Parse Proxy URL if present
        proxy_config = None
        if self.proxy_url:
            # Assuming format: http://user:pass@host:port
            # Playwright expects { "server": "...", "username": "...", "password": "..." }
            # Simplification: passing the URL directly often works if it contains auth,
            # but Playwright sometimes needs separate credentials.
            # TODO: Improve proxy parsing safety.
            proxy_config = {"server": self.proxy_url}

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                proxy=proxy_config
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()

            try:
                # 1. Login
                await self.login(page)
                
                # 2. Join Groups / Engage
                groups_keywords = ["Asian Dating", "Single Men"]
                for keyword in groups_keywords:
                    await self.explore_and_engage(page, keyword)
                    await asyncio.sleep(random.randint(5, 15)) # Human-like pause

            except Exception as e:
                logging.error(f"Facebook Bot Error: {e}")
                await page.screenshot(path="fb_error.png")
            finally:
                await browser.close()

    async def login(self, page):
        logging.info("Logging into Facebook...")
        await page.goto("https://www.facebook.com/")
        try:
            # Check if already logged in (cookies)
            if await page.query_selector('label[aria-label="Search Facebook"]'):
                logging.info("Already logged in.")
                return

            await page.fill('input[name="email"]', self.email)
            await page.fill('input[name="pass"]', self.password)
            await page.click('button[name="login"]')
            await page.wait_for_navigation()
            logging.info("Login successful.")
        except Exception as e:
            logging.error(f"Login failed: {e}")
            raise e

    async def explore_and_engage(self, page, keyword):
        logging.info(f"Searching for groups: {keyword}")
        # Search URL
        await page.goto(f"https://www.facebook.com/search/groups/?q={keyword}")
        await asyncio.sleep(5)
        
        # Simple Logic: Click 'Join' on the first visible button if haven't joined.
        # This is risky and needs DOM inspection to avoid infinite loops or detection.
        # joining_buttons = await page.query_selector_all('div[aria-label="Join"]')
        # if joining_buttons:
        #    await joining_buttons[0].click()
        #    logging.info(f"Requested to join a group for {keyword}")
