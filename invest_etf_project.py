# Подключаем библиотеки
import httplib2 
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials	
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import investpy
import requests
from lxml import html
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import traceback
import time
import os

CREDENTIALS_FILE = os.environ['credentials_file_path']  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = os.environ['spreadsheet_id'] 
SAMPLE_RANGE_NAME = 'Data!A2:E8'

xpath = {
    'US' : {
    'Name' : '//h1[@class="data-title"]/text()[2]',
    'Provider' : '//div[./span[text()="Issuer"]]/span[not(text()="Issuer")]/a/text()',
    'Index tracked':'//div[./span[text()="Index Tracked"]]/span[not(text()="Index Tracked")]/a/text()',
    'Category' : '//div[./span[text()="Category"]]//a/text()',
    'Country_General' : '//div[./span[text()="Region (General)"]]//a/text()',
    'Country' : '//div[./span[text()="Region (Specific)"]]//a/text()',
    'Focus_General' : '//div[./span[text()="Sector (General)"]]//a/text()',
    'Focus' : '//div[./span[text()="Sector (Specific)"]]//a/text()',
    'Bond Type_General':'//li[./span[text()="Bond Type(s)"]]/span[@class="pull-right"]/a/text()',
    'Bond Type':'//li[./span[text()="Bond Type(s)"]]/span[@class="pull-right"]/a/text()',
    'Expense ratio' : '//div[./span[text()="Expense Ratio"]]/span[not(text()="Expense Ratio")]/text()',
    'P/E':'//div[./div[text()="~value~"] and ./div[text()="P/E Ratio"]]/div[@class="text-center" and not(text()="P/E Ratio")]/text()',
    'Dividend Yield' : '//tr[./td[contains(text(),"Annual Dividend Yield")]]/td[@data-th="Fund"]/text()',
    'AUM Currency':'//li[./span[text()="AUM"]]/span[not(@class="pull-right")]/text()',
    'Total Assets' : '//li[./span[text()="AUM"]]/span[@class="pull-right"]/text()',
    'Prev. Close' : '//span[@id="stock_price_value"]/text()',
    'Low 52w' : '//li[./span[text()="52 Week Lo"]]/span[@class="pull-right"]/text()',
    'High 52w' : '//li[./span[text()="52 Week Hi"]]/span[@class="pull-right"]/text()',
    '1-Month Change':'//tr[./td[contains(text(),"1 Month Return")]]/td[2]/text()',
    '3-Month Change':'//tr[./td[contains(text(),"3 Month Return")]]/td[2]/text()',
    #'6-Month Change':'//div[@class="row"]//div[not(contains(@class,"relative")) and ./div[contains(text(),"26 Week Return")]]//span/text()',
    '1-Year Change' : '//tr[./td[contains(text(),"1 Year Return")]]/td[2]/text()',
    '3-Year Change' : '//tr[./td[contains(text(),"3 Year Return")]]/td[2]/text()'
    },
    'EU': {
    'Name' : '//h1/span[@class="h1"]/text()',
    'Domicile':'//div[./div[contains(text(),"Dividend/ Taxes")]]//table//tr[./td[@class="vallabel" and contains(text(),"Fund domicile")]]/td[@class="val"]/text()',
    'Distribution Policy':'//div[./div[contains(text(),"Dividend/ Taxes")]]//table//tr[./td[@class="vallabel" and contains(text(),"Distribution policy")]]/td[@class="val"]/text()',
    'Provider' : '//div[./div[contains(text(),"Legal structure")]]//table//tr[./td[@class="vallabel" and contains(text(),"Fund Provider")]]/td[@class="val2"]',
    'Category':'//div[./div[contains(text(),"Risk")]]//table//tr[./td[@class="vallabel" and contains(text(),"Strategy risk")]]/td[@class="val2"]/text()',
    'Expense ratio':'//div[./div[contains(text(),"Fees")]]/div[@class="infobox"]//div[@class="val"]/text()',
    'Dividend Yield':'//div[contains(@class,"moduleWithBottomBorder")]/div[contains(@class,"module keyStatistics")]//div[contains(@class,"rowListItemWrap") and .//span[text()="Dividend Indicated Gross Yield"]]//span[contains(@class,"fieldValue")]',
    'AUM Currency':'//div[./div[contains(text(),"Risk")]]/div[@class="infobox"]//div[@class="val"]/text()',
    'Total Assets':'//div[./div[contains(text(),"Risk")]]/div[@class="infobox"]//div[@class="val"]/text()',
    'Prev. Close':'//div[./div[contains(text(),"Quote")]]/div[@class="infobox"]//div[@class="val"]/span[2]/text()',
    'Currency':'//div[./div[contains(text(),"Quote")]]/div[@class="infobox"]//div[@class="val"]/span[1]/text()',
    'Low 52w':'//li[@class="Summary-stat" and ./span[@class="Summary-label" and text()="52 Week Low"]]/span[@class="Summary-value"]/text()',
    'High 52w':'//li[@class="Summary-stat" and ./span[@class="Summary-label" and text()="52 Week High"]]/span[@class="Summary-value"]/text()',
    '1-Month Change':'//div[./div[@class="row"]//h3[contains(text(),"Return")]]//table[2]/tbody/tr/td[1]/text()',
    '3-Month Change':'//div[./div[@class="row"]//h3[contains(text(),"Return")]]//table[2]/tbody/tr/td[2]/text()',
    '6-Month Change':'//div[./div[@class="row"]//h3[contains(text(),"Return")]]//table[2]/tbody/tr/td[3]/text()',
    '1-Year Change':'//div[./div[@class="row"]//h3[contains(text(),"Return")]]//table[2]/tbody/tr/td[4]/text()',
    '3-Year Change':'//div[./div[@class="row"]//h3[contains(text(),"Return")]]//table[2]/tbody/tr/td[5]/text()'
        }
    }
        
