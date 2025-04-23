# 📈 ETF Data Aggregator — Scraper & Google Sheets Sync

This project automates the **collection and aggregation of ETF data** from multiple financial data sources and uploads it into a centralized **Google Sheet** for personal investment analysis.

---

## 🔍 Overview

This tool performs the following tasks:

1. **Scrapes ETF data** from:
   - 🟡 [JustETF](https://www.justetf.com/)
   - 🔵 [ETFdb](https://etfdb.com/)
   - 🔧 [Investing.com API]
2. **Cleans, merges, and normalizes** data across sources
3. **Exports final dataset** to a connected **Google Spreadsheet**

---

## 🛠️ Tech Stack

- **Python**
  - `requests`, `BeautifulSoup` — for scraping
  - `pandas` — for data handling
  - `gspread`, `oauth2client` — for Google Sheets API integration
  - `json`, `datetime`, etc.

---

## 🧰 Features

- ✅ Multi-source ETF data scraping (tickers, assets, performance, TER, categories)
- ✅ Data cleaning and normalization
- ✅ Export to **Google Sheets**
- ✅ Easily customizable ETF watchlist
- ✅ API fallback and error handling

---

## 📁 Project Structure

```
├── invest_etf_project.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Google Sheets API:
   - Create a project at [console.cloud.google.com](https://console.cloud.google.com)
   - Enable **Google Sheets API**
   - Create and download a **service account key** (JSON)
4. Share your Google Sheet with the service account email
5. Make sure your ETF tickers are already listed in the first column of the target Google Sheet
6. Run the script:
   ```bash
   python src/main.py
   ```

---

## 📊 Use Case

Monitor a custom ETF watchlist (e.g. thematic, regional, sector-based funds) in near real-time by consolidating data from multiple trusted sources into a single Google Sheet.

---

## 📄 License

MIT License — Free to use and modify for personal and research purposes.

---

## ✉️ Contact

Developed by **Kirill Palenov**  
📧 kirill.palenov[at]gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/kirillpalenov)
