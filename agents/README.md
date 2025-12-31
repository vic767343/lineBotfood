# Agents System Documentation

## 概述

本系統包含三個專門的 Agent，用於協助專案規劃和執行：

1. **Strategic Planner（戰略規劃者）**: 負責互動需求分析、里程碑計畫與依賴關係管理
2. **Steering Architect（架構設計師）**: 負責產品藍圖、技術選型與結構規範
3. **Task Executor（任務執行者）**: 負責讀取規格並實作專案（腳手架、設定、測試框架等）

## 安裝

系統已整合在現有專案中，無需額外安裝。

## 快速開始

### 基本使用

```python
from agents import AgentManager

# 初始化 Agent Manager
manager = AgentManager()

# 列出所有 Agents
agents = manager.list_agents()
print(agents)
```

## Agent 詳細說明

### 1. Strategic Planner（戰略規劃者）

負責專案的戰略規劃和需求分析。

#### 功能

- **需求分析 (analyze_requirements)**
  - 互動需求分析
  - 利害關係人識別
  - 複雜度評估
  - 風險識別

- **里程碑規劃 (create_milestones)**
  - 建立專案里程碑
  - 定義交付成果
  - 設定目標日期

- **依賴管理 (manage_dependencies)**
  - 管理任務依賴關係
  - 追蹤依賴鏈
  - 依賴分析

#### 使用範例

```python
from agents import StrategicPlanner

planner = StrategicPlanner()

# 分析需求
result = planner.process({
    "action": "analyze_requirements",
    "data": {
        "title": "用戶註冊功能",
        "description": "實現用戶註冊和驗證流程",
        "interactions": ["註冊表單", "郵件驗證", "登入"],
        "stakeholders": ["終端用戶", "產品經理", "開發團隊"],
        "priority": "high"
    }
})

# 建立里程碑
milestone_result = planner.process({
    "action": "create_milestones",
    "data": {
        "name": "MVP 發布",
        "description": "最小可行產品發布",
        "target_date": "2024-03-31",
        "deliverables": ["用戶註冊", "基本功能", "文檔"]
    }
})

# 管理依賴關係
dependency_result = planner.process({
    "action": "manage_dependencies",
    "data": {
        "item_id": "task-001",
        "depends_on": ["task-000", "setup-database"]
    }
})
```

### 2. Steering Architect（架構設計師）

負責技術架構和產品設計。

#### 功能

- **產品藍圖 (create_blueprint)**
  - 系統架構設計
  - 組件定義
  - 資料流設計
  - 擴展性規劃

- **技術選型 (select_technology)**
  - 評估技術方案
  - 比較替代方案
  - 分析優缺點
  - 社群支援評估

- **規範定義 (define_specification)**
  - 編碼規範
  - API 規範
  - 資料庫規範
  - 安全規範

#### 使用範例

```python
from agents import SteeringArchitect

architect = SteeringArchitect()

# 建立產品藍圖
blueprint_result = architect.process({
    "action": "create_blueprint",
    "data": {
        "name": "食物追蹤系統",
        "description": "LINE Bot 食物追蹤與健康管理系統",
        "architecture_style": "微服務架構",
        "components": ["Web API", "LINE Bot", "資料庫", "圖像處理服務"],
        "layers": ["呈現層", "業務邏輯層", "資料存取層"],
        "horizontal_scalability": True
    }
})

# 選擇技術
tech_result = architect.process({
    "action": "select_technology",
    "data": {
        "category": "backend",
        "name": "Flask",
        "version": "3.1.2",
        "rationale": "輕量級、易於擴展、Python 生態系統",
        "pros": ["快速開發", "靈活性高", "豐富的擴展"],
        "cons": ["需要手動配置", "較大型應用需要額外架構"],
        "learning_curve": "low",
        "maturity": "stable"
    }
})

# 定義規範
spec_result = architect.process({
    "action": "define_specification",
    "data": {
        "name": "API 命名規範",
        "type": "api",
        "description": "RESTful API 路由命名規範",
        "rules": [
            "使用複數名詞",
            "使用小寫字母",
            "使用連字號分隔單詞",
            "版本化 API 路徑"
        ],
        "enforcement": "required"
    }
})
```

### 3. Task Executor（任務執行者）

負責實際執行開發任務。

#### 功能

- **讀取規格 (read_specification)**
  - 解析規格文件
  - 提取任務列表
  - 識別需求和約束

- **建立腳手架 (create_scaffolding)**
  - 專案目錄結構
  - 基礎檔案建立
  - 模板應用

- **配置設定 (setup_configuration)**
  - 環境配置
  - 應用設定
  - 依賴管理

- **建立測試框架 (setup_test_framework)**
  - 測試框架安裝
  - 測試目錄結構
  - 覆蓋率配置

- **執行任務 (execute_task)**
  - 任務執行
  - 步驟追蹤
  - 結果記錄

#### 使用範例

