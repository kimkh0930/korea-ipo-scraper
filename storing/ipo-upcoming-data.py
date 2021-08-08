import requests
import pandas as pd
import gspread
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from crawling_38com import *

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
        spreadsheet.append_row(newrow)

def main_function():
    target_url = 'http://www.38.co.kr/html/fund/index.htm?o=k&page=%s'
    page_to_crawl = 3
    target_table_summary = '공모주 청약일정'
    target_web = WebInfo(page_to_crawl, target_table_summary)

    for page in range(target_web._page, 0, -1):
        ipo_upcoming_data = IpoData.get_ipo_data_from_38com(target_web, page)
        # print("'{}' 탭의 page {}에 대한 정보".format(target_web._table_summary, page))
        print(ipo_upcoming_data)
        #ipo_spreadsheet = get_google_spreadsheet('ipo_participated')
        #write_on_spreadsheet(ipo_spreadsheet, ipo_upcoming_data)

        #Allowed read & write requests per min : 60 requests
        #time.sleep(60)

if __name__ == '__main__':
    main_function()