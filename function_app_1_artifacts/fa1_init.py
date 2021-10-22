import datetime
import datetime as dt
import logging, json, uuid
import pandas_datareader as web
import azure.functions as func

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
            data = data.to_json() # converts to a string
        logging.info(f'Successfully received stock price data.')
    except Exception as e:
        logging.warning(f'Exception: {e}. Failed to load stock price data.')
    finally:
        if data is None:
            final_value = 'No data returned.'
        else:
            final_value = data
    return final_value

def main(mytimer: func.TimerRequest, msg: func.Out[str], message: func.Out[str]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    msg.set(f"Function app triggered at {utc_timestamp}")

    # Build table object
    data = get_stock_data()
    rowKey = str(uuid.uuid4())
    table_input = {"Name":data,"PartitionKey":"message","RowKey": rowKey}
    message.set(json.dumps(table_input))

    #if mytimer.past_due:
    #    logging.info('The timer is past due!')

    #logging.info('Python timer trigger function ran at %s', utc_timestamp)
