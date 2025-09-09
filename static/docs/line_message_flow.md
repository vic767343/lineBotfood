    # LINE 訊息處理流程圖

    ## 使用者訊息處理流程

    ```mermaid
    flowchart TD
        A[使用者發送訊息] --> B[LINE Webhook接收訊息]
        B --> C{去重機制檢查\nEventDeduplicator}
        C -->|已處理過| D[結束流程]
        C -->|新訊息| E{訊息類型判斷}

        %% 文字訊息處理流程
        E -->|文字訊息| F[LineMessageHandler\n_handle_text_message_fast]
        F --> F1{統一響應服務檢查\nUnifiedResponseService}
        F1 -->|命中快速響應| F2[回覆使用者]
        F1 -->|未命中| F3{檢查NLP快取}
        F3 -->|命中快取| F4[回覆快取結果]
        F3 -->|未命中快取| F5[NLPService處理]

        %% NLP處理流程
        F5 --> N1[處理文字訊息\nnlpProcess]
        N1 --> N2{檢測意圖類型}
        N2 -->|BMI計算意圖| N3[調用ManagerCalService]
        N2 -->|食物紀錄意圖| N4[調用FoodDataService]
        N2 -->|更新身體資訊意圖| N5[調用PhysInfoDataService]
        N2 -->|一般對話意圖| N6[使用Gemini生成回應]
        N3 --> N7[整合處理結果]
        N4 --> N7
        N5 --> N7
        N6 --> N7
        N7 --> F2

        %% 圖片訊息處理流程
        E -->|圖片訊息| G[LineMessageHandler\n_handle_image_message]
        G --> G1[獲取圖片內容]
        G1 --> G2{檢查圖片快取}
        G2 -->|命中快取| G3[回覆快取結果]
        G2 -->|未命中快取| G4[調用ImageProcessService]
        G4 --> G5[圖片解析與分析\nimageParse]
        G5 --> G6[使用Gemini分析圖片內容]
        G6 --> G7[整理分析結果]
        G7 --> G8[更新快取]
        G8 --> G9[回覆使用者]

        %% 其他訊息類型
        E -->|音訊訊息| H[LineMessageHandler\n_handle_audio_message]
        H --> H1[告知目前不支援音訊訊息]
        E -->|其他類型| I[回覆不支援的訊息類型]

        %% 回覆流程
        F2 --> J[send_reply函數發送回覆]
        F4 --> J
        G3 --> J
        G9 --> J
        H1 --> J
        I --> J
        J --> K[使用LINE Messaging API發送回覆]
        K --> L[流程結束]
    ```

    ## 資料庫儲存流程

    ```mermaid
    flowchart TD
        A[NLPService識別儲存意圖] --> B{意圖類型}

        %% 身體資訊儲存流程
        B -->|身體資訊儲存| C[PhysInfoDataService]
        C --> C1[create_phys_info方法]
        C1 --> C2[驗證輸入資料]
        C2 --> C3[檢查master_id是否存在]
        C3 -->|不存在| C4[建立新foodMaster記錄]
        C3 -->|存在| C5[跳過建立master]
        C4 --> C6[插入physInfo記錄]
        C5 --> C6
        C6 --> C7[提交資料庫交易]

        %% 食物紀錄儲存流程
        B -->|食物紀錄儲存| D[FoodDataService]
        D --> D1[create_food_detail方法]
        D1 --> D2[驗證輸入資料]
        D2 --> D3[檢查master_id是否存在]
        D3 -->|不存在| D4[建立新foodMaster記錄]
        D3 -->|存在| D5[跳過建立master]
        D4 --> D6[插入foodDetail記錄]
        D5 --> D6
        D6 --> D7[提交資料庫交易]

        %% 搜尋流程
        B -->|搜尋意圖| E[FoodDataService]
        E --> E1[search_food_records方法]
        E1 --> E2[準備搜尋條件]
        E2 --> E3[執行資料庫查詢]
        E3 --> E4[格式化搜尋結果]

        %% 連接工廠和錯誤處理
        subgraph 資料庫連接管理
        X[ConnectionFactory.create_connection]
        Y[ConnectionFactory.get_query_count]
        Z[ConnectionFactory.commit_and_close]
        end

        subgraph 錯誤處理
        O[OptimizedErrorHandler]
        end

        C2 --> X
        C3 --> Y
        C7 --> Z
        D2 --> X
        D3 --> Y
        D7 --> Z
        E2 --> X
        E4 --> Z

        C1 --> O
        D1 --> O
        E1 --> O
    ```

    ## 整體資料流動

    ```mermaid
    flowchart LR
        User[使用者] -->|發送訊息| LINE[LINE平台]
        LINE -->|Webhook| Server[應用伺服器]
        Server -->|訊息處理| Controller[LineWebHookRESTController]
        Controller <-->|呼叫服務| Services[服務層]
        Services <-->|資料庫操作| DB[(資料庫)]

        subgraph 服務層
        NLP[NLPService]
        Image[ImageProcessService]
        Food[FoodDataService]
        Phys[PhysInfoDataService]
        Manager[ManagerCalService]
        end

        Controller -->|回應訊息| LINE
        LINE -->|傳送回覆| User

        subgraph 快取機制
        Cache1[nlp_cache]
        Cache2[image_cache]
        Cache3[user_cache]
        end

        NLP <--> Cache1
        Image <--> Cache2
        Services <--> Cache3
    ```

    ## 關鍵資料表結構

    ```mermaid
    erDiagram
        foodMaster ||--o{ foodDetail : 包含
        foodMaster ||--o{ physInfo : 包含

        foodMaster {
            string id PK
            string user_id
            datetime created_at
            datetime updated_at
        }

        foodDetail {
            string id PK
            string master_id FK
            string food_name
            float calories
            datetime created_at
            string meal_type
            string image_path
        }

        physInfo {
            string id PK
            string master_id FK
            string gender
            int age
            float height
            float weight
            string allergic_foods
            datetime created_at
            datetime updated_at
        }
    ```
