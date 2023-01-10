import asyncio
import aiohttp
import json
import time
from aiohttp_socks import SocksConnector, SocksVer
from functools import lru_cache

class InstagramAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.api_url = "https://graph.instagram.com"
        # API endpoints
        self.profile_url = f"{self.api_url}/me"
        self.posts_url = f"{self.api_url}/me/media"
        self.likes_url = f"{self.api_url}/{{post_id}}/likes"
        self.comments_url = f"{self.api_url}/{{post_id}}/comments"
        self.insights_url = f"{self.api_url}/{{post_id}}/insights"

    async def _request(self, url, params):
        # Set up the parameters for the API request
        params = {
            "access_token": self.access_token,
            **params
        }

        # Create a new SocksConnector with connection pooling
        connector = SocksConnector.from_url("socks5://127.0.0.1:9150", timeout=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Make the API request
            async with session.get(url, params=params) as response:
                # Return the response from the API
                return await response.text()

    @lru_cache(maxsize=None)
    async def get_data(self, url, params={}):
        # Make the API request
        response = await self._request(url, params)
        # Parse the JSON response
        data = json.loads(response)
        # Get the rate limit data from the response headers
        rate_limit_remaining = int(response.headers["x-ratelimit-remaining"])
        rate_limit_reset = int(response.headers["x-ratelimit-reset"])
        # Calculate the time until the rate limit reset
        rate_limit_reset_time = rate_limit_reset - time.time()
        # Check if the rate limit has been exceeded
        if rate_limit_remaining == 0:
            # Sleep for the time until the rate limit reset
            await asyncio.sleep(rate_limit_reset_time)
        # Return the data
        return data

    async def get_profile_data(self):
        # Get the user's profile data
        data = await self.get_data(self.profile_url, params={})
        # Return the data
        return data

    async def get_posts_data(self):
        # Get the user's posts data
        data = await self.get_data(self.posts_url, params={})
        # Return the data
        return data

    async def get_likes_data(self, post_id):
        # Get the likes data for the specified post
        likes_url = self.likes_url.format(post_id=post_id)
        data = await self.get_data(likes_url, params={})
        # Return the data
        return data

    async def get_comments_data(self, post_id):
        # Get the comments data for the specified post
        comments_url = self.comments_url.format(post_id=post_id)
        data = await self.get_data(comments_url, params={})
        # Return the data
        return data

    async def get_insights_data(self, post_id):
        # Get the insights data for the specified post
        insights_url = self.insights_url.format(post_id=post_id)
        data = await self.get_data(insights_url, params={})
        # Return the data
        return data

async def main():
    # Replace with your own access_token
    access_token = "ACCESS_TOKEN"
    api = InstagramAPI(access_token)

    # Create a Semaphore to rate limit the number of concurrent API requests
    sem = asyncio.Semaphore(5)

    # Get the user's profile data
    async with sem:
        profile_data = await api.get_profile_data()
        print(profile_data)

    # Get the user's posts data
    async with sem:
        posts_data = await api.get_posts_data()
        print(posts_data)

    # Get the likes, comments, and insights data for each post using asyncio.gather()
    tasks = []
    for post in posts_data["data"]:
        post_id = post["id"]
        task1 = asyncio.create_task(api.get_likes_data(post_id))
        task2 = asyncio.create_task(api.get_comments_data(post_id))
        task3 = asyncio.create_task(api.get_insights_data(post_id))
        tasks.extend([task1, task2, task3])
    data = await asyncio.gather(*tasks)
    print(data)

# Run the main() function asynchronously
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())