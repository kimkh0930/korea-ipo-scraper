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
    def __init__(self, WebInfo):
        self.web_info = WebInfo

    def __get_filtered_tr_data(self):
        full_url = self.web_info._url % self.web_info._page
        response = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        data = soup.find('table', {'summary': str(self.web_info._table_summary)})
        filtered_tr_data = data.find_all('tr')[2:]
        #print(filtered_tr_data)
        return filtered_tr_data

    def get_ipo_data_from_38com(self, page):
        schedule_web_info = WebInfo(self._url, page, self._table_summary)
        temp_ipo_data_schedule = IpoData(schedule_web_info)
        total_row_data_schedule = temp_ipo_data_schedule.__get_filtered_tr_data()

        get_table_info = {
            '공모주 청약일정': get_bidding_date_table_info(total_row_data_schedule),
            '신규상장종목': get_ipo_date_table_info(total_row_data_schedule),
            '수요예측결과': get_demand_forcast_result_table_info(total_row_data_schedule),
        }
        try:
            total_data = get_table_info[self._table_summary]
            return total_data
        except Exception as e:
            print(e)
            print("Wrong Table Summary")
            return None

#공모청약일정 테이블 crawling
def get_bidding_date_table_info(table_data):
    company_list = []
    subscription_start_list = []
    subscription_finish_list = []
    refund_date_list = []
    share_price_low_list = []
    share_price_high_list = []
    public_offering_price_list = []
    underwriter_list = []
    proportional_dist_ratio_list = []

    for i in range(0, len(table_data)):
        data_list = table_data[i].text.replace('\xa0', '').replace(" ", "").split('\n')[1:-1]
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

    bidding_date_info = pd.DataFrame({'종목명': company_list,
                             '청약시작': subscription_start_list,
                             '청약마감': subscription_start_list,
                             '환불일': refund_date_list,
                             '밴드하단': share_price_low_list,
                             '밴드상단': share_price_high_list,
                             '공모가': public_offering_price_list,
                            '비례경쟁률': proportional_dist_ratio_list,
                          '주간사': underwriter_list})

    return bidding_date_info[::-1] #역순으로 넣기

#신규상장 테이블 crawling
def get_ipo_date_table_info(table_data):
    company_list = []
    subscription_start_list = []
    subscription_finish_list = []
    refund_date_list = []
    share_price_low_list = []
    share_price_high_list = []
    public_offering_price_list = []
    underwriter_list = []
    proportional_dist_ratio_list = []

    for i in range(0, len(table_data)):
        data_list = table_data[i].text.replace('\xa0', '').replace(" ", "").split('\n')[1:-1]
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

    bidding_date_info = pd.DataFrame({'종목명': company_list,
                             '청약시작': subscription_start_list,
                             '청약마감': subscription_start_list,
                             '환불일': refund_date_list,
                             '밴드하단': share_price_low_list,
                             '밴드상단': share_price_high_list,
                             '공모가': public_offering_price_list,
                            '비례경쟁률': proportional_dist_ratio_list,
                          '주간사': underwriter_list})

    return bidding_date_info[::-1] #역순으로 넣기

#수요예측결과 테이블 crawling
def get_demand_forcast_result_table_info(table_data):
    company_list = []
    subscription_start_list = []
    subscription_finish_list = []
    refund_date_list = []
    share_price_low_list = []
    share_price_high_list = []
    public_offering_price_list = []
    underwriter_list = []
    proportional_dist_ratio_list = []

    for i in range(0, len(table_data)):
        data_list = table_data[i].text.replace('\xa0', '').replace(" ", "").split('\n')[1:-1]
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

    bidding_date_info = pd.DataFrame({'종목명': company_list,
                             '청약시작': subscription_start_list,
                             '청약마감': subscription_start_list,
                             '환불일': refund_date_list,
                             '밴드하단': share_price_low_list,
                             '밴드상단': share_price_high_list,
                             '공모가': public_offering_price_list,
                            '비례경쟁률': proportional_dist_ratio_list,
                          '주간사': underwriter_list})

    return bidding_date_info[::-1] #역순으로 넣기