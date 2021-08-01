import requests
import pandas as pd
import gspread
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

class WebInfo:
    def __init__(self, url, page, table_summary):
        self._url = url
        self._page = page
        self._table_summary = table_summary

class IpoData(WebInfo):
    def get_ipo_data(self):
        full_url = self._url % self._page
        response = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        data = soup.find('table', {'summary': str(self._table_summary)})
        pg_row_data = data.find_all('tr')[2:]

        return pg_row_data

def get_ipo_data_from_38com(url, page, summary):
    schedule_web_info = WebInfo(url, page, summary)
    temp_ipo_data_schedule = IpoData(schedule_web_info._url, schedule_web_info._page, schedule_web_info._table_summary)
    total_row_data_schedule = temp_ipo_data_schedule.get_ipo_data()

    #print(total_row_data_schedule)

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
        if not total_row_data_schedule[i].find('font', attrs={'color': '#0066CC'}):
            break

        data_list = total_row_data_schedule[i].text.replace('\xa0', '').replace(" ", "").split('\n')[1:-1]
        underwriter = data_list[5].split(",")
        for j, uw in enumerate(underwriter):
            company_list.append(data_list[0].replace('(유가)', ''))

            sub_start_date = str(datetime.strptime(data_list[1][:10], '%Y.%m.%d'))[0:10]
            sub_fin_date = datetime.strptime(data_list[1][:5] + data_list[1][-5:], '%Y.%m.%d')
            refund_date = sub_fin_date + timedelta(days=4) if sub_fin_date.weekday() > 4 else sub_fin_date + timedelta(days=2)

            # TypeError: Object of type Timestamp/datetime is not JSON serializable -> type change to str
            sub_fin_date = (str(sub_fin_date))[0:10]
            refund_date = str(refund_date)[0:10]

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
                             '청약마감': subscription_finish_list,
                             '환불일': refund_date_list,
                             '밴드하단': share_price_low_list,
                             '밴드상단': share_price_high_list,
                             '공모가': public_offering_price_list,
                            '비례경쟁률': proportional_dist_ratio_list,
                          '주간사': underwriter_list})

    return final[::-1] #역순으로 넣기

def main_function():
    target_url = 'http://www.38.co.kr/html/fund/index.htm?o=k&page=%s'
    page_to_crawl = 1
    target_table_summary = '공모주 청약일정'
    target_web = WebInfo(target_url, page_to_crawl, target_table_summary)

    ipo_upcoming_data = get_ipo_data_from_38com(target_web._url, page_to_crawl, target_web._table_summary)

    today = datetime.now()
    sub_start_day_before_list = []
    sub_start_list = []
    sub_fin_list = []
    # refund_day_before_list = []
    # refund_list = []

    for row in ipo_upcoming_data.to_numpy():
        sub_start = datetime.strptime(row[1], "%Y-%m-%d")
        sub_fin = datetime.strptime(row[2], "%Y-%m-%d")
        # refund_date = datetime.strptime(row[3], "%Y-%m-%d")

        date_diff_sub_start = (today - sub_start).days
        date_diff_sub_fin = (today - sub_fin).days
        # date_diff_refund_date = (today - refund_date).days


        #청약 시작일 : 공모가/주간사 같이 print          // 시작 전날, 당일 Alarm
        if date_diff_sub_start == -1:
            sub_start_day_before_list.append(row)
        elif date_diff_sub_start == 0:
            sub_start_list.append(row)

        # 청약 마감일 : 공모가/주간사 같이 print          // 당일 Alarm
        elif date_diff_sub_fin == 0:
            sub_fin_list.append(row)

        # #환불일 : 환불액(수수료 포함), 주간사 같이 print   // 전일, 당일 Alarm
        # elif date_diff_refund_date == -1:
        #     refund_day_before_list.append(row)
        # elif date_diff_refund_date == 0:
        #     refund_list.append(row)
        else:
            break

    print("!!청약 시작 하루전")
    print(sub_start_day_before_list)
    print("-------------------")
    print("!!청약 시작")
    print(sub_start_list)
    print("-------------------")
    print("!!청약 마감")
    print(sub_fin_list)
    print("-------------------")
    # print("!!청약 환불 전일")
    # print(refund_day_before_list)
    # print("-------------------")
    # print("!!청약 환불일")
    # print(refund_list)
    # print("-------------------")

if __name__ == '__main__':
    main_function()