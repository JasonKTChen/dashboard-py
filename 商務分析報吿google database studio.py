
import pymysql
import pandas as pd
from datetime import datetime
from datetime import date
import pygsheets 

def step(x):
    if x == 1:
        return '未接受'
    elif x == 4:
        return '確認訂餐時間'
    elif x == 5:
        return '已接單'
    elif x == 6:
        return '準備完成'
    elif x == 7:
        return '已完成'
    elif x == 72:
        return '店家刪單'
    elif x == 73:
        return '店家退單'
    elif x == 74:
        return '客戶取消'
    elif x == 82:
        return '退款完成'
    elif x == 83:
        return '付款後作廢'
    
def line(x):
    if x == 'line':
        x = 'lineoa'
    return x

def keep_name(x):
    i = x.find('(')
    x = x[:i]
    return x

# 現有店家（未排除測試店家）
exist_stores =  '''select  '''

# 訂位使用情況
reservation = "select "

# 線上點餐使用情況
order = "select "

# UberEats使用情況
ue = "select "

db_settings = {
    "host":
}

try:
    conn = pymysql.connect(**db_settings)
    with conn.cursor() as cursor:
        cursor.execute(exist_stores)
        exist =  pd.DataFrame(cursor.fetchall()) # 有效店家資訊
#         cursor.execute(reservation)
#         res_record = pd.DataFrame(cursor.fetchall())# 排隊預約資訊
        cursor.execute(order)
        order_record = pd.DataFrame(cursor.fetchall())# 線上點餐資訊
        cursor.execute(ue)
        ue_record = pd.DataFrame(cursor.fetchall()) # UberEats資訊
        
except Exception as ex:
    print(ex)
    
cursor.close()
conn.close()

# # 王品店家&副機數
# wp_overall = ''' select  distinct s.name, p.quantity-1 from store s
# left join pos_vip_buy b on s.company_id = b.company_id
# left join pos_vip p on b.pid = p.pos_vip_buy_id
# left join dudoo_client.companys c on c.company_id = s.company_id 
# where c.hq_hierarchy_id = 158  and begin_date != '0000-00-00 00:00:00'
# and p.start_date <= date(now()) and end_date >= date(now()) and p.service_id = 8
# and b.severity = '一般客戶' '''

# wp_orderq = ''' SELECT  o.company_id,c.name,o.`type`,o.final_take_time ,o.step ,o.amount,o.platform
# FROM dudoo_client.companys c
# left join 
# (select distinct s.company_id
# from dudoo_center.store s
# left join dudoo_center.pos_vip_buy b on s.company_id = b.company_id
# left join dudoo_center.pos_vip p on b.pid = p.pos_vip_buy_id
# left join dudoo_client.companys c on c.company_id = s.company_id 
# where c.hq_hierarchy_id = 158  and begin_date != '0000-00-00 00:00:00'
# and p.start_date <= date(now()) and end_date >= date(now()) and p.service_id = 62
# and b.severity = '一般客戶' ) as p on p.company_id = c.company_id
# left join dudoo_client.orders o  on p.company_id = o.company_id and o.deleted = 0
# left join dudoo_client.bills b on b.sale_id = o.sale_id
# left join dudoo_client.bill_invoices bi on b.bill_id = bi.bill_id
# where bi.split_sn = 0 and bi.status = 3  ''' 

# wp_service = ''' SELECT DISTINCT pv.company_id,c2.name,pv.start_date
# from dudoo_center.pos_vip pv 
# left join dudoo_center.services s on s.id = pv.service_id 
# left join dudoo_client.companys c2 on c2.company_id =pv.company_id 
# where s.id = 64 '''

# db_settings = {
#     "host": "db-wp01r01.dudooeat.com",
#     "port": 3306,
#     "user": "DATA_ANALYSIS",
#     "password": "dudoo522",
#     'db':'dudoo_center',
#     "charset": "utf8"
# }
# try:
#     # 建立Connection物件
#     conn = pymysql.connect(**db_settings)
#     with conn.cursor() as cursor:
#         #逐一下 Query
#         cursor.execute(wp_overall)
#         wp_record = pd.DataFrame(cursor.fetchall()) # 王品店家資訊
#         cursor.execute(wp_orderq)
#         wp_o_record = pd.DataFrame(cursor.fetchall()) # 王品線上點餐資訊
#         cursor.execute(wp_service)
#         wp_s_record = pd.DataFrame(cursor.fetchall()) # 王品線上點餐資訊
# except Exception as ex:
#     print(ex)
    
