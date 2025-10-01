import sqlite3
import pandas as pd
import gradio as gr
import plotly.graph_objects as go

file_path = 'data/'
db_name = 'COVID-19.db'
connection = sqlite3.connect(f'{file_path}{db_name}')
sql = '''select * from daily_report'''
daily_report = pd.read_sql(sql=sql ,con = connection )

sql = '''select * from time_series'''
time_series = pd.read_sql(sql=sql ,con = connection )
connection.close()

# 氣泡地圖圖
# Scattermapbox -----------------------------------------------------------------------------
# 創建畫布
fig = go.Figure(
    go.Scattermapbox(lat=daily_report["latitude"],
                     lon=daily_report["longitude"],
                     mode="markers",
                     marker={"size": daily_report["confirmed"],
                             "color": daily_report["confirmed"],
                             "sizemin": 2,
                             "sizeref": daily_report["confirmed"].max()/2500, # 最大氣泡大小：數值越大氣泡越小，數值越小氣泡越大
                             "sizemode": "area"}
                    )
                )
# 更新畫布
fig.update_layout(mapbox_style="open-street-map",
                  mapbox=dict(zoom=2,
                              center=go.layout.mapbox.Center(
                              lat=0,  # 地圖中心點
                              lon=0), # 地圖中心點
                              )
                  )

# 布置到 gradio 中
with gr.Blocks() as demo:
    gr.Markdown("""# Covid 19 Global Map""") # 網頁名稱，沒有想是使用 Markdown 來顯示。
    gr.Plot(fig)

demo.launch()
demo.close()

# Scattermap -----------------------------------------------------------------------------
# Scattermapbox 即將淘汰，使用 Scattermap 取代。
def format_hover_row(df):
    """
    建立地圖 hover 提示字串。
    根據資料粒度決定不同格式：
    - county 有值 → 顯示 (country, province, county)
    - province 有值 → 顯示 (country, province)
    - 只剩 country → 顯示 country
    """
    if df.county != None:
        col = f"({df.country}, {df.province}, {df.county})"
    elif df["province"] != None:
        col = f"({df.country}, {df.province})"
    else :
        col = f"{df.country}"
    return f"Location: {col}<br>Confirmed: {df.confirmed}<br>Deaths: {df.deaths}"

daily_report["information_when_hovered"] = daily_report.apply(lambda x:format_hover_row(x), axis=1)

fig = go.Figure(
    go.Scattermap(
        lat=daily_report["latitude"],
        lon=daily_report["longitude"],
        customdata=daily_report['information_when_hovered'],
        hovertemplate="%{customdata}",
        mode="markers",
        marker=dict(
            size=daily_report["confirmed"],
            color=daily_report["confirmed"],
            sizemin=2,
            sizeref=max(daily_report["confirmed"].max(), 1) / 2500,
            sizemode="area"
        )
    )
)
fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                map=dict(
                        style="open-street-map",
                        center=dict(lat=23.7, lon=121),  # 地圖中心
                        zoom=2                           # 初始化地圖大小，越小放越大（0=整個地球）
                    ),
                )
# 布置到 gradio 中
with gr.Blocks() as demo:
    gr.Markdown("""# Covid 19 Global Map""") # 網頁名稱，沒有想是使用 Markdown 來顯示。
    gr.Plot(fig)

demo.launch()
demo.close()

# -----------------------------------------------------------------------------
# 折線圖
time_series = time_series[time_series["country"] == "Taiwan*"] # 抓取台灣資料
time_series["reported_on"] = pd.to_datetime(time_series["reported_on"])

with gr.Blocks() as demo:
    gr.Markdown("""# Covid 19 Country Time Series""")
    gr.LinePlot(time_series, x="reported_on", y="confirmed")
    gr.LinePlot(time_series, x="reported_on", y="deaths")
    gr.LinePlot(time_series, x="reported_on", y="doses_administered")

demo.launch()
demo.close()

