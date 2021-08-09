from crawling_38com import *

#청약 전날, 당일을 위한 데이터 추출
def main_function():
    page_to_crawl = 1
    target_web_bidding_before = WebInfo(page_to_crawl, '공모주 청약일정')
    bidding_date_before_data = IpoData.get_ipo_data_from_38com(target_web_bidding_before, page_to_crawl)

    target_web_demand = WebInfo(page_to_crawl, '수요예측결과')
    demand_forcast_dict = IpoData.get_ipo_data_from_38com(target_web_demand, page_to_crawl)

    sub_start_tomorrow_list = []
    sub_start_list = []
    sub_fin_list = []

    today = datetime.now()

    for row in bidding_date_before_data.to_numpy():
        row = list(row)
        try:
            row = row + demand_forcast_dict[row[BiddingDateColumn.COMPANY_NAME.value]]
        except KeyError as e:
            #청약 전날, 당일, 마감일이 아닐 경우 -> 수요예측 곌과가 없어서 dictionary에 key, value 없음
            break

        sub_start = datetime.strptime(row[1], "%Y-%m-%d")
        sub_fin = datetime.strptime(row[2], "%Y-%m-%d")

        date_diff_sub_start = (today - sub_start).days
        date_diff_sub_fin = (today - sub_fin).days

        # 청약 시작일 : 공모가/주간사 같이 print          // 시작 전날, 당일 Alarm
        if date_diff_sub_start == -1:
            sub_start_tomorrow_list.append(row)
        elif date_diff_sub_start == 0:
            sub_start_list.append(row)

        # 청약 마감일 : 공모가/주간사 같이 print          // 당일 Alarm
        elif date_diff_sub_fin == 0:
            sub_fin_list.append(row)

        else:
            #위에서 끝나겠지만, 확실하게 한번 더 break문 적어둠.
            break

    print("1. 청약 시작 하루 전 종목😃")
    for _, row in enumerate(sub_start_tomorrow_list):
        print(f'종목명 :{row[BiddingDateColumn.COMPANY_NAME.value]} / '
              f'청약 시작일, 종료일 : {row[BiddingDateColumn.SUB_START.value]}, {row[BiddingDateColumn.SUB_FINISH.value]}')
    print("-------------------")

    print("2. 청약 시작😃")
    for _, row in enumerate(sub_start_list):
        print(f'<{(_+1)}>. 종목명 : {row[BiddingDateColumn.COMPANY_NAME.value]} // '
              f'(청약 시작일, 종료일) : ({row[BiddingDateColumn.SUB_START.value]}, {row[BiddingDateColumn.SUB_FINISH.value]}) // '
              f'환불일 : {row[BiddingDateColumn.REFUND_DATE.value]}')
        print(f'     공모가 : {row[BiddingDateColumn.OFFERING_PRICE.value]} (밴드 범위 : {row[BiddingDateColumn.SHARE_PRICE_LOW.value]}~{row[BiddingDateColumn.SHARE_PRICE_HIGH.value]})')
        print(f'     주간사 : {row[BiddingDateColumn.UNDERWRITER.value]}')
        #8 -> 보기좋게 수정 예정
        print(f'     공모 규모 : {row[8+DemandForcastColumn.IPO_AMOUNT.value]}')
        print(f'     기관 경쟁률 : {row[8+DemandForcastColumn.COMPETITION_RATIO.value]}, 의무보유 확약 비율 : {row[8+DemandForcastColumn.COMMITMENT_RATIO.value]}')
        print()
    print("-------------------")

    print("3. 청약 마감😃")
    print(sub_fin_list)
    print("-------------------")


if __name__ == '__main__':
    main_function()