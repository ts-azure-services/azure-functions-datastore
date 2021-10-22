# Reference: https://docs.microsoft.com/en-us/azure/storage/queues/storage-python-how-to-use-queue-storage?tabs=python
import os, uuid
from dotenv import load_dotenv
from azure.storage.queue import (
        QueueClient,
        BinaryBase64EncodePolicy,
        BinaryBase64DecodePolicy
)

# Load env variables
env_var=load_dotenv('./../storage_variables.env')
auth_dict = {"storage_key":os.environ['CONN_STRING']}

# Peek at queue
q_name = 'outqueue'
connect_string = auth_dict['storage_key']
queue_client = QueueClient.from_connection_string(connect_string, q_name)

# Get queue length
properties = queue_client.get_queue_properties()
count = properties.approximate_message_count
print("Message count: " + str(count))

# Get queue messages
messages = queue_client.peek_messages(max_messages=5)
for message in messages:
    print("Peeked message id: " + message.id)
    print("Peeked message: " + message.content)

