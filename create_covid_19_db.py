import pandas as pd
import sqlite3

class CreateCovid19DB():
    def __init__(self, file_path, db_name):
        self.file_path = file_path
        self.db_name = db_name
        # 每日報告
        self.daily_report = pd.read_csv(f'{file_path}03-09-2023.csv')
        # 確診
        self.confirmed = pd.read_csv(f'{file_path}time_series_covid19_confirmed_global.csv')
        # 疫苗
        self.vaccine = pd.read_csv(f'{file_path}time_series_covid19_vaccine_global.csv')
        # 死亡人數
        self.deaths = pd.read_csv(f'{file_path}time_series_covid19_deaths_global.csv')
    
    def create_time_series(self):
        # 合併 time_series 資料
        # 寬轉長
        melt_list = ['Province/State', 'Country/Region', 'Lat', 'Long']
        confirmed = self.confirmed.melt(id_vars=melt_list, var_name='date', value_name='Confirmed')
        deaths = self.deaths.melt(id_vars=melt_list, var_name='date', value_name='Death')

        # 調整欄位一致性
        confirmed = confirmed.rename(columns={'date':'Date'})
        deaths = deaths.rename(columns={'date':'Date'})
        vaccine = self.vaccine.rename(columns={'Province_State':'Province/State', 'Country_Region':'Country/Region'})
        vaccine['Province/State'] = vaccine['Province/State'].astype('object')

        # 轉換格式日期：重點 pd.to_datetime 看不懂需要補充(format=)
        confirmed['Date'] = pd.to_datetime(confirmed['Date'], format='%m/%d/%y') 
        deaths['Date'] = pd.to_datetime(deaths['Date'], format='%m/%d/%y')
        vaccine['Date'] = pd.to_datetime(vaccine['Date'])

        # 清除多餘欄位
        confirmed = confirmed.drop(columns=['Lat', 'Long'])
        deaths = deaths.drop(columns=['Lat', 'Long'])
        vaccine = vaccine.drop(columns=['UID', 'People_at_least_one_dose'])

        # 合併
        join_keys = ['Province/State', 'Country/Region', 'Date']
        time_series = confirmed.merge(deaths, left_on=join_keys, right_on=join_keys, how='left')
        time_series = time_series.merge(vaccine, left_on=join_keys, right_on=join_keys, how='left')
        time_series = time_series.groupby(['Country/Region', 'Date'])[['Confirmed',  'Death',  'Doses_admin']].sum().reset_index()
        time_series['Doses_admin'] = time_series['Doses_admin'].astype('int64')
        time_series.columns = ['country', 'reported_on', 'confirmed', 'deaths', 'doses_administered']
        print('create_time_series pass')
        return time_series
    
    def create_daily_report(self):
        # 處理每日資料 03-09-2023.csv
        # 清除多餘欄位、調整欄位位置和名稱。
        daily_report = self.daily_report[['Country_Region', 'Province_State', 'Admin2', 'Confirmed', 'Deaths','Lat', 'Long_']]
        daily_report.columns = ['country', 'province', 'county', 'confirmed', 'deaths', 'latitude', 'longitude']
        print('create_daily_report pass')
        return daily_report
    
    def create_database(self):
        # 載入資料
        time_series = self.create_time_series()
        daily_report = self.create_daily_report()

        # 日期只想要保留文字部分
        time_series['reported_on'] = time_series['reported_on'].dt.strftime('%Y-%m-%d')
        
        # 新增 SQLite.db
        connection = sqlite3.connect(f'{self.file_path}{self.db_name}')
        time_series.to_sql('time_series', con=connection, if_exists='replace', index=False)
        daily_report.to_sql('daily_report', con=connection, if_exists='replace', index=False)
        connection.close()
        print('create_database pass')

file_path = '練習專案五：大疫世代/covid_19_pandemic/data/'
db_name = 'COVID_19.db'
covide_db = CreateCovid19DB(file_path, db_name)
covide_db.create_database()
