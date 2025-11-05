#!/usr/bin/env python3
"""
Setup script for Social Network Analysis Project
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_config_file():
    """Check if config.py has proper credentials"""
    if os.path.exists("config.py"):
        print("✅ config.py file exists")
        print("💡 Please verify your API credentials in config.py")
        return True
    else:
        print("❌ config.py file not found")
        return False

def check_mongodb():
    """Check MongoDB connection"""
    print("\n🔍 Checking MongoDB connection...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB connection successful (local)")
        return True
    except Exception as e:
        print("⚠️ Local MongoDB not accessible")
        print("💡 You can use MongoDB Atlas (cloud) instead")
        print("   Connection string format: mongodb+srv://username:password@cluster.mongodb.net/")
        return False

def main():
    """Main setup function"""
    print("🚀 Social Network Analysis - Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check configuration file
    check_config_file()
    
    # Check MongoDB
    check_mongodb()
    
    print("\n" + "="*50)
    print("✅ Setup completed!")
    print("\n📋 Next steps:")
    print("1. Verify your Twitter API credentials in config.py")
    print("2. Set up MongoDB (local or Atlas)")
    print("3. Run: python main.py")
    print("\n📚 For detailed instructions, see README.md")

if __name__ == "__main__":
    main() 