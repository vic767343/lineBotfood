"""
Base Agent class for all agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
import json
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the base agent.
        
        Args:
            name: The name of the agent
            description: Description of what the agent does
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agents.{name}")
        self.history: List[Dict[str, Any]] = []
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        Args:
            input_data: Dictionary containing input data for processing
            
        Returns:
            Dictionary containing processing results
        """
        pass
    
    def log_activity(self, activity_type: str, details: Dict[str, Any]) -> None:
        """
        Log agent activity.
        
        Args:
            activity_type: Type of activity being logged
            details: Details of the activity
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
        Get the activity history of the agent.
        
        Returns:
            List of activity entries
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear the activity history."""
        self.history.clear()
        self.logger.info(f"{self.name} - History cleared")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the agent.
        
        Returns:
            Dictionary containing agent information
        """
        return {
            "name": self.name,
            "description": self.description,
            "history_count": len(self.history)
        }
