# AgentOS 超新手操作指南

這份文件給第一次碰 Docker 和 AgentOS 的同學，照做就能把 baseline 跑起來。

你要完成的目標：

1. 本機 API 跑起來
2. 在 os.agno.com 連上你的本機 AgentOS
3. 看到 `knowledge-agent` 與 `mcp-agent`

---

## 0. 先準備好兩件事

1. 已安裝 Docker Desktop
2. 已安裝 Git（如果你要用 git clone）

如果你是第一堂課沒來，先去 Google AI Studio 申請 Gemini API Key：

1. 打開 https://aistudio.google.com/
2. 登入 Google 帳號
3. 建立 API Key
4. 複製 key，等等會放到 `.env`

---

## 1. 取得專案（兩種方式擇一）

### 方式 A：git clone

```bash
git clone <你的repo網址>
cd agentos-docker
```

### 方式 B：下載 zip

1. 在 GitHub 按 `Code` -> `Download ZIP`
2. 解壓縮
3. 用 Terminal 進到解壓後的 `agentos-docker`

```bash
cd agentos-docker
```

---

## 2. 設定 `.env`

在專案根目錄建立或修改 `.env`，至少有這兩行：

```env
GOOGLE_API_KEY=你的_gemini_api_key
AGNO_MODEL_ID=gemini-2.5-flash
```

注意：

1. `=` 左右不要有空格
2. 不要用舊模型 `gemini-2.0-flash`

---

## 3. 啟動系統

```bash
docker compose up -d --build
```

### 3.1 如果出現 Docker daemon 錯誤

若你看到：

```text
Cannot connect to the Docker daemon ... Is the docker daemon running?
```

代表 Docker Desktop 還沒啟動。

請做：

1. 點兩下開啟 Docker Desktop App
2. 等到 Docker 完全啟動（圖示顯示 running）
3. 再重跑 `docker compose up -d --build`

---

## 4. 正確檢查容器狀態（不只看名稱）

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

你應該至少看到：

1. `agentos-db` 狀態是 `Up ...`
2. `agentos-api` 狀態是 `Up ...`

如果 `agentos-api` 是 `Restarting ...`，代表有錯，還沒成功。

---

## 5. 如果你看到 Restarting，不是等就好

常見訊息：

```text
Container ... is restarting, wait until the container is running
```

這句話不是要你一直等，通常代表容器啟動就崩潰。

請立刻看 log：

```bash
docker compose logs --no-color --tail=100 agentos-api
```

### 5.1 常見錯誤：entrypoint 權限不足

如果你看到：

```text
exec /app/scripts/entrypoint.sh: permission denied
```

請執行：

```bash
chmod +x scripts/entrypoint.sh
docker compose up -d --build --force-recreate --no-deps agentos-api
```

然後再檢查：

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

---

## 6. 健康檢查 API

```bash
curl http://127.0.0.1:8000/health
```

預期看到類似：

```json
{"status":"ok", ...}
```

---

## 7. 載入知識庫（第一次必做）

```bash
docker exec -it agentos-api python -m agents.knowledge_agent
```

成功會看到類似：

```text
INFO Adding content from URL ...
INFO Upserted batch of 1 documents.
```

---

## 8. 連到 os.agno.com（重點）

課堂使用的是雲端介面，不是 localhost 畫面。

1. 打開 https://os.agno.com
2. 登入後選 `Connect your AgentOS`
3. 自己幫這個連線取一個名字（例如 `my-local-agentos`）
4. URL 輸入：

```text
http://localhost:8000
```

連線成功後，你會在 os.agno.com 看到：

1. `knowledge-agent`
2. `mcp-agent`

這兩個 agent 是在 os.agno.com 裡面看，不是在 `http://localhost:8000` 頁面看。

---

## 9. Baseline 測試

先不要改任何程式，先確認 baseline 可跑。

### 9.1 測試 knowledge-agent

在 AgentOS UI 中操作：

