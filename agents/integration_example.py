"""
整合範例：將代理與 LINE Bot 食物追蹤系統整合使用。

本檔案展示如何將三個代理整合到現有的 LINE Bot 食物追蹤應用程式中，
用於專案規劃和功能開發。
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import AgentManager


class ProjectPlanningHelper:
    """協助使用代理來規劃 LINE Bot 新功能的輔助類別。"""
    
    def __init__(self):
        """使用代理管理器初始化規劃輔助工具。"""
        self.manager = AgentManager()
        self.planner = self.manager.get_agent("strategic-planner")
        self.architect = self.manager.get_agent("steering-architect")
        self.executor = self.manager.get_agent("task-executor")
    
    def plan_new_feature(self, feature_name: str, feature_description: str):
        """
        為新功能執行完整的規劃工作流程。
        
        Args:
            feature_name: 新功能的名稱
            feature_description: 功能的描述
            
        Returns:
            完整的規劃結果
        """
        results = {
            "feature": feature_name,
            "steps": []
        }
        
        # Step 1: Analyze requirements
        print(f"\n[Step 1] Analyzing requirements for: {feature_name}")
        req_result = self.planner.process({
            "action": "analyze_requirements",
            "data": {
                "title": feature_name,
                "description": feature_description,
                "interactions": [],
                "stakeholders": ["Users", "Development Team"],
                "priority": "medium"
            }
        })
        results["steps"].append({"step": "requirements", "result": req_result})
        print(f"✓ Requirement analyzed: {req_result['requirement']['id']}")
        
        # Step 2: Create milestone
        print(f"\n[Step 2] Creating milestone...")
        milestone_result = self.planner.process({
            "action": "create_milestones",
            "data": {
                "name": f"{feature_name} - MVP",
                "description": f"Minimum viable version of {feature_name}",
                "deliverables": ["Core functionality", "Unit tests", "Documentation"]
            }
        })
        results["steps"].append({"step": "milestone", "result": milestone_result})
        print(f"✓ Milestone created: {milestone_result['milestone']['name']}")
        
        # Step 3: Create technical blueprint
        print(f"\n[Step 3] Creating technical blueprint...")
        blueprint_result = self.architect.process({
            "action": "create_blueprint",
            "data": {
                "name": f"{feature_name} Architecture",
                "description": f"Technical architecture for {feature_name}",
                "components": ["Service Layer", "Controller", "Data Model"],
                "architecture_style": "Layered Architecture"
            }
        })
        results["steps"].append({"step": "blueprint", "result": blueprint_result})
        print(f"✓ Blueprint created: {blueprint_result['blueprint']['id']}")
        
        # Step 4: Define specifications
        print(f"\n[Step 4] Defining specifications...")
        spec_result = self.architect.process({
            "action": "define_specification",
            "data": {
                "name": f"{feature_name} Coding Standards",
                "type": "coding",
                "description": "Coding standards for this feature",
                "rules": [
                    "Follow PEP 8 style guide",
                    "Add type hints to all functions",
                    "Write docstrings for all public methods",
                    "Keep functions under 50 lines"
                ],
                "enforcement": "required"
            }
        })
        results["steps"].append({"step": "specification", "result": spec_result})
        print(f"✓ Specification defined: {spec_result['specification']['name']}")
        
        # Step 5: Plan implementation tasks
        print(f"\n[Step 5] Planning implementation...")
        impl_result = self.executor.process({
            "action": "read_specification",
            "data": {
                "spec_id": f"spec-{feature_name.lower().replace(' ', '-')}",
                "name": f"{feature_name} Implementation",
                "type": "feature",
                "content": {
                    "tasks": [
                        {
                            "name": "Create service module",
                            "description": f"Implement {feature_name} service"
                        },
                        {
                            "name": "Create controller",
                            "description": f"Add controller endpoints for {feature_name}"
                        },
                        {
                            "name": "Write tests",
                            "description": "Add unit and integration tests"
                        }
                    ]
                }
            }
        })
        results["steps"].append({"step": "implementation_plan", "result": impl_result})
        print(f"✓ Implementation planned: {len(impl_result['tasks_to_execute'])} tasks")
        
        return results


def example_plan_nutrition_analysis():
    """範例：規劃營養分析功能。"""
    print("=" * 70)
    print("  Example: Planning 'Nutrition Analysis' Feature")
    print("=" * 70)
    
    helper = ProjectPlanningHelper()
    
    results = helper.plan_new_feature(
        feature_name="Nutrition Analysis",
        feature_description="Analyze uploaded food images and provide detailed nutrition information including macros, vitamins, and minerals"
    )
    
    print("\n" + "=" * 70)
    print("  Planning Complete!")
    print("=" * 70)
    print(f"\nTotal planning steps completed: {len(results['steps'])}")
    print("\nNext steps:")
    print("1. Review and refine the requirements")
    print("2. Start implementation following the planned tasks")
    print("3. Track progress against the milestone")


def example_plan_meal_recommendation():
    """範例：規劃餐點推薦系統。"""
    print("\n\n" + "=" * 70)
    print("  Example: Planning 'Meal Recommendation' Feature")
    print("=" * 70)
    
    helper = ProjectPlanningHelper()
    
    results = helper.plan_new_feature(
        feature_name="Meal Recommendation System",
        feature_description="Provide personalized meal recommendations based on user's dietary history, preferences, and health goals"
    )
    
    print("\n" + "=" * 70)
    print("  Planning Complete!")
    print("=" * 70)
    print(f"\nTotal planning steps completed: {len(results['steps'])}")


def example_full_workflow():
    """範例：新專案模組的完整工作流程。"""
    print("\n\n" + "=" * 70)
    print("  Example: Full Workflow - Calorie Tracking Enhancement")
    print("=" * 70)
    
    manager = AgentManager()
    
    workflow_result = manager.execute_workflow({
        "type": "new_project",
        "requirements": {
            "title": "Enhanced Calorie Tracking",
            "description": "Add advanced calorie tracking with weekly/monthly summaries and trend analysis",
            "interactions": ["View summaries", "Compare periods", "Export data"],
            "stakeholders": ["Users", "Nutritionists", "Product Team"],
            "priority": "high"
        },
        "milestones": {
            "name": "Calorie Tracking v2.0",
            "description": "Enhanced calorie tracking with analytics",
            "target_date": "2024-07-31",
            "deliverables": [
                "Summary views",
                "Trend charts",
                "Data export",
                "User documentation"
            ]
        },
        "blueprint": {
            "name": "Calorie Analytics Architecture",
            "description": "Architecture for advanced calorie tracking and analytics",
            "architecture_style": "Event-driven Architecture",
            "components": [
                "Data Aggregation Service",
                "Analytics Engine",
                "Visualization Service",
                "Export Service"
            ]
        },
        "technologies": [
            {
                "category": "data-processing",
                "name": "Pandas",
                "version": "2.3.3",
                "rationale": "Excellent for data analysis and manipulation"
            }
        ],
        "scaffolding": {
            "project_name": "calorie-analytics",
            "project_type": "module",
            "directories": [
                "Service/CalorieAnalytics",
                "Service/CalorieAnalytics/aggregation",
                "Service/CalorieAnalytics/visualization"
            ],
            "files": [
                {
                    "path": "Service/CalorieAnalytics/__init__.py",
                    "template": "python_init"
                }
            ]
        },
        "test_framework": {
            "framework_name": "pytest",
            "type": "integration",
            "coverage_enabled": True,
            "coverage_threshold": 85
        }
    })
    
    print(f"\n✓ Workflow completed with {workflow_result['total_steps']} steps")
    print("\nWorkflow summary:")
    for i, step in enumerate(workflow_result['steps'], 1):
        print(f"  {i}. {step['agent']}: {step['action']}")


if __name__ == "__main__":
    # Run examples
    example_plan_nutrition_analysis()
    example_plan_meal_recommendation()
    example_full_workflow()
    
    print("\n\n" + "=" * 70)
    print("  All Integration Examples Completed")
    print("=" * 70)
    print("\n📝 Key Takeaways:")
    print("  • Use agents to plan new features systematically")
    print("  • Integrate agents into your development workflow")
    print("  • Leverage pre-built workflows for consistency")
    print("  • Track progress through agent history")
