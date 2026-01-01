"""
所有代理的基礎類別。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
import json
from datetime import datetime


class BaseAgent(ABC):
    """所有代理的基礎類別。"""
    
    def __init__(self, name: str, description: str):
        """
        初始化基礎代理。
        
        Args:
            name: 代理的名稱
            description: 代理功能的描述
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agents.{name}")
        self.history: List[Dict[str, Any]] = []
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理輸入資料並返回結果。
        
        Args:
            input_data: 包含處理輸入資料的字典
            
        Returns:
            包含處理結果的字典
        """
        pass
    
    def log_activity(self, activity_type: str, details: Dict[str, Any]) -> None:
        """
        記錄代理活動。
        
        Args:
            activity_type: 正在記錄的活動類型
            details: 活動的詳細資訊
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": activity_type,
            "details": details
        }
        self.history.append(entry)
        self.logger.info(f"{self.name} - {activity_type}: {json.dumps(details, ensure_ascii=False)}")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        取得代理的活動歷史記錄。
        
        Returns:
            活動項目列表
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """清除活動歷史記錄。"""
        self.history.clear()
        self.logger.info(f"{self.name} - History cleared")
    
    def get_info(self) -> Dict[str, Any]:
        """
        取得代理的資訊。
        
        Returns:
            包含代理資訊的字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "history_count": len(self.history)
        }
