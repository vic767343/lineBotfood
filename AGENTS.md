# Agents 系統快速指南

## 概述

本專案包含三個專門的 AI 代理（Agents）來協助軟體專案的規劃與執行：

### 🎯 Strategic Planner（戰略規劃者）
- **職責**: 互動需求分析、里程碑計畫與依賴關係管理
- **適用於**: 專案啟動、需求分析、計畫制定

### 🏗️ Steering Architect（架構設計師）
- **職責**: 產品藍圖、技術選型與結構規範
- **適用於**: 系統設計、技術決策、規範制定

### ⚙️ Task Executor（任務執行者）
- **職責**: 讀取規格並實作專案（腳手架、設定、測試框架）
- **適用於**: 專案實作、配置管理、任務執行

## 快速開始

### 基本使用

```python
from agents import AgentManager

# 初始化管理器
manager = AgentManager()

# 列出所有可用的 Agents
agents = manager.list_agents()
print(agents)
```

### 使用 Strategic Planner

```python
from agents import StrategicPlanner

planner = StrategicPlanner()

# 分析需求
result = planner.process({
    "action": "analyze_requirements",
    "data": {
        "title": "用戶註冊功能",
        "description": "實現用戶註冊和驗證流程",
        "interactions": ["註冊表單", "郵件驗證"],
        "stakeholders": ["用戶", "開發團隊"],
        "priority": "high"
    }
})
```

### 使用 Steering Architect

```python
from agents import SteeringArchitect

architect = SteeringArchitect()

# 建立產品藍圖
result = architect.process({
    "action": "create_blueprint",
    "data": {
        "name": "系統架構",
        "description": "完整的系統架構設計",
        "architecture_style": "微服務架構",
        "components": ["API層", "服務層", "資料層"]
    }
})
```

### 使用 Task Executor

```python
from agents import TaskExecutor

executor = TaskExecutor()

# 建立專案腳手架
result = executor.process({
    "action": "create_scaffolding",
    "data": {
        "project_name": "new-feature",
        "project_type": "module",
        "directories": ["src", "tests", "docs"],
        "files": [
            {"path": "src/__init__.py", "template": "python_init"}
        ]
    }
})
```

## 執行完整工作流程

```python
from agents import AgentManager

manager = AgentManager()

# 執行新專案工作流程
result = manager.execute_workflow({
    "type": "new_project",
    "requirements": {
        "title": "新功能開發",
        "description": "實現新的核心功能",
        "interactions": ["API", "資料庫"],
        "stakeholders": ["產品團隊", "開發團隊"]
    },
    "milestones": {
        "name": "Alpha 版本",
        "target_date": "2024-04-15"
    },
    "blueprint": {
        "name": "系統架構",
        "architecture_style": "分層架構"
    },
    "technologies": [
        {
            "category": "backend",
            "name": "Flask",
            "version": "3.1.2"
        }
    ],
    "scaffolding": {
        "project_name": "new-feature",
        "project_type": "module",
        "directories": ["src", "tests"]
    },
    "test_framework": {
        "framework_name": "pytest",
        "type": "unit"
    }
})
```

## 範例程式

專案包含兩個完整的範例程式：

1. **`agents/example.py`**: 展示每個 Agent 的基本功能
   ```bash
   python agents/example.py
   ```

2. **`agents/integration_example.py`**: 展示如何將 Agents 整合到 LINE Bot 專案
   ```bash
   python agents/integration_example.py
   ```

## 目錄結構

```
agents/
├── README.md                    # 完整文檔
├── __init__.py                  # 套件初始化
├── base_agent.py               # Agent 基礎類別
├── strategic_planner.py        # 戰略規劃者
├── steering_architect.py       # 架構設計師
├── task_executor.py            # 任務執行者
├── agent_manager.py            # Agent 管理器
├── config.json                 # 配置檔案
├── example.py                  # 基本範例
└── integration_example.py      # 整合範例
```

## 主要功能

### Strategic Planner 功能
- ✅ 需求分析 (`analyze_requirements`)
- ✅ 里程碑規劃 (`create_milestones`)
- ✅ 依賴關係管理 (`manage_dependencies`)

### Steering Architect 功能
- ✅ 產品藍圖設計 (`create_blueprint`)
- ✅ 技術選型 (`select_technology`)
- ✅ 規範定義 (`define_specification`)

### Task Executor 功能
- ✅ 規格解析 (`read_specification`)
- ✅ 建立腳手架 (`create_scaffolding`)
- ✅ 配置設定 (`setup_configuration`)
- ✅ 測試框架設定 (`setup_test_framework`)
- ✅ 任務執行 (`execute_task`)

## 詳細文檔

完整的 API 文檔和使用指南請參閱 [`agents/README.md`](agents/README.md)

## 最佳實踐

1. **按順序使用**: 先規劃 → 再設計 → 最後執行
2. **記錄決策**: 使用 Agents 追蹤重要的專案決策
3. **利用工作流程**: 使用預定義的工作流程確保一致性
4. **定期檢查**: 使用 `get_system_status()` 追蹤進度

## 設定

系統配置位於 `agents/config.json`，可以根據需求調整：

```json
{
  "agents": {
    "strategic-planner": {
      "enabled": true,
      "capabilities": [...]
    },
    ...
  }
}
```

## 故障排除

如果遇到導入問題：

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from agents import AgentManager
```

## 授權

與主專案相同的授權。
