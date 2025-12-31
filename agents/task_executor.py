"""
Task Executor Agent

Responsibilities:
- Reading specifications
- Implementing projects (scaffolding, configuration, test framework)
- Executing development tasks
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
import os
import json


class TaskExecutor(BaseAgent):
    """
    Task Executor Agent that handles:
    - Reading and parsing specifications
    - Project implementation (scaffolding, configuration, test framework)
    - Task execution and tracking
    """
    
    def __init__(self):
        super().__init__(
            name="task-executor",
            description="負責讀取規格並實作專案（腳手架、設定、測試框架等）"
        )
        self.tasks: List[Dict[str, Any]] = []
        self.implementations: List[Dict[str, Any]] = []
        self.configurations: Dict[str, Any] = {}
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process task execution requests.
        
        Args:
            input_data: Dictionary with keys:
                - action: 'read_specification' | 'create_scaffolding' | 'setup_configuration' | 'setup_test_framework' | 'execute_task'
                - data: Relevant data for the action
                
        Returns:
            Dictionary containing processing results
        """
        action = input_data.get("action")
        data = input_data.get("data", {})
        
        if action == "read_specification":
            return self._read_specification(data)
        elif action == "create_scaffolding":
            return self._create_scaffolding(data)
        elif action == "setup_configuration":
            return self._setup_configuration(data)
        elif action == "setup_test_framework":
            return self._setup_test_framework(data)
        elif action == "execute_task":
            return self._execute_task(data)
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }
    
    def _read_specification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read and parse specification.
        
        Args:
            data: Dictionary containing specification information
            
        Returns:
            Parsed specification results
        """
        spec = {
            "id": data.get("spec_id", ""),
            "name": data.get("name", ""),
            "type": data.get("type", ""),
            "content": data.get("content", {}),
            "parsed_tasks": self._parse_tasks_from_spec(data.get("content", {})),
            "requirements": data.get("requirements", []),
            "constraints": data.get("constraints", [])
        }
        
        self.log_activity("specification_read", {
            "spec_id": spec["id"],
            "name": spec["name"],
            "tasks_found": len(spec["parsed_tasks"])
        })
        
        return {
            "status": "success",
            "specification": spec,
            "tasks_to_execute": spec["parsed_tasks"]
        }
    
    def _create_scaffolding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create project scaffolding.
        
        Args:
            data: Dictionary containing scaffolding information
            
        Returns:
            Scaffolding creation results
        """
        scaffolding = {
            "id": len(self.implementations) + 1,
            "project_name": data.get("project_name", ""),
            "project_type": data.get("project_type", ""),
            "structure": data.get("structure", {}),
            "directories": data.get("directories", []),
            "files": data.get("files", []),
            "templates_used": data.get("templates", []),
            "status": "created"
        }
        
        # Simulate directory creation
        created_items = []
        for directory in scaffolding["directories"]:
            created_items.append({
                "type": "directory",
                "path": directory,
                "created": True
            })
        
        for file_info in scaffolding["files"]:
            created_items.append({
                "type": "file",
                "path": file_info.get("path", ""),
                "template": file_info.get("template", ""),
                "created": True
            })
        
        scaffolding["created_items"] = created_items
        self.implementations.append(scaffolding)
        
        self.log_activity("scaffolding_created", {
            "project_name": scaffolding["project_name"],
            "items_created": len(created_items)
        })
        
        return {
            "status": "success",
            "scaffolding": scaffolding,
            "summary": {
                "directories": len(scaffolding["directories"]),
                "files": len(scaffolding["files"])
            }
        }
    
    def _setup_configuration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup project configuration.
        
        Args:
            data: Dictionary containing configuration information
            
        Returns:
            Configuration setup results
        """
        config_type = data.get("type", "")
        config = {
            "type": config_type,
            "name": data.get("name", ""),
            "settings": data.get("settings", {}),
            "environment": data.get("environment", "development"),
            "file_path": data.get("file_path", ""),
            "format": data.get("format", "json")
        }
        
        self.configurations[config_type] = config
        
        self.log_activity("configuration_setup", {
            "type": config_type,
            "name": config["name"]
        })
        
        return {
            "status": "success",
            "configuration": config,
            "total_configurations": len(self.configurations)
        }
    
    def _setup_test_framework(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup test framework.
        
        Args:
            data: Dictionary containing test framework information
            
        Returns:
            Test framework setup results
        """
        framework = {
            "name": data.get("framework_name", ""),
            "type": data.get("type", ""),  # unit, integration, e2e
            "configuration": data.get("configuration", {}),
            "test_directories": data.get("test_directories", []),
            "test_patterns": data.get("test_patterns", []),
            "dependencies": data.get("dependencies", []),
            "scripts": data.get("scripts", {}),
            "coverage_enabled": data.get("coverage_enabled", True),
            "coverage_threshold": data.get("coverage_threshold", 80)
        }
        
        self.log_activity("test_framework_setup", {
            "framework": framework["name"],
            "type": framework["type"]
        })
        
        return {
            "status": "success",
            "framework": framework,
            "next_steps": [
                "安裝測試依賴項",
                "創建測試目錄結構",
                "配置測試運行器",
                "撰寫初始測試案例"
            ]
        }
    
    def _execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a development task.
        
        Args:
            data: Dictionary containing task information
            
        Returns:
            Task execution results
        """
        task = {
            "id": len(self.tasks) + 1,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "type": data.get("type", ""),
            "priority": data.get("priority", "medium"),
            "status": "in_progress",
            "steps": data.get("steps", []),
            "completed_steps": [],
            "result": None
        }
        
        # Simulate task execution
        for step in task["steps"]:
            task["completed_steps"].append({
                "step": step,
                "status": "completed",
                "output": f"已完成: {step}"
            })
        
        task["status"] = "completed"
        task["result"] = {
            "success": True,
            "output": "任務執行成功",
            "artifacts": data.get("expected_artifacts", [])
        }
        
        self.tasks.append(task)
        
        self.log_activity("task_executed", {
            "task_id": task["id"],
            "name": task["name"],
            "status": task["status"]
        })
        
        return {
            "status": "success",
            "task": task,
            "total_tasks": len(self.tasks)
        }
    
    def _parse_tasks_from_spec(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse tasks from specification content."""
        tasks = []
        
        # Extract tasks from various specification formats
        if "tasks" in content:
            tasks = content["tasks"]
        elif "implementation_steps" in content:
            for step in content["implementation_steps"]:
                tasks.append({
                    "name": step.get("name", ""),
                    "description": step.get("description", ""),
                    "type": "implementation"
                })
        
        return tasks
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all executed tasks."""
        return self.tasks.copy()
    
    def get_all_implementations(self) -> List[Dict[str, Any]]:
        """Get all implementations (scaffolding, etc.)."""
        return self.implementations.copy()
    
    def get_all_configurations(self) -> Dict[str, Any]:
        """Get all configurations."""
        return self.configurations.copy()
    
    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """Get status of a specific task."""
        for task in self.tasks:
            if task["id"] == task_id:
                return {
                    "found": True,
                    "task": task
                }
        
        return {
            "found": False,
            "message": f"Task {task_id} not found"
        }
