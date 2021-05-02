# Mentorship System (Backend)

![Build Status](https://github.com/anitab-org/mentorship-backend/workflows/Run%20tests/badge.svg)
[![codecov](https://codecov.io/gh/anitab-org/mentorship-backend/branch/develop/graph/badge.svg)](https://codecov.io/gh/anitab-org/mentorship-backend)
[![project chat](https://img.shields.io/badge/zulip-join_chat-brightgreen.svg)](https://anitab-org.zulipchat.com/#narrow/stream/222534-mentorship-system)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![Docs](https://img.shields.io/badge/documentation-mentorship--backend-blue.svg)](https://anitab-org.github.io/mentorship-backend)


Mentorship System is an application that allows women in tech to mentor each other, on career development topics, through 1:1 relations for a certain period.
This is the Backend REST API for the Mentorship System.

This API is being used by 3 frontend projects currently being developed:
- android: [anitab-org/mentorship-android](https://github.com/anitab-org/mentorship-android)
- iOS: [anitab-org/mentorship-ios](https://github.com/anitab-org/mentorship-ios)
- flutter: [anitab-org/mentorship-flutter](https://github.com/anitab-org/mentorship-flutter)

**Table of Contents**

- [Features](#Features)
- [Setup and run](#setup-and-run)
    - [Run app in Windows](#run-app-in-Windows)
    - [Run app in Linux](#run-app-in-Linux)
    - [Run with Docker](#run-with-docker)
    - [Run tests](#run-tests)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Branches](#branches)
- [Contact](#contact)
- [License](#license)

## Features

- Login and register a new user
- Create a user profile, view and edit user profiles
- Change user password, refresh jwt tokens
- Create relation between two users with a fixed period of time
- Both mentor and mentee in a relation can create tasks
- Assign and remove admin roles to users and list all admins
- List all the relationships of a given user
- List details of current, past and pending mentorship relations
- Create a new task in a mentorship relation if the specified user is already involved in it.
- Retrieve and delete tasks from mentorship relation
- Task comment functionalities like create a task comment, get task comments using a task id.
- Get statistics of a user like Pending Requests, Accepted Requests, Rejected Requests, Completed Relations, Cancelled Relations and upto 3 recent achievements

## Setup and run

To setup the project locally read these wiki pages and follow the instructions:

 - [Fork, Clone and Remote](https://github.com/anitab-org/mentorship-backend/wiki/Fork%2C-Clone-%26-Remote)
 - [Export Environment Variables](docs/environment-variables.md)

### Run app in Windows

The project runs on Python 3.

1. Create a virtual environment:
```
virtualenv venv --python=python3
```

2. Activate the virtual environment:
For Git Bash Users:
```
source ./venv/Scripts/activate
```
For Windows Command Line Users:
```
venv\Scripts\activate
```

3. Install all the dependencies in `requirements.txt` file:
```
pip install -r requirements.txt
```

4. Make sure you create `.env` using `.env.template` and update the values of corresponding environment variables
or make sure you exported the following [environment variables](docs/environment-variables.md):

```
export FLASK_ENVIRONMENT_CONFIG=<local-or-dev-or-test-or-prod-or-stag>
export SECRET_KEY=<your-secret-key>
export SECURITY_PASSWORD_SALT=<your-security-password-salt>
export MAIL_DEFAULT_SENDER=<mail-default-sender>
export MAIL_SERVER=<mail-server>
export APP_MAIL_USERNAME=<app-mail-username>
export APP_MAIL_PASSWORD=<app-mail-password>
export MOCK_EMAIL=<True-or-False>
```

If you're testing any environment other than "local", then you have to also set these other variables:
```
export DB_TYPE=<database_type>
export DB_USERNAME=<database_username>
export DB_PASSWORD=<database_password>
export DB_ENDPOINT=<database_endpoint>
export DB_NAME=<database_name>
```

5. Run the app:
```
python run.py
```

6. Navigate to http://localhost:5000 in your browser

7. When you are done using the app, deactivate the virtual environment:
```
deactivate
```

### Run app in Linux

The project runs on Python 3.

1. Create a virtual enviorntment:
```
virtualenv venv
```

2. Activate the virtual environment:
```
source venv/bin/activate
```

3. Install all the dependencies in `requirements.txt` file:
```
pip3 install -r requirements.txt
```

4. Make sure you create `.env` using `.env.template` and update the values of corresponding environment variables. Make sure you exported the following [environment variables](docs/environment-variables.md) if you didn't adapt `.env.template` in the `.env` file:

```
export FLASK_ENVIRONMENT_CONFIG=<local-or-dev-or-test-or-prod-or-stag>
export SECRET_KEY=<your-secret-key>
export SECURITY_PASSWORD_SALT=<your-security-password-salt>
export MAIL_DEFAULT_SENDER=<mail-default-sender>
export MAIL_SERVER=<mail-server>
export APP_MAIL_USERNAME=<app-mail-username>
export APP_MAIL_PASSWORD=<app-mail-password>
export MOCK_EMAIL=<True-or-False>
```

If you're testing any environment other than "local", then you have to also set these other variables in the .env file.
```
export DB_TYPE=<database_type>
export DB_USERNAME=<database_username>
export DB_PASSWORD=<database_password>
export DB_ENDPOINT=<database_endpoint>
export DB_NAME=<database_name>
```

Use: `printenv` to print the environment variables and check all configurations.

5. Run the app with `python run.py` or:
```
 export FLASK_APP=run.py
 flask run
```

6. Navigate to http://localhost:5000 or the current server in which you are running(will be shown when app is running) in your browser.

7. When you are done using the app, deactivate the virtual environment:
```
deactivate
```

or use:

```
source deactivate
```

### Run with docker

1. Make sure you exported the following [environment variables](docs/environment-variables.md) to `.env` file

2. Build docker image
```
docker build -t mentorship-backend:latest .
```
3. Deploy
Docker container ports must be mapped to the host machine port using '--publish' so they're visible.
```sh
docker run --env "FLASK_APP=run.py" --publish 5000:5000 mentorship-backend:latest
```

### Run tests

To run the unitests run the following command in the terminal (while the virtual environment is activated):

```
python -m unittest discover tests
```

### Auto-formatting with black

We use [_Black_](https://github.com/psf/black) to format code automatically so that we don't have to worry about clean and
readable code. To install _Black_:

```
pip install black
```

To run black:

```
black .
```

### Run migration Scripts

* For new contributors who just completed environment setup, run the following command **AFTER** running the application for the first time.

```
flask db stamp head
```

This will attach the alembic version number on the repo (if any) to the local db.

* For existing contributors, run the following command:

```
flask db upgrade
```

This will apply the changes to the existing local db as well as attach the alembic version number. 

 
## Documentation

Documentation for the project is hosted [here](https://anitab-org.github.io/mentorship-backend/). We use Docusaurus for maintaining the documentation of the project.

You can learn more about this project through the documentation in the [docs](./docs) folder and on [our Wiki](https://github.com/anitab-org/mentorship-backend/wiki).

- **Language:** Python 3
- **Framework:** [Flask](http://flask.pocoo.org/)
- **Flask Extensions:** [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/), [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org), [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/en/latest/), [Flask-Mail](https://pythonhosted.org/Flask-Mail)

Here are some links to documentation for this project:

- [How to use Backend Swagger UI](https://github.com/anitab-org/mentorship-backend/wiki/Using-Backend-Swagger-UI) and [test PR guide](/docs/test-pr-guide.md) contains a few resources for you to understand how to use the Swagger user interface provided by this app.
- [Features Overview](/docs/features.md) has a high level understanding of the features this application has.
- [Future ideas for the project](https://github.com/anitab-org/mentorship-backend/wiki/Future-ideas).
- [Troubleshoot guide](/docs/troubleshoots.md) contains common isssues other contributors may run into in their setup.
- [Quality Assurance test cases](/docs/quality-assurance-test-cases.md) has test cases for each endpoint we have which you can use to learn about how each feature should work.
- [CI/CD Process](/docs/ci_cd_process.md) which explains the processes and tools involved in deploying new code.
- [Code Organisation](/docs/code_organization.md) which explains the code organisation and architecture within the repository.
- [User Authentication](/docs/user_authentication.md) which is JSON Web Token (JWT) based and tells about the user authentication in the application.

Understand more about our technical decisions made along with this project development in [Technical Decisions Wiki page](https://github.com/anitab-org/mentorship-backend/wiki/Technical-Decisions).

## Contributing

Please read our [Contributing guidelines](./.github/CONTRIBUTING.md), [Code of Conduct](./docs/code_of_conduct.md) and [Reporting Guidelines](./docs/reporting_guidelines.md)

Please follow our [Commit Message Style Guide](https://github.com/anitab-org/mentorship-backend/wiki/Commit-Message-Style-Guide) and [Coding Standards](./docs/coding_standards.md) while sending PRs.

### Contributors

Thanks goes to these people ([emoji key](https://github.com/all-contributors/all-contributors#emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://isabelcosta.github.io/"><img src="https://avatars.githubusercontent.com/u/11148726?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Isabel Costa</b></sub></a><br /><a href="#maintenance-isabelcosta" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/vj-codes"><img src="https://avatars.githubusercontent.com/u/60894542?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Vaishnavi Joshi</b></sub></a><br /><a href="#maintenance-vj-codes" title="Maintenance">🚧</a> <a href="#design-vj-codes" title="Design">🎨</a></td>
    <td align="center"><a href="https://github.com/epicadk"><img src="https://avatars.githubusercontent.com/u/56596662?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Aditya Kurkure</b></sub></a><br /><a href="https://github.com/anitab-org/mentorship-backend/commits?author=epicadk" title="Code">💻</a> <a href="#maintenance-epicadk" title="Maintenance">🚧</a> <a href="https://github.com/anitab-org/mentorship-backend/commits?author=epicadk" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/devkapilbansal"><img src="https://avatars.githubusercontent.com/u/42766576?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Kapil Bansal</b></sub></a><br /><a href="https://github.com/anitab-org/mentorship-backend/commits?author=devkapilbansal" title="Code">💻</a> <a href="#maintenance-devkapilbansal" title="Maintenance">🚧</a> <a href="https://github.com/anitab-org/mentorship-backend/commits?author=devkapilbansal" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/gaurivn"><img src="https://avatars.githubusercontent.com/u/48416306?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Gauri V. Nair</b></sub></a><br /><a href="https://github.com/anitab-org/mentorship-backend/commits?author=gaurivn" title="Code">💻</a> <a href="#maintenance-gaurivn" title="Maintenance">🚧</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification.
Contributions of any kind welcome!

## Branches

The repository has the following permanent branches:

 * **master** This contains the code which has been released.

 * **develop** This contains the latest code. All the contributing PRs must be sent to this branch. When we want to release the next version of the app, this branch is merged into the `master` branch. This is the branch that is used in the deployed version of the app on Heroku.

 * **bit** This branch is for Mentorship System backend and [BridgeInTech backend](https://github.com/anitab-org/bridge-in-tech-backend) full integration version. All the contributing PRs related to BIT-MS integration issue must be sent to this branch.<br>. 


## Contact

You can reach the maintainers and our community on [AnitaB.org Open Source Zulip](https://anitab-org.zulipchat.com/). If you are interested in contributing to the mentorship system, we have a dedicated stream for this project [#mentorship-system](https://anitab-org.zulipchat.com/#narrow/stream/222534-mentorship-system), where you can ask questions and interact with the community, join with us!

## License

Mentorship System is licensed under the GNU General Public License v3.0. Learn more about it in the [LICENSE](LICENSE) file.
