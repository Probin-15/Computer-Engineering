#!/usr/bin/env python3
"""
Connection Test Script for Social Network Analysis
=================================================

This script tests all connections and configurations before running the main pipeline.
It verifies:
1. Twitter API connectivity
2. MongoDB connection
3. Environment variables
4. Python dependencies

Author: Social Network Analysis Practical
Date: 2024
"""

import os
import sys
import tweepy
import pymongo
import importlib
from config import TWITTER_CONFIG, MONGODB_CONFIG

def test_environment_variables():
    """Test if all required configuration values are set"""
    print("🔍 Testing Configuration Values...")
    
    # Test Twitter config
    twitter_keys = ['api_key', 'api_secret', 'bearer_token', 'access_token', 'access_token_secret']
    for key in twitter_keys:
        value = TWITTER_CONFIG.get(key)
        if value:
            # Mask sensitive values for display
            display_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"  ✅ TWITTER_{key.upper()}: {display_value}")
        else:
            print(f"  ❌ Missing TWITTER_{key.upper()}")
            return False
    
    # Test MongoDB config
    mongo_conn = MONGODB_CONFIG.get('connection_string')
    if mongo_conn:
        print(f"  ✅ MONGODB_CONNECTION_STRING: {mongo_conn[:30]}...")
    else:
        print("  ❌ Missing MONGODB_CONNECTION_STRING")
        return False
    
    print("  ✅ All configuration values are set")
    return True

def test_python_dependencies():
    """Test if all required Python packages are installed"""
    print("\n📦 Testing Python Dependencies...")
    
    required_packages = [
        'tweepy',
        'pymongo',
        'networkx',
        'matplotlib',
        'pandas',
        'seaborn',
        'plotly'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n  ❌ Missing packages: {missing_packages}")
        print("  💡 Run: pip install -r requirements.txt")
        return False
    
    print("  ✅ All required packages are installed")
    return True

def test_twitter_api():
    """Test Twitter API connectivity"""
    print("\n🐦 Testing Twitter API Connection...")
    
    try:
        # Initialize Twitter client
        client = tweepy.Client(
            bearer_token=TWITTER_CONFIG['bearer_token'],
            consumer_key=TWITTER_CONFIG['api_key'],
            consumer_secret=TWITTER_CONFIG['api_secret'],
            access_token=TWITTER_CONFIG['access_token'],
            access_token_secret=TWITTER_CONFIG['access_token_secret'],
            wait_on_rate_limit=True
        )
        
        # Test API with a simple search
        tweets = client.search_recent_tweets(
            query="#python",
            max_results=10,
            tweet_fields=['author_id', 'created_at']
        )
        
        if tweets.data:
            print(f"  ✅ Twitter API connection successful")
            print(f"  📊 Retrieved {len(tweets.data)} test tweets")
            return True
        else:
            print("  ⚠️ Twitter API connected but no tweets returned")
            return True
            
    except Exception as e:
        print(f"  ❌ Twitter API connection failed: {e}")
        return False

def test_mongodb():
    """Test MongoDB connection"""
    print("\n🗄️ Testing MongoDB Connection...")
    
    try:
        # Test connection with proper SSL settings
        client = pymongo.MongoClient(
            MONGODB_CONFIG['connection_string'],
            serverSelectionTimeoutMS=10000
        )
        
        # Test with a ping
        client.admin.command('ping')
        
        # Test database and collection access
        db = client['social_network_pract1']
        collection = db['tweets']
        
        # Test write operation
        test_doc = {"test": True, "timestamp": "2024-01-01"}
        result = collection.insert_one(test_doc)
        
        # Test read operation
        retrieved = collection.find_one({"_id": result.inserted_id})
        
        # Clean up test document
        collection.delete_one({"_id": result.inserted_id})
        
        print("  ✅ MongoDB connection successful")
        print("  📊 Database: social_network_pract1")
        print("  📊 Collection: tweets")
        print("  ✅ Read/Write operations tested successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ MongoDB connection failed: {e}")
        return False

def test_networkx():
    """Test NetworkX functionality"""
    print("\n🔗 Testing NetworkX Graph Operations...")
    
    try:
        import networkx as nx
        
        # Create a test graph
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('B', 'C', weight=2)
        G.add_edge('C', 'A', weight=3)
        
        # Test basic operations
        nodes = G.number_of_nodes()
        edges = G.number_of_edges()
        density = nx.density(G)
        
        print(f"  ✅ NetworkX test graph created")
        print(f"  📊 Nodes: {nodes}, Edges: {edges}, Density: {density:.3f}")
        
        # Test centrality measures
        betweenness = nx.betweenness_centrality(G)
        print(f"  ✅ Centrality measures calculated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ NetworkX test failed: {e}")
        return False

def test_visualization():
    """Test visualization libraries"""
    print("\n📊 Testing Visualization Libraries...")
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.graph_objects as go
        
        # Test matplotlib
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 2])
        plt.close()
        print("  ✅ Matplotlib working")
        
        # Test seaborn
        sns.set_style("whitegrid")
        print("  ✅ Seaborn working")
        
        # Test plotly
        fig = go.Figure(data=go.Bar(x=[1, 2, 3], y=[1, 4, 2]))
        print("  ✅ Plotly working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Visualization test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 SOCIAL NETWORK ANALYSIS - CONNECTION TEST")
    print("="*60)
    
    all_tests_passed = True
    
    # Test environment variables
    if not test_environment_variables():
        all_tests_passed = False
    
    # Test Python dependencies
    if not test_python_dependencies():
        all_tests_passed = False
    
    # Test Twitter API
    if not test_twitter_api():
        all_tests_passed = False
    
    # Test MongoDB
    if not test_mongodb():
        all_tests_passed = False
    
    # Test NetworkX
    if not test_networkx():
        all_tests_passed = False
    
    # Test visualization
    if not test_visualization():
        all_tests_passed = False
    
    print("\n" + "="*60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your system is ready to run the social network analysis")
        print("\n🚀 Next step: python main.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("💡 Please fix the issues above before running the main pipeline")
    
    print("="*60)

if __name__ == "__main__":
    main() 