```python
from agents import TaskExecutor

executor = TaskExecutor()

# 讀取規格
spec_result = executor.process({
    "action": "read_specification",
    "data": {
        "spec_id": "spec-001",
        "name": "用戶認證模組",
        "type": "feature",
        "content": {
            "tasks": [
                {"name": "建立認證端點", "description": "實現 /auth/login 和 /auth/register"},
                {"name": "JWT 令牌生成", "description": "實現 JWT 認證機制"}
            ]
        }
    }
})

# 建立腳手架
scaffold_result = executor.process({
    "action": "create_scaffolding",
    "data": {
        "project_name": "auth-service",
        "project_type": "microservice",
        "directories": ["src", "tests", "config", "docs"],
        "files": [
            {"path": "src/__init__.py", "template": "python_init"},
            {"path": "tests/__init__.py", "template": "python_init"},
            {"path": "README.md", "template": "readme"}
        ]
    }
})

# 設定配置
config_result = executor.process({
    "action": "setup_configuration",
    "data": {
        "type": "application",
        "name": "app_config",
        "settings": {
            "debug": False,
            "port": 5000,
            "database_url": "postgresql://localhost/mydb"
        },
        "environment": "production",
        "format": "json"
    }
})

# 建立測試框架
test_result = executor.process({
    "action": "setup_test_framework",
    "data": {
        "framework_name": "pytest",
        "type": "unit",
        "test_directories": ["tests/unit", "tests/integration"],
        "coverage_enabled": True,
        "coverage_threshold": 80
    }
})

# 執行任務
task_result = executor.process({
    "action": "execute_task",
    "data": {
        "name": "實現用戶註冊 API",
        "description": "建立用戶註冊端點並實現驗證邏輯",
        "type": "feature",
        "priority": "high",
        "steps": [
            "建立路由處理器",
            "實現資料驗證",
            "建立資料庫模型",
            "撰寫單元測試"
        ]
    }
})
```

## Agent Manager

Agent Manager 提供統一介面來協調所有 Agents。

### 使用範例

```python
from agents import AgentManager

manager = AgentManager()

# 獲取特定 Agent
planner = manager.get_agent("strategic-planner")
architect = manager.get_agent("steering-architect")
executor = manager.get_agent("task-executor")

# 列出所有 Agents
agents = manager.list_agents()

# 執行完整工作流程
workflow_result = manager.execute_workflow({
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

# 獲取系統狀態
status = manager.get_system_status()

# 重置所有 Agents
manager.reset_all_agents()
```

## 工作流程

系統支援預定義的工作流程，例如 "new_project" 工作流程：

1. Strategic Planner 分析需求
2. Strategic Planner 建立里程碑
3. Steering Architect 建立產品藍圖
4. Steering Architect 選擇技術
5. Task Executor 建立專案腳手架
6. Task Executor 設定測試框架

## 配置

系統配置位於 `agents/config.json`：

```json
{
  "agents": {
    "strategic-planner": {
      "enabled": true,
      "capabilities": [...]
    },
    "steering-architect": {
      "enabled": true,
      "capabilities": [...]
    },
    "task-executor": {
      "enabled": true,
      "capabilities": [...]
    }
  },
  "workflows": {
    "new_project": {
      "steps": [...]
    }
  }
}
```

## 日誌記錄

所有 Agents 都支援日誌記錄：

- 每個動作都會被記錄
- 可以追蹤 Agent 的活動歷史
- 使用 Python 的標準 logging 模組

## API 參考

### BaseAgent

所有 Agents 的基礎類別。

#### 方法

- `process(input_data)`: 處理輸入資料
- `log_activity(activity_type, details)`: 記錄活動
- `get_history()`: 獲取活動歷史
- `clear_history()`: 清除歷史
- `get_info()`: 獲取 Agent 資訊

### StrategicPlanner

#### 方法

- `get_all_requirements()`: 獲取所有需求
- `get_all_milestones()`: 獲取所有里程碑
- `get_all_dependencies()`: 獲取所有依賴關係

### SteeringArchitect

#### 方法

- `get_technology_stack()`: 獲取完整技術堆疊
- `get_all_blueprints()`: 獲取所有藍圖
- `get_all_specifications()`: 獲取所有規範
- `get_architecture_summary()`: 獲取架構摘要

### TaskExecutor

#### 方法

- `get_all_tasks()`: 獲取所有任務
- `get_all_implementations()`: 獲取所有實作
- `get_all_configurations()`: 獲取所有配置
- `get_task_status(task_id)`: 獲取任務狀態

## 最佳實踐

1. **按順序使用 Agents**: 先規劃（Strategic Planner）、再設計（Steering Architect）、最後執行（Task Executor）
2. **記錄所有決策**: 使用 Agents 記錄重要決策和理由
3. **定期檢查狀態**: 使用 `get_system_status()` 追蹤整體進度
4. **利用工作流程**: 使用預定義工作流程確保流程一致性
5. **保留歷史記錄**: 不要過早清除歷史，它們對於追蹤和審計很有用

## 故障排除

### Agent 無法初始化

確保所有依賴項已安裝：
```bash
pip install -r requirements.txt
```

### 工作流程執行失敗

檢查輸入資料格式是否正確，參考文檔中的範例。

### 日誌記錄問題

確保 logging 配置正確：
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 擴展

系統設計為可擴展的。要新增新的 Agent：

1. 繼承 `BaseAgent`
2. 實現 `process()` 方法
3. 在 `AgentManager` 中註冊新 Agent
4. 更新 `config.json`

## 授權

與主專案相同的授權。
