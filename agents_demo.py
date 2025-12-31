"""
完整範例：三個代理協作

展示 strategic-planner, steering-architect, 和 task-executor 如何協作完成專案規劃和實作
"""

import asyncio
from agents.strategic_planner_agent import StrategicPlannerAgent
from agents.steering_architect_agent import SteeringArchitectAgent
from agents.task_executor_agent import TaskExecutorAgent


async def main():
    """主函數：展示三個代理的協作流程"""
    
    print("=" * 80)
    print("三個代理協作示範：智慧飲食管理系統專案")
    print("=" * 80)
    
    # 專案需求描述
    project_requirements = """
    專案名稱：智慧飲食管理系統 (Smart Diet Management System)
    
    業務目標：
    - 幫助使用者追蹤和管理日常飲食
    - 提供 AI 驅動的營養分析和建議
    - 透過 LINE Bot 提供便捷的使用體驗
    
    核心功能：
    1. 食物圖片識別與分析
    2. 自動卡路里計算
    3. 個人化飲食建議
    4. 飲食歷史追蹤與統計
    5. 體重管理與目標設定
    
    目標使用者：
    - 注重健康的一般消費者
    - 需要體重管理的使用者
    - 想要了解飲食習慣的人群
    
    預期規模：
    - 初期：1,000-10,000 活躍用戶
    - 成長期：10,000-100,000 活躍用戶
    """
    
    # ========================================================================
    # 階段 1: Strategic Planner - 策略規劃
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("階段 1: Strategic Planner - 策略規劃")
    print("=" * 80)
    print("正在分析需求、規劃里程碑、識別依賴關係...\n")
    
    strategic_planner = StrategicPlannerAgent()
    strategic_plan = await strategic_planner.create_strategic_plan(project_requirements)
    
    print(f"\n【專案名稱】 {strategic_plan.project_name}")
    
    print("\n【互動需求分析】")
    for i, req in enumerate(strategic_plan.requirements, 1):
        print(f"\n需求 {i}: {req.requirement_id}")
        print(f"  描述: {req.description}")
        print(f"  使用者故事: {req.user_story}")
        print(f"  優先級: {req.priority}")
        print(f"  預估工作量: {req.estimated_effort}")
    
    print("\n【里程碑計畫】")
    for i, milestone in enumerate(strategic_plan.milestones, 1):
        print(f"\n里程碑 {i}: {milestone.milestone_id} - {milestone.name}")
        print(f"  描述: {milestone.description}")
        print(f"  截止日期: {milestone.deadline}")
        print(f"  交付成果:")
        for deliverable in milestone.deliverables:
            print(f"    - {deliverable}")
        if milestone.dependencies:
            print(f"  依賴: {', '.join(milestone.dependencies)}")
    
    print("\n【依賴關係】")
    for i, dep in enumerate(strategic_plan.dependencies, 1):
        print(f"{i}. {dep.from_item} -> {dep.to_item}")
        print(f"   類型: {dep.dependency_type}")
        print(f"   說明: {dep.description}")
    
    print(f"\n【策略規劃總結】\n{strategic_plan.summary}")
    
    # ========================================================================
    # 階段 2: Steering Architect - 架構設計
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("階段 2: Steering Architect - 架構設計")
    print("=" * 80)
    print("正在設計產品藍圖、選擇技術堆疊、定義架構...\n")
    
    steering_architect = SteeringArchitectAgent()
    
    # 基於策略規劃的結果，添加技術約束
    tech_constraints = """
    現有技術堆疊：
    - Python 3.13+
    - Flask 框架
    - SQL Server 資料庫
    - Google Gemini AI
    - LINE Messaging API
    
    團隊技能：
    - Python 後端開發
    - SQL 資料庫設計
    - RESTful API 開發
    - 基本的前端開發能力
    """
    
    architectural_design = await steering_architect.create_architectural_design(
        project_requirements, 
        tech_constraints
    )
    
    print(f"\n【專案名稱】 {architectural_design.project_name}")
    
    print("\n【產品藍圖】")
    current_quarter = None
    for feature in architectural_design.product_roadmap:
        if feature.quarter != current_quarter:
            print(f"\n{feature.quarter}:")
            current_quarter = feature.quarter
        print(f"  - {feature.name} ({feature.status})")
        print(f"    {feature.description}")
    
    print("\n【技術選型】")
    tech_by_category = {}
    for tech in architectural_design.technology_stack:
        if tech.category not in tech_by_category:
            tech_by_category[tech.category] = []
        tech_by_category[tech.category].append(tech)
    
    for category, techs in tech_by_category.items():
        print(f"\n{category.upper()}:")
        for tech in techs:
            print(f"  - {tech.technology} (v{tech.version})")
            print(f"    理由: {tech.reason}")
            if tech.alternatives:
                print(f"    替代方案: {', '.join(tech.alternatives)}")
    
    print("\n【架構元件】")
    for i, component in enumerate(architectural_design.architecture_components, 1):
        print(f"\n元件 {i}: {component.component_name}")
        print(f"  職責: {component.responsibility}")
        print(f"  介面: {', '.join(component.interfaces)}")
        print(f"  依賴: {', '.join(component.dependencies) if component.dependencies else '無'}")
        print(f"  設計模式: {', '.join(component.design_patterns)}")
    
    print("\n【結構規範】")
    print("\n目錄結構:")
    for path, desc in architectural_design.structure_specification.directory_structure.items():
        print(f"  {path}")
        print(f"    -> {desc}")
    
    print("\n命名規範:")
    for key, value in architectural_design.structure_specification.naming_conventions.items():
        print(f"  - {key}: {value}")
    
    print("\n程式碼標準:")
    for standard in architectural_design.structure_specification.code_standards:
        print(f"  - {standard}")
    
    print(f"\n【架構圖描述】\n{architectural_design.architecture_diagram_description}")
    print(f"\n【架構設計總結】\n{architectural_design.summary}")
    
    # ========================================================================
    # 階段 3: Task Executor - 任務執行
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("階段 3: Task Executor - 任務執行")
    print("=" * 80)
    print("正在生成腳手架、設定檔、測試框架和核心程式碼...\n")
    
    task_executor = TaskExecutorAgent()
    
    # 整合前兩個階段的結果作為規格
    detailed_specification = f"""
    專案規格：{project_requirements}
    
    里程碑：
    {', '.join([m.name for m in strategic_plan.milestones])}
    
    架構設計：
    {architectural_design.summary}
    """
    
    # 從架構設計提取技術堆疊資訊
    tech_stack_info = "\n".join([
        f"- {tech.category}: {tech.technology} (v{tech.version})"
        for tech in architectural_design.technology_stack
    ])
    
    implementation_plan = await task_executor.create_implementation_plan(
        detailed_specification,
        tech_stack_info
    )
    
    print(f"\n【專案名稱】 {implementation_plan.project_name}")
    
    print("\n【腳手架規劃】")
    print(f"框架: {implementation_plan.scaffolding.framework}")
    print("\n目錄結構:")
    for directory in implementation_plan.scaffolding.directory_structure:
        print(f"  - {directory}")
    
    print("\n初始檔案:")
    for file_path, description in implementation_plan.scaffolding.initial_files.items():
        print(f"  - {file_path}")
        print(f"    {description}")
    
    print("\n初始化命令:")
    for i, cmd in enumerate(implementation_plan.scaffolding.commands, 1):
        print(f"  {i}. {cmd}")
    
    print("\n【設定配置】")
    print(f"設定檔: {implementation_plan.configuration.config_file}")
    print(f"格式: {implementation_plan.configuration.config_format}")
    
    print("\n必要設定項目:")
    for key, desc in implementation_plan.configuration.required_settings.items():
        print(f"  - {key}: {desc}")
    
    print("\n環境變數:")
    for env_var in implementation_plan.configuration.environment_variables:
        print(f"  - {env_var}")
    
    print("\n範例設定檔:")
    print("  " + "\n  ".join(implementation_plan.configuration.sample_config.split("\n")))
    
    print("\n【測試框架】")
    print(f"測試框架: {implementation_plan.test_framework.framework_name}")
    print(f"測試目錄: {implementation_plan.test_framework.test_directory}")
    print(f"檔案命名規範: {implementation_plan.test_framework.test_file_naming}")
    
    print("\n設定命令:")
    for i, cmd in enumerate(implementation_plan.test_framework.setup_commands, 1):
        print(f"  {i}. {cmd}")
    
    print("\n範例測試:")
    print("  " + "\n  ".join(implementation_plan.test_framework.sample_test.split("\n")))
    
    print("\n【核心元件】")
    for i, component in enumerate(implementation_plan.core_components, 1):
        print(f"\n元件 {i}: {component.file_path}")
        print(f"  說明: {component.description}")
        if component.dependencies:
            print(f"  依賴: {', '.join(component.dependencies)}")
        print(f"  程式碼:")
        # 只顯示前10行，避免輸出過長
        code_lines = component.code.split("\n")[:10]
        for line in code_lines:
            print(f"    {line}")
        if len(component.code.split("\n")) > 10:
            print(f"    ... (省略 {len(component.code.split('\n')) - 10} 行)")
    
    print("\n【整合步驟】")
    for i, step in enumerate(implementation_plan.integration_steps, 1):
        print(f"  {i}. {step}")
    
    print("\n【部署檢查清單】")
    for i, item in enumerate(implementation_plan.deployment_checklist, 1):
        print(f"  {i}. {item}")
    
    print(f"\n【實作計畫總結】\n{implementation_plan.summary}")
    
    # ========================================================================
    # 總結
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("三個代理協作完成！")
    print("=" * 80)
    print("""
完整的專案規劃流程：

1. Strategic Planner (策略規劃師)
   ✓ 分析了 {req_count} 個互動需求
   ✓ 規劃了 {milestone_count} 個里程碑
   ✓ 識別了 {dep_count} 個依賴關係

2. Steering Architect (架構指導師)
   ✓ 設計了 {feature_count} 個產品功能
   ✓ 選擇了 {tech_count} 項技術
   ✓ 定義了 {component_count} 個架構元件

3. Task Executor (任務執行者)
   ✓ 創建了完整的腳手架規劃
   ✓ 配置了專案設定和測試框架
   ✓ 生成了 {code_count} 個核心元件的程式碼骨架

專案現在已經準備好開始實作！
""".format(
        req_count=len(strategic_plan.requirements),
        milestone_count=len(strategic_plan.milestones),
        dep_count=len(strategic_plan.dependencies),
        feature_count=len(architectural_design.product_roadmap),
        tech_count=len(architectural_design.technology_stack),
        component_count=len(architectural_design.architecture_components),
        code_count=len(implementation_plan.core_components)
    ))
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
