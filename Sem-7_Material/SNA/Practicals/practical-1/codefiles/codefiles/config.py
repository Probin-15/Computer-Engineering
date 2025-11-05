# Twitter API Configuration
TWITTER_CONFIG = {
    'api_key': 'UNJurKaE2GUkfHGkjXtcz9eSU',
    'api_secret': 'IwwzI8YwCOHeUgHcNxkGdsSwBD4BMgpA3PpLprd5P1uiiYpD9K',
    'bearer_token': 'AAAAAAAAAAAAAAAAAAAAALIc3AEAAAAAmbdKzhulKnmlFWOMiNnQF17ArOY%3D6mG6GwcYD8Pff1dr1WgqDMfRZd26Sna1EIpe20jVzNWSJqsOBL',
    'access_token': '1943991967500890112-Q5ClSGUZcj9JYsjhSCaBIXn1yyYRD9',
    'access_token_secret': 'xpOLke93ceKeJcgeCclYSUQi2MW53oxWLYRWVbu1KFB21'
}

# MongoDB Configuration
MONGODB_CONFIG = {
    'connection_string': 'mongodb+srv://22dcs038:RWpx8wE5MH2LnW4a@cluster0.44dawfr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true',
    'database_name': 'social_network_pract1',
    'collection_name': 'tweets'
}

# Data Collection Configuration
DATA_CONFIG = {
    'max_tweets': 10000,  # Maximum tweets to collect
    'hashtags': ['#python', '#programming', '#technology', '#AI', '#machinelearning'],
    'languages': ['en'],  # Languages to filter
    'min_retweets': 5,  # Minimum retweets for a tweet to be included
    'min_likes': 10      # Minimum likes for a tweet to be included
} 