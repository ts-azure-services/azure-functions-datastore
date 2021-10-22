#!/bin/bash
#Script to provision a new Azure ML workspace
grn=$'\e[1;32m'
end=$'\e[0m'

# Start of script
SECONDS=0
printf "${grn}CLEANING UP FUNCTION APP, AND ASSOCIATED FILES...${end}\n"
sleep 2

rm -rf ./.vscode
rm -rf ./.python_package
rm -rf ./fa1
rm -rf ./fa2
rm ./getting_started.md
rm ./host.json
rm ./local.settings.json

