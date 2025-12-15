import json
import os
from pathlib import Path

# Load environment variables from .env file


def get_config():
    """
    載入配置檔案
    
    Returns:
        dict: 配置檔案的內容
    """
    config_path = Path(__file__).parent / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Override sensitive data with environment variables
    if 'gemini' in config and 'apikey' in config['gemini']:
        config['gemini']['apikey'] = os.getenv('GEMINI_API_KEY', config['gemini']['apikey'])
    
    return config
