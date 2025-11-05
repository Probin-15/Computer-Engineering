import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import networkx as nx
import pymongo
from config import MONGODB_CONFIG
import numpy as np
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class SocialNetworkVisualizer:
    def __init__(self):
        """Initialize MongoDB connection and setup visualization style"""
        self.setup_mongodb()
        self.setup_visualization_style()
        
    def setup_mongodb(self):
        """Setup MongoDB connection"""
        try:
            self.client = pymongo.MongoClient(
                MONGODB_CONFIG['connection_string'],
                serverSelectionTimeoutMS=10000
            )
            self.db = self.client[MONGODB_CONFIG['database_name']]
            self.collection = self.db[MONGODB_CONFIG['collection_name']]
            print("✅ MongoDB connection established for visualization")
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            raise
    
    def setup_visualization_style(self):
        """Setup matplotlib and seaborn style"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def create_engagement_analysis(self):
        """Create engagement analysis plots"""
        print("📊 Creating engagement analysis...")
        
        # Get engagement data
        pipeline = [
            {
                '$project': {
                    'retweet_count': 1,
                    'like_count': 1,
                    'reply_count': 1,
                    'quote_count': 1,
                    'hashtag_count': {'$size': '$hashtags'},
                    'mention_count': {'$size': '$mentions'}
                }
            }
        ]
        
        engagement_data = list(self.collection.aggregate(pipeline))
        df = pd.DataFrame(engagement_data)
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Social Network Engagement Analysis', fontsize=16, fontweight='bold')
        
        # Retweet distribution
        axes[0, 0].hist(df['retweet_count'], bins=30, alpha=0.7, color='skyblue')
        axes[0, 0].set_title('Retweet Distribution')
        axes[0, 0].set_xlabel('Retweet Count')
        axes[0, 0].set_ylabel('Frequency')
        
        # Like distribution
        axes[0, 1].hist(df['like_count'], bins=30, alpha=0.7, color='lightgreen')
        axes[0, 1].set_title('Like Distribution')
        axes[0, 1].set_xlabel('Like Count')
        axes[0, 1].set_ylabel('Frequency')
        
        # Reply distribution
        axes[0, 2].hist(df['reply_count'], bins=30, alpha=0.7, color='salmon')
        axes[0, 2].set_title('Reply Distribution')
        axes[0, 2].set_xlabel('Reply Count')
        axes[0, 2].set_ylabel('Frequency')
        
        # Hashtag count distribution
        axes[1, 0].hist(df['hashtag_count'], bins=range(0, df['hashtag_count'].max() + 2), 
                       alpha=0.7, color='gold')
        axes[1, 0].set_title('Hashtag Count Distribution')
        axes[1, 0].set_xlabel('Number of Hashtags')
        axes[1, 0].set_ylabel('Frequency')
        
        # Mention count distribution
        axes[1, 1].hist(df['mention_count'], bins=range(0, df['mention_count'].max() + 2), 
                       alpha=0.7, color='plum')
        axes[1, 1].set_title('Mention Count Distribution')
        axes[1, 1].set_xlabel('Number of Mentions')
        axes[1, 1].set_ylabel('Frequency')
        
        # Engagement correlation
        correlation_data = df[['retweet_count', 'like_count', 'reply_count', 'quote_count']].corr()
        sns.heatmap(correlation_data, annot=True, cmap='coolwarm', ax=axes[1, 2])
        axes[1, 2].set_title('Engagement Metrics Correlation')
        
        plt.tight_layout()
        plt.savefig('engagement_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Engagement analysis saved as engagement_analysis.png")
    
    def create_hashtag_analysis(self):
        """Create hashtag analysis plots"""
        print("📊 Creating hashtag analysis...")
        
        # Get hashtag data
        pipeline = [
            {'$unwind': '$hashtags'},
            {'$group': {'_id': '$hashtags', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 20}
        ]
        
        hashtag_data = list(self.collection.aggregate(pipeline))
        
        if not hashtag_data:
            print("⚠️ No hashtag data available")
            return
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Hashtag Analysis', fontsize=16, fontweight='bold')
        
        # Top hashtags bar chart
        hashtags = [item['_id'] for item in hashtag_data]
        counts = [item['count'] for item in hashtag_data]
        
        axes[0, 0].barh(range(len(hashtags)), counts, color='skyblue')
        axes[0, 0].set_yticks(range(len(hashtags)))
        axes[0, 0].set_yticklabels(hashtags)
        axes[0, 0].set_title('Top 20 Hashtags by Frequency')
        axes[0, 0].set_xlabel('Frequency')
        
        # Hashtag frequency distribution (log scale)
        axes[0, 1].hist(counts, bins=20, alpha=0.7, color='lightgreen')
        axes[0, 1].set_xscale('log')
        axes[0, 1].set_title('Hashtag Frequency Distribution (Log Scale)')
        axes[0, 1].set_xlabel('Frequency (log scale)')
        axes[0, 1].set_ylabel('Number of Hashtags')
        
        # Hashtag co-occurrence network (simplified)
        co_occurrence_data = self.get_hashtag_co_occurrence()
        if co_occurrence_data:
            # Create a simple network visualization
            G = nx.Graph()
            for (h1, h2), weight in co_occurrence_data.items():
                G.add_edge(h1, h2, weight=weight)
            
            # Get top nodes by degree
            top_nodes = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:10]
            top_node_names = [node for node, _ in top_nodes]
            
            # Create subgraph
            subgraph = G.subgraph(top_node_names)
            pos = nx.spring_layout(subgraph)
            
            nx.draw(subgraph, pos, ax=axes[1, 0], 
                   node_color='lightcoral', 
                   node_size=[G.degree(node) * 50 for node in subgraph.nodes()],
                   with_labels=True, font_size=8)
            axes[1, 0].set_title('Top Hashtag Co-occurrence Network')
        
        # Hashtag usage over time (if timestamp data available)
        time_data = self.get_hashtag_time_series()
        if time_data:
            axes[1, 1].plot(time_data['dates'], time_data['counts'], marker='o')
            axes[1, 1].set_title('Hashtag Usage Over Time')
            axes[1, 1].set_xlabel('Date')
            axes[1, 1].set_ylabel('Number of Tweets with Hashtags')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('hashtag_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Hashtag analysis saved as hashtag_analysis.png")
    
    def get_hashtag_co_occurrence(self):
        """Get hashtag co-occurrence data"""
        pipeline = [
            {'$match': {'hashtags': {'$size': {'$gte': 2}}}},
            {'$project': {'hashtags': 1}},
            {'$limit': 1000}  # Limit for performance
        ]
        
        tweets = list(self.collection.aggregate(pipeline))
        co_occurrence = Counter()
        
        for tweet in tweets:
            hashtags = tweet['hashtags']
            for i in range(len(hashtags)):
                for j in range(i + 1, len(hashtags)):
                    pair = tuple(sorted([hashtags[i], hashtags[j]]))
                    co_occurrence[pair] += 1
        
        return dict(co_occurrence.most_common(20))
    
    def get_hashtag_time_series(self):
        """Get hashtag usage over time"""
        pipeline = [
            {'$match': {'hashtags': {'$ne': []}}},
            {'$group': {
                '_id': {
                    'year': {'$year': '$created_at'},
                    'month': {'$month': '$created_at'},
                    'day': {'$dayOfMonth': '$created_at'}
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        time_data = list(self.collection.aggregate(pipeline))
        
        if not time_data:
            return None
        
        # Convert to dates and counts
        dates = []
        counts = []
        for item in time_data:
            date = f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}"
            dates.append(date)
            counts.append(item['count'])
        
        return {'dates': dates, 'counts': counts}
    
    def create_user_analysis(self):
        """Create user analysis plots"""
        print("📊 Creating user analysis...")
        
        # Get user activity data
        pipeline = [
            {'$group': {
                '_id': '$author_id',
                'tweet_count': {'$sum': 1},
                'avg_retweets': {'$avg': '$retweet_count'},
                'avg_likes': {'$avg': '$like_count'},
                'total_hashtags': {'$sum': {'$size': '$hashtags'}},
                'total_mentions': {'$sum': {'$size': '$mentions'}}
            }},
            {'$sort': {'tweet_count': -1}},
            {'$limit': 50}
        ]
        
        user_data = list(self.collection.aggregate(pipeline))
        
        if not user_data:
            print("⚠️ No user data available")
            return
        
        df = pd.DataFrame(user_data)
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('User Activity Analysis', fontsize=16, fontweight='bold')
        
        # Top users by tweet count
        top_users = df.head(15)
        axes[0, 0].barh(range(len(top_users)), top_users['tweet_count'], color='lightblue')
        axes[0, 0].set_yticks(range(len(top_users)))
        axes[0, 0].set_yticklabels([f"User_{i+1}" for i in range(len(top_users))])
        axes[0, 0].set_title('Top 15 Users by Tweet Count')
        axes[0, 0].set_xlabel('Number of Tweets')
        
        # User engagement scatter plot
        axes[0, 1].scatter(df['avg_retweets'], df['avg_likes'], alpha=0.6, color='lightgreen')
        axes[0, 1].set_xlabel('Average Retweets')
        axes[0, 1].set_ylabel('Average Likes')
        axes[0, 1].set_title('User Engagement: Retweets vs Likes')
        
        # Hashtag vs Mentions usage
        axes[1, 0].scatter(df['total_hashtags'], df['total_mentions'], alpha=0.6, color='salmon')
        axes[1, 0].set_xlabel('Total Hashtags Used')
        axes[1, 0].set_ylabel('Total Mentions Made')
        axes[1, 0].set_title('User Behavior: Hashtags vs Mentions')
        
        # Tweet count distribution
        axes[1, 1].hist(df['tweet_count'], bins=20, alpha=0.7, color='gold')
        axes[1, 1].set_xlabel('Number of Tweets')
        axes[1, 1].set_ylabel('Number of Users')
        axes[1, 1].set_title('Distribution of User Tweet Counts')
        
        plt.tight_layout()
        plt.savefig('user_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ User analysis saved as user_analysis.png")
    
    def create_network_metrics_dashboard(self):
        """Create a comprehensive network metrics dashboard"""
        print("📊 Creating network metrics dashboard...")
        
        # Get basic statistics
        total_tweets = self.collection.count_documents({})
        unique_users = len(self.collection.distinct("author_id"))
        unique_hashtags = len(self.collection.distinct("hashtags"))
        unique_mentions = len(self.collection.distinct("mentions"))
        
        # Create dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Network Overview', 'Engagement Metrics', 'Content Analysis', 'User Activity'),
            specs=[[{"type": "indicator"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "scatter"}]]
        )
        
        # Network overview indicators
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=total_tweets,
            title={"text": "Total Tweets"},
            delta={'reference': total_tweets * 0.9},
            domain={'row': 0, 'column': 0}
        ), row=1, col=1)
        
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=unique_users,
            title={"text": "Unique Users"},
            delta={'reference': unique_users * 0.9},
            domain={'row': 0, 'column': 0}
        ), row=1, col=1)
        
        # Engagement metrics
        engagement_data = self.get_engagement_summary()
        fig.add_trace(go.Bar(
            x=['Retweets', 'Likes', 'Replies', 'Quotes'],
            y=[engagement_data['avg_retweets'], engagement_data['avg_likes'], 
               engagement_data['avg_replies'], engagement_data['avg_quotes']],
            name='Average Engagement'
        ), row=1, col=2)
        
        # Content analysis pie chart
        content_data = [unique_hashtags, unique_mentions, total_tweets - unique_hashtags - unique_mentions]
        fig.add_trace(go.Pie(
            labels=['Hashtags', 'Mentions', 'Plain Tweets'],
            values=content_data,
            name='Content Types'
        ), row=2, col=1)
        
        # User activity scatter
        user_activity = self.get_user_activity_data()
        fig.add_trace(go.Scatter(
            x=user_activity['tweet_counts'],
            y=user_activity['engagement_scores'],
            mode='markers',
            name='User Activity'
        ), row=2, col=2)
        
        fig.update_layout(height=800, title_text="Social Network Analysis Dashboard")
        fig.write_html("network_dashboard.html")
        print("✅ Network dashboard saved as network_dashboard.html")
    
    def get_engagement_summary(self):
        """Get engagement summary statistics"""
        pipeline = [
            {'$group': {
                '_id': None,
                'avg_retweets': {'$avg': '$retweet_count'},
                'avg_likes': {'$avg': '$like_count'},
                'avg_replies': {'$avg': '$reply_count'},
                'avg_quotes': {'$avg': '$quote_count'}
            }}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else {'avg_retweets': 0, 'avg_likes': 0, 'avg_replies': 0, 'avg_quotes': 0}
    
    def get_user_activity_data(self):
        """Get user activity data for scatter plot"""
        pipeline = [
            {'$group': {
                '_id': '$author_id',
                'tweet_count': {'$sum': 1},
                'avg_engagement': {'$avg': {'$add': ['$retweet_count', '$like_count']}}
            }},
            {'$limit': 100}
        ]
        
        user_data = list(self.collection.aggregate(pipeline))
        return {
            'tweet_counts': [user['tweet_count'] for user in user_data],
            'engagement_scores': [user['avg_engagement'] for user in user_data]
        }

def main():
    """Main function to create all visualizations"""
    print("🚀 Starting Social Network Visualization...")
    
    try:
        # Initialize visualizer
        visualizer = SocialNetworkVisualizer()
        
        # Create different types of visualizations
        visualizer.create_engagement_analysis()
        visualizer.create_hashtag_analysis()
        visualizer.create_user_analysis()
        visualizer.create_network_metrics_dashboard()
        
        print("✅ All visualizations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in visualization: {e}")

if __name__ == "__main__":
    main() 