"""
專案規劃與執行的代理套件。

本套件包含三個專門的代理：
- strategic-planner: 互動需求分析、里程碑規劃與依賴關係管理
- steering-architect: 產品藍圖、技術選型與結構規範
- task-executor: 讀取規格並實作專案（腳手架、配置、測試框架）
"""

from .strategic_planner import StrategicPlanner
from .steering_architect import SteeringArchitect
from .task_executor import TaskExecutor
from .agent_manager import AgentManager

__all__ = [
    'StrategicPlanner',
    'SteeringArchitect',
    'TaskExecutor',
    'AgentManager'
]
