from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent
from dotenv import load_dotenv
import asyncio
load_dotenv()
# 設置日誌記錄


class calorieAnalysis(BaseModel):
    food_items:list[str]
    calorie: list[float]
    
class ImageProcessService:
    def __init__(self, agentModel , event_bus ,pydanetic_ai ,):
        agentModel = 'google-gla:gemini-2.5-flash'
        self.agentModel = agentModel


    async def imageParse(self, image_data: bytes):
        imageAgent = Agent(self.agentModel ,
                           output_type=calorieAnalysis,
                           system_prompt=
                           """
                           你是一個食物圖像分析專家，請根據提供的圖片內容進行菜色描述及calorie分析，例如:菜色及calorie。請用中文回答。
                           """)
        
        try:
            # 呼叫 Agent
            # 我們將文字提示和圖片內容封裝在一個清單中傳遞
            result = await imageAgent.run(
                [
                "請幫我分析圖片的食物內容。",
                BinaryContent(data=image_data, media_type="image/jpeg")
                ]
            )
            print(f"回答: {result.data}")
            return result.data
        except Exception as e:
            print(f"Image analysis failed: {e}")
            return None
