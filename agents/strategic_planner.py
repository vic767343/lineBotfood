"""
Strategic Planner Agent

Responsibilities:
- Interaction requirement analysis
- Milestone planning
- Dependency relationship management
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class StrategicPlanner(BaseAgent):
    """
    Strategic Planner Agent that handles:
    - Interaction requirement analysis
    - Milestone planning
    - Dependency relationships
    """
    
    def __init__(self):
        super().__init__(
            name="strategic-planner",
            description="負責互動需求分析、里程碑計畫與依賴關係管理"
        )
        self.requirements: List[Dict[str, Any]] = []
        self.milestones: List[Dict[str, Any]] = []
        self.dependencies: Dict[str, List[str]] = {}
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process strategic planning requests.
        
        Args:
            input_data: Dictionary with keys:
                - action: 'analyze_requirements' | 'create_milestones' | 'manage_dependencies'
                - data: Relevant data for the action
                
        Returns:
            Dictionary containing processing results
        """
        action = input_data.get("action")
        data = input_data.get("data", {})
        
        if action == "analyze_requirements":
            return self._analyze_requirements(data)
        elif action == "create_milestones":
            return self._create_milestones(data)
        elif action == "manage_dependencies":
            return self._manage_dependencies(data)
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }
    
    def _analyze_requirements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze interaction requirements.
        
        Args:
            data: Dictionary containing requirement information
            
        Returns:
            Analysis results
        """
        requirement = {
            "id": len(self.requirements) + 1,
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "interactions": data.get("interactions", []),
            "stakeholders": data.get("stakeholders", []),
            "priority": data.get("priority", "medium"),
            "analysis": {
                "complexity": self._assess_complexity(data),
                "risks": self._identify_risks(data),
                "user_flows": data.get("user_flows", [])
            }
        }
        
        self.requirements.append(requirement)
        self.log_activity("requirement_analysis", {
            "requirement_id": requirement["id"],
            "title": requirement["title"]
        })
        
        return {
            "status": "success",
            "requirement": requirement,
            "total_requirements": len(self.requirements)
        }
    
    def _create_milestones(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create project milestones.
        
        Args:
            data: Dictionary containing milestone information
            
        Returns:
            Milestone creation results
        """
        milestone = {
            "id": len(self.milestones) + 1,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "target_date": data.get("target_date", ""),
            "deliverables": data.get("deliverables", []),
            "requirements": data.get("requirements", []),
            "status": "planned"
        }
        
        self.milestones.append(milestone)
        self.log_activity("milestone_created", {
            "milestone_id": milestone["id"],
            "name": milestone["name"]
        })
        
        return {
            "status": "success",
            "milestone": milestone,
            "total_milestones": len(self.milestones)
        }
    
    def _manage_dependencies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage dependency relationships.
        
        Args:
            data: Dictionary containing dependency information
            
        Returns:
            Dependency management results
        """
        item_id = data.get("item_id", "")
        depends_on = data.get("depends_on", [])
        
        if item_id:
            self.dependencies[item_id] = depends_on
            self.log_activity("dependencies_updated", {
                "item_id": item_id,
                "depends_on": depends_on
            })
            
            return {
                "status": "success",
                "item_id": item_id,
                "dependencies": depends_on,
                "dependency_chain": self._get_dependency_chain(item_id)
            }
        
        return {
            "status": "error",
            "message": "item_id is required"
        }
    
    def _assess_complexity(self, data: Dict[str, Any]) -> str:
        """Assess the complexity of a requirement."""
        interactions = data.get("interactions", [])
        stakeholders = data.get("stakeholders", [])
        
        complexity_score = len(interactions) + len(stakeholders)
        
        if complexity_score < 3:
            return "low"
        elif complexity_score < 6:
            return "medium"
        else:
            return "high"
    
    def _identify_risks(self, data: Dict[str, Any]) -> List[str]:
        """Identify potential risks in a requirement."""
        risks = []
        
        if not data.get("stakeholders"):
            risks.append("缺少利害關係人定義")
        
        if not data.get("interactions"):
            risks.append("缺少互動流程定義")
        
        if data.get("priority") == "high" and not data.get("deadline"):
            risks.append("高優先級需求缺少截止日期")
        
        return risks
    
    def _get_dependency_chain(self, item_id: str) -> List[str]:
        """Get the full dependency chain for an item."""
        chain = []
        visited = set()
        
        def traverse(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)
            
            deps = self.dependencies.get(current_id, [])
            for dep in deps:
                chain.append(dep)
                traverse(dep)
        
        traverse(item_id)
        return chain
    
    def get_all_requirements(self) -> List[Dict[str, Any]]:
        """Get all analyzed requirements."""
        return self.requirements.copy()
    
    def get_all_milestones(self) -> List[Dict[str, Any]]:
        """Get all created milestones."""
        return self.milestones.copy()
    
    def get_all_dependencies(self) -> Dict[str, List[str]]:
        """Get all dependency relationships."""
        return self.dependencies.copy()
