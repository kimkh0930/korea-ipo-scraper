import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class WebInfo:
    def __init__(self, url, page, table_summary):
        self._url = url
        self._page = page
        self._table_summary = table_summary

class IpoData(WebInfo):
    def get_ipo_data(self):
        total_row_data = []
        for pg in range(2, self._page+1):
            full_url = self._url % pg
            response = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            data = soup.find('table', {'summary': str(self._table_summary)})
            pg_row_data = data.find_all('tr')[2:]
            total_row_data += pg_row_data

        return total_row_data

def get_ipo_data_from_38com():
    schedule_web_info = WebInfo('http://www.38.co.kr/html/fund/index.htm?o=k&page=%s', 1, '공모주 청약일정')
    temp_ipo_data_schedule = IpoData(schedule_web_info._url, schedule_web_info._page, schedule_web_info._table_summary)
    total_row_data_schedule = temp_ipo_data_schedule.get_ipo_data()

    company_list = []
    subscription_start_list = []
    subscription_finish_list = []
    refund_date_list = []
    share_price_low_list = []
    share_price_high_list = []
    public_offering_price_list = []
    underwriter_list = []
    proportional_dist_ratio_list = []

    for i in range(0, len(total_row_data_schedule)):
        data_list = total_row_data_schedule[i].text.replace('\xa0', '').replace(" ", "").split('\n')[1:-1]
        underwriter = data_list[5].split(",")
        for j, uw in enumerate(underwriter):
            company_list.append(data_list[0].replace('(유가)', ''))

            sub_start_date = datetime.strptime(data_list[1][:10], '%Y.%m.%d')
            sub_fin_date = datetime.strptime(data_list[1][:5] + data_list[1][-5:], '%Y.%m.%d')
            refund_date = sub_fin_date + timedelta(days=4) if sub_fin_date.weekday() > 4 else sub_fin_date + timedelta(days=2)

            subscription_start_list.append(sub_start_date)
            subscription_finish_list.append(sub_fin_date)
            refund_date_list.append(refund_date)

            share_price_low_list.append(data_list[3].split("~")[0])
            share_price_high_list.append(data_list[3].split("~")[1])
            public_offering_price_list.append(data_list[2])
            underwriter_list.append(uw)
            proportional_dist_ratio_list.append(data_list[4])

    final = pd.DataFrame({'종목명': company_list,
                             '청약시작': subscription_start_list,
                             '청약마감': subscription_start_list,
                             '환불일': refund_date_list,
                             '밴드하단': share_price_low_list,
                             '밴드상단': share_price_high_list,
                             '공모가': public_offering_price_list,
                            '비례경쟁률': proportional_dist_ratio_list,
                          '주간사': underwriter_list})

    return final[::-1] #역순으로 넣기

#참고 : http://hleecaster.com/python-google-drive-spreadsheet-api/
def get_google_spreadsheet(sheet_name):
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    json_file_name = '/Users/jeonhyeongju/Documents/dev/utopian-rush-321203-e98a7a2d6d08.json'
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/16iCUpmBNQg24qCc3zi9qsK17OmwwtC4EkEUggaJpFJY/edit#gid=0'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
    gc = gspread.authorize(credentials)

    doc = gc.open_by_url(spreadsheet_url)

    return doc.worksheet(sheet_name)

def write_on_spreadsheet(spreadsheet, data):
    for row in data.to_numpy():
        newrow = [''] + row.tolist() + ['', ''] #신규 상장일, 기관 경쟁률 및 의무보유 확약 빈칸
        print(newrow)
        # TypeError: Object of type Timestamp is not JSON serializable
        newrow[2:5] = [newrow[2].to_pydatetime(), newrow[3].to_pydatetime(), newrow[4].to_pydatetime()]
        spreadsheet.append_row(newrow)

ipo_upcoming_data = get_ipo_data_from_38com()
ipo_spreadsheet = get_google_spreadsheet('ipo_participated')

write_on_spreadsheet(ipo_spreadsheet, ipo_upcoming_data)