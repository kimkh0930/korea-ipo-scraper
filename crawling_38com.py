import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from enum import Enum

class DemandForcastColumn(Enum):
    IPO_AMOUNT = 0              #공모 규모
    COMPETITION_RATIO = 1       #기관 경쟁률
    COMMITMENT_RATIO = 2        #의무보유 확약 비율

class BiddingDateColumn(Enum):
    COMPANY_NAME = 0            #종목명
    SUB_START = 1               #공모 시작
    SUB_FINISH = 2              #공모 마감
    REFUND_DATE = 3             #환불일
    SHARE_PRICE_LOW = 4         #밴드 하단
    SHARE_PRICE_HIGH = 5        #밴드 상단
    OFFERING_PRICE = 6          #확정 공모가
    UNDERWRITER = 7             #주간사
    RATIO = 8                   #청약 경쟁률

class WebInfo:
    def __init__(self, page, table_summary):
        url = {
            '공모주 청약일정': 'http://www.38.co.kr/html/fund/index.htm?o=k&page=%s',
            '신규상장종목': 'http://www.38.co.kr/html/fund/index.htm?o=nw&page=%s',
            '수요예측결과': 'http://www.38.co.kr/html/fund/index.htm?o=r1&page=%s',
        }
        try:
            self._url = url[table_summary]
        except Exception as e:
            print(e)
            print("Wrong Table Summary")

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
        return filtered_tr_data

    def get_ipo_data_from_38com(self, page, when="before"):
        schedule_web_info = WebInfo(page, self._table_summary)
        temp_ipo_data_schedule = IpoData(schedule_web_info)
        total_row_data_schedule = temp_ipo_data_schedule.__get_filtered_tr_data()

        if self._table_summary == '공모주 청약일정':
            if when == 'before':
                total_data = get_bidding_date_before_table_info(total_row_data_schedule)
            else:
                total_data = get_bidding_date_after_table_info(total_row_data_schedule)
            return total_data

        elif self._table_summary == '신규상장종목':
            if when == 'before':
                total_data = get_ipo_before_data_table_info(total_row_data_schedule)
            else:
                total_data = get_ipo_after_data_table_info(total_row_data_schedule)
            return total_data

        elif self._table_summary == '수요예측결과':
            total_data = get_demand_forcast_result_table_info(total_row_data_schedule)
            return total_data

        else:
            print('Wrong Table Summary')
            return None

#공모청약일정 테이블 crawling : 청약 예정
def get_bidding_date_before_table_info(table_data):
    company_list = []                       #종목명
    subscription_start_list = []            #공모 시작
    subscription_finish_list = []           #공모 마감
    refund_date_list = []                   #환불일
    share_price_low_list = []               #밴드 하단(희망 공모가 하단)
    share_price_high_list = []              #밴드 상단(희망 공모가 상단)
    public_offering_price_list = []         #확정 공모가
    underwriter_list = []                   #주간사
    proportional_dist_ratio_list = []       #청약 경쟁률 -> 청약 끝나고 저잘할 때 씀.

    for i in range(0, len(table_data)):
        #청약 예정('#0066CC'), 청약 중인 종목('#E3231E')이 아니면 끝내기
        if not (table_data[i].find('font', attrs={'color': '#0066CC'})\
                or table_data[i].find('font', attrs={'color': '#E3231E'})):
            break
        else:
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

    bidding_date_before_info = pd.DataFrame({'종목명': company_list,
                                             '청약시작': subscription_start_list,
                                             '청약마감': subscription_start_list,
                                             '환불일': refund_date_list,
                                             '밴드하단': share_price_low_list,
                                             '밴드상단': share_price_high_list,
                                             '공모가': public_offering_price_list,
                                             '비례경쟁률': proportional_dist_ratio_list,
                                             '주간사': underwriter_list})
    print(bidding_date_before_info)

    return bidding_date_before_info[::-1] #역순으로 넣기