# # 關閉遊標
# cursor.close()
# conn.close()

# wp_record.columns = ['company_name','sub']



# #店家資料處理
# wp_record['brand'] =  wp_record['company_name'].apply(lambda x : keep_name(x))
# wp_record = wp_record.loc[:,['brand','company_name','sub']]

# #線上訂餐資料處理
# wp_o_record.columns = ['company_id','company_name','type','final_take_time','step','amount','platform']
# wp_o_record['brand'] =  wp_o_record['company_name'].apply(lambda x : keep_name(x))
# wp_o_record['step'] = wp_o_record['step'].apply(lambda x: step(x))
# wp_o_record['platform'] = wp_o_record['platform'].apply(lambda x: line(x))

# #線上點餐合約開始日
# wp_s_record.columns = ['company_id','company_name','start_date']
# wp_o_record = pd.merge(wp_s_record,wp_o_record,on = ['company_id','company_name'],how = 'inner')
# wp_o_record['using_days'] = datetime.now().date() - wp_o_record['start_date']
# wp_o_record['using_days'] = wp_o_record['using_days'].dt.days

#資料表處理
exist.columns = ['company_id','company_name','address','city','start_date','end_date','sub','state']
north = ['台北市','新北市','基隆市','桃園','新竹','宜蘭']
central = ['台中市','苗栗','彰化','南投','雲林']
south = ['高雄市','台南','嘉義市','嘉義','屏東','澎湖']
east = ['花蓮','台東']

exist['region']=''
for i in range(len(exist)):
    if exist['city'].iloc[i] in north:
        exist['region'].iloc[i] = '北部'
    elif exist['city'].iloc[i] in central:
        exist['region'].iloc[i] = '中部'
    elif exist['city'].iloc[i] in south:
        exist['region'].iloc[i] = '南部'
    elif exist['city'].iloc[i] in east:
        exist['region'].iloc[i] = '東部'
    else:
        exist['region'].iloc[i] = '其他'
        
# # 挑出訂位紀錄所需欄位
# res_record = res_record.loc[:,[1,2,13,17,20,23]]
# res_record.columns = ['company_id','username','res_datetime','finish','deleted','platform']
# # 清出真正有使用的店家紀錄
# real_res = pd.DataFrame()
# for i in exist['company_id'].unique():
#     if i in res_record['company_id'].unique():
#         real_res = pd.concat([real_res,res_record[res_record['company_id']==i]])
# # 實際有完成且沒被取消的訂單
# real_res = real_res[real_res['finish']!=0]
# real_res = real_res[real_res['deleted']==0]
# real_res = real_res[~real_res['username'].str.contains('測試')]
# real_res = real_res[~real_res['username'].str.contains('新光保全')]
# real_res = real_res[~real_res['username'].str.contains('測試')]
# real_res = real_res[~real_res['username'].str.contains('喬治')]
# real_res = real_res[~real_res['username'].str.contains('柏詠')]
# real_res = real_res[~real_res['username'].str.contains('佐翰')]
# real_res = real_res[~real_res['username'].str.contains('楊巧薇')]
# real_res = real_res[~real_res['username'].str.contains('大維')]
# real_res = pd.merge(exist,real_res,on='company_id',how = 'inner')
# real_res['year'] = real_res['res_datetime'].dt.year
# real_res['month'] = real_res['res_datetime'].dt.month


    
# 清洗線上點餐資料
online = order_record.loc[:,[0,1,4,5,8,13,14,18,26,33,37]]
online.columns = ['order_id','company_id','user_id','type','username','sales_amount','amount','create_time','final_take_time','step','platform']

online = online[online['step']!=23] # 無23階段，測試用
online = online[online['step']!=0] # step 0 的 sales amount幾乎為0，判定為無效交易
online['step'] = online['step'].apply(lambda x: step(x))


