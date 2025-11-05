import tweepy
import pymongo
import json
import time
from datetime import datetime
from config import TWITTER_CONFIG, MONGODB_CONFIG, DATA_CONFIG
import re

class TwitterDataCollector:
    def __init__(self):
        """Initialize Twitter API client and MongoDB connection"""
        self.setup_twitter_api()
        self.setup_mongodb()
        
    def setup_twitter_api(self):
        """Setup Twitter API client using Tweepy"""
        try:
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=TWITTER_CONFIG['bearer_token'],
                consumer_key=TWITTER_CONFIG['api_key'],
                consumer_secret=TWITTER_CONFIG['api_secret'],
                access_token=TWITTER_CONFIG['access_token'],
                access_token_secret=TWITTER_CONFIG['access_token_secret'],
                wait_on_rate_limit=True
            )
            print("✅ Twitter API client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Twitter API: {e}")
            raise
    
    def setup_mongodb(self):
        """Setup MongoDB connection"""
        try:
            self.client_mongo = pymongo.MongoClient(
                MONGODB_CONFIG['connection_string'],
                serverSelectionTimeoutMS=10000
            )
            self.db = self.client_mongo[MONGODB_CONFIG['database_name']]
            self.collection = self.db[MONGODB_CONFIG['collection_name']]
            
            # Test connection
            self.client_mongo.admin.command('ping')
            print("✅ MongoDB connection established successfully")
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            print("💡 Make sure MongoDB is running on the correct port")
            raise
    
    def extract_hashtags(self, text):
        """Extract hashtags from tweet text"""
        hashtags = re.findall(r'#\w+', text.lower())
        return hashtags
    
    def extract_mentions(self, text):
        """Extract mentions from tweet text"""
        mentions = re.findall(r'@\w+', text.lower())
        return mentions
    
    def collect_tweets_by_hashtags(self):
        """Collect tweets using hashtags"""
        all_tweets = []
        
        for hashtag in DATA_CONFIG['hashtags']:
            print(f"🔍 Collecting tweets for {hashtag}...")
            
            try:
                # Search tweets with hashtag
                tweets = tweepy.Paginator(
                    self.client.search_recent_tweets,
                    query=f"{hashtag} lang:en",
                    max_results=100,
                    tweet_fields=['author_id', 'created_at', 'public_metrics', 'entities']
                ).flatten(limit=1000)
                
                hashtag_tweets = []
                for tweet in tweets:
                    # Extract hashtags and mentions
                    hashtags = self.extract_hashtags(tweet.text)
                    mentions = self.extract_mentions(tweet.text)
                    
                    # Create tweet document
                    tweet_doc = {
                        'tweet_id': str(tweet.id),
                        'text': tweet.text,
                        'author_id': tweet.author_id,
                        'created_at': tweet.created_at,
                        'hashtags': hashtags,
                        'mentions': mentions,
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'quote_count': tweet.public_metrics['quote_count'],
                        'collected_at': datetime.now(),
                        'source_hashtag': hashtag
                    }
                    
                    # Filter by engagement criteria
                    if (tweet_doc['retweet_count'] >= DATA_CONFIG['min_retweets'] or 
                        tweet_doc['like_count'] >= DATA_CONFIG['min_likes']):
                        hashtag_tweets.append(tweet_doc)
                
                all_tweets.extend(hashtag_tweets)
                print(f"📊 Collected {len(hashtag_tweets)} tweets for {hashtag}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error collecting tweets for {hashtag}: {e}")
                continue
        
        return all_tweets
    
    def store_tweets_in_mongodb(self, tweets):
        """Store tweets in MongoDB"""
        if not tweets:
            print("⚠️ No tweets to store")
            return
        
        try:
            # Insert tweets into MongoDB
            result = self.collection.insert_many(tweets)
            print(f"✅ Successfully stored {len(result.inserted_ids)} tweets in MongoDB")
            
            # Create indexes for better query performance
            self.collection.create_index([("tweet_id", pymongo.ASCENDING)], unique=True)
            self.collection.create_index([("hashtags", pymongo.ASCENDING)])
            self.collection.create_index([("mentions", pymongo.ASCENDING)])
            self.collection.create_index([("author_id", pymongo.ASCENDING)])
            
            print("✅ Database indexes created successfully")
            
        except Exception as e:
            print(f"❌ Error storing tweets in MongoDB: {e}")
            raise
    
    def get_collection_stats(self):
        """Get statistics about the collected data"""
        try:
            total_tweets = self.collection.count_documents({})
            unique_users = len(self.collection.distinct("author_id"))
            unique_hashtags = len(self.collection.distinct("hashtags"))
            unique_mentions = len(self.collection.distinct("mentions"))
            
            print("\n📊 Collection Statistics:")
            print(f"Total tweets: {total_tweets}")
            print(f"Unique users: {unique_users}")
            print(f"Unique hashtags: {unique_hashtags}")
            print(f"Unique mentions: {unique_mentions}")
            
            return {
                'total_tweets': total_tweets,
                'unique_users': unique_users,
                'unique_hashtags': unique_hashtags,
                'unique_mentions': unique_mentions
            }
            
        except Exception as e:
            print(f"❌ Error getting collection stats: {e}")
            return None

def main():
    """Main function to run the data collection"""
    print("🚀 Starting Twitter Data Collection...")
    
    try:
        # Initialize collector
        collector = TwitterDataCollector()
        
        # Collect tweets
        tweets = collector.collect_tweets_by_hashtags()
        
        if tweets:
            # Store in MongoDB
            collector.store_tweets_in_mongodb(tweets)
            
            # Get statistics
            collector.get_collection_stats()
            
            print("✅ Data collection completed successfully!")
        else:
            print("⚠️ No tweets were collected")
            
    except Exception as e:
        print(f"❌ Error in data collection: {e}")

if __name__ == "__main__":
    main() 