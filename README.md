# LineBotFood - 智慧飲食管理 LINE Bot

這是一個基於 Python Flask 開發的 LINE Bot 應用程式，結合了 Google Gemini AI 模型，提供智慧化的飲食記錄、影像辨識與個人健康資訊管理功能。

## 📋 專案簡介

LineBotFood 旨在透過對話式介面簡化飲食追蹤的過程。使用者可以直接上傳食物照片或輸入文字，系統會利用 AI 進行分析，自動辨識食物內容並估算營養資訊，同時記錄使用者的身體數據，協助進行健康管理。

## ✨ 主要功能

*   **AI 影像辨識**：整合 Google Gemini Vision 模型，可分析使用者上傳的食物照片，自動辨識食物種類與內容。
*   **自然語言處理 (NLP)**：使用 Gemini 模型理解使用者的文字訊息，提取飲食記錄或身體資訊（如年齡、性別等）。
*   **飲食記錄管理**：自動將辨識出的食物資訊存入資料庫，追蹤每日飲食。
*   **個人健康資訊**：記錄並管理使用者的身體數據。
*   **高效能架構**：
    *   **非同步處理 (AsyncProcessor)**：提升回應速度。
    *   **快取機制 (SimpleCache)**：減少重複運算與 API 呼叫。
    *   **資料庫連接池 (ConnectionPool)**：優化 SQL Server 連線管理。
    *   **錯誤處理 (OptimizedErrorHandler)**：強健的異常處理機制。

## 🛠️ 技術架構

*   **語言**: Python 3.13+
*   **Web 框架**: Flask
*   **AI 模型**: Google Gemini (Generative AI)
*   **資料庫**: Microsoft SQL Server (透過 pyodbc 連接)
*   **通訊協定**: LINE Messaging API
*   **其他依賴**: Pandas, Requests

## 📂 專案結構

```
lineBotfood/
├── app.py                      # 程式進入點
├── pyproject.toml              # 專案依賴配置
├── application/                # Flask App 初始化
├── config/                     # 設定檔目錄
│   ├── config.json             # API Key 設定 (Gemini 等)
│   ├── dataBase.py             # 資料庫連線設定
│   ├── line_config.py          # LINE Bot 設定
│   └── Prompt.py               # AI 提示詞 (Prompts)
├── Conrtoller/                 # 控制器 (API Endpoints)
│   ├── FoodController.py       # 食物相關 API
│   ├── LineWebHookRESTController.py # LINE Webhook 處理
│   └── ...
├── Service/                    # 業務邏輯層
│   ├── FoodDataService.py      # 食物資料服務
│   ├── ImageProcessService.py  # 影像處理服務 (Gemini)
│   ├── nlpService.py           # NLP 服務 (Gemini)
│   ├── ConnectionFactory.py    # 資料庫連接工廠
│   └── ...
├── dataBaseSQL/                # 資料庫 SQL 腳本
│   ├── foodDetail.sql
│   ├── foodMaster.sql
│   └── physInfo.sql
├── static/                     # 靜態檔案 (圖片、文件)
└── templates/                  # HTML 模板 (Web 介面)
```

## 🚀 安裝與設定

### 1. 環境準備

確保已安裝 Python 3.13 或以上版本，以及 SQL Server (需安裝 ODBC Driver 18)。

### 2. 安裝依賴套件

```bash
pip install flask pandas google-generativeai pyodbc requests
# 或參考 pyproject.toml 安裝
```

### 3. 資料庫設定

1.  建立一個名為 `Food` 的 SQL Server 資料庫。
2.  執行 `dataBaseSQL/` 目錄下的 SQL 腳本以建立資料表 (`foodMaster`, `foodDetail`, `physInfo`)。
3.  修改 `config/dataBase.py` 或設定環境變數 `PASSWORD` 以配置資料庫連線密碼。

### 4. API Key 設定

請確保 `config/config.json` 或相關設定檔中填入正確的 API Key：
*   **Google Gemini API Key**
*   **LINE Channel Access Token**
*   **LINE Channel Secret**

### 5. 啟動應用程式

```bash
python app.py
```
預設會在 `http://127.0.0.1:1997` 啟動服務。

### 6. LINE Webhook 設定

使用 ngrok 或其他工具將本地 1997 port 公開到網際網路，並將 URL (例如 `https://your-domain.com/api/v1/callback`) 填入 LINE Developers Console 的 Webhook URL 欄位。

## 📝 使用說明

1.  加入 LINE Bot 好友。
2.  **傳送文字**：輸入「我今天吃了漢堡」，AI 會嘗試解析並記錄。
3.  **傳送圖片**：上傳一張食物照片，AI 會分析照片內容並回覆食物資訊。

## ⚠️ 注意事項

*   本專案使用 SQL Server，請確保驅動程式 (ODBC Driver 18) 已正確安裝。
*   Gemini API 可能會產生費用，請留意使用量。
