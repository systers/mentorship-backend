dev: 
	python run.py
docker_host_dev: 
	flask run --host 0.0.0.0
python_tests: 
	python -m unittest discover tests 
docker_test: 
	docker-compose -f docker-compose.test.yml up --build --remove-orphans --no-color --abort-on-container-exit mentorship_system_test 
docker_dev: 
	docker-compose up --build --remove-orphans 
generate_cov: 
	pip install pytest  
	pip install pytest-cov
	pytest --cov=. --cov-report=xml
	mv ./coverage.xml /dockerbuild/cov/
	
