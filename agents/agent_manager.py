"""
Agent Manager

Manages and coordinates all agents in the system.
"""

from typing import Dict, Any, List, Optional
import logging
from .strategic_planner import StrategicPlanner
from .steering_architect import SteeringArchitect
from .task_executor import TaskExecutor


class AgentManager:
    """
    Manages and coordinates all agents.
    
    Provides a unified interface to work with:
    - Strategic Planner
    - Steering Architect
    - Task Executor
    """
    
    def __init__(self):
        """Initialize the agent manager with all agents."""
        self.logger = logging.getLogger("agents.manager")
        
        # Initialize agents
        self.strategic_planner = StrategicPlanner()
        self.steering_architect = SteeringArchitect()
        self.task_executor = TaskExecutor()
        
        self.agents = {
            "strategic-planner": self.strategic_planner,
            "steering-architect": self.steering_architect,
            "task-executor": self.task_executor
        }
        
        self.logger.info("Agent Manager initialized with 3 agents")
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """
        Get a specific agent by name.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all available agents.
        
        Returns:
            List of agent information
        """
        return [agent.get_info() for agent in self.agents.values()]
    
    def execute_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete workflow across multiple agents.
        
        Args:
            workflow_data: Dictionary containing workflow information
            
        Returns:
            Workflow execution results
        """
        workflow_type = workflow_data.get("type", "")
        results = {
            "workflow_type": workflow_type,
            "steps": []
        }
        
        if workflow_type == "new_project":
            # Step 1: Analyze requirements with Strategic Planner
            requirements = workflow_data.get("requirements", {})
            req_result = self.strategic_planner.process({
                "action": "analyze_requirements",
                "data": requirements
            })
            results["steps"].append({
                "agent": "strategic-planner",
                "action": "analyze_requirements",
                "result": req_result
            })
            
            # Step 2: Create milestones with Strategic Planner
            milestones = workflow_data.get("milestones", {})
            milestone_result = self.strategic_planner.process({
                "action": "create_milestones",
                "data": milestones
            })
            results["steps"].append({
                "agent": "strategic-planner",
                "action": "create_milestones",
                "result": milestone_result
            })
            
            # Step 3: Create blueprint with Steering Architect
            blueprint = workflow_data.get("blueprint", {})
            blueprint_result = self.steering_architect.process({
                "action": "create_blueprint",
                "data": blueprint
            })
            results["steps"].append({
                "agent": "steering-architect",
                "action": "create_blueprint",
                "result": blueprint_result
            })
            
            # Step 4: Select technologies with Steering Architect
            technologies = workflow_data.get("technologies", [])
            for tech in technologies:
                tech_result = self.steering_architect.process({
                    "action": "select_technology",
                    "data": tech
                })
                results["steps"].append({
                    "agent": "steering-architect",
                    "action": "select_technology",
                    "result": tech_result
                })
            
            # Step 5: Create scaffolding with Task Executor
            scaffolding = workflow_data.get("scaffolding", {})
            scaffolding_result = self.task_executor.process({
                "action": "create_scaffolding",
                "data": scaffolding
            })
            results["steps"].append({
                "agent": "task-executor",
                "action": "create_scaffolding",
                "result": scaffolding_result
            })
            
            # Step 6: Setup test framework with Task Executor
            test_framework = workflow_data.get("test_framework", {})
            test_result = self.task_executor.process({
                "action": "setup_test_framework",
                "data": test_framework
            })
            results["steps"].append({
                "agent": "task-executor",
                "action": "setup_test_framework",
                "result": test_result
            })
        
        results["status"] = "completed"
        results["total_steps"] = len(results["steps"])
        
        self.logger.info(f"Workflow '{workflow_type}' completed with {len(results['steps'])} steps")
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get status of all agents in the system.
        
        Returns:
            System status information
        """
        return {
            "agents": self.list_agents(),
            "strategic_planner": {
                "requirements": len(self.strategic_planner.get_all_requirements()),
                "milestones": len(self.strategic_planner.get_all_milestones()),
                "dependencies": len(self.strategic_planner.get_all_dependencies())
            },
            "steering_architect": self.steering_architect.get_architecture_summary(),
            "task_executor": {
                "tasks": len(self.task_executor.get_all_tasks()),
                "implementations": len(self.task_executor.get_all_implementations()),
                "configurations": len(self.task_executor.get_all_configurations())
            }
        }
    
    def reset_all_agents(self) -> Dict[str, Any]:
        """
        Reset all agents to initial state.
        
        Returns:
            Reset confirmation
        """
        for agent in self.agents.values():
            agent.clear_history()
        
        self.logger.info("All agents have been reset")
        
        return {
            "status": "success",
            "message": "所有代理已重置"
        }
