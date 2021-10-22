# Intent
- Azure Functions is a convenient service that allows one to take advantage of scheduled 'serverless' jobs off
  a timed trigger. To demonstrate, this repo pulls sample stock data from a finance API, and logs that into a
  datastore.
	- In the first scenario it will pull from the API and log a simple confirmation message in Azure
	  Queue, and the details of the actual pull (deserialized json) in Azure Table Storage.
	- In the second scenario, it will perform the same operations but immediately store results in a SQL
	  Database.
  
# Steps
- A Makefile exists and to complete the process end to end, run ```make all```.
- Recommended to create a virtual environment and load all dependencies from the ```requirements.txt``` file.
  Reference the Makefile, specifically the ```make install``` step. This step will also setup all the infra
  requirements (creation of a function app, storage account, app insights and a SQL Database) and write out
  three environment files:
	- ```functionappname.env``` This stores the function app name for later publish.
	- ```storage_variables.env``` This will have the storage account connection string (to be used with
	  the ```query``` scripts for the first function app to see results in the queue and table storage)
	- ```db_variables.env``` This will have the host, user, password, and database name of the SQL DB
	  resource
- Can create the function apps by running the Makefile step ```make function_setup```. This will initialize
  the function app by creating a number of setup files (e.g. host.json, local.settings.json, etc.) and
  creating containers for both function apps (fa1, fa2).
- The ```make copy_artifacts``` step will overwrite the creation function app files with the code to create a
  function app linked to queue and table storage (for option 1), and to a SQL database (for option 2).
- The final Makefile stpe is to run ```make publish_app``` which will publish all the function apps to the
  function app created in Azure.
- Other:
	- For 'fa1', you can use the ```query_queue.py``` and ```query_table_storage.py``` to see
	  the latest changes in the Queue and Table Storage.
	- For 'fa2', you have to manually load the environment variables for the host, database,
	  db user, and db password in the Configuration section of the Function App. If needed, you can also use Key
	  Vault to store secrets or sensitive information e.g. user and password. Note the environment
	  variable names in the __init__.py file of fa2.
	- Prior to publishing 'fa2', run ```test_sql.py``` to check if a connection can be made to
	  the SQL Database (contained in function_app_2_artifacts). Configure appropriately by ensuring the SQL Database is set to ```Allow public services```
	  and that it recognizes your Client IP and the IP of the script. Configurations will be different if you
	  leverage VNET, or Private Endpoint.
	- In the current 'fa2' SQL DB logic, it will always look to first create the table and then import records. Subsequent
	  pulls will fail on the create step, but this will be bypassed and additional inserts will be appended to the
	  table. Future iterations of this logic may clean this up with a better SQL query.
	- Basic SQL commands to test the load:
		- select schema_name(t.schema_id) as schema_name,t.name as table_name, t.create_date,t.modify_date from sys.tables t order by schema_name, table_name;
		- drop table sample;
		- select * from sample;
	- ```cleanup.sh``` is used to remove all deployed function apps and associated files once done.
