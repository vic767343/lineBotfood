"""
Task Executor Agent

負責：
1. 讀取規格 (Read Specifications)
2. 實作專案 (Implement Project)
   - 腳手架 (Scaffolding)
   - 設定 (Configuration)
   - 測試框架 (Test Framework)
"""

from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List, Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class ScaffoldingPlan(BaseModel):
    """腳手架規劃模型"""
    framework: str = Field(description="框架名稱")
    directory_structure: List[str] = Field(description="需要創建的目錄清單")
    initial_files: Dict[str, str] = Field(description="初始檔案清單，key是檔案路徑，value是檔案內容描述")
    commands: List[str] = Field(description="需要執行的命令清單")


class ConfigurationSetup(BaseModel):
    """設定配置模型"""
    config_file: str = Field(description="設定檔名稱")
    config_format: str = Field(description="設定格式：json, yaml, ini, py等")
    required_settings: Dict[str, str] = Field(description="必要的設定項目和說明")
    environment_variables: List[str] = Field(description="需要的環境變數清單")
    sample_config: str = Field(description="範例設定檔內容")


class TestFrameworkSetup(BaseModel):
    """測試框架設定模型"""
    framework_name: str = Field(description="測試框架名稱")
    test_directory: str = Field(description="測試目錄路徑")
    test_file_naming: str = Field(description="測試檔案命名規範")
    setup_commands: List[str] = Field(description="設定測試框架的命令")
    sample_test: str = Field(description="範例測試程式碼")
    coverage_config: Optional[str] = Field(description="測試覆蓋率設定")


class CodeSnippet(BaseModel):
    """程式碼片段模型"""
    file_path: str = Field(description="檔案路徑")
    description: str = Field(description="程式碼說明")
    code: str = Field(description="程式碼內容")
    dependencies: List[str] = Field(description="需要的依賴套件")


class ImplementationPlan(BaseModel):
    """實作計畫完整輸出"""
    project_name: str = Field(description="專案名稱")
    scaffolding: ScaffoldingPlan = Field(description="腳手架規劃")
    configuration: ConfigurationSetup = Field(description="設定配置")
    test_framework: TestFrameworkSetup = Field(description="測試框架設定")
    core_components: List[CodeSnippet] = Field(description="核心元件程式碼")
    integration_steps: List[str] = Field(description="整合步驟")
    deployment_checklist: List[str] = Field(description="部署檢查清單")
    summary: str = Field(description="實作計畫總結")


class TaskExecutorAgent:
    """任務執行代理
    
    負責讀取規格並生成實作計畫，包括腳手架、設定、測試框架等
    """
    
    def __init__(self, model_name: str = 'google-gla:gemini-2.5-flash'):
        """初始化任務執行代理
        
        Args:
            model_name: 使用的AI模型名稱
        """
        self.model_name = model_name
        self.agent = Agent(
            model_name,
            output_type=ImplementationPlan,
            system_prompt="""
你是一位經驗豐富的軟體開發工程師和 DevOps 專家。你的職責是：

1. **讀取規格**：
   - 理解技術規格和架構設計
   - 識別關鍵實作要點
   - 分解成可執行的任務

2. **腳手架建立**：
   - 設計清晰的專案結構
   - 創建必要的目錄和初始檔案
   - 提供框架初始化命令
   - 確保專案結構符合最佳實踐

3. **設定配置**：
   - 設計靈活的設定系統
   - 定義必要的設定參數
   - 提供範例設定檔
   - 說明環境變數的使用

4. **測試框架**：
   - 選擇適當的測試框架
   - 設定測試環境
   - 提供測試範例
   - 配置測試覆蓋率工具

5. **核心實作**：
   - 提供核心元件的程式碼骨架
   - 說明元件之間的整合方式
   - 確保程式碼品質和可維護性

請提供詳細、可執行的實作計畫。
"""
        )
    
    async def create_implementation_plan(
        self, 
        specification: str,
        technology_stack: Optional[str] = None
    ) -> ImplementationPlan:
        """創建實作計畫
        
        Args:
            specification: 專案規格說明
            technology_stack: 技術堆疊資訊（可選）
            
        Returns:
            ImplementationPlan: 完整的實作計畫
        """
        prompt = f"""
請根據以下規格創建詳細的實作計畫：

專案規格：
{specification}
"""
        
        if technology_stack:
            prompt += f"""

技術堆疊：
{technology_stack}
"""
        
        prompt += """

請提供：
1. 完整的腳手架規劃（目錄結構、初始檔案、執行命令）
2. 詳細的設定配置（設定檔、環境變數、範例設定）
3. 測試框架設定（測試工具、目錄結構、範例測試）
4. 核心元件的程式碼骨架（至少3個核心元件）
5. 整合步驟說明
6. 部署檢查清單
7. 實作計畫總結

請確保所有程式碼範例都是可執行的，並包含必要的註解。
請確保輸出符合 ImplementationPlan 的資料結構。
"""
        
        result = await self.agent.run(prompt)
        return result.data
    
    async def generate_scaffolding(self, specification: str) -> ScaffoldingPlan:
        """生成腳手架規劃
        
        Args:
            specification: 專案規格
            
        Returns:
            ScaffoldingPlan: 腳手架規劃
        """
        plan = await self.create_implementation_plan(specification)
        return plan.scaffolding
    
    async def generate_configuration(self, specification: str) -> ConfigurationSetup:
        """生成設定配置
        
        Args:
            specification: 專案規格
            
        Returns:
            ConfigurationSetup: 設定配置
        """
        plan = await self.create_implementation_plan(specification)
        return plan.configuration
    
    async def setup_test_framework(self, specification: str) -> TestFrameworkSetup:
        """設定測試框架
        
        Args:
            specification: 專案規格
            
        Returns:
            TestFrameworkSetup: 測試框架設定
        """
        plan = await self.create_implementation_plan(specification)
        return plan.test_framework
    
    async def generate_core_components(self, specification: str) -> List[CodeSnippet]:
        """生成核心元件程式碼
        
        Args:
            specification: 專案規格
            
        Returns:
            List[CodeSnippet]: 核心元件程式碼清單
        """
        plan = await self.create_implementation_plan(specification)
        return plan.core_components


