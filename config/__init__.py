import json
import os
from pathlib import Path

def get_config():
    """
    載入配置檔案
    
    Returns:
        dict: 配置檔案的內容
    """
    config_path = Path(__file__).parent / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
