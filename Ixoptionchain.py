# Libraries
import requests
import json
import math
import csv
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

# Python program to print
# colored text and background
def strRed(skk):         return "\033[91m {}\033[00m".format(skk)
def strGreen(skk):       return "\033[92m {}\033[00m".format(skk)
def strYellow(skk):      return "\033[93m {}\033[00m".format(skk)
def strLightPurple(skk): return "\033[94m {}\033[00m".format(skk)
def strPurple(skk):      return "\033[95m {}\033[00m".format(skk)
def strCyan(skk):        return "\033[96m {}\033[00m".format(skk)
def strLightGray(skk):   return "\033[97m {}\033[00m".format(skk)
def strBlack(skk):       return "\033[98m {}\033[00m".format(skk)
def strBold(skk):        return "\033[1m {}\033[0m".format(skk)

# Method to get nearest strikes
def round_nearest(x,num=50): return int(math.ceil(float(x)/num)*num)
def nearest_strike_bnf(x): return round_nearest(x,100)
def nearest_strike_nf(x): return round_nearest(x,50)

# Urls for fetching Data
url_oc      = "https://www.nseindia.com/option-chain"
url_bnf     = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
url_nf      = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
url_indices = "https://www.nseindia.com/api/allIndices"

# Headers
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'}

sess = requests.Session()
cookies = dict()

# Local methods
def set_cookie():
    request = sess.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    #print (cookies)

def get_data(url):
    set_cookie()
    response = sess.get(url, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==401):
        set_cookie()
        response = sess.get(url_nf, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==200):
        return response.text
    return ""

def set_header():
    global bnf_ul
    global nf_ul
    global bnf_nearest
    global nf_nearest
    response_text = get_data(url_indices)
    data = json.loads(response_text)
    
    for index in data["data"]:
        if index["index"]=="NIFTY 50":
            nf_ul = index["last"]
            print("nifty")
        if index["index"]=="NIFTY BANK":
            bnf_ul = index["last"]
            print("banknifty")
    bnf_nearest=nearest_strike_bnf(bnf_ul)
    nf_nearest=nearest_strike_nf(nf_ul)

# Showing Header in structured format with Last Price and Nearest Strike

def print_header(index="",ul=0,nearest=0):
    print(strPurple( index.ljust(12," ") + " => ")+ strLightPurple(" Last Price: ") + strBold(str(ul)) + strLightPurple(" Nearest Strike: ") + strBold(str(nearest)))

def print_hr():
    print(strYellow("|".rjust(70,"-")))

# Fetching CE and PE data based on Nearest Expiry Date
def print_oi(num,step,nearest,url):
    strike = nearest - (step*num)
    start_strike = nearest - (step*num)
    response_text = get_data(url)
    data = json.loads(response_text)
    currExpiryDate = data["records"]["expiryDates"][0]
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if item["strikePrice"] == strike and item["strikePrice"] < start_strike+(step*num*2):
                #print(strCyan(str(item["strikePrice"])) + strGreen(" CE ") + "[ " + strBold(str(item["CE"]["openInterest"]).rjust(10," ")) + " ]" + strRed(" PE ")+"[ " + strBold(str(item["PE"]["openInterest"]).rjust(10," ")) + " ]")
              p =  str(item["strikePrice"]) + " CE " + "[ " + strBold(str(item["CE"]["openInterest"]).rjust(10," ")) + " ]" + "[ " + strBold(str(item["CE"]["totalTradedVolume"]).rjust(10," ")) + strBold(str(item["CE"]["lastPrice"]).rjust(10," ")) + "[ " + strBold(str(item["CE"]["changeinOpenInterest"]).rjust(10," ")) + strBold(str(item["CE"]["pchangeinOpenInterest"]).rjust(10," ")) + " ]" + " PE " + "[ " + strBold(str(item["PE"]["openInterest"]).rjust(10," ")) + "[ " + strBold(str(item["PE"]["totalTradedVolume"]).rjust(10," ")) + strBold(str(item["PE"]["lastPrice"]).rjust(10," ")) + strBold(str(item["PE"]["changeinOpenInterest"]).rjust(10," ")) + strBold(str(item["PE"]["pchangeinOpenInterest"]).rjust(10," ")) + " ]"
              print (p)
              strike = strike + step 
              #f = open("dashboarddata.csv", "w")
              #f.truncate()
              #os.remove("dashboarddata.csv")
              with open('dashboarddata.csv', 'a') as ofile:   
                                
                   fieldnames = ['Strikprice', 'Optiontype', 'COI', 'OI', 'Volume']
                   writer = csv.DictWriter(ofile, fieldnames=fieldnames)        
                   if ofile.tell() == 0:
                      writer.writeheader()

                   #writer.writerow({'Strikprice': item["strikePrice"], 'Optiontype': 'CE',  'Call COI': item["CE"]["changeinOpenInterest"], 'Put COI': item["PE"]["changeinOpenInterest"], 'Call OI': item["CE"]["openInterest"], 'Put OI': item["PE"]["openInterest"], 'CE Volume': item["CE"]["totalTradedVolume"], 'PE Volume': item["PE"]["totalTradedVolume"]  } )
                   writer.writerow({'Strikprice': item["strikePrice"], 'Optiontype': 'CE',  'COI': item["CE"]["changeinOpenInterest"], 'OI': item["CE"]["openInterest"], 'Volume': item["CE"]["totalTradedVolume"] } )
                   writer.writerow({'Strikprice': item["strikePrice"], 'Optiontype': 'PE',  'COI': item["PE"]["changeinOpenInterest"], 'OI': item["PE"]["openInterest"], 'Volume': item["PE"]["totalTradedVolume"] } )

    #jsonString = json.dumps(data) 
    #jsonFile = open("data.json", "w")
    #jsonFile.write(jsonString)  
    #jsonFile.close()  
    # 
    
    app = dash.Dash(
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    )

    df = pd.read_csv(
    "dashboarddata.csv"
    )

    

    fig = px.bar(
    df,
    x="Strikprice",
    y="Volume",
    barmode = 'group',
    height=400,
    color="Optiontype"
    )
       
    app.layout = html.Div([
       html.Div([
       html.H1('Nifty Volume')
        ]),
       html.Div([
                 dcc.Graph(id="Nifty Volume", figure=fig)], className='six columns')

     ])                     
     

    if __name__ == "__main__":
        app.run_server(debug=True)        

set_header()
print('\033c')
print_hr()
print_header("Nifty",nf_ul,nf_nearest)
print_hr()
print_oi(10,100,nf_nearest,url_nf)
print_hr()
#print_header("Bank Nifty",bnf_ul,bnf_nearest)
#print_hr()
#print_oi(10,100,bnf_nearest,url_bnf)
#print_hr()


