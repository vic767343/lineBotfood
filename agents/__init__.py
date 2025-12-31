"""
Agents package for project planning and execution.

This package contains three specialized agents:
- strategic-planner: Interaction requirement analysis, milestone planning, and dependency relationships
- steering-architect: Product blueprint, technology selection, and structural specifications
- task-executor: Reads specifications and implements projects (scaffolding, configuration, test framework)
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
