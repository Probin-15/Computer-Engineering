import networkx as nx
import pymongo
import pandas as pd
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from config import MONGODB_CONFIG
import json

class SocialNetworkGraphBuilder:
    def __init__(self):
        """Initialize MongoDB connection and graph objects"""
        self.setup_mongodb()
        self.hashtag_graph = nx.DiGraph()
        self.mention_graph = nx.DiGraph()
        self.user_hashtag_graph = nx.DiGraph()
        
    def setup_mongodb(self):
        """Setup MongoDB connection"""
        try:
            self.client = pymongo.MongoClient(
                MONGODB_CONFIG['connection_string'],
                serverSelectionTimeoutMS=10000
            )
            self.db = self.client[MONGODB_CONFIG['database_name']]
            self.collection = self.db[MONGODB_CONFIG['collection_name']]
            print("✅ MongoDB connection established for graph building")
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            raise
    
    def build_hashtag_graph(self):
        """Build directed weighted graph based on hashtag co-occurrence"""
        print("🔗 Building hashtag co-occurrence graph...")
        
        # Get all tweets with hashtags
        tweets = self.collection.find({"hashtags": {"$ne": []}})
        
        hashtag_pairs = defaultdict(int)
        
        for tweet in tweets:
            hashtags = tweet['hashtags']
            if len(hashtags) >= 2:
                # Create pairs of hashtags
                for i in range(len(hashtags)):
                    for j in range(i + 1, len(hashtags)):
                        pair = tuple(sorted([hashtags[i], hashtags[j]]))
                        hashtag_pairs[pair] += 1
        
        # Add edges to graph
        for (hashtag1, hashtag2), weight in hashtag_pairs.items():
            self.hashtag_graph.add_edge(hashtag1, hashtag2, weight=weight)
            self.hashtag_graph.add_edge(hashtag2, hashtag1, weight=weight)  # Undirected for co-occurrence
        
        print(f"✅ Hashtag graph built with {self.hashtag_graph.number_of_nodes()} nodes and {self.hashtag_graph.number_of_edges()} edges")
        return self.hashtag_graph
    
    def build_mention_graph(self):
        """Build directed weighted graph based on user mentions"""
        print("🔗 Building user mention graph...")
        
        # Get all tweets with mentions
        tweets = self.collection.find({"mentions": {"$ne": []}})
        
        mention_edges = defaultdict(int)
        
        for tweet in tweets:
            author = tweet['author_id']
            mentions = tweet['mentions']
            
            # Create edges from author to mentioned users
            for mention in mentions:
                mention_clean = mention.replace('@', '')
                edge = (author, mention_clean)
                mention_edges[edge] += 1
        
        # Add edges to graph
        for (source, target), weight in mention_edges.items():
            self.mention_graph.add_edge(source, target, weight=weight)
        
        print(f"✅ Mention graph built with {self.mention_graph.number_of_nodes()} nodes and {self.mention_graph.number_of_edges()} edges")
        return self.mention_graph
    
    def build_user_hashtag_graph(self):
        """Build bipartite graph between users and hashtags"""
        print("🔗 Building user-hashtag bipartite graph...")
        
        # Get all tweets
        tweets = self.collection.find({})
        
        user_hashtag_edges = defaultdict(int)
        
        for tweet in tweets:
            author = tweet['author_id']
            hashtags = tweet['hashtags']
            
            # Create edges from user to hashtags
            for hashtag in hashtags:
                edge = (author, hashtag)
                user_hashtag_edges[edge] += 1
        
        # Add edges to graph
        for (user, hashtag), weight in user_hashtag_edges.items():
            self.user_hashtag_graph.add_edge(user, hashtag, weight=weight)
        
        print(f"✅ User-hashtag graph built with {self.user_hashtag_graph.number_of_nodes()} nodes and {self.user_hashtag_graph.number_of_edges()} edges")
        return self.user_hashtag_graph
    
    def calculate_graph_metrics(self, graph, graph_name):
        """Calculate various graph metrics"""
        if graph.number_of_nodes() == 0:
            print(f"⚠️ {graph_name} is empty")
            return {}
        
        metrics = {
            'nodes': graph.number_of_nodes(),
            'edges': graph.number_of_edges(),
            'density': nx.density(graph),
            'is_connected': nx.is_connected(graph.to_undirected()) if not graph.is_directed() else nx.is_weakly_connected(graph),
            'average_clustering': nx.average_clustering(graph.to_undirected()) if not graph.is_directed() else nx.average_clustering(graph.to_undirected()),
        }
        
        # Degree statistics
        if graph.is_directed():
            in_degrees = [d for n, d in graph.in_degree()]
            out_degrees = [d for n, d in graph.out_degree()]
            metrics.update({
                'avg_in_degree': sum(in_degrees) / len(in_degrees),
                'avg_out_degree': sum(out_degrees) / len(out_degrees),
                'max_in_degree': max(in_degrees),
                'max_out_degree': max(out_degrees),
            })
        else:
            degrees = [d for n, d in graph.degree()]
            metrics.update({
                'avg_degree': sum(degrees) / len(degrees),
                'max_degree': max(degrees),
            })
        
        print(f"\n📊 {graph_name} Metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")
        
        return metrics
    
    def get_top_nodes(self, graph, metric='degree', top_n=10):
        """Get top nodes by specified metric"""
        if graph.number_of_nodes() == 0:
            return []
        
        if metric == 'degree':
            if graph.is_directed():
                node_scores = [(n, d) for n, d in graph.in_degree()]
            else:
                node_scores = [(n, d) for n, d in graph.degree()]
        elif metric == 'betweenness':
            node_scores = nx.betweenness_centrality(graph).items()
        elif metric == 'closeness':
            node_scores = nx.closeness_centrality(graph).items()
        elif metric == 'eigenvector':
            node_scores = nx.eigenvector_centrality(graph, max_iter=1000).items()
        else:
            return []
        
        # Sort by score (descending)
        sorted_nodes = sorted(node_scores, key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_n]
    
    def save_graph_data(self, graph, filename):
        """Save graph data to JSON file"""
        try:
            # Convert graph to JSON-serializable format
            graph_data = {
                'nodes': [{'id': n, 'degree': graph.degree(n)} for n in graph.nodes()],
                'edges': [{'source': u, 'target': v, 'weight': graph[u][v].get('weight', 1)} 
                         for u, v in graph.edges()]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2)
            
            print(f"✅ Graph data saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving graph data: {e}")
    
    def visualize_graph(self, graph, graph_name, max_nodes=50):
        """Create a simple visualization of the graph"""
        if graph.number_of_nodes() == 0:
            print(f"⚠️ Cannot visualize empty {graph_name}")
            return
        
        # Limit nodes for visualization
        if graph.number_of_nodes() > max_nodes:
            # Get top nodes by degree
            top_nodes = [n for n, d in sorted(graph.degree(), key=lambda x: x[1], reverse=True)[:max_nodes]]
            subgraph = graph.subgraph(top_nodes)
        else:
            subgraph = graph
        
        plt.figure(figsize=(12, 8))
        
        # Use spring layout for positioning
        pos = nx.spring_layout(subgraph, k=1, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(subgraph, pos, node_size=100, node_color='lightblue')
        
        # Draw edges
        nx.draw_networkx_edges(subgraph, pos, alpha=0.5, edge_color='gray')
        
        # Draw labels (only for smaller graphs)
        if subgraph.number_of_nodes() <= 20:
            nx.draw_networkx_labels(subgraph, pos, font_size=8)
        
        plt.title(f"{graph_name} (Top {subgraph.number_of_nodes()} nodes)")
        plt.axis('off')
        
        # Save the plot
        filename = f"{graph_name.lower().replace(' ', '_')}_visualization.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Graph visualization saved as {filename}")
    
    def create_degree_distribution_plot(self, graph, graph_name):
        """Create degree distribution plot"""
        if graph.number_of_nodes() == 0:
            return
        
        plt.figure(figsize=(10, 6))
        
        if graph.is_directed():
            in_degrees = [d for n, d in graph.in_degree()]
            out_degrees = [d for n, d in graph.out_degree()]
            
            plt.subplot(1, 2, 1)
            plt.hist(in_degrees, bins=20, alpha=0.7, label='In-degree')
            plt.xlabel('In-degree')
            plt.ylabel('Frequency')
            plt.title(f'{graph_name} - In-degree Distribution')
            plt.legend()
            
            plt.subplot(1, 2, 2)
            plt.hist(out_degrees, bins=20, alpha=0.7, label='Out-degree', color='orange')
            plt.xlabel('Out-degree')
            plt.ylabel('Frequency')
            plt.title(f'{graph_name} - Out-degree Distribution')
            plt.legend()
        else:
            degrees = [d for n, d in graph.degree()]
            plt.hist(degrees, bins=20, alpha=0.7)
            plt.xlabel('Degree')
            plt.ylabel('Frequency')
            plt.title(f'{graph_name} - Degree Distribution')
        
        filename = f"{graph_name.lower().replace(' ', '_')}_degree_distribution.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Degree distribution plot saved as {filename}")

