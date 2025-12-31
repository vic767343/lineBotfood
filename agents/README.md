# Agents 模組說明

本目錄包含三個專業的 AI 代理，用於協助專案規劃、架構設計和實作執行。

## 三個代理概述

### 1. Strategic Planner Agent (策略規劃代理)
**檔案**: `strategic_planner_agent.py`

**職責**：
- **互動需求分析** (Interaction Requirement Analysis)
  - 理解專案目標和使用者需求
  - 將需求轉化為清晰的使用者故事
  - 評估需求優先級和工作量
  
- **里程碑計畫** (Milestone Planning)
  - 將專案分解為可管理的階段
  - 定義每個里程碑的交付成果
  - 設定合理的時間表
  
- **依賴關係** (Dependency Relationships)
  - 識別需求之間的依賴關係
  - 標記阻塞性依賴和建議性依賴
  - 優化開發順序以減少阻塞

**主要方法**：
```python
# 創建完整的策略規劃
plan = await agent.create_strategic_plan(project_description)

# 分析互動需求
requirements = await agent.analyze_requirements(requirements_text)

# 規劃里程碑
milestones = await agent.plan_milestones(project_description)

# 識別依賴關係
dependencies = await agent.identify_dependencies(project_description)
```

### 2. Steering Architect Agent (架構指導代理)
**檔案**: `steering_architect_agent.py`

**職責**：
- **產品藍圖** (Product Roadmap)
  - 規劃產品功能的優先級和時間表
  - 定義每個季度的交付目標
  - 平衡短期需求和長期願景
  
- **技術選型** (Technology Selection)
  - 評估各種技術方案的優劣
  - 考慮團隊技能、專案需求、維護成本
  - 提供技術選擇的充分理由和替代方案
  
- **結構規範** (Structure Specification)
  - 設計清晰的專案結構
  - 定義命名規範和編碼標準
  - 規劃模組和元件的職責
  - 確保架構的可擴展性和可維護性

**主要方法**：
```python
# 創建完整的架構設計
design = await agent.create_architectural_design(project_description, constraints)

# 設計產品藍圖
roadmap = await agent.design_product_roadmap(project_description)

# 進行技術選型
technologies = await agent.select_technologies(project_description, constraints)

# 定義結構規範
structure = await agent.define_structure(project_description)
```

### 3. Task Executor Agent (任務執行代理)
**檔案**: `task_executor_agent.py`

**職責**：
- **讀取規格** (Read Specifications)
  - 理解技術規格和架構設計
  - 識別關鍵實作要點
  - 分解成可執行的任務
  
- **腳手架建立** (Scaffolding)
  - 設計清晰的專案結構
  - 創建必要的目錄和初始檔案
  - 提供框架初始化命令
  
- **設定配置** (Configuration)
  - 設計靈活的設定系統
  - 定義必要的設定參數
  - 提供範例設定檔
  
- **測試框架** (Test Framework)
  - 選擇適當的測試框架
  - 設定測試環境
  - 提供測試範例
  - 配置測試覆蓋率工具

**主要方法**：
```python
# 創建完整的實作計畫
plan = await agent.create_implementation_plan(specification, technology_stack)

# 生成腳手架規劃
scaffolding = await agent.generate_scaffolding(specification)

# 生成設定配置
configuration = await agent.generate_configuration(specification)

# 設定測試框架
test_framework = await agent.setup_test_framework(specification)

# 生成核心元件程式碼
components = await agent.generate_core_components(specification)
```

## 使用方式

### 單獨使用各個代理

**Strategic Planner 範例**：
```python
import asyncio
from agents.strategic_planner_agent import StrategicPlannerAgent

async def main():
    agent = StrategicPlannerAgent()
    plan = await agent.create_strategic_plan("""
        建立一個智慧飲食管理系統，需要以下功能：
        1. 使用者可以上傳食物照片
        2. 系統自動識別食物並計算卡路里
        3. 提供個人化的飲食建議
    """)
    print(f"專案名稱: {plan.project_name}")
    print(f"需求數量: {len(plan.requirements)}")
    print(f"里程碑數量: {len(plan.milestones)}")

asyncio.run(main())
```

