install:
	pip install --upgrade pip && pip install -r requirements.txt
	./create-function-app.sh

function_setup:
	func init --worker-runtime python
	func new --template "Timer trigger" --name fa1
	func new --template "Timer trigger" --name fa2

copy_artifacts:
	# Copy function app 1 artifacts
	cp ./function_app_1_artifacts/fa1_init.py ./fa1/__init__.py
	cp ./function_app_1_artifacts/fa1_function_json.sample ./fa1/function.json

	# Copy function app 2 artifacts
	cp ./function_app_2_artifacts/fa2_init.py ./fa2/__init__.py
	cp ./function_app_2_artifacts/fa2_function_json.sample ./fa2/function.json

publish_app:
	. functionappname.env;\
		echo functionappname: $${FUNCAPPNAME}; \
	func azure functionapp publish $${FUNCAPPNAME}

all: install function_setup copy_artifacts publish_app
