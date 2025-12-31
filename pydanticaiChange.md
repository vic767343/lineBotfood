# 遷移至 Pydantic AI 評估與計畫

## 1. 評估結果
**可行性：極高**
**推薦程度：強烈推薦**

目前專案在 `Service/nlpService.py` 與 `Service/ImageProcessService.py` 中大量使用手動定義的 JSON Schema 與手動解析 JSON 回應。遷移至 `pydantic-ai` 能顯著解決型別安全與解析錯誤的問題。

## 2. 核心優勢

*   **自動化結構驗證 (Type Safety)**
    *   **現狀**: 手動維護 JSON Schema (`parameters` 字典)，需手動 `json.loads` 並處理例外。
    *   **改善**: 定義 Pydantic Model，自動產生 Schema 給 Gemini，並自動驗證回傳資料。
*   **程式碼簡潔化**
    *   移除 `try-except json.JSONDecodeError`。
    *   移除手動欄位檢查邏輯。
    *   Prompt 與資料結構定義分離。
*   **開發體驗 (DX)**
    *   IDE 支援完整的自動補全 (Autocompletion)。
    *   原生支援 `async/await`，契合現代 Python 非同步架構。

## 3. 影響範圍

主要涉及以下服務檔案的重構：

### `Service/nlpService.py`
*   **目標**: 取代 `phys_info_function` 與 `search_intent_function` 的字典定義。
*   **改動**:
    1.  建立 `PhysicalInfo` 與 `SearchIntent` Pydantic Models。
    2.  將 `genai.GenerativeModel` 替換為 `pydantic_ai.Agent`。
    3.  使用 `agent.run()` 直接獲取結構化物件。

### `Service/ImageProcessService.py`
*   **目標**: 規範化圖片分析的輸出結果。
*   **改動**:
    1.  建立 `FoodAnalysisResult` Pydantic Model。
    2.  使用 Agent 處理圖片輸入並回傳驗證後的物件。

## 4. 實作範例對比

### 修改前 (現狀)
```python
# 手動定義 Schema
self.phys_info_function = {
    "name": "extract_physical_info",
    "parameters": {
        "type": "object",
        "properties": {
            "age": {"type": "integer"},
            # ...
        }
    }
}
# 呼叫與解析
response = model.generate_content(..., tools=[self.phys_info_function])
# 需手動處理 function_call 解析
```

### 修改後 (Pydantic AI)
```python
from pydantic import BaseModel, Field
from pydantic_ai import Agent

class PhysicalInfo(BaseModel):
    gender: str = Field(description="用戶的性別(男/女)")
    age: int = Field(description="用戶的年齡(歲)")
    # ...

# 初始化 Agent
agent = Agent('gemini-1.5-flash', result_type=PhysicalInfo)

# 執行 (自動驗證)
result = await agent.run("我今年25歲...")
print(result.data.age) # 25 (Type: int)
```

## 5. 遷移步驟計畫

1.  **安裝依賴**
    ```bash
    pip install pydantic-ai
    ```
2.  **定義 Models**
    *   在 `Service` 目錄下或新建 `Models` 目錄，定義所有需要的 Pydantic Models。
3.  **重構 NLP Service**
    *   優先重構 `extract_physical_info` 功能。
    *   接著重構 `extract_search_intent` 功能。
4.  **重構 Image Service**
    *   定義食物分析結果的 Model。
    *   更新 `imageParse` 方法。
5.  **測試驗證**
    *   驗證資料解析是否正確。
    *   確認錯誤處理機制 (Retry/Fallback) 是否正常運作。

## 6. 注意事項
*   **非同步 (Async)**: `pydantic-ai` 強烈建議使用 `await`，需確認呼叫端的相容性。
*   **模型設定**: 需確認 `pydantic-ai` 的 Gemini 模型配置 (API Key 傳遞方式) 與現有 `config.json` 的整合。
