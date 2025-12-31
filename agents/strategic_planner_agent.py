"""
Strategic Planner Agent

負責：
1. 互動需求分析 (Interaction Requirement Analysis)
2. 里程碑計畫 (Milestone Planning)
3. 依賴關係 (Dependency Relationships)
"""

from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


class InteractionRequirement(BaseModel):
    """互動需求模型"""
    requirement_id: str = Field(description="需求ID")
    description: str = Field(description="需求描述")
    user_story: str = Field(description="使用者故事")
    priority: str = Field(description="優先級：high, medium, low")
    estimated_effort: str = Field(description="預估工作量")


class Milestone(BaseModel):
    """里程碑模型"""
    milestone_id: str = Field(description="里程碑ID")
    name: str = Field(description="里程碑名稱")
    description: str = Field(description="里程碑描述")
    deliverables: List[str] = Field(description="交付成果清單")
    deadline: str = Field(description="截止日期")
    dependencies: List[str] = Field(description="依賴的其他里程碑ID")


class DependencyRelationship(BaseModel):
    """依賴關係模型"""
    from_item: str = Field(description="依賴來源")
    to_item: str = Field(description="依賴目標")
    dependency_type: str = Field(description="依賴類型：blocking, related, suggested")
    description: str = Field(description="依賴關係描述")


class StrategicPlan(BaseModel):
    """策略規劃完整輸出"""
    project_name: str = Field(description="專案名稱")
    requirements: List[InteractionRequirement] = Field(description="互動需求清單")
    milestones: List[Milestone] = Field(description="里程碑清單")
    dependencies: List[DependencyRelationship] = Field(description="依賴關係清單")
    summary: str = Field(description="規劃總結")


class StrategicPlannerAgent:
    """策略規劃代理
    
    負責分析專案需求、規劃里程碑、識別依賴關係
    """
    
    def __init__(self, model_name: str = 'google-gla:gemini-2.5-flash'):
        """初始化策略規劃代理
        
        Args:
            model_name: 使用的AI模型名稱
        """
        self.model_name = model_name
        self.agent = Agent(
            model_name,
            output_type=StrategicPlan,
            system_prompt="""
你是一位經驗豐富的專案策略規劃師。你的職責是：

1. **互動需求分析**：
   - 理解專案目標和使用者需求
   - 將需求轉化為清晰的使用者故事
   - 評估需求優先級和工作量
   - 識別關鍵互動場景

2. **里程碑計畫**：
   - 將專案分解為可管理的階段
   - 定義每個里程碑的交付成果
   - 設定合理的時間表
   - 確保里程碑之間的邏輯順序

3. **依賴關係**：
   - 識別需求之間的依賴關係
   - 標記阻塞性依賴和建議性依賴
   - 確保依賴關係清晰可追蹤
   - 優化開發順序以減少阻塞

請以結構化的方式輸出完整的策略規劃。
"""
        )
    
    async def create_strategic_plan(self, project_description: str) -> StrategicPlan:
        """創建策略規劃
        
        Args:
            project_description: 專案描述和需求
            
        Returns:
            StrategicPlan: 完整的策略規劃
        """
        result = await self.agent.run(
            f"""
請為以下專案創建完整的策略規劃：

專案描述：
{project_description}

請提供：
1. 詳細的互動需求分析（至少3-5個需求）
2. 明確的里程碑計畫（至少3個里程碑）
3. 清晰的依賴關係圖
4. 整體規劃總結

請確保輸出符合 StrategicPlan 的資料結構。
"""
        )
        return result.data
    
    async def analyze_requirements(self, requirements_text: str) -> List[InteractionRequirement]:
        """分析互動需求
        
        Args:
            requirements_text: 需求描述文本
            
        Returns:
            List[InteractionRequirement]: 需求清單
        """
        plan = await self.create_strategic_plan(requirements_text)
        return plan.requirements
    
    async def plan_milestones(self, project_description: str) -> List[Milestone]:
        """規劃專案里程碑
        
        Args:
            project_description: 專案描述
            
        Returns:
            List[Milestone]: 里程碑清單
        """
        plan = await self.create_strategic_plan(project_description)
        return plan.milestones
    
    async def identify_dependencies(self, project_description: str) -> List[DependencyRelationship]:
        """識別依賴關係
        
        Args:
            project_description: 專案描述
            
        Returns:
            List[DependencyRelationship]: 依賴關係清單
        """
        plan = await self.create_strategic_plan(project_description)
        return plan.dependencies


# 範例使用
async def example_usage():
    """範例：使用策略規劃代理"""
    agent = StrategicPlannerAgent()
    
    project_desc = """
    建立一個智慧飲食管理系統，需要以下功能：
    1. 使用者可以上傳食物照片
    2. 系統自動識別食物並計算卡路里
    3. 提供個人化的飲食建議
    4. 追蹤使用者的飲食歷史
    5. 整合LINE Bot介面
    """
    
    plan = await agent.create_strategic_plan(project_desc)
    
    print("=" * 50)
    print(f"專案名稱: {plan.project_name}")
    print("\n需求清單:")
    for req in plan.requirements:
        print(f"  - [{req.requirement_id}] {req.description}")
        print(f"    優先級: {req.priority}, 工作量: {req.estimated_effort}")
    
    print("\n里程碑:")
    for milestone in plan.milestones:
        print(f"  - [{milestone.milestone_id}] {milestone.name}")
        print(f"    截止日期: {milestone.deadline}")
        print(f"    依賴: {', '.join(milestone.dependencies) if milestone.dependencies else '無'}")
    
    print("\n依賴關係:")
    for dep in plan.dependencies:
        print(f"  - {dep.from_item} -> {dep.to_item} ({dep.dependency_type})")
    
    print(f"\n總結:\n{plan.summary}")
    print("=" * 50)


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
