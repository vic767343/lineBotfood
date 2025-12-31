
from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent
from dotenv import load_dotenv
load_dotenv()
# 1. 定義我們想要的結構化輸出資料格式
class calorieAnalysis(BaseModel):
    food_items:list[str]
    calorie: list[float]
    

# 2. 初始化 Agent，設定支援 Vision 的模型 (例如 gpt-4o)
# 注意：你需要先設定好環境變數 OPENAI_API_KEY
agent = Agent(
    'google-gla:gemini-2.5-flash',
    output_type=calorieAnalysis,
    system_prompt="你是一個食物圖像分析專家，請根據提供的圖片內容進行菜色描述及calorie分析，例如:菜色及calorie。請用中文回答。"
)

async def analyze_image():
    # 3. 準備圖片數據 (讀取本地檔案)
    image_path = Path("C:\\Users\\vic76\\Desktop\\Object\\lineBotfood\\static\\images\\try.jpg")
    image_data = image_path.read_bytes()

    # 4. 呼叫 Agent
    # 我們將文字提示和圖片內容封裝在一個清單中傳遞
    result = await agent.run(
        [
            "請幫我分析這張圖片的食物內容。",
            BinaryContent(data=image_data, media_type="image/jpeg")
        ]
    )

    # 5. 取得強型別的解析結果
    print(f"回答: {result}")
if __name__ == "__main__":

    import asyncio
    asyncio.run(analyze_image())