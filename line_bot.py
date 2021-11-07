#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import pymysql
import requests
import threading
import datetime


update = ''' select '''

update_report = '''select  '''


db_settings = {
    "host":,
    "port": ,
    "user": ,
    "password":,
}

try:
    # build Connection
    conn = pymysql.connect(**db_settings)
    with conn.cursor() as cursor:
        cursor.execute(update)
        cursor.execute(update_report)
        namelist = pd.DataFrame(cursor.fetchall())
        
except Exception as ex:
    print(ex)
    
    
# close cursor
cursor.close()
conn.close()

# namelist.columns = ['店家名稱','地址','狀態','合約開始日','合約到期日','負責業務']
namelist.columns = ['店家名稱','負責業務','合約到期日']
namelist['到期日程'] = namelist['合約到期日'].apply(lambda x: (x-datetime.datetime.today().date()).days)
# namelist = namelist.drop_duplicates(subset='店家名稱')

# clean data
def clean_data(sales_data):
    sales_data = sales_data[~sales_data["店家名稱"].str.contains("古拉")]
    sales_data = sales_data[~sales_data["店家名稱"].str.contains("測")]
    sales_data = sales_data[~sales_data["店家名稱"].str.contains("資產")]
    sales_data = sales_data[~sales_data["店家名稱"].str.contains("104培訓")]
    sales_data = sales_data[~sales_data["店家名稱"].str.contains("新光中區")]
    sales_data = sales_data[~sales_data["店家名稱"].str.contains("閉")]
    sales_data = sales_data.reset_index(drop=True)
    return sales_data
namelist = clean_data(namelist)
namelist
# in one week
seven_days = namelist[namelist['到期日程'] <= 7]

# in two weeks
two_week = namelist[(namelist['到期日程'] >= 8) & (namelist['到期日程'] <= 14)]

# in one month
one_month = namelist[namelist['到期日程'] == 30]

headers = {
        "Authorization": "Bearer " + "fUo1CqvygSQK10UtbrKjw6A8XwRv7DmqO4cwt0QYpaJ",
        "Content-Type": "application/x-www-form-urlencoded"
    }
def check_len(time):
    if len(time) > 0:
        word = ''
        for i in range(len(time)):
            word += time['店家名稱'].tolist()[i]+'('+time['負責業務'].tolist()[i]+')'+'\n'
    else:
        word = '無'
    return word

check_len(seven_days)
check_len(two_week) 
# check_len(one_month)

def func():
    p1 = check_len(seven_days)
    p2 = check_len(two_week)

    params = {"message": '\n'+"1週內到期店家:" + '\n'
              + p1 + '\n' + "2週內到期店家:" + '\n'
              + p2 + '\n' +'請業務聯繫店家洽談續約事宜～'}
    # use API to post message 
    r = requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, params=params)
func()



#     timer = threading.Timer(86400, func)
#     timer.start()


# now_time = datetime.datetime.now()
# next_time = now_time + datetime.timedelta(days=+1)
# next_year = next_time.date().year
# next_month = next_time.date().month
# next_day = next_time.date().day
# next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 07:00:00", "%Y-%m-%d %H:%M:%S")
# timer_start_time = (next_time - now_time).total_seconds()
# print(timer_start_time)
# timer = threading.Timer(timer_start_time, func)
# timer.start()




