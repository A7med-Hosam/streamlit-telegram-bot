from pprint import pprint
import requests
from pathlib import Path
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta, timezone
import modal 


imaged = (
    modal.Image.debian_slim().pip_install("fastapi[standard]")
    # .apt_install("git")
    # .apt_install("curl")
    # .apt_install("make")
    .run_commands("pip install --upgrade pip")
    .run_commands("pip install requests")
    .run_commands("pip install pybit")
)

# imaged = modal.Image.debian_slim().pip_install("fastapi[standard]")
app = modal.App(name="example-lifecycle-web", image=imaged)


@app.function(image=imaged,region="eu")
@modal.fastapi_endpoint(
    docs=True  # adds interactive documentation in the browser
)

    # script_dir = Path(__file__).parent
def update_pnl_balance():

    NOTION_TOKEN = "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"
    PAGE_ID = "22267e6ab25480d0b2f2d2e0fe98b971"
    DATABASE_ID = "22267e6ab25480a0abd3d704c959d194"
    WALLET_BALANCE_ID = '22867e6a-b254-8005-8b58-de1397c59453'
    TODAYS_TOTAL_PNL_ID = '22267e6a-b254-805e-9153-e722274b4bdc'
    CLOSED_PNL_ID = "22967e6a-b254-8037-81c5-c1dac0d24893"
    LIVE_PNL_ID = "22967e6a-b254-805a-8658-e523626ac208"

    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    session = HTTP(
        testnet=False,
        api_key="xqPk7N4KBd0cH3UHRl",
        api_secret="Le8h8lf07ImeaDeLD3XsskM6PrgY9YHeJSVK",
    )


    balanceDetails = session.get_wallet_balance(
        accountType="UNIFIED",
        coin="USDT",
    )["result"]["list"][0]


    def get_day_pnl(day_num):
        todays_date_full=  datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        end_date_full= todays_date_full - timedelta(day_num)
        end_date_timestamp= int(datetime.timestamp(end_date_full)*1000)
        end_date_format= end_date_full.strftime('%Y-%m-%d')

        start_date_full= todays_date_full - timedelta(day_num+1)
        start_date_timestamp= int(datetime.timestamp(start_date_full)*1000)
        start_date_format= start_date_full.strftime('%Y-%m-%d')

        trades_data= (session.get_closed_pnl(
            category="linear",
            startTime= start_date_timestamp,
            endTime= end_date_timestamp,
            limit=10000,
        ))['result']['list']

        day_pnl= 0
        for trade in trades_data:
            day_pnl+= float(trade["closedPnl"])
        day_pnl= round(day_pnl,4)

        return day_pnl,start_date_format,start_date_full,start_date_timestamp

    def get_multiple_days_pnl(num_days):
        today = -1
        days= num_days-1
        while today < days:
            pnl= get_day_pnl(today)[0]
            
            today+=1
        return round(pnl,4)

    def edit_block(block_id, data,type):
        url = f"https://api.notion.com/v1/blocks/{block_id}/"

        payload = {type: data}
        results = requests.patch(url, json=payload, headers=headers)

        pprint(results)
        return results

    def update_number(block_id,number,static,type):
        if static == False:
            sign = ""
            number_color = "gray"
            if number > 0:
                number_color = "green"
                sign = "+"
            elif number < 0:
                number_color = "red"
                sign = "-"
            else:
                number_color = "gray"
            number_str = f'{sign} {abs(number)}$'
        else:
            number_color = "gray"
            number_str = f'{abs(number)}$'

        data = {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": number_str,
                    "link": None
                },
                "annotations": {
                    "bold": False,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": number_color
                },
                "plain_text": "+ 0.53$",
                "href": None
            }
            ],
            "color": number_color
        }
        edit_block(block_id, data,type)


    wallet_balance = round(float(balanceDetails["totalEquity"]),4)
    live_pnl = round(float(balanceDetails["coin"][0]["unrealisedPnl"]),4)
    todays_closed_pnl = get_multiple_days_pnl(1)
    total_pnl = round(todays_closed_pnl + live_pnl,4)

    # simple text dashboard for telegram
    Simple_Dashboard = f'''
    Balance = {wallet_balance}
    Today's Pnl 
        {total_pnl}
  Live             Closed
  {live_pnl}        {todays_closed_pnl}

'''
    print(Simple_Dashboard)

    update_number(LIVE_PNL_ID,live_pnl,False,"paragraph")

    update_number(CLOSED_PNL_ID,todays_closed_pnl,False,"paragraph")

    update_number(TODAYS_TOTAL_PNL_ID,total_pnl,False,"heading_2")

    update_number(WALLET_BALANCE_ID, wallet_balance,True,"heading_2")

    full_list = [wallet_balance,total_pnl,live_pnl,todays_closed_pnl]

    return full_list
