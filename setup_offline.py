"""
Setup script to download and cache tiktoken encoding for offline use.
Run this script once to cache the encoding file.
"""

import tiktoken
import os

print("Downloading and caching tiktoken encoding...")

try:
    # Download and cache the cl100k_base encoding
    encoding = tiktoken.get_encoding("cl100k_base")
    print("✅ Successfully cached cl100k_base encoding")
    
    # Show cache location
    cache_dir = os.path.expanduser("~/.cache/tiktoken_cache")
    print(f"💾 Encoding cached at: {cache_dir}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Please ensure you have internet connectivity and try again.")
