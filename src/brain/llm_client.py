from openai import OpenAI
import json
from src.config import Config
from src.brain.personas import get_system_prompt

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
        )
        self.model = Config.OPENROUTER_MODEL

    def generate_daily_story(self):
        """Generates a story concept for the day with dual-platform targeting."""
        prompt = """
        Generate a concept for today's social media posts.
        The story involves Mei (42yo Asian VP) and Lady K (22yo Domme).
        
        Output JSON format:
        {
            "story_title": "Short title",
            "scene_description_sfw": "A safe-for-work visual description (e.g., office setting, clothed, subtle power dynamics).",
            "scene_description_nsfw": "An explicit visual description for FanVue (e.g., lingerie, humiliation, bondage, or nudity).",
            "caption_mainstream": "A captivating but safe caption for Facebook/Instagram (suggestive but clean).",
            "caption_fanvue": "Explicit caption for FanVue."
        }
        """
        response = self.client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": Config.OPENROUTER_REFERER,
                "X-Title": "FanVue Agent",
            },
            model=self.model,
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def generate_image_prompt(self, scene_description, safety="safe"):
        """
        Refines a scene description into a Runware image prompt.
        safety: "safe" or "nsfw"
        """
        safety_instruction = ""
        if safety == "safe":
            safety_instruction = "Ensure the image is fully clothed, professional, and safe for Instagram/Facebook. No nudity."
        else:
            safety_instruction = "This is for an adult platform. Nudity and fetish wear are allowed and encouraged."

        prompt = f"""
        Convert this scene description into a stable diffusion image prompt.
        Focus on: cinematic lighting, photorealistic, 8k, highly detailed.
        
        Context: {safety_instruction}
        
        Scene: {scene_description}
        
        Characters:
        - Mei: 42 year old Asian woman, milf, glasses, business attire (if safe) or lingerie (if nsfw), submissive expression.
        - Lady K: (If visible) 22 year old woman, dominant, smirk.
        
        Output only the prompt string.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert AI art prompter."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
