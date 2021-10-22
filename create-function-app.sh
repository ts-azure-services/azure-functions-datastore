#!/bin/bash
#Script to provision a new Azure ML workspace
grn=$'\e[1;32m'
end=$'\e[0m'

# Start of script
SECONDS=0
printf "${grn}STARTING CREATION OF FUNCTION APP, STORAGE ACCOUNT AND APP INSIGHTS...${end}\n"

# Source subscription ID, and prep config file
source sub.env
sub_id=$SUB_ID

# Set the default subscription 
az account set -s $sub_id

# Source unique name for RG, workspace creation
#random_name_generator='/random_name.py'
#unique_name=$(python $PWD$random_name_generator)
unique_name='albatross'
number=$[ ( $RANDOM % 10000 ) + 1 ]
resourcegroup=$unique_name$number
storagename=$unique_name$number'storageacct'
appinsightsname=$unique_name$number'appinsights'
functionappname=$unique_name$number'functionapp'
dbname=$unique_name$number'db'
dbservername=$unique_name$number'dbserver'
adminusername=$unique_name'adminuser'
adminpassword=$(uuidgen)
location='westus'

# Create a resource group
printf "${grn}STARTING CREATION OF RESOURCE GROUP...${end}\n"
rg_create=$(az group create --name $resourcegroup --location $location)
printf "Result of resource group create:\n $rg_create \n"

# Create storage account
printf "${grn}STARTING CREATION OF STORAGE ACCOUNT...${end}\n"
result=$(az storage account create \
	--name $storagename \
	--location $location \
	--resource-group $resourcegroup \
	--sku 'Standard_LRS')
printf "Result of storage account create:\n $result \n"
sleep 20

# Get storage account connection string
printf "${grn}GETTING STORAGE ACCOUNT CONNECTION STRING...${end}\n"
storageaccountkey=$(az storage account show-connection-string \
	-g $resourcegroup \
	-n $storagename)

# Capture credentials for 'jq' parsing
credFile='cred.json'
printf "$storageaccountkey" > $credFile
sakey=$(cat $credFile | jq '.connectionString')
rm $credFile

# Create app insights
printf "${grn}STARTING CREATION OF APP INSIGHTS...${end}\n"
result=$(az monitor app-insights component create \
	--app $appinsightsname \
	--location $location \
	--resource-group $resourcegroup)
printf "Result of app insights create:\n $result \n"

# Create function app 
printf "${grn}STARTING CREATION OF FUNCTION APP...${end}\n"
result=$(az functionapp create \
	--name $functionappname \
	--storage-account $storagename \
	--app-insights $appinsightsname \
	--consumption-plan-location $location \
	--resource-group $resourcegroup \
	--os-type 'Linux' \
	--runtime 'python' \
	--runtime-version '3.8' \
	--functions-version 3)
printf "Result of function create:\n $result \n"


# Create Azure SQL Server 
printf "${grn}STARTING CREATION OF AZURE SQL SERVER...${end}\n"
result=$(az sql server create \
	--name $dbservername \
	--resource-group $resourcegroup \
	--location $location \
	--admin-user $adminusername \
	--admin-password $adminpassword)
printf "Result of Azure SQL Server create:\n $result \n"
sleep 40

# Configure a firewall rule on Azure SQL Server 
echo "Guessing your external IP address from ipinfo.io"
IP=$(curl -s ipinfo.io/ip)

printf "${grn}STARTING CREATION OF AZURE SQL SERVER FIREWALL RULE...${end}\n"
sqlserverdetails=$(az sql server firewall-rule create \
	--resource-group $resourcegroup \
	--server $dbservername \
	--n 'AllowYourIp' \
	--start-ip-address $IP \
	--end-ip-address $IP
)
printf "Result of Azure SQL Server Firewall create:\n $sqlserverdetails \n"
sleep 25

# Create SQL Database
printf "${grn}STARTING CREATION OF AZURE SQL DATABASE...${end}\n"
result=$(az sql db create \
	--name $dbname \
	--resource-group $resourcegroup \
	--server $dbservername \
	--edition 'Basic' \
)
printf "Result of Azure SQL Database create:\n $result \n"

# Create storage key variables file
printf "${grn}WRITING OUT STORAGE ACCOUNT CONNECTION STRING...${end}\n"
env_variable_file='storage_variables.env'
printf "CONN_STRING=$sakey \n" > $env_variable_file

# Write out function app name
printf "${grn}WRITE OUT FUNCTION APP NAME...${end}\n"
fa_variable_file='functionappname.env'
printf "FUNCAPPNAME=$functionappname \n" > $fa_variable_file

# Create database variables file
printf "${grn}WRITING OUT DATABASE VARIABLES...${end}\n"
env_variable_file='db_variables.env'
printf "HOST=$dbservername.database.windows.net \n" > $env_variable_file
printf "DATABASE=$dbname \n" >> $env_variable_file
printf "DB_USER=$adminusername \n" >> $env_variable_file
printf "DB_PWD=$adminpassword \n" >> $env_variable_file

printf "${grn}GRAB A COFFEE FOR 20 SECONDS......${end}\n"
sleep 20 # just to give time for artifacts to settle in the system, and be accessible
