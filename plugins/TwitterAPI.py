import asyncio
import aiohttp

class TwitterAPI:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.cache = {}  # Initialize an empty cache
        self.semaphore = asyncio.Semaphore(180)  # Initialize a semaphore with a rate limit of 180 requests per 15 minutes

    async def request(self, url, params):
        # Check if the request is in the cache
        cache_key = (url, frozenset(params.items()))
        if cache_key in self.cache:
            return self.cache[cache_key]
        # Acquire the semaphore to ensure that the rate limit is not exceeded
        async with self.semaphore:
            # Make the request to the Twitter API
            async with aiohttp.ClientSession() as session:
                async with session.get(url, auth=(self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret), params=params) as response:
                    data = await response.json()
                    # Add the response to the cache
                    self.cache[cache_key] = data
                    return data

    async def get_tweets(self, screen_name, max_id=None):
        url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        params = {
            "screen_name": screen_name,
            "count": 100,  # Number of tweets to retrieve
            "include_rts": False,  # Exclude retweets
            "max_id": max_id,  # ID of the oldest tweet to retrieve
        }
        return await self.request(url, params)

    async def get_rate_limit_status(self):
        url = "https://api.twitter.com/1.1/application/rate_limit_status.json"
        params = {
            "resources": "statuses",
        }
        return await self.request(url, params)

    async def get_all_tweets(self, screen_name):
        # Initialize the list of all tweets
        all_tweets = []
        # Initialize the ID of the oldest tweet to retrieve
        max_id = None
        # Keep making requests to the Twitter API until we have retrieved all tweets
        while True:
            # Check the rate limit status
            rate_limit_status = await self.get_rate_limit_status()
            # Get the number of remaining requests for the "statuses/user_timeline" endpoint
            remaining = rate_limit_status["resources"]["statuses"]["/statuses/user_timeline"]["remaining"]
            # If we have reached the rate limit, wait until the rate limit window resets
            if remaining == 0:
                reset_time = rate_limit_status["resources"]["statuses"]["/statuses/user_timeline"]["reset"]
                print(f"Rate limit reached. Waiting until {reset_time} to make more requests.")
                await asyncio.sleep(reset_time)
            # Make a request to the Twitter API to retrieve the next batch of tweets
            tweets = await self.get_tweets(screen_name, max_id)
            # If there are no more tweets to retrieve, break out of the loop
            if not tweets:
                break
            # Add the retrieved tweets to the list of all tweets
            all_tweets.extend(tweets)
            # Update the ID of the oldest tweet to retrieve
            max_id = min(tweet["id"] for tweet in tweets) - 1
        # Return the list of all tweets
        return all_tweets

async def main():
    # Next, you will need to create a Twitter developer account and obtain your
    # consumer key, consumer secret, access token, and access token secret.
    # You can do this by following the instructions at this link:
    # https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api

    consumer_key = "YOUR_CONSUMER_KEY"
    consumer_secret = "YOUR_CONSUMER_SECRET"
    access_token = "YOUR_ACCESS_TOKEN"
    access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"

    # Create a TwitterAPI object
    twitter = TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)

    # Use the asyncio event loop to execute the get_all_tweets function asynchronously
    loop = asyncio.get_event_loop()
    tasks = []
    for screen_name in ["twitter_username_1", "twitter_username_2", "twitter_username_3"]:
        task = asyncio.ensure_future(twitter.get_all_tweets(screen_name))
        tasks.append(task)

    # Wait for all tasks to complete
    tweets = await asyncio.gather(*tasks)

    # The "tweets" variable is a list of lists of tweet objects. Each inner list
    # corresponds to the tweets for a particular twitter_username. You can access
    # various properties of each tweet, such as the text, the creation time, and
    # the number of likes and retweets.

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())