countries = {'france':'^-FR', 'italy':'^-IT', 'netherlands':'^-NL','germany':'-DE'}

def get_xpath(region, column, value):
    return xpath[region][column].replace('~value~',value)

def get_tree(trees,column):
    try:
        return trees[column]
    except KeyError:
        return trees['main']

def get_value_from_html(trees, region, column, value = ''):
    #content = html.parse(link)
    tree = get_tree(trees, column)
    if tree == None:
        return
    val = tree.xpath(get_xpath(region,column,value))
    if val == None or val == []:
        return None
    return val[0]
    

def set_value(df, index, column, info, trees, region):
    try:
        if info != None:
            val = info[column]
        else:
            val = None
    except KeyError:
        val = None
    if val == None:
        val = get_value_from_html(trees, region, column, df.loc[index]['Ticker'])
    if val != None:
        if isinstance(val, str):
            try:
                if '%' in val:
                    val = float(val.replace('%','').replace('p.a.','')) / 100
                elif 'm' in val.lower():
                    val = float(val.lower().replace('m','').replace('$','').replace('\n','').replace('eur','').replace(',','').strip()) * 1000000
                else:
                    val = float(val.replace('$',''))
            except ValueError:
                val = val.replace('\n','')
        df.at[index,column] = val

def get_change(df, search, index, column, period, trees, region, investing_com_found):
    date_n_ago = datetime.now() - period
    try:
        if not investing_com_found:
            raise IndexError
        hist = search.retrieve_historical_data(date_n_ago.strftime("%d/%m/%Y"), (date_n_ago + timedelta(days=1)).strftime("%d/%m/%Y"))
        df.at[index,column] = (search.information['prevClose'] - hist.iloc[0]['Close']) / hist.iloc[0]['Close']
    except IndexError:
        set_value(df,index,column,None,trees,region)
    except ConnectionError:
        set_value(df,index,column,None,trees,region)

def set_value_from_html(df, index, column, trees, region):
    try:
        if df.at[index,column] == '':
            df.at[index,column] = get_value_from_html(trees, region, column).replace('\n','')
        return df.at[index,column]
    except Exception:
            pass