#공모청약일정 테이블 crawling : 청약 끝남(ipo 알림, 저장시 사용)
def get_bidding_date_after_table_info(table_data):
    company_list = []                       #종목명
    subscription_start_list = []            #공모 시작
    subscription_finish_list = []           #공모 마감
    refund_date_list = []                   #환불일
    share_price_low_list = []               #밴드 하단(희망 공모가 하단)
    share_price_high_list = []              #밴드 상단(희망 공모가 상단)
    public_offering_price_list = []         #확정 공모가
    underwriter_list = []                   #주간사
    proportional_dist_ratio_list = []       #청약 경쟁률 -> 청약 끝나고 저잘할 때 씀.

    for i in range(0, len(table_data)):
        #청약 예정, 청약 중인 종목들은 넘어가기
        if (table_data[i].find('font', attrs={'color': '#0066CC'})
                or table_data[i].find('font', attrs={'color': '#E3231E'})):
            continue
        else:
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

    bidding_date_after_info = pd.DataFrame({'종목명': company_list,
                                             '청약시작': subscription_start_list,
                                             '청약마감': subscription_start_list,
                                             '환불일': refund_date_list,
                                             '밴드하단': share_price_low_list,
                                             '밴드상단': share_price_high_list,
                                             '공모가': public_offering_price_list,
                                             '비례경쟁률': proportional_dist_ratio_list,
                                             '주간사': underwriter_list})
    print(bidding_date_after_info)

    return bidding_date_after_info[::-1] #역순으로 넣기

#신규상장 전 테이블 crawling : 날짜만 가져오면 됨
def get_ipo_before_data_table_info(table_data):
    ipo_date_dict = dict()

    for i in range(0, len(table_data)):
        if not (table_data[i].find('font', attrs={'color': '0066CC'}) \
                or table_data[i].find('font', attrs={'color': 'E3231E'})):
            break
        else:
            data_list = table_data[i].text.replace('\xa0', '').replace(" ", "").split('\n')[1:-1]
            company_name = data_list[0].replace('(유가)', '')
            ipo_date = str(datetime.strptime(data_list[1].strip(), '%Y/%m/%d')).replace('-', '.')[:10]

            ipo_date_dict[company_name] = ipo_date
    print(ipo_date_dict)

    return ipo_date_dict

#신규상장 후 테이블 crawling : ipo 후(저장시 사용 : storing)
def get_ipo_after_data_table_info(table_data):
    ipo_after_dict = dict()

    for i in range(0, len(table_data)):
        if (table_data[i].find('font', attrs={'color': '#0066CC'})
                or table_data[i].find('font', attrs={'color': '#E3231E'})):
            continue
        else:
            data_list = table_data[i].text.replace('\xa0', '').replace(" ", "").split('\n')[1:-1]
            company_name = data_list[0].replace('(유가)', '')# 기업명
            ipo_date = str(datetime.strptime(data_list[1].strip(), '%Y/%m/%d')).replace('-', '.')[:10]# 신규상장일

            # 시초가, 시초/공모 -> 상장 전에는 [-, %] 만 표시되어 있음
            try:
                opening_price_ratio = data_list[7]                                  # 시초가/공모가(비율)
                opening_price = int(data_list[6].replace(',', ''))                  # 시초가
            except:
                opening_price = int(data_list[6].replace('-', '0'))

            # TypeError: Object of type Timestamp/datetime is not JSON serializable -> type change to str

        ipo_after_dict[company_name] = [ipo_date, opening_price, opening_price_ratio]

    #print(ipo_after_dict)
    return ipo_after_dict

#수요예측결과 테이블 crawling
def get_demand_forcast_result_table_info(table_data):
    demand_forcast_result_dict = dict()

    for i in range(0, len(table_data)):
        data_list = table_data[i].text.replace('\xa0', '').replace(' ', '').split('\n')[1:-1]
        company_name = data_list[0].replace('(유가)', '')

        ipo_amount = round(int(data_list[4].strip().replace(',', ''))/100) #공모금액(규모)
        ipo_amount = (str(ipo_amount) + '억' if ipo_amount < 10000
                               else str(ipo_amount//1000) + '조' + str(ipo_amount%1000) + '억')

        competition_ratio = data_list[5].strip()                    #기관 경쟁률
        commitment_ratio = data_list[6].strip()                     #의무보유 확약 비율(기관)
        demand_forcast_result_dict[company_name] = [ipo_amount, competition_ratio, commitment_ratio]

    #print(demand_forcast_result_dict)
    return demand_forcast_result_dict