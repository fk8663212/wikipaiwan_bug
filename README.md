# Paiwan Wikipedia 文字爬蟲

這個專案用來從[排灣語維基百科](https://pwn.wikipedia.org)批次下載所有條目的純文字內容，並將每一條目儲存成一個獨立的 `.txt` 檔，方便後續語料處理或語言研究使用。

---

## 功能概觀

- 從「所有頁面」索引（`Special:AllPages`）開始，依序抓取所有條目的 URL。
- 對每個條目：
  - 取得主標題與內文（包含標題階層、段落、列表等）
  - 轉為純文字，每個條目輸出成一個 `.txt` 檔
- 自動略過不合法檔名字元，避免檔案建立失敗。

主要腳本：

- `crawl_pwn_wiki_plaintext.py`：負責抓取頁面索引與條目內容，並寫出到 `outputs/` 資料夾。

---

## 環境需求

- Python 3.8 以上（建議使用虛擬環境）
- 主要依賴套件：
  - `requests`
  - `beautifulsoup4`

---

## 安裝步驟

1. 取得專案原始碼：

   ```bash
   git clone <this-repo-url>
   cd wikipaiwan_bug
   ```

2. 建議建立虛擬環境（可選）：

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows 請改用 .venv\Scripts\activate
   ```

3. 安裝必要套件：

   ```bash
   pip install requests beautifulsoup4
   ```

   或若有 `requirements.txt`：

   ```bash
   pip install -r requirements.txt
   ```

---

## 使用方法

### 直接執行爬蟲

在專案根目錄執行：

```bash
python crawl_pwn_wiki_plaintext.py
```

腳本會：

1. 從 `START_INDEX_URL`（目前從條目「1984」開始）開始，逐頁爬取「所有頁面」索引。
2. 收集所有條目的 URL 與標題。
3. 依序下載每個條目的 HTML。
4. 從 HTML 中抽取主標題與內文（`h2/h3/h4/p/li` 等節點的純文字）。
5. 將每個條目輸出成 `outputs/<條目名稱>.txt`。

執行過程中，終端機會顯示目前正在處理的索引頁與條目進度。

---

## 輸出結果

執行完成後，專案根目錄會出現 `outputs/` 資料夾，結構大致如下：

```text
outputs/
├── 1984.txt
├── ...其他條目....
└── ...
```

- 檔名來自維基條目標題，經 `sanitize_filename` 處理後移除不合法字元並限制長度。
- 每個檔案內容為純文字，行與行之間以換行符號分隔。

---

## 重要設定與注意事項

### User-Agent

在 `crawl_pwn_wiki_plaintext.py` 中有自訂的 `User-Agent`：

```python
HEADERS = {
    "User-Agent": "PaiwanCorpusCrawler/1.0 (contact: your_email@example.com)"
}
```

建議你將 `your_email@example.com` 改成你自己的聯絡方式，以便在有需要時站方可以聯繫。

### 爬蟲禮節

- 程式在爬取索引頁與條目時會 `time.sleep(1)`，避免對伺服器造成過大負擔。
- 若要縮短或調整間隔，請務必遵守目標網站的使用條款與 `robots.txt`。

---

## 參數與延伸修改建議

目前主要參數集中在 `crawl_pwn_wiki_plaintext.py`：

- `BASE_URL`：目標維基站台主機。
- `START_INDEX_URL`：從哪一頁的「所有頁面」開始爬取。
- `output_dir`：在 `main()` 中預設為 `"outputs"`。

你可以依需求修改：

- 只爬特定命名空間的頁面。
- 篩選或排除某些類型條目。
- 調整輸出格式（例如：JSON、TSV 或加上 metadata）。

---

## 授權與資料使用

- 此程式僅為技術工具範例，實際爬取的維基內容受原站台授權條款約束（例如 Creative Commons 等）。
- 使用與散布爬取資料時，請遵守排灣語維基百科與 Wikimedia Foundation 的相關條款與授權規範。
