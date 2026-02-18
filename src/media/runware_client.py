import asyncio
from runware import Runware, IImageInference
from src.config import Config

class RunwareClient:
    def __init__(self):
        self.api_key = Config.RUNWARE_API_KEY
        self.model_id = Config.RUNWARE_MODEL_ID
        
    async def generate_image(self, prompt):
        """
        Generates an image using the Official Runware SDK.
        """
        try:
            runware = Runware(api_key=self.api_key)
            await runware.connect()

            request_image = IImageInference(
                positivePrompt=prompt,
                negativePrompt="ugly, blurry, low quality, cartoon, anime, deformed",
                width=1024,
                height=1344,
                numberResults=1,
                model=self.model_id,
                steps=25,
            )

            response = await runware.imageInference(request_image)
            
            # Ensure connection is closed
            # Note: The SDK might handle this differently, but explicit disconnect is safe
            # await runware.disconnect() 
            
            if response and len(response) > 0:
                 return response[0].imageURL
            return None

        except Exception as e:
            print(f"Runware Error: {e}")
            return None

# Wrapper for synchronous calls if needed (for the main loop which is currently sync)
def generate_image_sync(prompt):
    client = RunwareClient()
    return asyncio.run(client.generate_image(prompt))