def fill_etf(df, index, ticker, country):
    try:
        search_results = investpy.search.search_quotes(ticker, products=['etfs'], countries=[country])
        if len(search_results)==0:
            raise RuntimeError
        search = search_results[0]
        info = search.retrieve_information()
        df.at[index, 'Name'] = search.name
        df.at[index,'Investing.com'] = 'https://www.investing.com' + search.tag
        investing_com_found = True
    except Exception as e:
        search = None
        info = None
        investing_com_found = False
    trees  = {}
    if country.lower() == 'united states':
        link = 'https://etfdb.com/etf/' + ticker
        trees['main'] = html.fromstring(requests.get(link).text)
        region = 'US'
        if not investing_com_found:
            set_value_from_html(df,index,'Name', trees,region)
        set_value_from_html(df,index,'Category',trees,region)
        df.at[index,'Distribution Policy'] = 'Distributing'
        if df.at[index,'Category'] == 'High Yield Bonds':
            type = 'Bond Type'
        else:
            type = 'Focus'
        if set_value_from_html(df,index,'Country',trees,region) == 'Broad':
            df.at[index,'Country'] = get_value_from_html(trees, region, 'Country_General')
        if set_value_from_html(df,index,type,trees,region) == 'Broad':
            df.at[index,'Focus'] = get_value_from_html(trees, region, type + '_General')
        pe = df.at[index,'P/E']
        set_value(df,index,'P/E',info,trees,region)
        if df.at[index,'P/E'] == 'No Ranking Available':
            df.at[index,'P/E'] = pe
        set_value_from_html(df, index, 'Index tracked', trees, region)
    else:
        link = 'https://www.justetf.com/etf-profile.html?isin=' + df.at[index,'ISIN']
        trees['main'] = html.fromstring(requests.get(link).text)
        region = 'EU'
        if not investing_com_found:
            set_value_from_html(df,index,'Name', trees,region)
        #set_value_from_html(df,index,'Distribution Policy',trees,region)
        cnbc = html.fromstring(requests.get('https://www.cnbc.com/quotes/' + ticker + countries[country.lower()]).text)
        get_change(df,search,index,'6-Month Change',relativedelta(months=6),trees,region,investing_com_found)
        trees['Low 52w'] = cnbc
        trees['High 52w'] = cnbc
        if df.at[index,'Distribution Policy'] == 'Distributing':
            trees['Dividend Yield'] = cnbc
        else:
            trees['Dividend Yield'] = None
    set_value_from_html(df, index,'Provider',trees,region)
    set_value(df,index,'Dividend Yield',info,trees,region)
    set_value(df,index,'Total Assets',info,trees,region)
    set_value(df,index,'Prev. Close',info,trees,region)
    get_change(df,search,index,'1-Month Change',relativedelta(months=1),trees,region,investing_com_found)
    get_change(df,search,index,'3-Month Change',relativedelta(months=3),trees,region,investing_com_found)
    set_value(df,index,'1-Year Change',info,trees,region)
    get_change(df,search,index,'3-Year Change',relativedelta(years=3),trees,region,investing_com_found)
    df.at[index,'Currency'] = 'EUR' if region == 'EU' else 'USD'
    df.at[index,'Link'] = link
    set_value(df,index,'Expense ratio',info,trees,region)
    set_value(df, index, 'Low 52w',None,trees,region)
    set_value(df, index, 'High 52w',None,trees,region)
    
    
    


gc = gspread.authorize(credentials)

worksheet = gc.open("ETF")

#df = pd.DataFrame(worksheet.sheet1.get_all_records())
df = get_as_dataframe(worksheet.sheet1)
df.fillna('', inplace=True)
for index, row in df.iterrows():
    if row['Refresh'] == 'y':
        not_calc = True
    else:
        not_calc = False
    while not_calc:
        try:
            print('Collecting data for ' + row['Ticker'] + ' (' + str(index + 1) + ' of ' + str(len(df)) + ')')
            fill_etf(df,index,row['Ticker'], row['Listing country'])
            not_calc = False
        except ConnectionError as exc:
            print('From ' + str(datetime.now()) + ' sleeping for 10 mins')
            time.sleep(600)
            pass
        except Exception as exc:
            print('Error while reading ' + row['Ticker'])
            print(str(exc))
            print(traceback.format_exc())
            not_calc = False


#worksheet.sheet1.update([df.columns.values.tolist()] + df.values.tolist())
set_with_dataframe(worksheet.sheet1,df)

#ranges = ["Data!A2:E8"] # 
          
#results = service.spreadsheets().values().get(spreadsheetId = SPREADSHEET_ID, 
#                                     ranges = SAMPLE_RANGE_NAME, 
#                                     valueRenderOption = 'FORMATTED_VALUE',  
#                                     dateTimeRenderOption = 'FORMATTED_STRING').execute() 
#sheet_values = results['valueRanges'][0]['values']
#sheet = service.spreadsheets()
#result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
#                                range=SAMPLE_RANGE_NAME).execute()
#sheet_values = result.get('values', [])
#print(sheet_values)

