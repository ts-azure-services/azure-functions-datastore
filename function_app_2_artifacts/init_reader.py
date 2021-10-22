import os
from dotenv import load_dotenv
import datetime
import datetime as dt
import logging, json, uuid
import pandas_datareader as web
import azure.functions as func
import pyodbc

def get_env_variables():
    # Load env variables
    env_var=load_dotenv('./../db_variables.env')
    env_dict = {
            "server":os.environ['HOST'],
            "database":os.environ['DATABASE'],
            "user":os.environ['DB_USER'],
            "pwd":os.environ['DB_PWD']
            }
    return env_dict


def get_stock_data():
    data = None
    try:
        # Load stock price data from specific companies
        #company = ['FB', 'MSFT', 'AAPL']
        company = ['FB']
        start = dt.datetime(2020,1,1)
        end = dt.datetime(2020,3,1)
        for i in company:
            data = web.DataReader(i, 'yahoo', start, end) # returns a df
            data = data.reset_index()
            data.columns=data.columns.str.lower()
            data.columns=data.columns.str.replace(' ','')
            #data = data.to_json() # converts to a string
        logging.info(f'Successfully received stock price data.')
    except Exception as e:
        logging.warning(f'Exception: {e}. Failed to load stock price data.')
    finally:
        if data is None:
            final_value = 'No data returned.'
        else:
            final_value = data
    return final_value

def create_table(driver=None, server=None, database=None,username=None, password=None, query=None):
    try:
        with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+password) as conn:
        #with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+password) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
        logging.info('Successfully created the table.')
    except Exception as e:
        logging.warning(e)

def insert_rows(driver=None, server=None, database=None,username=None, password=None, df=None):
    try:
        with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+password) as conn:
            with conn.cursor() as cursor:
                for index, row in df.iterrows():
                    cursor.execute("INSERT INTO sample (date, high, low, open_price, close_price, volume, adj_close) VALUES(?,?,?,?,?,?,?)",
                            row.date, row.high, row.low, row.open, row.close,row.volume, row.adjclose)
                conn.commit()
        logging.info('Successfully inserted rows.')
    except Exception as e:
        logging.warning(e)

create_query="""CREATE TABLE sample (
id INT PRIMARY KEY IDENTITY (1,1),date DATETIME,
        high real, low real,
        open_price real, close_price real,
        volume real, adj_close real
        );"""


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    # Get stock data
    data = get_stock_data()

    # Load environment variables
    env_dict = get_env_variables()
    server = env_dict['server']
    db = env_dict['database']
    user = env_dict['user']
    pwd = env_dict['pwd']
    driver= '{ODBC Driver 17 for SQL Server}'

    # Create table
    create_table(driver=driver, server=server, database=db, username=user, password=pwd,query=create_query)

    # Insert rows
    insert_rows(driver=driver, server=server,database=db, username=user, password=pwd,df=data)

