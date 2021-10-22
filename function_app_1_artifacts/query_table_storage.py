# Reference: https://docs.microsoft.com/en-us/azure/cosmos-db/table/how-to-use-python
import os, uuid
from dotenv import load_dotenv
from azure.data.tables import TableServiceClient, TableClient

# Load env variables
env_var=load_dotenv('./../storage_variables.env')
auth_dict = {"storage_key":os.environ['CONN_STRING']}
#service = TableServiceClient(
#        endpoint="https://<my_account_name>.table.core.windows.net/",
#        credential=auth_dict['storage_key']
#        )


# Query table data
my_filter = "PartitionKey eq 'message'"
table_client = TableClient.from_connection_string(
        conn_str=auth_dict['storage_key'],
        table_name='rawdata'
        )

entities = table_client.query_entities(my_filter)
for entity in entities:
    for key in entity.keys():
        print("Key: {}, Value: {}".format(key, entity[key]))