online['platform'] = online['platform'].apply(lambda x: line(x))

online_gs = pd.merge(online,exist[['company_id','company_name','region']])
# res_gs = real_res.loc[:,['company_name','username','start_date','city','res_datetime','platform']]
ue_record = ue_record.loc[:,[0,1,4,5,8,13,14,18,26,33,37]]
ue_record.columns = ['order_id','company_id','user_id','type','username','sales_amount','amount','create_time','final_take_time','step','platform']

ue_record['step'] = ue_record['step'].apply(lambda x: step(x))
ue_record = pd.merge(exist,ue_record,on='company_id',how = 'inner')
ue_record.drop('address',axis=1,inplace = True)



# #更新google sheet 資料
# gc = pygsheets.authorize(service_file='/Users/chenjingmin/Desktop/dudoo/商務分析/My Project-d688762acd90.json')
# sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Ybd5N7XAQl468ajfNc313ZlMx2rSX10aNKjSMEki95Q/edit#gid=710065356')
# ordering_gs = sht[0]
# ordering_gs.clear()
# ordering_gs.set_dataframe(online_gs, start = "A1",fit = True)

# reservation_gs = sht[1]
# reservation_gs.clear()
# reservation_gs.set_dataframe(res_gs, start = "A1",fit = True)

# ubereats_gs = sht[2]
# ubereats_gs.clear()
# ubereats_gs.set_dataframe(ue_record, start = "A1",fit = True)

# store_gs = sht[3]
# store_gs.clear()
# store_gs.set_dataframe(exist, start = "A1",fit = True)

# opwp_gs = sht[4]
# opwp_gs.clear()
# opwp_gs.set_dataframe(wp_record, start = "A1",fit = True)

# oowp_gs = sht[5]
# oowp_gs.clear()
# oowp_gs.set_dataframe(wp_o_record, start = "A1",fit = True)


# In[6]:


exist


# In[25]:


ue_record.to_excel("/Users/jasonchen/Desktop/dudoo/Ubereats_record0409.xlsx")


# In[26]:


online_gs.to_excel("/Users/jasonchen/Desktop/dudoo/onlineorders_record0409.xlsx")


# In[18]:


ue_record_revise


# In[11]:


ue_record[ue_record["final_take_time"] == "0000-00-00 00:00:00"]


# In[12]:


ue_record["create_time"] = pd.to_datetime(ue_record["create_time"],format='%Y-%m-%d %H:%M:%S')


# In[16]:


ue_record_revise = ue_record[ue_record["create_time"] > datetime.strptime('2021-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')]
ue_record_revise.drop(['company_id','sub','state','order_id','user_id','username','platform'],axis=1,inplace = True)


# In[19]:


#更新google sheet 資料
gc = pygsheets.authorize(service_file='/Users/jasonchen/Desktop/dudoo/My Project-d688762acd90.json')
sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Ybd5N7XAQl468ajfNc313ZlMx2rSX10aNKjSMEki95Q/edit#gid=710065356')

ubereats_gs = sht[2]
ubereats_gs.clear()
ubereats_gs.set_dataframe(ue_record_revise, start = "A1",fit = True)
# store_gs = sht[3]
# store_gs.clear()
# store_gs.set_dataframe(exist, start = "A1",fit = True)


# In[ ]:





# In[57]:


exist["start_date"] = pd.to_datetime(exist["start_date"],format='%Y-%m-%d %H:%M:%S')
exist["end_date"] = pd.to_datetime(exist["end_date"],format='%Y-%m-%d %H:%M:%S')


# In[71]:


tt = exist[exist["start_date"]>= datetime.strptime('2021-02-01 00:00:00', '%Y-%m-%d %H:%M:%S')]
feb = tt[tt["start_date"]< datetime.strptime('2021-03-01 00:00:00', '%Y-%m-%d %H:%M:%S')]
mar = tt[tt["start_date"]>= datetime.strptime('2021-03-01 00:00:00', '%Y-%m-%d %H:%M:%S')]


# In[72]:


tt


# In[81]:


exist.to_excel("/Users/jasonchen/Desktop/0324店家總數.xlsx")


# In[65]:


mar


# In[ ]:




