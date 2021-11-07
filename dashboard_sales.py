
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from dash.exceptions import PreventUpdate
import datetime
from dateutil.relativedelta import relativedelta
import pymysql

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() 

app = dash.Dash()
colors = {'backgroundColor': '#FFFFFF','text':'#FF5733'}

# Open database connection
db_settings = {
    ""
}
try:
    # build Connection
    conn = pymysql.connect(**db_settings)
    with conn.cursor() as cursor:
        #逐一下 Query
        sql = "MySQL"
        cursor.execute(sql1)
        df = pd.DataFrame(cursor.fetchall())
        cursor.execute(sql2)
        df1 = pd.DataFrame(cursor.fetchall())
except Exception as ex:
    print(ex)
    
# close cursor
cursor.close()
conn.close()

# standardize time
df['trans_time'] = df['trans_year'].apply(lambda x:str(x))+'/'+df['trans_month'].apply(lambda x:str(x))
df['trans_time'] = pd.to_datetime(df['trans_time'],format='%Y/%m')

# filter company name of each store
hq_name = df['hq_name'].unique()
brand = df.groupby('hq_name')

def generate_section_banner(title):
    return html.H3(className="section-banner",children=title,style = {'color':'rgb(107,107,107)','fontWeight':'bold'})

# histogram
x_label = df1['Unnamed: 0'].astype(str).tolist()

barplot = []
color = ['#CC543A','#FB9966','#F19483','#FB966E','#DB8E71']
col = df1.columns
for i in range(1,6):
    barplot.append(
        go.Bar(
            y = df1[col[i]],
            x = x_label,
            name = col[i],
            marker = 
            dict(
                color = color[i-1]))
        )
lay = go.Layout(barmode = 'stack',
                title = '支付方式總覽',
               titlefont=dict(family='Courier New, monospace', size=22, color='#7f7f7f'),
               yaxis=dict(title='百分比 (%)',
                          titlefont=dict(size=18,color='#FF5733'),
                          tickfont=dict(
                              size=16, color='#FF5733')
    ),
               xaxis=dict(
                   titlefont=dict(
                       size=16,color='#FF5733'),
                   tickfont=dict(
                       size=16,color='#FF5733')),
               hovermode='x',
               plot_bgcolor = '#FFFFFF',
               )
fig =  go.Figure(data = barplot, layout = lay)

def get_marks_from_start_end(start, end):

    result = []
    current = start
    while current <= end:
        result.append(current)
        current += relativedelta(months=1)
    return {unix_time_millis(m):{'label':str(m.strftime('%Y-%m'))} for m in result}

# layout
app.layout = html.Div([
    html.H1(children='肚肚 店鋪月銷售資訊',
            style={ 'color':'#FF5733',
                    'textAlign':'center',
                    'fontWeight':'bold' ,
                    'fontSize':'1.2cm'}),    
    html.Div(
        children = [
        html.Div([
        html.H3('選擇欲查看的店面資訊',
                style={'color':colors['text'],
                       'fontWeight':'bold'}),
        html.Div(children =[
            html.Div(children=[
                dcc.Dropdown(
                id = 'company',
                style={'backgroundColor': '#FFFFFF','width' : 350},
                options = [{'value':i,'label':i} for i in hq_name],
                placeholder = 'Choose a company',
                multi = False)
            ]),
            html.Div(children=[
                dcc.Dropdown(
                id = 'shop',
                style={'backgroundColor': '#FFFFFF','width' : 800},
                placeholder = 'Choose a shop',
                multi = True)])
            ]),
                  

]),
        html.Div(children = [
            html.Div(
            children=[ 
                generate_section_banner("月銷售額變動圖"),  
                dcc.Graph(id='shops',
                      animate=True)]  ),
            
            # 總體支付比例畫成長條圖，然後各月份的支付變動以折線圖呈現
            html.Div(
            children=[
                generate_section_banner("支付方式比例圖"),
                dcc.Graph(
                    id = 'overall',
                    animate = True,
                    figure = fig
                ),
                dcc.Graph(id='bar',
                      animate=True),
                
                dcc.Slider(
                id='month-slider',
                min = unix_time_millis(df['trans_time'].min()),
                max = unix_time_millis(df['trans_time'].max()),
                value = unix_time_millis(df['trans_time'].min()),
                step = None,
                #TODO add markers for key dates
                marks = get_marks_from_start_end(df['trans_time'].min(),df['trans_time'].max())
            ),
                html.Div(id='updatemode-output-container', 
                         style={'margin-top': 20,
                                'fontSize':22,
                                'textAlign':'center',
                                'color':'#FF5733',
                                'fontWeight':'bold'})
            ]                    
    )]
                 
,style={'backgroundColor': colors['backgroundColor'],'text':colors['text']})])])



