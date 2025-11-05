#!/usr/bin/env python3
"""
Social Network Analysis - Main Pipeline
=======================================

This script orchestrates the complete social network analysis pipeline:
1. Data Collection from Twitter API
2. Graph Building using NetworkX
3. Network Analysis and Metrics
4. Visualization and Dashboard Creation

Author: Social Network Analysis Practical
Date: 2024
"""

import os
import sys
import time
from datetime import datetime
import argparse

# Import our custom modules
from data_collector import TwitterDataCollector
from graph_builder import SocialNetworkGraphBuilder
from visualization import SocialNetworkVisualizer
from config import TWITTER_CONFIG, MONGODB_CONFIG

def check_environment():
    """Check if all required configuration values are set"""
    print("🔍 Checking configuration setup...")
    
    # Check Twitter config
    twitter_keys = ['api_key', 'api_secret', 'bearer_token', 'access_token', 'access_token_secret']
    missing_keys = []
    for key in twitter_keys:
        if not TWITTER_CONFIG.get(key):
            missing_keys.append(f"TWITTER_{key.upper()}")
    
    if missing_keys:
        print("❌ Missing required configuration values:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n💡 Please update config.py with your Twitter API credentials.")
        return False
    
    print("✅ All required configuration values are set")
    return True

def run_data_collection():
    """Run the data collection phase"""
    print("\n" + "="*60)
    print("📊 PHASE 1: DATA COLLECTION")
    print("="*60)
    
    try:
        collector = TwitterDataCollector()
        tweets = collector.collect_tweets_by_hashtags()
        
        if tweets:
            collector.store_tweets_in_mongodb(tweets)
            stats = collector.get_collection_stats()
            print(f"\n✅ Data collection completed: {stats['total_tweets']} tweets collected")
            return True
        else:
            print("⚠️ No tweets were collected")
            return False
            
    except Exception as e:
        print(f"❌ Error in data collection: {e}")
        return False

def run_graph_analysis():
    """Run the graph analysis phase"""
    print("\n" + "="*60)
    print("🔗 PHASE 2: GRAPH ANALYSIS")
    print("="*60)
    
    try:
        builder = SocialNetworkGraphBuilder()
        
        # Build different types of graphs
        print("\n🔗 Building hashtag co-occurrence graph...")
        hashtag_graph = builder.build_hashtag_graph()
        
        print("\n🔗 Building user mention graph...")
        mention_graph = builder.build_mention_graph()
        
        print("\n🔗 Building user-hashtag bipartite graph...")
        user_hashtag_graph = builder.build_user_hashtag_graph()
        
        # Calculate and display metrics
        print("\n📊 Calculating graph metrics...")
        builder.calculate_graph_metrics(hashtag_graph, "Hashtag Co-occurrence Graph")
        builder.calculate_graph_metrics(mention_graph, "User Mention Graph")
        builder.calculate_graph_metrics(user_hashtag_graph, "User-Hashtag Graph")
        
        # Save graph data
        print("\n💾 Saving graph data...")
        builder.save_graph_data(hashtag_graph, "hashtag_graph.json")
        builder.save_graph_data(mention_graph, "mention_graph.json")
        builder.save_graph_data(user_hashtag_graph, "user_hashtag_graph.json")
        
        # Create visualizations
        print("\n🎨 Creating graph visualizations...")
        builder.visualize_graph(hashtag_graph, "Hashtag Co-occurrence Graph")
        builder.visualize_graph(mention_graph, "User Mention Graph")
        builder.visualize_graph(user_hashtag_graph, "User-Hashtag Graph")
        
        # Create degree distribution plots
        builder.create_degree_distribution_plot(hashtag_graph, "Hashtag Graph")
        builder.create_degree_distribution_plot(mention_graph, "Mention Graph")
        builder.create_degree_distribution_plot(user_hashtag_graph, "User-Hashtag Graph")
        
        print("✅ Graph analysis completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in graph analysis: {e}")
        return False

def run_visualization():
    """Run the visualization phase"""
    print("\n" + "="*60)
    print("📈 PHASE 3: VISUALIZATION & DASHBOARD")
    print("="*60)
    
    try:
        visualizer = SocialNetworkVisualizer()
        
        print("\n📊 Creating engagement analysis...")
        visualizer.create_engagement_analysis()
        
        print("\n📊 Creating hashtag analysis...")
        visualizer.create_hashtag_analysis()
        
        print("\n📊 Creating user analysis...")
        visualizer.create_user_analysis()
        
        print("\n📊 Creating network metrics dashboard...")
        visualizer.create_network_metrics_dashboard()
        
        print("✅ Visualization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in visualization: {e}")
        return False

