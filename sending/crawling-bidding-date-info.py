import gspread
from crawling_38com import *

#청약 전날, 당일을 위한 데이터 추출

def main_function():
    page_to_crawl = 1
    # target_web_공모전 = WebInfo(page_to_crawl, '공모주 청약일정')
    # ipo_upcoming_data = IpoData.get_ipo_data_from_38com(target_web_공모전, page_to_crawl)
    # #
    # target_web_공모후 = WebInfo(page_to_crawl, '공모주 청약일정')
    # ipo_upcoming_data = IpoData.get_ipo_data_from_38com(target_web_공모후, page_to_crawl, 'after')
    # #
    # target_web_신규전 = WebInfo(page_to_crawl, '신규상장종목')
    # ipo_upcoming_data = IpoData.get_ipo_data_from_38com(target_web_신규전, page_to_crawl)
    #
    # target_web_신규후 = WebInfo(page_to_crawl, '신규상장종목')
    # ipo_upcoming_data = IpoData.get_ipo_data_from_38com(target_web_신규후, page_to_crawl, 'after')
    #
    # target_web_수요 = WebInfo(page_to_crawl, '수요예측결과')
    # ipo_upcoming_data = IpoData.get_ipo_data_from_38com(target_web_수요,
    # page_to_crawl)

    # today = datetime.now()
    # sub_start_day_before_list = []
    # sub_start_list = []
    # sub_fin_list = []
    # # refund_day_before_list = []
    # # refund_list = []
    # print(ipo_upcoming_data)
    #
    # for row in ipo_upcoming_data.to_numpy():
    #     sub_start = datetime.strptime(row[1], "%Y-%m-%d")
    #     sub_fin = datetime.strptime(row[2], "%Y-%m-%d")
    #     # refund_date = datetime.strptime(row[3], "%Y-%m-%d")
    #
    #     date_diff_sub_start = (today - sub_start).days
    #     date_diff_sub_fin = (today - sub_fin).days
    #     # date_diff_refund_date = (today - refund_date).days
    #
    #     #청약 시작일 : 공모가/주간사 같이 print          // 시작 전날, 당일 Alarm
    #     if date_diff_sub_start == -1:
    #         sub_start_day_before_list.append(row)
    #     elif date_diff_sub_start == 0:
    #         sub_start_list.append(row)
    #
    #     # 청약 마감일 : 공모가/주간사 같이 print          // 당일 Alarm
    #     elif date_diff_sub_fin == 0:
    #         sub_fin_list.append(row)
    #
    #     # #환불일 : 환불액(수수료 포함), 주간사 같이 print   // 전일, 당일 Alarm
    #     # elif date_diff_refund_date == -1:
    #     #     refund_day_before_list.append(row)
    #     # elif date_diff_refund_date == 0:
    #     #     refund_list.append(row)
    #     else:
    #         break
    #
    # print("1. 청약 시작 하루 전 종목😃")
    # print(sub_start_day_before_list)
    # print("-------------------")
    # print("!!청약 시작")
    # print(sub_start_list)
    # print("-------------------")
    # print("!!청약 마감")
    # print(sub_fin_list)
    # print("-------------------")
    # # print("!!청약 환불 전일")
    # # print(refund_day_before_list)
    # # print("-------------------")
    # # print("!!청약 환불일")
    # # print(refund_list)
    # # print("-------------------")

if __name__ == '__main__':
    main_function()