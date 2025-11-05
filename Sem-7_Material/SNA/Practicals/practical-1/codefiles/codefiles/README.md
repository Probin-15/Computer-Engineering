# Social Network Analysis - Twitter Data Pipeline

This project implements a complete social network analysis pipeline for extracting and analyzing Twitter data. It builds directed weighted graphs using hashtags and mentions, stores data in MongoDB, and provides comprehensive visualizations and metrics.

## 🎯 Project Overview

### Key Features
- **Data Collection**: Extract tweets using Twitter API v2 with Tweepy
- **Graph Building**: Create directed weighted graphs using NetworkX
- **Database Storage**: Store and pre-process data using MongoDB
- **Network Analysis**: Calculate in-degree, out-degree, density, and other metrics
- **Visualization**: Generate static plots and interactive dashboards
- **Scalability**: Designed to handle networks with 1000+ nodes

### Graph Types Built
1. **Hashtag Co-occurrence Graph**: Shows relationships between hashtags
2. **User Mention Graph**: Shows user interaction patterns  
3. **User-Hashtag Bipartite Graph**: Shows user-hashtag associations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (local or Atlas)
- Twitter Developer Account

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd social-network-pract1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB**
   - **Local MongoDB**: Install and start MongoDB service
   - **MongoDB Atlas**: Create free cluster and get connection string

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your credentials
   nano .env
   ```

### Required API Keys

#### Twitter API Keys (Free)
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a free account and apply for Basic access
3. Create a new app to get:
   - API Key
   - API Secret
   - Bearer Token
   - Access Token
   - Access Token Secret

#### MongoDB Connection
- **Local**: `mongodb://localhost:27017/`
- **Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/`

## 📊 Usage

### Complete Pipeline
Run the entire analysis pipeline:
```bash
python main.py
```

### Individual Phases
```bash
# Data collection only
python main.py --phase collect

# Graph analysis only
python main.py --phase analyze

# Visualization only
python main.py --phase visualize

# Skip data collection (if you already have data)
python main.py --skip-collection
```

### Manual Execution
```bash
# Collect data
python data_collector.py

# Build graphs
python graph_builder.py

# Create visualizations
python visualization.py
```

## 📁 Project Structure

```
social-network-pract1/
├── main.py                 # Main pipeline orchestrator
├── data_collector.py       # Twitter data collection
├── graph_builder.py        # NetworkX graph construction
├── visualization.py        # Matplotlib/Plotly visualizations
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables template
├── README.md             # This file
└── generated_files/      # Output directory
    ├── *.png            # Static visualizations
    ├── *.json           # Graph data files
    ├── network_dashboard.html  # Interactive dashboard
    └── analysis_report.txt     # Comprehensive report
```

## 🔧 Configuration

### Data Collection Settings
Edit `config.py` to customize:
- Hashtags to search for
- Minimum engagement thresholds
- Maximum tweets to collect
- Language filters

### MongoDB Settings
Configure database settings in `config.py`:
- Connection string
- Database name
- Collection name

## 📈 Output Files

### Visualizations
- `engagement_analysis.png`: Engagement metrics analysis
- `hashtag_analysis.png`: Hashtag usage and co-occurrence
- `user_analysis.png`: User activity patterns
- `*_visualization.png`: Graph network visualizations
- `*_degree_distribution.png`: Degree distribution plots

### Data Files
- `hashtag_graph.json`: Hashtag co-occurrence graph data
- `mention_graph.json`: User mention graph data
- `user_hashtag_graph.json`: User-hashtag graph data

### Interactive Dashboard
- `network_dashboard.html`: Comprehensive interactive dashboard

### Reports
- `analysis_report.txt`: Detailed analysis report

## 🔍 Network Metrics

The analysis calculates and visualizes:

### Basic Metrics
- **Nodes**: Number of vertices in the graph
- **Edges**: Number of connections
- **Density**: Ratio of actual to possible edges
- **Connectivity**: Whether the graph is connected

### Degree Analysis
- **In-degree**: Number of incoming connections
- **Out-degree**: Number of outgoing connections
- **Average degree**: Mean degree across all nodes
- **Degree distribution**: Histogram of node degrees

### Centrality Measures
- **Betweenness centrality**: Node importance as bridge
- **Closeness centrality**: Average distance to other nodes
- **Eigenvector centrality**: Influence based on neighbors

## 🛠️ Troubleshooting

### MongoDB Connection Issues
**Problem**: `ECONNREFUSED 127.0.0.1:27022`
**Solutions**:
1. Use default port: `mongodb://localhost:27017/`
2. Start MongoDB service: `net start MongoDB`
3. Use MongoDB Atlas (cloud)

### Twitter API Issues
**Problem**: Rate limiting or authentication errors
**Solutions**:
1. Check API credentials in `.env`
2. Verify Twitter Developer App permissions
3. Wait for rate limit reset

### Missing Dependencies
**Problem**: Import errors
**Solution**:
```bash
pip install -r requirements.txt
```

## 📚 Learning Outcomes

This project addresses key skills:

### Technical Skills
- **API Integration**: Twitter API v2 with Tweepy
- **NoSQL Database**: MongoDB operations and aggregation
- **Graph Theory**: NetworkX for graph analysis
- **Data Visualization**: Matplotlib, Seaborn, Plotly
- **Data Processing**: Pandas for data manipulation

### Analysis Skills
- **Social Network Analysis**: Understanding network structures
- **Data Pipeline Design**: End-to-end data processing
- **Statistical Analysis**: Network metrics and distributions
- **Visualization Design**: Creating informative plots

## 🎓 Academic Requirements

### Practical Objectives Met
- ✅ Extract data from Twitter APIs
- ✅ Build directed weighted graphs (1000+ nodes)
- ✅ Store data in NoSQL database (MongoDB)
- ✅ Calculate in-degree, out-degree, density
- ✅ Visualize network statistics
- ✅ Pre-process social media data

### Key Questions Addressed
1. **API Data Extraction**: How to use Tweepy for Twitter data collection
2. **Graph Structure**: How to build and measure network properties
3. **MongoDB Usage**: How to store and query social media data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect Twitter's API terms of service and data usage policies.

## 🙏 Acknowledgments

- Twitter API for providing data access
- NetworkX for graph analysis capabilities
- MongoDB for NoSQL database solution
- Matplotlib/Plotly for visualization tools

---

**Note**: This project is designed for educational purposes and social network analysis research. Always comply with Twitter's API terms of service and data usage policies. 