# 範例使用
async def example_usage():
    """範例：使用任務執行代理"""
    agent = TaskExecutorAgent()
    
    specification = """
    專案：智慧飲食管理 LINE Bot
    
    需求：
    1. 接收 LINE Webhook 事件
    2. 處理文字訊息和圖片訊息
    3. 使用 AI 分析食物圖片
    4. 計算卡路里並記錄到資料庫
    5. 提供查詢和統計功能
    
    架構：
    - 後端：Python Flask
    - 資料庫：SQL Server
    - AI：Google Gemini
    - 訊息平台：LINE Messaging API
    """
    
    tech_stack = """
    - Python 3.13+
    - Flask 3.1+
    - pydantic-ai 1.34+
    - pyodbc 5.3+
    - pytest (測試框架)
    """
    
    plan = await agent.create_implementation_plan(specification, tech_stack)
    
    print("=" * 50)
    print(f"專案名稱: {plan.project_name}")
    
    print("\n腳手架規劃:")
    print(f"  框架: {plan.scaffolding.framework}")
    print("  目錄結構:")
    for directory in plan.scaffolding.directory_structure:
        print(f"    - {directory}")
    print("  初始化命令:")
    for cmd in plan.scaffolding.commands:
        print(f"    $ {cmd}")
    
    print("\n設定配置:")
    print(f"  設定檔: {plan.configuration.config_file}")
    print(f"  格式: {plan.configuration.config_format}")
    print("  必要設定:")
    for key, desc in plan.configuration.required_settings.items():
        print(f"    - {key}: {desc}")
    print("  環境變數:")
    for env_var in plan.configuration.environment_variables:
        print(f"    - {env_var}")
    
    print("\n測試框架:")
    print(f"  框架: {plan.test_framework.framework_name}")
    print(f"  測試目錄: {plan.test_framework.test_directory}")
    print(f"  檔案命名: {plan.test_framework.test_file_naming}")
    print("  設定命令:")
    for cmd in plan.test_framework.setup_commands:
        print(f"    $ {cmd}")
    
    print("\n核心元件:")
    for component in plan.core_components:
        print(f"  - {component.file_path}")
        print(f"    說明: {component.description}")
        if component.dependencies:
            print(f"    依賴: {', '.join(component.dependencies)}")
    
    print("\n整合步驟:")
    for i, step in enumerate(plan.integration_steps, 1):
        print(f"  {i}. {step}")
    
    print("\n部署檢查清單:")
    for i, item in enumerate(plan.deployment_checklist, 1):
        print(f"  {i}. {item}")
    
    print(f"\n總結:\n{plan.summary}")
    print("=" * 50)


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
