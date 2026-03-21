# AgentOS 課堂操作指南

這份文件是給學生直接照著操作的 step-by-step 手冊。

目標分成兩段：

1. 先把 baseline 跑起來
2. 再做一個自己的延伸版本

---

## 1. 你會完成什麼

完成後你應該可以：

- 啟動 AgentOS 與資料庫
- 載入知識庫內容
- 用 `os.agno.com` 測試 agent
- 分辨 `knowledge-agent` 和 `mcp-agent` 的差異
- 選一個方向做延伸實作

---

## 2. 進入專案資料夾

按照先前投影片安裝的話會有 `agentos-docker` 專案資料夾
用指令進入該資料夾

範例：

```bash
cd agentos-docker
```

---

## 3. 設定 `.env`

agentos-docker資料夾裡裡應該有.env檔案，請放入下面兩行
```env
GOOGLE_API_KEY=你的_gemini_api_key
AGNO_MODEL_ID=gemini-2.5-flash
```

注意：

- `GOOGLE_API_KEY=` 後面不要多空格
- 不要寫成 `GOOGLE_API_KEY = ...`
- 不要用舊模型 `gemini-2.0-flash`

---

## 4. 啟動系統

在專案資料夾中執行：

```bash
docker compose up -d --build
```

確認容器有起來：

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

預期至少看到：

- `agentos-api`
- `agentos-db`

確認 API 正常：

```bash
curl http://127.0.0.1:8000/health
```

預期看到：

```json
{"status":"ok", ...}
```

---

## 5. 載入知識庫文件

第一次使用要先把文件灌進知識庫：

```bash
docker exec -it agentos-api python -m agents.knowledge_agent
```

如果成功，會看到類似：

```text
INFO Adding content from URL ...
INFO Upserted batch of 1 documents.
```

如果這步沒有成功，後面 `knowledge-agent` 可能不會正常回答。

---

## 6. 使用 AgentOS UI

正常情況下，課堂主要使用 [https://os.agno.com](https://os.agno.com)。

請先確認本地 API 已啟動，然後進行連線。

### 6.1 打開 AgentOS UI

在瀏覽器打開：

```text
https://os.agno.com
```

### 6.2 連接本地 AgentOS

依序操作：

1. 登入 `os.agno.com`
2. 點選新增 OS
3. 選擇 `Local`
4. 輸入：

```text
http://localhost:8000
```

5. 完成連線

如果連線成功，你應該可以看到目前的 agent，例如：

- `knowledge-agent`
- `mcp-agent`

---

## 7. Baseline 測試

先不要改任何程式，先確認 baseline 可跑。

### 7.1 測試 `knowledge-agent`

在 AgentOS UI 中：

- 選 `knowledge-agent`
- 輸入：

```text
What is Agno?
```

預期：

- 會得到一段關於 Agno 的介紹
- 會提到 `Framework`、`Runtime`、`Control Plane`
- 會顯示來源或相關依據

### 7.2 測試 `mcp-agent`

在 AgentOS UI 中：

- 選 `mcp-agent`
- 輸入：

```text
What tools do you have access to?
```

預期：

- 會說明可用工具
- 回答風格和 `knowledge-agent` 不同

---

## 8. 備援方案：Gradio UI

如果 `os.agno.com` 無法正常連線，再使用這個備援方案。

如果本機還沒有安裝 UI 需要的套件：

```bash
pip install gradio requests
```

啟動 UI：

```bash
python ui/app.py
```

打開瀏覽器：

```text
http://localhost:7860
```

---

## 9. 兩個 agent 的差異

### `knowledge-agent`

用途：

- 查已載入的知識庫內容

適合問題：

- `What is Agno?`
- `How do I create my first agent?`
- `What documents are in your knowledge base?`

### `mcp-agent`

用途：

- 用 MCP tool 查 Agno 文件

適合問題：

- `What tools do you have access to?`
- `Find examples of agents with memory.`
- `Search the docs for how to use LearningMachine.`

---

## 10. Baseline 完成標準

至少要做到：

- 成功啟動 `agentos-api`
- 成功載入知識庫文件
- 成功問 `knowledge-agent`
- 成功問 `mcp-agent`

完成這些後，才進入延伸實作。


## 11. 如果 `os.agno.com` 連不上

先檢查 API：

```bash
curl http://127.0.0.1:8000/health
```

如果 API 正常，但 `os.agno.com` 還是連不上，改用備援方案：

```bash
python ui/app.py
```

然後打開：

```text
http://localhost:7860
```

---

## 12. Gemini API key 常見問題

這部分是最常見的卡點。

### 問題 1：模型設成舊版

請確認 `.env` 使用的是：

```env
AGNO_MODEL_ID=gemini-2.5-flash
```

不要使用：

```env
AGNO_MODEL_ID=gemini-2.0-flash
```

### 問題 2：改了 `.env` 但容器沒更新

如果你改過 `.env`，請重新啟動：

```bash
docker compose down
docker compose up -d --build
```

### 問題 3：API key 沒讀進容器

檢查容器內的 key：

```bash
docker exec agentos-api printenv GOOGLE_API_KEY
```

如果是空的，代表 `.env` 沒有正確讀進去。

### 問題 4：配額錯誤

如果看到：

- `429 RESOURCE_EXHAUSTED`
- `limit: 0`

代表目前這把 key 對應的專案沒有可用 quota，或不是你以為那把 key。

### 問題 5：快速重測

如果 UI 有問題，也可以直接用 API 測：

```bash
curl -X POST "http://127.0.0.1:8000/agents/knowledge-agent/runs" \
  -F 'message=What is Agno?' \
  -F 'stream=false'
```


## 13. 延伸實作方向

可以選一個方向嘗試實作。

### 方向 A：改 Prompt / 角色

可以做：

- 助教 agent
- 新手教學 agent
- 條列摘要 agent
- 一定附來源的 agent

### 方向 B：新增 Agent

可以做：

- `course-agent`
- `lab-agent`
- `faq-agent`
- `coding-agent`

### 方向 C：換知識庫內容

把 Agno docs 換成自己的資料：

- 課程講義
- 實驗室規範
- 作業說明
- 專題文件

### 方向 D：加 Tool

幫 agent 增加新的能力：

- 查網站
- 查資料
- 呼叫自訂 function

### 方向 E：改 UI

可以改：

- 顯示更多欄位
- 調整版面
- 增加範例問題
- 做成更像聊天視窗


## 14. 如果卡住，先檢查這 5 件事

1. `docker ps` 有沒有看到 `agentos-api`
2. `curl http://127.0.0.1:8000/health` 有沒有回 `ok`
3. `.env` 有沒有 `GOOGLE_API_KEY`
4. `.env` 是不是 `AGNO_MODEL_ID=gemini-2.5-flash`
5. `docker exec agentos-api printenv GOOGLE_API_KEY` 有沒有值
