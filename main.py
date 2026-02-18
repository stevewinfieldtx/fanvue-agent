import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.brain.llm_client import LLMClient
from src.media.runware_client import RunwareClient
from src.platforms.fanvue import FanVueClient
from src.platforms.facebook_bot import FacebookBot

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def daily_routine():
    logging.info("Starting Daily Routine...")
    
    # 1. Initialize Clients
    llm = LLMClient()
    rw = RunwareClient()
    fv = FanVueClient()
    
    # 2. Generate Story
    logging.info("Generating Daily Story...")
    story = llm.generate_daily_story()
    logging.info(f"Story Concept: {story.get('story_title')}")
    
    # --- SFW Flow (Facebook/Instagram) ---
    logging.info("Generating SFW Content...")
    sfw_prompt_desc = story.get('scene_description_sfw')
    sfw_img_prompt = llm.generate_image_prompt(sfw_prompt_desc, safety="safe")
    
    sfw_image_url = await rw.generate_image(sfw_img_prompt)
    if sfw_image_url:
        logging.info(f"SFW Image Generated: {sfw_image_url}")
        
        # Instantiate FB Bot for posting
        fb_bot = FacebookBot()
        await fb_bot.post_content(text=story.get('caption_mainstream'), image_path=sfw_image_url)
        
    else:
        logging.error("Failed to generate SFW image.")

    # --- NSFW Flow (FanVue) ---
    logging.info("Generating NSFW Content for FanVue...")
    nsfw_prompt_desc = story.get('scene_description_nsfw')
    nsfw_img_prompt = llm.generate_image_prompt(nsfw_prompt_desc, safety="nsfw")
    
    nsfw_image_url = await rw.generate_image(nsfw_img_prompt)
    
    if nsfw_image_url:
        logging.info(f"NSFW Image Generated: {nsfw_image_url}")
        logging.info("Posting to FanVue...")
        await fv.post_content(text=story.get('caption_fanvue'), image_path=nsfw_image_url)
    else:
        logging.error("Failed to generate NSFW image.")
    
    logging.info("Daily Routine Complete.")

async def main_loop():
    scheduler = AsyncIOScheduler()
    
    # Schedule Daily Content (e.g., at 10:00 AM)
    scheduler.add_job(daily_routine, 'cron', hour=10, minute=0)
    
    # Schedule Social Engagement (e.g., every 6 hours)
    fb_bot = FacebookBot()
    scheduler.add_job(fb_bot.run_engagement_cycle, 'interval', hours=6)
    
    scheduler.start()
    logging.info("Scheduler started. Press Ctrl+C to exit.")
    
    # Run the daily routine once immediately for testing/first run
    logging.info("Running initial daily routine...")
    try:
        await daily_routine()
    except Exception as e:
        logging.error(f"Error during initial run: {e}")
    
    # Keep the script running
    try:
        while True:
            await asyncio.sleep(1000)
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    asyncio.run(main_loop())