# input
def out(doct):
    
    @app.callback(
        dash.dependencies.Output('company', 'value'),
        [dash.dependencies.Input('company', 'options')])

    def update_company(company):
        if not company:
            raise PreventUpdate

        return company[0]['value']
    
    @app.callback(
        dash.dependencies.Output('shop','options'),
        [dash.dependencies.Input('company','value')])
    
    def update_company(company):
        individual = brand.get_group(company)
        store_name = individual['store_name'].unique()

        return [{'value':i,'label':i} for i in store_name]
    
    @app.callback(
        dash.dependencies.Output('shop','value'),
        [dash.dependencies.Input('shop','options')])
    
    def update_shops(shop):
        return shop[0]['value'] 
    
    @app.callback(
        dash.dependencies.Output('shops', 'figure'),
        [dash.dependencies.Input('shop', 'value')])
    
    def update_figure(choose):
        traces = [ ]
        
        if type(choose) != list:     
            by_name = df[df['store_name']==choose]
            t1 = by_name.groupby(['sales_meal_type','trans_time','store_name']).agg('sum').reset_index()
            how = by_name['sales_meal_type'].unique()
            
            for i in how:
                t2 = t1[t1['sales_meal_type']==i]
                traces.append(go.Scatter(
                    x = t2['trans_time'],
                    y = t2['amount'],
                    text = i,
                    mode='lines+markers',
                    opacity=0.7,
                    marker={
                        'line': {'width': 0.5, 'color': 'white'},
                        'symbol': 'circle',
                        'sizemode': 'area'},
                    name=choose))

        else:
            for i in choose:
                by_name = df[df['store_name']==i]
                t1 = by_name.groupby(['sales_meal_type','trans_time','store_name']).agg('sum').reset_index()
                how = by_name['sales_meal_type'].unique()
                
                for j in how:
                    t2 = t1[t1['sales_meal_type']==j]
                    
                    traces.append(go.Scatter(
                        x = t2['trans_time'],
                        y = t2['amount'],
                        text = j,
                        mode='lines+markers',
                        opacity=0.7,
                        marker={
                            'line': {'width': 0.5, 'color': 'white'},
                            'symbol': 'circle',
                            'sizemode': 'area'
                        },
                        name=i
                ))
        return {
            'data': traces,
            'layout': go.Layout(
                height = 500,
                xaxis={'titlefont':dict(size=18),
                          'tickfont':dict(
                              size=16, color='#FF5733')},
                yaxis={'title': '銷售額(NT$)','titlefont':dict(size=14),
                          'tickfont':dict(
                              size=16, color='#FF5733') },
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                showlegend=False,
                hovermode='closest',
                font=dict(color='#FF5733'),
                paper_bgcolor = '#FFFFFF',
                plot_bgcolor = '#FFFFFF',
                )
            
    } 

        
out(df)

@app.callback(
    dash.dependencies.Output('updatemode-output-container', 'children'),
    [dash.dependencies.Input('month-slider','value')])

def display_month(value):
    return str(datetime.datetime.fromtimestamp(value).strftime('%Y-%m'))


@app.callback(
    dash.dependencies.Output('bar','figure'),
    [dash.dependencies.Input('month-slider','value')]
    )
def update_bar(month):
    value = str(datetime.datetime.fromtimestamp(month).strftime('%Y-%m-%d'))
    by_region = df.groupby(['trans_time','region','payment_type']).agg(sum)
    by_region = by_region.drop(['company_id','trans_year','trans_month','trans_type'],axis = 1)
    by_region = by_region[by_region.index.get_level_values('trans_time')== value].reset_index().groupby(['region','payment_type']).agg(sum).loc[:,'amount'].reset_index(level=1)
    
    ## build histogram information
       
    bar_data = pd.DataFrame()
    for i in by_region.index.unique():
        t1 = by_region[by_region.index== i].reset_index(drop=True).T
        t1.columns = t1.iloc[0]
        t1 = t1.drop(t1.index[0])
        t1 = t1.div(t1.sum(axis=1), axis=0)*100
        t1 = t1.rename(index={'amount':i})
        bar_data = pd.concat([bar_data,t1])
    bar_data.fillna(0,inplace = True)
    bar_data = bar_data.reset_index()
    
    if value == '2019-08-01': 
        bar_data['禮券/餐券']=[0,0,0,0]
        
    bar_data = bar_data.loc[:,['index','現金支付','信用卡支付','外送平台','電子支付','禮券/餐券']]
    bar_data = bar_data.reindex(index = [1,0,2,3])
    x_label = bar_data['index'].astype(str).tolist()

    # display the dashboard 
    barplot = []
    color = ['#CC543A','#FB9966','#F19483','#FB966E','#DB8E71']
    col = bar_data.columns
    for i in range(1,6):
        barplot.append(
            go.Bar(
                y = bar_data[col[i]],
                x = x_label,
                name = col[i],
                marker = 
                dict(

                    color = color[i-1]))
            )

    lay = go.Layout(barmode = 'stack',
                   title = '分區支付方式', titlefont=dict(family='Courier New, monospace', size=22, color='#7f7f7f'),
                   yaxis=dict(title='百分比 (%)',
                              titlefont=dict(size=18,color='#FF5733'),
                              tickfont=dict(
                                  size=16,color='#FF5733')
        ),
                   xaxis=dict(
                       titlefont=dict(
                           size=16, color='#FF5733'),
                       tickfont=dict(
                           size=16, color='#FF5733')),
                   hovermode='x',
                   plot_bgcolor = '#FFFFFF')
                    
    return go.Figure(data = barplot,layout=lay)





if __name__ == '__main__':
    app.run_server(port = 8002,debug=True,host='127.0.0.1')