**Steering Architect 範例**：
```python
import asyncio
from agents.steering_architect_agent import SteeringArchitectAgent

async def main():
    agent = SteeringArchitectAgent()
    design = await agent.create_architectural_design(
        project_description="智慧飲食管理系統",
        constraints="必須使用 Python 和 Flask"
    )
    print(f"技術選型數量: {len(design.technology_stack)}")
    print(f"架構元件數量: {len(design.architecture_components)}")

asyncio.run(main())
```

**Task Executor 範例**：
```python
import asyncio
from agents.task_executor_agent import TaskExecutorAgent

async def main():
    agent = TaskExecutorAgent()
    plan = await agent.create_implementation_plan(
        specification="智慧飲食管理 LINE Bot",
        technology_stack="Python Flask + SQL Server + Google Gemini"
    )
    print(f"腳手架框架: {plan.scaffolding.framework}")
    print(f"核心元件數量: {len(plan.core_components)}")

asyncio.run(main())
```

### 三個代理協作

執行完整的協作示範：
```bash
python agents_demo.py
```

這將展示三個代理如何協作完成一個完整的專案規劃流程：
1. Strategic Planner 進行需求分析和里程碑規劃
2. Steering Architect 根據需求進行架構設計和技術選型
3. Task Executor 根據架構設計生成實作計畫和程式碼骨架

## 技術架構

### 依賴套件
- `pydantic`: 資料驗證和設定管理
- `pydantic-ai`: AI 代理框架
- `python-dotenv`: 環境變數管理
- `google-generativeai`: Google Gemini AI 模型

### 資料模型
每個代理都定義了清晰的資料模型（使用 Pydantic BaseModel），確保：
- 類型安全
- 資料驗證
- 結構化輸出
- 易於序列化和反序列化

### AI 模型
預設使用 `google-gla:gemini-2.5-flash` 模型，可以透過初始化參數自訂：
```python
agent = StrategicPlannerAgent(model_name='google-gla:gemini-2.0-pro')
```

## 環境設定

1. 安裝依賴：
```bash
pip install pydantic pydantic-ai python-dotenv google-generativeai
```

2. 設定環境變數（建立 `.env` 檔案）：
```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

3. 執行範例：
```bash
# 執行個別代理範例
python agents/strategic_planner_agent.py
python agents/steering_architect_agent.py
python agents/task_executor_agent.py

# 執行完整協作示範
python agents_demo.py
```

## 輸出格式

所有代理都使用結構化的 Pydantic 模型輸出，可以輕鬆轉換為 JSON：

```python
plan = await agent.create_strategic_plan(project_description)

# 轉換為字典
plan_dict = plan.model_dump()

# 轉換為 JSON
plan_json = plan.model_dump_json(indent=2)
```

## 進階使用

### 自訂 System Prompt
```python
agent = StrategicPlannerAgent()
agent.agent.system_prompt = "你是一位專精於醫療系統的策略規劃師..."
```

### 鏈式呼叫
```python
# 策略規劃 -> 架構設計 -> 實作計畫
planner = StrategicPlannerAgent()
architect = SteeringArchitectAgent()
executor = TaskExecutorAgent()

strategic_plan = await planner.create_strategic_plan(requirements)
architectural_design = await architect.create_architectural_design(
    requirements, 
    tech_constraints
)
implementation_plan = await executor.create_implementation_plan(
    requirements,
    tech_stack_from_architect
)
```

## 注意事項

1. **API 費用**：這些代理使用 Google Gemini API，可能會產生費用，請留意使用量
2. **回應時間**：AI 代理的回應時間取決於網路狀況和模型負載，通常需要 5-30 秒
3. **結果品質**：AI 生成的內容需要人工審核和調整，作為專案規劃的參考而非最終答案
4. **版本相容性**：請確保使用 pydantic-ai 1.34.0 或更新版本

## 授權

本模組遵循專案的整體授權條款。
