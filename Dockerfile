FROM python:3.7
COPY ./requirements.txt /dockerBuild/requirements.txt
WORKDIR /dockerBuild
RUN pip install --no-cache-dir -r requirements.txt
ENV DB_TYPE=postgresql
ENV DB_USERNAME=postgres
ENV DB_PASSWORD=postgres
ENV DB_ENDPOINT=postgres:5432
ENV DB_TEST_ENDPOINT=test_postgres:5432 
ENV DB_NAME=mentorship_system
ENV DB_TEST_NAME=mentorship_system_test
ENV POSTGRES_HOST=postgres
ENV POSTGRES_PORT=5432 
ENV FLASK_ENVIRONMENT_CONFIG=dev
ENV FLASK_APP=run.py
COPY . /dockerBuild
ENTRYPOINT [ "make" ]
CMD [ "docker_host_dev" ]
