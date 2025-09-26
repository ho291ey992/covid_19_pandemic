# 練習專案五：大疫世代

## 簡介

這個專案「大疫世代」透過 CSSE at Johns Hopkins University [csse_covid_19_data](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data) 提供 2020-01-22 至 2023-03-09 的每日報告與時間序列資料製作出了頁籤式疫情儀表板。我們使用了 `pandas` 與 `sqlite3` 建立了資料庫，利用 `gradio` 進行概念驗證並做出成品。可以透過 Hugging Face Spaces 的連結：<https://huggingface.co/spaces/Yao-Jen/covid_19_pandemic> 參考成品。

## 如何重現

- 安裝 [Miniconda](https://docs.anaconda.com/miniconda)
- 依據 `environment.yml` 建立環境：

```bash
conda env create -f environment.yml
```

- 將 `data/` 資料夾中的 4 個 CSV 檔案：`03-09-2023.csv`、`time_series_covid19_confirmed_global.csv`、`time_series_covid19_deaths_global.csv` 與 `time_series_covid19_vaccine_global.csv` 放置於專案資料夾的 `data/` 資料夾中
- 啟動環境並執行 `python create_covid_19_db.py` 就能在 `data/` 資料夾中建立 `covid_19.db`
- 啟動環境並執行 `python app.py` 並前往 `http://127.0.0.1:7860` 瀏覽成品。