def main():
    """Main function to build and analyze graphs"""
    print("🚀 Starting Social Network Graph Analysis...")
    
    try:
        # Initialize graph builder
        builder = SocialNetworkGraphBuilder()
        
        # Build different types of graphs
        hashtag_graph = builder.build_hashtag_graph()
        mention_graph = builder.build_mention_graph()
        user_hashtag_graph = builder.build_user_hashtag_graph()
        
        # Calculate metrics for each graph
        hashtag_metrics = builder.calculate_graph_metrics(hashtag_graph, "Hashtag Co-occurrence Graph")
        mention_metrics = builder.calculate_graph_metrics(mention_graph, "User Mention Graph")
        user_hashtag_metrics = builder.calculate_graph_metrics(user_hashtag_graph, "User-Hashtag Graph")
        
        # Get top nodes for each graph
        print("\n🏆 Top 10 Hashtags by Degree:")
        top_hashtags = builder.get_top_nodes(hashtag_graph, 'degree', 10)
        for node, degree in top_hashtags:
            print(f"  {node}: {degree}")
        
        print("\n🏆 Top 10 Users by In-degree (Most Mentioned):")
        top_mentioned = builder.get_top_nodes(mention_graph, 'degree', 10)
        for node, degree in top_mentioned:
            print(f"  {node}: {degree}")
        
        # Save graph data
        builder.save_graph_data(hashtag_graph, "hashtag_graph.json")
        builder.save_graph_data(mention_graph, "mention_graph.json")
        builder.save_graph_data(user_hashtag_graph, "user_hashtag_graph.json")
        
        # Create visualizations
        builder.visualize_graph(hashtag_graph, "Hashtag Co-occurrence Graph")
        builder.visualize_graph(mention_graph, "User Mention Graph")
        builder.visualize_graph(user_hashtag_graph, "User-Hashtag Graph")
        
        # Create degree distribution plots
        builder.create_degree_distribution_plot(hashtag_graph, "Hashtag Graph")
        builder.create_degree_distribution_plot(mention_graph, "Mention Graph")
        builder.create_degree_distribution_plot(user_hashtag_graph, "User-Hashtag Graph")
        
        print("\n✅ Graph analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in graph analysis: {e}")

if __name__ == "__main__":
    main() 