"""
Steering Architect Agent

負責：
1. 產品藍圖 (Product Roadmap)
2. 技術選型 (Technology Selection)
3. 結構規範 (Structure Specification)
"""

from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List, Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class ProductFeature(BaseModel):
    """產品功能模型"""
    feature_id: str = Field(description="功能ID")
    name: str = Field(description="功能名稱")
    description: str = Field(description="功能描述")
    quarter: str = Field(description="計劃季度，例如 Q1 2024")
    status: str = Field(description="狀態：planned, in_progress, completed")


class TechnologyStack(BaseModel):
    """技術堆疊模型"""
    category: str = Field(description="技術類別：backend, frontend, database, ai_ml, infrastructure等")
    technology: str = Field(description="技術名稱")
    version: str = Field(description="建議版本")
    reason: str = Field(description="選擇理由")
    alternatives: List[str] = Field(description="替代方案清單")


class ArchitectureComponent(BaseModel):
    """架構元件模型"""
    component_name: str = Field(description="元件名稱")
    responsibility: str = Field(description="職責描述")
    interfaces: List[str] = Field(description="對外介面清單")
    dependencies: List[str] = Field(description="依賴的其他元件")
    design_patterns: List[str] = Field(description="使用的設計模式")


class StructureSpecification(BaseModel):
    """結構規範模型"""
    directory_structure: Dict[str, str] = Field(description="目錄結構，key是路徑，value是說明")
    naming_conventions: Dict[str, str] = Field(description="命名規範")
    code_standards: List[str] = Field(description="程式碼標準清單")
    documentation_requirements: List[str] = Field(description="文件需求")


class ArchitecturalDesign(BaseModel):
    """架構設計完整輸出"""
    project_name: str = Field(description="專案名稱")
    product_roadmap: List[ProductFeature] = Field(description="產品藍圖")
    technology_stack: List[TechnologyStack] = Field(description="技術選型")
    architecture_components: List[ArchitectureComponent] = Field(description="架構元件")
    structure_specification: StructureSpecification = Field(description="結構規範")
    architecture_diagram_description: str = Field(description="架構圖描述")
    summary: str = Field(description="架構設計總結")


class SteeringArchitectAgent:
    """架構指導代理
    
    負責產品藍圖規劃、技術選型、系統架構設計
    """
    
    def __init__(self, model_name: str = 'google-gla:gemini-2.5-flash'):
        """初始化架構指導代理
        
        Args:
            model_name: 使用的AI模型名稱
        """
        self.model_name = model_name
        self.agent = Agent(
            model_name,
            output_type=ArchitecturalDesign,
            system_prompt="""
你是一位資深的軟體架構師和技術顧問。你的職責是：

1. **產品藍圖**：
   - 規劃產品功能的優先級和時間表
   - 定義每個季度的交付目標
   - 平衡短期需求和長期願景
   - 確保產品演進的連貫性

2. **技術選型**：
   - 評估各種技術方案的優劣
   - 考慮團隊技能、專案需求、維護成本
   - 提供技術選擇的充分理由
   - 列出替代方案以應對變化
   - 考慮技術的成熟度和社群支援

3. **結構規範**：
   - 設計清晰的專案結構
   - 定義命名規範和編碼標準
   - 規劃模組和元件的職責
   - 確保架構的可擴展性和可維護性
   - 應用適當的設計模式

請提供專業、實用且易於理解的架構設計。
"""
        )
    
    async def create_architectural_design(self, project_description: str, constraints: Optional[str] = None) -> ArchitecturalDesign:
        """創建完整的架構設計
        
        Args:
            project_description: 專案描述
            constraints: 技術約束或限制（可選）
            
        Returns:
            ArchitecturalDesign: 完整的架構設計
        """
        prompt = f"""
請為以下專案創建完整的架構設計：

專案描述：
{project_description}
"""
        
        if constraints:
            prompt += f"""

技術約束：
{constraints}
"""
        
        prompt += """

請提供：
1. 產品藍圖（至少3個季度的功能規劃）
2. 詳細的技術選型（包括後端、前端、資料庫、AI/ML等）
3. 系統架構元件設計
4. 完整的結構規範（目錄結構、命名規範、程式碼標準）
5. 架構圖的文字描述
6. 整體架構設計總結

請確保輸出符合 ArchitecturalDesign 的資料結構。
"""
        
        result = await self.agent.run(prompt)
        return result.data
    
    async def design_product_roadmap(self, project_description: str) -> List[ProductFeature]:
        """設計產品藍圖
        
        Args:
            project_description: 專案描述
            
        Returns:
            List[ProductFeature]: 產品功能清單
        """
        design = await self.create_architectural_design(project_description)
        return design.product_roadmap
    
    async def select_technologies(self, project_description: str, constraints: Optional[str] = None) -> List[TechnologyStack]:
        """進行技術選型
        
        Args:
            project_description: 專案描述
            constraints: 技術約束
            
        Returns:
            List[TechnologyStack]: 技術堆疊清單
        """
        design = await self.create_architectural_design(project_description, constraints)
        return design.technology_stack
    
    async def define_structure(self, project_description: str) -> StructureSpecification:
        """定義專案結構規範
        
        Args:
            project_description: 專案描述
            
        Returns:
            StructureSpecification: 結構規範
        """
        design = await self.create_architectural_design(project_description)
        return design.structure_specification


# 範例使用
async def example_usage():
    """範例：使用架構指導代理"""
    agent = SteeringArchitectAgent()
    
    project_desc = """
    建立一個智慧飲食管理系統，需要：
    - LINE Bot 整合
    - AI 圖像識別功能
    - 使用者數據管理
    - 營養計算和建議
    - 歷史記錄查詢
    目標使用者：注重健康的一般消費者
    預期規模：初期 1000-10000 用戶
    """
    
    constraints = """
    - 必須使用 Python 作為主要後端語言
    - 需要整合 LINE Messaging API
    - 資料庫偏好使用關聯式資料庫
    - AI 模型使用 Google Gemini
    """
    
    design = await agent.create_architectural_design(project_desc, constraints)
    
    print("=" * 50)
    print(f"專案名稱: {design.project_name}")
    
    print("\n產品藍圖:")
    for feature in design.product_roadmap:
        print(f"  - [{feature.quarter}] {feature.name} ({feature.status})")
        print(f"    {feature.description}")
    
    print("\n技術選型:")
    for tech in design.technology_stack:
        print(f"  - {tech.category}: {tech.technology} (v{tech.version})")
        print(f"    理由: {tech.reason}")
        if tech.alternatives:
            print(f"    替代方案: {', '.join(tech.alternatives)}")
    
    print("\n架構元件:")
    for component in design.architecture_components:
        print(f"  - {component.component_name}")
        print(f"    職責: {component.responsibility}")
        print(f"    設計模式: {', '.join(component.design_patterns)}")
    
    print("\n結構規範:")
    print("  目錄結構:")
    for path, desc in design.structure_specification.directory_structure.items():
        print(f"    {path}: {desc}")
    
    print(f"\n架構圖描述:\n{design.architecture_diagram_description}")
    print(f"\n總結:\n{design.summary}")
    print("=" * 50)


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
