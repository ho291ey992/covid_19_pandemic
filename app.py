import sqlite3
import pandas as pd
import gradio as gr
import plotly.graph_objects as go

class Covid19():
    def __init__(self, file_part):
        connection = sqlite3.connect(f"{file_part}")
        sql = """select * from daily_report"""
        self.daily_report = pd.read_sql(sql=sql ,con = connection )

        sql = """select * from time_series"""
        self.time_series = pd.read_sql(sql=sql ,con = connection )
        connection.close()

    def format_hover_row(self, df):
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

    # 地圖繪製
    def filter_global_map(self, country_names):
        filtered_daily_report = self.daily_report[self.daily_report["country"].isin(country_names)]

        fig = go.Figure(
            # Scattermapbox 即將淘汰，使用 Scattermap 取代。
            go.Scattermap(
                lat=filtered_daily_report["latitude"],
                lon=filtered_daily_report["longitude"],
                customdata=filtered_daily_report['information_when_hovered'],
                hovertemplate="%{customdata}",
                mode="markers",
                marker=dict(
                    size=filtered_daily_report["confirmed"],
                    color=filtered_daily_report["confirmed"],
                    sizemin=2,
                    sizeref=max(filtered_daily_report["confirmed"].max(), 1) / 2500,
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
        return fig
    
    # 地圖網頁
    def global_map_page(self):
        time_series_global_map = self.time_series[self.time_series["reported_on"] == "2023-03-09"]
        total_confirmed = time_series_global_map["confirmed"].sum() # 確診數
        total_deaths = time_series_global_map["deaths"].sum() # 死亡數
        total_doses_administered = time_series_global_map["doses_administered"].sum() # 疫苗數

        sum_confirmed_by_country = self.daily_report.groupby(by="country")["confirmed"].sum().sort_values(ascending=False).reset_index()
        top_confirmed = sum_confirmed_by_country.loc[:30, "country"].tolist() # 排名前 30 國家

        self.time_series["reported_on"] = pd.to_datetime(self.time_series["reported_on"])
        self.daily_report["information_when_hovered"] = self.daily_report.apply(lambda x:self.format_hover_row(x), axis=1)

        with gr.Blocks() as global_map_tab:
            gr.Markdown("""# Covid 19 Global Map""") 
            with gr.Row():
                gr.Label(value=f"{total_confirmed:,}", label="Total cases")
                gr.Label(value=f"{total_deaths:,}", label="Total deaths")
                gr.Label(value=f"{total_doses_administered:,}", label="Total doses administered")

            with gr.Column():
                countries = gr.Dropdown(choices=self.daily_report["country"].drop_duplicates().tolist(),
                                        label="Select countries:",
                                        multiselect=True,
                                        value=top_confirmed)
                btn = gr.Button(value="Update")
            global_map = gr.Plot()
            global_map_tab.load(fn=self.filter_global_map,
                    inputs=countries,
                    outputs=global_map)
            btn.click(fn=self.filter_global_map,
                    inputs=countries,
                    outputs=global_map)
        print("global_map_page pass")
        return global_map_tab

    # 折線圖網頁
    def country_time_series_page(self):
        with gr.Blocks() as country_time_series_tab:
            gr.Markdown("""# Covid 19 Country Time Series""")
            with gr.Row():
                country = gr.Dropdown(choices=self.time_series["country"].unique().tolist(),
                            label="Select countries:",
                            value="Taiwan*")
            total_confimed = gr.LinePlot(self.time_series.head(), x="reported_on", y="confirmed")
            total_deaths = gr.LinePlot(self.time_series.head(), x="reported_on", y="deaths")
            total_doses_administered = gr.LinePlot(self.time_series.head(), x="reported_on", y="doses_administered")

            # 監聽使用者互動事件（像是你切換 Dropdown）。 
            # 在 5.x 新版 Gradio 元件會初始值 (value) 直接觸發綁定的函數（@gr.on），第一次載入頁面會自動觸發 @gr.on，所以即使沒有 country_time_series_tab.load 折線圖也能正常顯示。
            # @gr.on 是個 decorator，它會把「下面定義的函數」自動註冊到這些 input/output 元件上。
            @gr.on(inputs=country, outputs=total_confimed)
            @gr.on(inputs=country, outputs=total_deaths)
            @gr.on(inputs=country, outputs=total_doses_administered)
            def filter_country(country):
                select_country_df = self.time_series[self.time_series["country"] == country]
                return select_country_df
        
        print("country_time_series_page pass")
        return country_time_series_tab

    # 合併、啟動網頁
    def create_web(self):
        self.demo = gr.TabbedInterface([self.global_map_page(), self.country_time_series_page()], 
                                       ["Global Map", "Country Time Series"])
        self.demo.launch()

    # 關閉網頁
    def close_web(self):
        self.demo.close()

file_path = "練習專案五：大疫世代/covid_19_pandemic/data/COVID_19.db"
covid_19 = Covid19(file_path)
covid_19.create_web()
covid_19.close_web()
