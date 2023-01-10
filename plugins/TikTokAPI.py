import asyncio
import aiohttp
import time
import json

class TikTokAPI:
    def __init__(self, api_key, user_id):
        self.api_key = api_key
        self.user_id = user_id
        self.session = None
        self.urls = {
            "profile": f"https://api.tiktok.com/v1/profile?user_id={user_id}&api_key={api_key}",
            "views": f"https://api.tiktok.com/v1/item/list?user_id={user_id}&api_key={api_key}",
            "shares": f"https://api.tiktok.com/v1/item/list?user_id={user_id}&api_key={api_key}",
            "likes": f"https://api.tiktok.com/v1/item/list?user_id={user_id}&api_key={api_key}",
            "comments": f"https://api.tiktok.com/v1/item/list?user_id={user_id}&api_key={api_key}",
            "posts": f"https://api.tiktok.com/v1/item/list?user_id={user_id}&api_key={api_key}",
        }
        
    async def create_session(self):
        self.session = aiohttp.ClientSession()
        
    async def fetch(self, url):
        # Check the TikTok rate limit
        rate_limit_remaining = int(self.session.headers.get("rateLimit-remaining"))
        if rate_limit_remaining == 0:
            rate_limit_reset = int(self.session.headers.get("rateLimit-reset"))
            current_time = int(time.time())
            time_to_wait = rate_limit_reset - current_time + 1
            print(f"Waiting {time_to_wait} seconds to reset rate limit")
            await asyncio.sleep(time_to_wait)
        
        # Make the request to the TikTok API
        async with self.session.get(url) as response:
            return await response.text()
        
    async def get_profile(self):
        return await self.fetch(self.urls["profile"])
    
    async def get_views(self):
        return await self.fetch(self.urls["views"])
    
    async def get_shares(self):
        return await self.fetch(self.urls["shares"])
    
    async def get_likes(self):
        return await self.fetch(self.urls["likes"])
    
    async def get_comments(self):
        return await self.fetch(self.urls["comments"])
    
    async def get_posts(self):
        return await self.fetch(self.urls["posts"])
    
    async def get_post_count(self):
        """
        Returns the total number of posts made by the user.
        """
        profile_data = json.loads(await self.get_profile())
        return profile_data["item_count"]
    
    async def iterate_posts(self):
        """
        Iterates over all of the posts made by the user and yields the post data.
        """
        total_posts = await self.get_post_count()
        for i in range(0, total_posts, 20):
            url = self.urls["posts"] + f"&count=20&offset={i}"
            posts_data = json.loads(await self.fetch(url))
            for post in posts_data["items"]:
                yield post
    
    async def close_session(self):
        await self.session.close()

async def main():
    # Set the API key and user ID
    api_key = "YOUR_API_KEY"
    user_id = "2222"
    
    # Create a new TikTok API instance
    api = TikTokAPI(api_key, user_id)
    
    # Create an HTTP session
    await api.create_session()
    
    # Get the profile data
    profile = await api.get_profile()
    print(profile)
    
    # Iterate over all of the posts
    async for post in api.iterate_posts():
        print(post)
    
    # Close the HTTP session
    await api.close_session()

if __name__ == "__main__":
    asyncio.run(main())