1. 選 `knowledge-agent`
2. 輸入：`What is Agno?`

預期：

1. 會得到一段關於 Agno 的介紹
2. 會提到 `Framework`、`Runtime`、`Control Plane`
3. 會顯示來源或相關依據

### 9.2 測試 mcp-agent

在 AgentOS UI 中操作：

1. 選 `mcp-agent`
2. 輸入：`What tools do you have access to?`

預期：

1. 會說明可用工具
2. 回答風格和 `knowledge-agent` 不同

---

## 10. 備援方案：Gradio UI

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

## 11. 兩個 agent 的差異

### knowledge-agent

用途：

1. 查已載入的知識庫內容

適合問題：

1. `What is Agno?`
2. `How do I create my first agent?`
3. `What documents are in your knowledge base?`

### mcp-agent

用途：

1. 用 MCP tool 查 Agno 文件

適合問題：

1. `What tools do you have access to?`
2. `Find examples of agents with memory.`
3. `Search the docs for how to use LearningMachine.`

---

## 12. Baseline 完成標準

至少要做到：

1. 成功啟動 `agentos-api`
2. 成功載入知識庫文件
3. 成功問 `knowledge-agent`
4. 成功問 `mcp-agent`

完成這些後，才進入延伸實作。

---

## 13. 常見訊息對照表

### 訊息 A

```text
The "OPENAI_API_KEY" variable is not set. Defaulting to a blank string.
```

通常可先忽略（本課程主要用 `GOOGLE_API_KEY`）。

### 訊息 B

```text
Cannot connect to the Docker daemon ...
```

Docker Desktop 沒啟動，請先開 app。

### 訊息 C

```text
exec /app/scripts/entrypoint.sh: permission denied
```

請執行 `chmod +x scripts/entrypoint.sh` 後重建容器(docker compose down  -> docker compose up)。

---

## 14. 真的卡住時，先做這 6 步

1. `docker ps` 檢查 `agentos-api` 是否 `Up`（不是 `Restarting`）
2. `docker compose logs --tail=100 agentos-api` 看最後錯誤
3. `curl http://127.0.0.1:8000/health` 看 API 是否回應
4. `docker exec agentos-api printenv GOOGLE_API_KEY` 看 key 是否有讀進去
5. 確認 `.env` 用的是 `AGNO_MODEL_ID=gemini-2.5-flash`
6. 重新建立 API 容器：`docker compose up -d --build --force-recreate --no-deps agentos-api`

---

## 15. 延伸實作方向（baseline 過了再做）

1. 改 prompt 角色（助教、摘要、一定附來源）
2. 新增自己的 agent（course-agent、faq-agent）
3. 換知識庫成課程講義或專題文件
4. 幫 agent 加新工具
5. 改 UI（例如 Gradio）

---

## 16. 官方文件與範例（推薦）

如果你想自己升級 agent，先看官方文件與範例：

1. Agno GitHub 原始碼：https://github.com/agno-agi/agno/tree/main
2. Agno 官方文件：https://docs.agno.com/introduction
3. Tools Cookbook（可直接抄範例改）：https://github.com/agno-agi/agno/tree/main/cookbook/91_tools

---

## 17. 最簡單升級：在 agents 加 tools

最小改動通常只要兩步：

1. 在檔案開頭新增 import
2. 在 `Agent(...)` 裡新增工具到 `tools=[...]`

範例概念：

```python
from agno.tools.youtube import YouTubeTools

agent = Agent(
	tools=[
		# 你原本的工具...
		YouTubeTools(),
	],
)
```

你也可以加上描述讓 UI 更清楚：

```python
description="You are able to do youtube analysis"
```

---

## 18. YouTube Tool 參考範例

官方範例位置：

1. https://github.com/agno-agi/agno/blob/main/cookbook/91_tools/youtube_tools.py

你可以先照著範例理解，再把 `YouTubeTools()` 加回自己的 agent。