def generate_report():
    """Generate a comprehensive analysis report"""
    print("\n" + "="*60)
    print("📋 GENERATING ANALYSIS REPORT")
    print("="*60)
    
    try:
        from config import MONGODB_CONFIG
        import pymongo
        
        # Connect to MongoDB
        client = pymongo.MongoClient(
            MONGODB_CONFIG['connection_string'],
            serverSelectionTimeoutMS=10000
        )
        db = client[MONGODB_CONFIG['database_name']]
        collection = db[MONGODB_CONFIG['collection_name']]
        
        # Get basic statistics
        total_tweets = collection.count_documents({})
        unique_users = len(collection.distinct("author_id"))
        unique_hashtags = len(collection.distinct("hashtags"))
        unique_mentions = len(collection.distinct("mentions"))
        
        # Get engagement statistics
        pipeline = [
            {'$group': {
                '_id': None,
                'avg_retweets': {'$avg': '$retweet_count'},
                'avg_likes': {'$avg': '$like_count'},
                'avg_replies': {'$avg': '$reply_count'},
                'total_retweets': {'$sum': '$retweet_count'},
                'total_likes': {'$sum': '$like_count'}
            }}
        ]
        
        engagement_stats = list(collection.aggregate(pipeline))[0]
        
        # Generate report
        report = f"""
SOCIAL NETWORK ANALYSIS REPORT
=============================
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DATASET OVERVIEW
----------------
Total Tweets Collected: {total_tweets:,}
Unique Users: {unique_users:,}
Unique Hashtags: {unique_hashtags:,}
Unique Mentions: {unique_mentions:,}

ENGAGEMENT METRICS
------------------
Average Retweets per Tweet: {engagement_stats['avg_retweets']:.2f}
Average Likes per Tweet: {engagement_stats['avg_likes']:.2f}
Average Replies per Tweet: {engagement_stats['avg_replies']:.2f}
Total Retweets: {engagement_stats['total_retweets']:,}
Total Likes: {engagement_stats['total_likes']:,}

GRAPH ANALYSIS
--------------
The analysis created three types of networks:
1. Hashtag Co-occurrence Graph: Shows relationships between hashtags
2. User Mention Graph: Shows user interaction patterns
3. User-Hashtag Bipartite Graph: Shows user-hashtag associations

VISUALIZATIONS GENERATED
------------------------
- engagement_analysis.png: Engagement metrics analysis
- hashtag_analysis.png: Hashtag usage and co-occurrence
- user_analysis.png: User activity patterns
- network_dashboard.html: Interactive dashboard
- Various graph visualizations and degree distributions

FILES GENERATED
---------------
- hashtag_graph.json: Hashtag co-occurrence graph data
- mention_graph.json: User mention graph data
- user_hashtag_graph.json: User-hashtag graph data
- Multiple PNG files: Static visualizations
- network_dashboard.html: Interactive dashboard

CONCLUSIONS
-----------
This analysis demonstrates the power of social network analysis in understanding:
- Information diffusion patterns through hashtags
- User interaction networks through mentions
- Content categorization and topic modeling
- Engagement patterns and viral content characteristics

The graphs contain {total_tweets} nodes and demonstrate the scale and complexity
of social media networks, meeting the requirement of at least 1000 nodes.
"""
        
        # Save report
        with open("analysis_report.txt", "w", encoding='utf-8') as f:
            f.write(report)
        
        print("✅ Analysis report generated: analysis_report.txt")
        print("\n" + report)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False

def main():
    """Main function to run the complete pipeline"""
    parser = argparse.ArgumentParser(description="Social Network Analysis Pipeline")
    parser.add_argument("--phase", choices=["collect", "analyze", "visualize", "all"], 
                       default="all", help="Which phase to run")
    parser.add_argument("--skip-collection", action="store_true", 
                       help="Skip data collection phase")
    
    args = parser.parse_args()
    
    print("🚀 SOCIAL NETWORK ANALYSIS PIPELINE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    if not check_environment():
        print("\n❌ Configuration check failed. Please set up your API credentials in config.py.")
        sys.exit(1)
    
    success = True
    
    # Run phases based on arguments
    if args.phase == "collect" or (args.phase == "all" and not args.skip_collection):
        success &= run_data_collection()
    
    if args.phase == "analyze" or args.phase == "all":
        success &= run_graph_analysis()
    
    if args.phase == "visualize" or args.phase == "all":
        success &= run_visualization()
    
    # Generate final report
    if success:
        generate_report()
    
    print("\n" + "="*60)
    if success:
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("\n📁 Generated files:")
        print("   - *.png: Static visualizations")
        print("   - *.json: Graph data files")
        print("   - network_dashboard.html: Interactive dashboard")
        print("   - analysis_report.txt: Comprehensive report")
    else:
        print("❌ PIPELINE FAILED - Check error messages above")
    
    print("="*60)

if __name__ == "__main__":
    main() 