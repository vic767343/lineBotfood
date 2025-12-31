"""
Example script demonstrating the usage of the three agents.

This script shows how to use:
- Strategic Planner
- Steering Architect
- Task Executor
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import AgentManager, StrategicPlanner, SteeringArchitect, TaskExecutor
import json


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def example_strategic_planner():
    """Demonstrate Strategic Planner usage."""
    print_section("Strategic Planner 範例")
    
    planner = StrategicPlanner()
    
    # 1. Analyze requirements
    print("1. 分析需求...")
    req_result = planner.process({
        "action": "analyze_requirements",
        "data": {
            "title": "LINE Bot 食物辨識功能",
            "description": "用戶上傳食物照片，系統自動辨識並記錄卡路里",
            "interactions": ["上傳照片", "查看分析結果", "查詢歷史記錄"],
            "stakeholders": ["終端用戶", "營養師", "開發團隊"],
            "priority": "high"
        }
    })
    print(json.dumps(req_result, indent=2, ensure_ascii=False))
    
    # 2. Create milestones
    print("\n2. 建立里程碑...")
    milestone_result = planner.process({
        "action": "create_milestones",
        "data": {
            "name": "Beta 測試版",
            "description": "完成核心功能並開始 Beta 測試",
            "target_date": "2024-06-30",
            "deliverables": ["圖像辨識 API", "卡路里計算", "歷史記錄功能"]
        }
    })
    print(json.dumps(milestone_result, indent=2, ensure_ascii=False))
    
    # 3. Manage dependencies
    print("\n3. 管理依賴關係...")
    dep_result = planner.process({
        "action": "manage_dependencies",
        "data": {
            "item_id": "image-recognition",
            "depends_on": ["database-setup", "api-framework"]
        }
    })
    print(json.dumps(dep_result, indent=2, ensure_ascii=False))


def example_steering_architect():
    """Demonstrate Steering Architect usage."""
    print_section("Steering Architect 範例")
    
    architect = SteeringArchitect()
    
    # 1. Create blueprint
    print("1. 建立產品藍圖...")
    blueprint_result = architect.process({
        "action": "create_blueprint",
        "data": {
            "name": "LINE Bot 食物追蹤系統",
            "description": "完整的食物追蹤和健康管理系統",
            "version": "1.0.0",
            "architecture_style": "微服務架構",
            "components": [
                "LINE Bot 介面",
                "圖像辨識服務",
                "資料存儲服務",
                "分析報告服務"
            ],
            "layers": ["呈現層", "應用層", "領域層", "基礎設施層"]
        }
    })
    print(json.dumps(blueprint_result, indent=2, ensure_ascii=False))
    
    # 2. Select technologies
    print("\n2. 選擇技術堆疊...")
    tech_selections = [
        {
            "category": "backend",
            "name": "Flask",
            "version": "3.1.2",
            "rationale": "輕量級、靈活、Python 生態系統豐富",
            "pros": ["快速開發", "易於擴展", "良好的文檔"],
            "cons": ["需要手動配置較多"],
            "learning_curve": "low",
            "maturity": "stable"
        },
        {
            "category": "image-processing",
            "name": "OpenCV",
            "version": "4.x",
            "rationale": "強大的圖像處理能力",
            "pros": ["功能完整", "性能優秀", "社群活躍"],
            "cons": ["學習曲線較陡"],
            "learning_curve": "medium",
            "maturity": "stable"
        },
        {
            "category": "database",
            "name": "PostgreSQL",
            "version": "14",
            "rationale": "可靠的關聯式資料庫",
            "pros": ["ACID 支援", "擴展性好", "免費開源"],
            "cons": ["需要資料庫管理知識"],
            "learning_curve": "medium",
            "maturity": "stable"
        }
    ]
    
    for tech in tech_selections:
        tech_result = architect.process({
            "action": "select_technology",
            "data": tech
        })
        print(f"\n選擇技術: {tech['name']}")
        print(json.dumps(tech_result, indent=2, ensure_ascii=False))
    
    # 3. Define specifications
    print("\n3. 定義結構規範...")
    spec_result = architect.process({
        "action": "define_specification",
        "data": {
            "name": "API 端點規範",
            "type": "api",
            "description": "RESTful API 設計規範",
            "rules": [
                "使用 HTTP 動詞表示操作 (GET, POST, PUT, DELETE)",
                "使用複數名詞作為資源名稱",
                "使用 JSON 作為資料格式",
                "使用適當的 HTTP 狀態碼",
                "版本化 API (例如: /api/v1/)"
            ],
            "enforcement": "required"
        }
    })
    print(json.dumps(spec_result, indent=2, ensure_ascii=False))


def example_task_executor():
    """Demonstrate Task Executor usage."""
    print_section("Task Executor 範例")
    
    executor = TaskExecutor()
    
    # 1. Read specification
    print("1. 讀取規格...")
    spec_result = executor.process({
        "action": "read_specification",
        "data": {
            "spec_id": "spec-food-recognition",
            "name": "食物辨識模組",
            "type": "feature",
            "content": {
                "tasks": [
                    {
                        "name": "建立圖像上傳端點",
                        "description": "實現 /api/v1/upload 端點接收圖像"
                    },
                    {
                        "name": "整合圖像辨識 AI",
                        "description": "調用 AI 模型進行食物辨識"
                    },
                    {
                        "name": "計算卡路里",
                        "description": "根據辨識結果計算營養資訊"
                    }
                ]
            }
        }
    })
    print(json.dumps(spec_result, indent=2, ensure_ascii=False))
    
    # 2. Create scaffolding
    print("\n2. 建立專案腳手架...")
    scaffold_result = executor.process({
        "action": "create_scaffolding",
        "data": {
            "project_name": "food-recognition-service",
            "project_type": "microservice",
            "directories": [
                "src/api",
                "src/models",
                "src/utils",
                "tests/unit",
                "tests/integration",
                "config",
                "docs"
            ],
            "files": [
                {"path": "src/__init__.py", "template": "python_init"},
                {"path": "src/api/__init__.py", "template": "python_init"},
                {"path": "tests/__init__.py", "template": "python_init"},
                {"path": "README.md", "template": "readme"},
                {"path": "requirements.txt", "template": "requirements"}
            ]
        }
    })
    print(json.dumps(scaffold_result, indent=2, ensure_ascii=False))
    
    # 3. Setup configuration
    print("\n3. 設定專案配置...")
    config_result = executor.process({
        "action": "setup_configuration",
        "data": {
            "type": "application",
            "name": "app_config",
            "settings": {
                "debug": False,
                "port": 5000,
                "host": "0.0.0.0",
                "database_url": "postgresql://localhost/foodbot",
                "image_upload_path": "/uploads",
                "max_file_size": 5242880
            },
            "environment": "development",
            "format": "json"
        }
    })
    print(json.dumps(config_result, indent=2, ensure_ascii=False))
    
    # 4. Setup test framework
    print("\n4. 建立測試框架...")
    test_result = executor.process({
        "action": "setup_test_framework",
        "data": {
            "framework_name": "pytest",
            "type": "unit",
            "test_directories": ["tests/unit", "tests/integration"],
            "test_patterns": ["test_*.py", "*_test.py"],
            "dependencies": ["pytest", "pytest-cov", "pytest-mock"],
            "coverage_enabled": True,
            "coverage_threshold": 80
        }
    })
    print(json.dumps(test_result, indent=2, ensure_ascii=False))
    
    # 5. Execute task
    print("\n5. 執行開發任務...")
    task_result = executor.process({
        "action": "execute_task",
        "data": {
            "name": "實現圖像上傳 API",
            "description": "建立圖像上傳端點並驗證檔案",
            "type": "feature",
            "priority": "high",
            "steps": [
                "建立 Flask 路由",
                "實現檔案驗證邏輯",
                "儲存上傳的圖像",
                "返回上傳結果",
                "撰寫單元測試"
            ]
        }
    })
    print(json.dumps(task_result, indent=2, ensure_ascii=False))


def example_agent_manager():
    """Demonstrate Agent Manager usage."""
    print_section("Agent Manager 範例")
    
    manager = AgentManager()
    
    # 1. List all agents
    print("1. 列出所有 Agents...")
    agents = manager.list_agents()
    print(json.dumps(agents, indent=2, ensure_ascii=False))
    
    # 2. Execute workflow
    print("\n2. 執行完整工作流程 (新專案)...")
    workflow_result = manager.execute_workflow({
        "type": "new_project",
        "requirements": {
            "title": "健康飲食追蹤功能",
            "description": "提供完整的飲食追蹤和分析功能",
            "interactions": ["記錄飲食", "查看分析", "設定目標"],
            "stakeholders": ["用戶", "營養師", "開發團隊"],
            "priority": "high"
        },
        "milestones": {
            "name": "MVP 發布",
            "description": "最小可行產品",
            "target_date": "2024-05-31",
            "deliverables": ["核心功能", "基本UI", "文檔"]
        },
        "blueprint": {
            "name": "飲食追蹤系統架構",
            "description": "完整的系統架構設計",
            "architecture_style": "分層架構",
            "components": ["API層", "業務邏輯層", "資料層"]
        },
        "technologies": [
            {
                "category": "backend",
                "name": "Flask",
                "version": "3.1.2",
                "rationale": "符合現有技術堆疊"
            }
        ],
        "scaffolding": {
            "project_name": "diet-tracker",
            "project_type": "module",
            "directories": ["src", "tests", "docs"],
            "files": [
                {"path": "src/__init__.py", "template": "python_init"}
            ]
        },
        "test_framework": {
            "framework_name": "pytest",
            "type": "unit",
            "coverage_enabled": True
        }
    })
    print(json.dumps(workflow_result, indent=2, ensure_ascii=False))
    
    # 3. Get system status
    print("\n3. 獲取系統狀態...")
    status = manager.get_system_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("  三個 Agents 系統使用範例")
    print("=" * 60)
    
    try:
        # Run individual agent examples
        example_strategic_planner()
        example_steering_architect()
        example_task_executor()
        
        # Run agent manager example
        example_agent_manager()
        
        print_section("所有範例執行完成")
        print("✓ Strategic Planner: 需求分析、里程碑規劃、依賴管理")
        print("✓ Steering Architect: 產品藍圖、技術選型、結構規範")
        print("✓ Task Executor: 規格讀取、專案實作、任務執行")
        print("✓ Agent Manager: 統一管理、工作流程協調")
        
    except Exception as e:
        print(f"\n錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
