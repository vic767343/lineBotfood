# FastAPI 遷移建議（從 Flask -> FastAPI）⚡

> 這份文件針對專案 `lineBotfood` 提供從 Flask 遷移到 FastAPI 的可行性評估、漸進遷移步驟、PoC 範例、風險與緩解、以及推行檢查清單。

---

## 一、為什麼考慮 FastAPI？💡

- 原生支援 async/await、I/O 密集型效能通常優於同步 Flask。 
- 使用 Pydantic 提供**型別驗證**與自動請求驗證（減少手寫驗證錯誤）。
- 自動產生 OpenAPI / Swagger UI（方便開發/測試）。
- 良好的 ASGI 生態（支援 WebSocket、背景任務與中介層）。

## 二、專案影響面總覽 🔍

- **控制層（Conrtoller/）**：需要把 Flask route/Blueprint 改為 FastAPI 的 APIRouter（主要改動點）。
- **啟動與部署**：由 WSGI（現有 Flask）改為 ASGI（Uvicorn / Gunicorn+Uvicorn worker）。
- **全域物件**：Flask 的 `request`, `g`, `current_app` 等需改為函式參數或 DI（依賴注入）。
- **Service 層**：若保留同步 DB 驅動，可短期內不需改動；如要 async DB，將需要改寫 Data Access 層（較大變更）。
- **現有擴充套件**：部分 Flask-only extensions 需替換或自行整合。

## 三、建議的漸進遷移流程（步驟）🔧

1. **建立分支**（例如 `feature/fastapi-poc`）並新增依賴：
   - pip install fastapi uvicorn pydantic
2. **PoC：新增最小 FastAPI 應用**（不刪除現有 Flask 應用）並提供 /health 與 /webhook 範例。
3. **轉換單一 Controller（優先選 Line webhook）**：把 `LineWebHookRESTController.py` 改寫為 APIRouter，驗證接收與回覆流程一致。
4. **建立 Pydantic schema**：用 model 定義 webhook payload 與回應 DTO，逐步替換原有手寫解析。
5. **保留 Service 層**（盡量不改）：將 Controller 層轉為 FastAPI，Service 可在同步模式下繼續使用以降低改動。
6. **測試與比較**：撰寫端到端測試，執行效能比較（Flask vs FastAPI），確定沒有功能回歸。
7. **擴大改寫範圍**：其他 Controller 陸續改寫，處理 middleware、例外管理、日誌等整合。
8. **決定 DB 策略**：若目標為全面 async，計畫第二階段改寫 DB 層（使用 async ORM 或 driver，例如 SQLAlchemy async / databases）。
9. **更新部署/CI**：替換測試與部署流程（使用 Uvicorn，更新 Dockerfile 與 CI 設定）。

## 四、PoC 範例（最小可運作範例）🔁

`app_fastapi.py`（放專案根目錄或 `application/` 下）

```python
from fastapi import FastAPI, APIRouter, BackgroundTasks, Request
from pydantic import BaseModel

class WebhookEvent(BaseModel):
    type: str
    # 可根據 LINE payload 擴充欄位

app = FastAPI(title="lineBotfood - FastAPI PoC")
router = APIRouter(prefix="/line")

@router.post("/webhook")
async def line_webhook(event: WebhookEvent, background_tasks: BackgroundTasks):
    # 轉發到現有 Service 層（同步呼叫也可）
    # from Service.FoodDataService import handle_event
    # background_tasks.add_task(handle_event, event.dict())
    return {"status": "ok"}

app.include_router(router)

# 以 uvicorn 啟動： uvicorn app_fastapi:app --host 0.0.0.0 --port 8000
```

### 將 `LineWebHookRESTController.py` 改寫成 APIRouter 的建議

- 將路由函式改為 `async def`（或 `def` 若仍採同步方式）。
- 使用 Pydantic 來 validate 與取代原本手寫解析。
- 讓 Controller 呼叫既有 `Service/` 層的函式（可透過 BackgroundTasks 執行非同步工作）。

## 五、測試、監控與回歸驗證 ✅

- 必須新增或更新：單元測試（Service 層）、整合測試（Webhook flow）、API 合約測試（Pydantic schema 驗證）。
- 建議 A/B 或 Shadow Deployment（先把流量導到 FastAPI PoC 小流量測試）。
- 加強結構化日誌與追蹤（例：增加 request id、Error monitoring）。

## 六、部署建議（快速範例）🐳

- 使用 Uvicorn： `uvicorn app_fastapi:app --host 0.0.0.0 --port 8000 --workers 4` 或使用 Gunicorn + Uvicorn workers。 
- Dockerfile（簡化範例）：

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 七、風險與緩解 ⚠️

- 風險：若立即把 DB 變成 async，改動大、BUG 風險高。  
  緩解：採二階段策略（先只改 Controller 層，保留同步 DB）。
- 風險：若使用大量 Flask-specific extensions，可能找不到一對一替代。  
  緩解：辨識最關鍵擴充套件並評估替代方案或手動整合。
- 風險：測試不足導致回歸。  
  緩解：強化測試覆蓋並執行灰度發布。

## 八、時間人力估計（粗略）⏱

- PoC（新增 FastAPI，變更 1 個 Controller 並測試）：1–3 天
- 中等範圍（多個 Controller 轉換、更新 CI & Docker，保留同步 DB）：3–10 天
- 全面 async（DB 及大量整合改寫）：數週

## 九、推行檢查清單（Checklist）✅

- [ ] 新增 `fastapi`、`uvicorn` 到開發依賴
- [ ] 建立 PoC 分支（推 PR）
- [ ] 改寫 `LineWebHookRESTController.py`，使用 APIRouter + Pydantic
- [ ] 撰寫 webhook 的整合測試
- [ ] 比較效能（簡單壓測）與資源使用
- [ ] 決定是否逐步改寫 DB 為 async
- [ ] 更新 Dockerfile 與 CI workflow

---

如果您想，我可以：

- 把 `LineWebHookRESTController.py` 實際改寫成 FastAPI 的 PoC（包含測試與範例 request）；或
- 產生一份 `app_fastapi.py`、更新的 `Dockerfile` 與 `GitHub Actions` 範本。

請選擇下一步（選一項即可），我會接著把實作放在專案分支上。