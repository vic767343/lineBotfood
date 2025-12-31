"""
Steering Architect Agent

Responsibilities:
- Product blueprint design
- Technology selection
- Structural specifications
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class SteeringArchitect(BaseAgent):
    """
    Steering Architect Agent that handles:
    - Product blueprint design
    - Technology selection and evaluation
    - Structural specifications and standards
    """
    
    def __init__(self):
        super().__init__(
            name="steering-architect",
            description="負責產品藍圖、技術選型與結構規範"
        )
        self.blueprints: List[Dict[str, Any]] = []
        self.technologies: Dict[str, Any] = {}
        self.specifications: List[Dict[str, Any]] = []
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process architecture requests.
        
        Args:
            input_data: Dictionary with keys:
                - action: 'create_blueprint' | 'select_technology' | 'define_specification'
                - data: Relevant data for the action
                
        Returns:
            Dictionary containing processing results
        """
        action = input_data.get("action")
        data = input_data.get("data", {})
        
        if action == "create_blueprint":
            return self._create_blueprint(data)
        elif action == "select_technology":
            return self._select_technology(data)
        elif action == "define_specification":
            return self._define_specification(data)
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }
    
    def _create_blueprint(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create product blueprint.
        
        Args:
            data: Dictionary containing blueprint information
            
        Returns:
            Blueprint creation results
        """
        blueprint = {
            "id": len(self.blueprints) + 1,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "version": data.get("version", "1.0.0"),
            "components": data.get("components", []),
            "architecture_style": data.get("architecture_style", ""),
            "layers": data.get("layers", []),
            "data_flow": data.get("data_flow", []),
            "integration_points": data.get("integration_points", []),
            "scalability": {
                "horizontal": data.get("horizontal_scalability", False),
                "vertical": data.get("vertical_scalability", False),
                "strategy": data.get("scalability_strategy", "")
            }
        }
        
        self.blueprints.append(blueprint)
        self.log_activity("blueprint_created", {
            "blueprint_id": blueprint["id"],
            "name": blueprint["name"]
        })
        
        return {
            "status": "success",
            "blueprint": blueprint,
            "total_blueprints": len(self.blueprints)
        }
    
    def _select_technology(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select and evaluate technology.
        
        Args:
            data: Dictionary containing technology information
            
        Returns:
            Technology selection results
        """
        category = data.get("category", "")
        technology = {
            "name": data.get("name", ""),
            "version": data.get("version", ""),
            "category": category,
            "rationale": data.get("rationale", ""),
            "alternatives": data.get("alternatives", []),
            "pros": data.get("pros", []),
            "cons": data.get("cons", []),
            "learning_curve": data.get("learning_curve", "medium"),
            "community_support": data.get("community_support", "medium"),
            "maturity": data.get("maturity", "stable"),
            "license": data.get("license", ""),
            "cost": data.get("cost", "free")
        }
        
        if category not in self.technologies:
            self.technologies[category] = []
        
        self.technologies[category].append(technology)
        self.log_activity("technology_selected", {
            "category": category,
            "name": technology["name"]
        })
        
        return {
            "status": "success",
            "technology": technology,
            "category_total": len(self.technologies[category])
        }
    
    def _define_specification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define structural specification.
        
        Args:
            data: Dictionary containing specification information
            
        Returns:
            Specification definition results
        """
        specification = {
            "id": len(self.specifications) + 1,
            "name": data.get("name", ""),
            "type": data.get("type", ""),  # coding, api, database, security, etc.
            "description": data.get("description", ""),
            "rules": data.get("rules", []),
            "examples": data.get("examples", []),
            "enforcement": data.get("enforcement", "recommended"),  # required, recommended, optional
            "tools": data.get("tools", []),
            "references": data.get("references", [])
        }
        
        self.specifications.append(specification)
        self.log_activity("specification_defined", {
            "specification_id": specification["id"],
            "name": specification["name"],
            "type": specification["type"]
        })
        
        return {
            "status": "success",
            "specification": specification,
            "total_specifications": len(self.specifications)
        }
    
    def get_technology_stack(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the complete technology stack."""
        return self.technologies.copy()
    
    def get_all_blueprints(self) -> List[Dict[str, Any]]:
        """Get all created blueprints."""
        return self.blueprints.copy()
    
    def get_all_specifications(self) -> List[Dict[str, Any]]:
        """Get all defined specifications."""
        return self.specifications.copy()
    
    def get_architecture_summary(self) -> Dict[str, Any]:
        """Get a summary of the architecture decisions."""
        return {
            "blueprints_count": len(self.blueprints),
            "technology_categories": list(self.technologies.keys()),
            "specifications_count": len(self.specifications),
            "latest_blueprint": self.blueprints[-1] if self.blueprints else None
        }
