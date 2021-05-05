This document contains some examples of test cases for each feature implemented on the backend.

**Tools:**
- Create disposable emails to create accounts and verify them. You can use https://temp-mail.org/ to generate the emails and verify them;
- Test the REST API with Swagger UI provided in the link of the deployed server;
- Test the REST API using [Postman](https://www.getpostman.com) (if you feel comfortable with this).

**Notes:**
- Outcome _Fail_ means the test case as no effect in the database, so no changes are done in the data. An error message should be returned;
- Outcome _Success_ means that the test case was successful and had an effect in the database, so this change/effect should be visible on the database. E.g.: If a user is registered successfully, you should be able to login, and be seen using the GET /users API;
- When testing something make sure only one aspect of the test is failing the requirements;
- “Logged in” means that a valid access token is being sent in the Authorization header;
- Nonrestricted API will have a marker -> (not restricted);
- A user can login successfully only if the email is verified.

## Access to restricted APIs

- This is the possible test cases when accessing a restricted API;
- The only unrestricted APIs are: POST /login, POST /register, GET /user/confirm_email/{token}, POST/user/resend_email;
- _Fail_ cases mean that you cannot access the app data and you’ll receive an error message regarding the authentication token;
- __This cases should override any potential success outcome from a restricted API_._

| Test Case                                                                                                                    | Outcome |
|------------------------------------------------------------------------------------------------------------------------------|---------|
| Send an Authorization header field containing: Bearer <access_token>. This token is valid, not expired, from a verified user | Success |
| Not send the access token                                                                                                    | Fail    |
| Access token is expired                                                                                                      | Fail    |
| Invalid token (e.g.: "asdf", "gnvindgins", something not returned from POST /login)                                          | Fail    |
| (weird case) Valid token, but the user was deleted                                                                           | Fail    |

## Users

### Login

**Service:** POST /login

| Test Case       | Outcome |
| ------------- | ------------- |
| Login an already registered and verified User with the correct username and password | Success |
| Login an already registered and verified User with correct email and password | Success |
| Login an already registered User with correct email and password, with email unverified | Fail |
| Login an already registered and verified User with correct email/username and wrong password | Fail |
| Login a User with non-existing email | Fail |
| Login a User with non-existing username | Fail |

### Register

**Service:** POST /register

| Test Case       | Outcome |
| ------------- | ------------- |
| Register a User with all fields present in the request body and valid (not empty, username and email are unique, email is a valid one) ones | Success |
| Register a User with terms and conditions checked (=True)      | Success      |
| Register User without sending Authorization Header with token | Success |
| Register a User with terms and conditions unchecked (=False) | Fail |
| Register a User with username and email from an already existing User | Fail |
| Register a User with one of the these fields missing from the request body: name, username, email, terms_and_conditions, password | Fail |
|Register a User with one of the these fields empty from the request body: name, username, email, terms_and_conditions, password | Fail |
|Register a User with invalid email (invalid does not respect e.g.: {A-Z, a-z, 0-9, _,-}@{A-Z, a-z, 0-9}.{A-Z, a-z, 0-9}) | Fail |

### Change Password

**Service:** PUT /user/change_password

| Test Case       | Outcome |
| ------------- | ------------- |
| Change password to a different password from the current one | Success |
| Change password to a password equal to the current one      | Fail |
| Change password to an empty password | Fail |
| Change password to a password with white spaces | Fail |

### Update User

**Service:** PUT /user

| Test Case                                                        | Outcome |
|------------------------------------------------------------------|---------|
| TBD                                                              | Success |
| Change username to a username already being used by another User | Fail    |

### Resend verification email

**Service:** POST /user/resend_email

| Test Case                                                                   | Outcome |
|-----------------------------------------------------------------------------|---------|
| Email in request body is an email from an existing user which is unverified | Success |
| Email in request body does not belong to a registered User                  | Fail    |
| Email in request body is from a Verified User                               | Fail    |

### Refresh token

**Service:** POST /user/refresh

| Test Case                                                        					  | Outcome |
|------------------------------------------------------------------------------------ |---------|
|Refresh token in Authorization field is the refresh token returned on login response | Success |
|Refresh token in Authorization field is not valid or without Bearer                  | Fail    |
|Refresh token in the Authorization field is expired               					  | Fail    |
|No Refresh token is given in the Authorization field after Bearer    			      | Fail    |


## Mentorship Relation

### Send request

**Service:** POST /mentorship_relation/send_request

| Test Case                                                                                                                                                                | Outcome |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| A User1 sends a request to a User2 which is not currently involved in a mentorship relation and has the email verified                                                   | Success |
| A User1 sends a request to a User2 which is in involved in a mentorship relation and has the email verified                                                              | Fail    |
| A User1 sends a request to a non existing User2 (user_id does not match any user in database)                                                                            | Fail    |
| A User1 sends a request to a User2 which is not involved in a mentorship relation and has the email verified. But the User1 is involved in a current mentorship relation | Fail    |
| A User1 sends a request to itself User1                                                                                                                                  | Fail    |
| A User1 sends a request to a User2, which does not have its email verified                                                                                               | Fail    |

### Delete Relation

**Service:** DELETE /mentorship_relation/{request_id}

| Test Case     | Outcome |
| ------------- | ------------- |
| A user that creates a mentorship request X deletes this mentorship request X | Success |
| A user that creates a mentorship request X deletes this mentorship request X (without token being sent in Authorization Header)  | Fail |
| A user that did not create mentorship request X tries to deletes mentorship request X | Fail |
| A user that tries to delete mentorship request X that does not exist (i.e., request_id does not exist in the system) | Fail |

### Accept Relation
**Service:** PUT /mentorship_relation/{request_id}/accept

| Test Case     | Outcome |
| ------------- | ------------- |
| Assuming User1 sent request X to User2, User2 accepts this request, while User2 is NOT involved in a current mentorship relation | Success |
| Assuming User1 sent request X to User2, User2 accepts this request, while User2 is involved in a current mentorship relation  | Fail |
| Assuming User1 sent request X to User2, User1 accepts this request | Fail |
| User1 accepts a mentorship relation which the User1 is not involved with | Fail |

### Reject Relation

**Service:**  PUT /mentorship_relation/{request_id}/reject

| Test Case     | Outcome |
| ------------- | ------------- |
| Having User1 sending a request to User2, User2 rejects this request | Success |
| Having User1 sending a request to User2, User1 rejects this request | Fail |
| User1 rejects a mentorship relation which the User1 is not involved with | Fail |

### Cancel Relation

**Service:** PUT /mentorship_relation/{request_id}/cancel

| Test Case     | Outcome |
| ------------- | ------------- |
| User1 (sent the request) cancels a mentorship relation that it is currently involved with User2 (the relation is in an ACCEPTED state) | Success |
| User2 (received the request) cancels a mentorship relation that it is currently involved with User1 (the relation is in an ACCEPTED state)  | Success |
| User1 cancel a mentorship relation which the User1 is not involved with | Fail |

### Update task

**Service:** PUT /mentorship_relation/{request_id}/task/{task_id}/complete

| Test Case       | Outcome |
| ------------- | ------------- |
| Logged in user completes task from an existing request in the ACCEPTED state, that involves the user (as a mentor or as a mentee) | Success |
| Logged in user tries to complete a task whose id does not exist, from an existing request in the ACCEPTED state, that involves the user (as a mentor or as a mentee) | Fail |
| Logged in user tries to complete a task which has already been completed, from an existing request in the ACCEPTED state, that involves the user (as a mentor or as a mentee) | Fail |
| Logged in user tries to complete a task, from an existing request in the ACCEPTED state, that does not involve the user (neither as a mentor nor as a mentee) | Fail |
| Not logged in user (invalid token) tries to complete a task, from an existing request in the ACCEPTED state | Fail |
| Logged in user tries to complete a task, with an invalid request (not an integer) | Fail |
| Logged in user tries to complete a task which is invalid (not an integer), from an existing request in the ACCEPTED state   | Fail |
| Logged in user tries to complete a task from an non existing request for this relationship (The request doesn't exist in any other relationship) | Fail |
| Logged in user tries to complete a task from an non existing request (The request  exists in a different relationship) | Fail |
| Logged in user tries to complete a task from a request which is not in the ACCEPTED state (as a mentor or as a mentee) | Fail |


### Tasks

#### Create

**Service:** POST /mentorship_relation/{relation_id}/task

|  Test Case                                                                                | Outcome |
| ----------------------------------------------------------------------------------------- |-------- |
| Create a task for a relation, in the accepted state, between logged user and another user | Success |
| Creating a task without a description (either empty or not in the request body at all)    | Fail    |
| Create a task when a logged user is not involved in the relation                          | Fail    |
| Create a task if relation state is different than accepted                                | Fail    |

#### List All Tasks

**Service:** GET /mentorship_relation/{request_id}/task

| Test Case                                                                                                                                               | Outcome |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Logged in user requests list all task,or out of all task,for a mentorship relation those which involves the user (as a mentor or as a mentee)           | Success |
| Logged in user requests list all task,or out of all task, for a mentorship relation which does not involves the user (neither as a mentor nor as a mentee) | Fail |
| Logged in user requests to list all task for a invalid mentorship relation , which involves the user (as a mentor or as a mentee)                       | Fail |     
| Not logged in user requests to List all task for any valid/invalid mentorship relation                                                                  | Fail |


## Admins

Only admin users have access to this.

### Assign a new admin

**Service:** POST /admin/new

| Test Case       | Outcome |
| ------------- | ------------- |
| An Admin User assigns admin role to a non-admin user ( both users should have email verified) | Success |
| A User which is not an Admin assigns admin role to any user (does not matter if the user being assigned is admin or not)  | Fail |
| A User which is not an Admin assigns admin role to itself | Fail |
| An Admin User assigns admin role to a non-existent User | Fail |

### Revoke an admin role

**Service:** POST /admin/remove

| Test Case       | Outcome |
| ------------- | ------------- |
| Revoking an admin user which is an admin, when the current user is an admin | Success |
| Revoking a non-admin user, when the current user is an admin | Fail |
| Revoking a non-existent user | Fail |
| Revoke self the admin role when self is the only admin | Fail |
| Revoke self the admin role when self is not the only admin | Success |
| Revoking an admin user, when the current user is not an admin | Fail |

### Returns all admin users

**Service:** GET /admins

| Test Case                                                                                | Outcome |
| ---------------------------------------------------------------------------------------- | ------- |
| An Admin User with valid access returns all assigned non-admin user which are now admins | Success |
| A User which is not an admin requests to return all assigned non-admin user              | Fail    |
| An Admin User tries to find a non-admin user , when returns all admin users              | Fail    |
| An Admin User returns self details                                                       | Fail    |

## Tasks

### Confirmation of users email

**Service:** GET /user/confirm_email/{token}

| Test Case                                                                                      | Outcome |
|------------------------------------------------------------------------------------------------|---------|
| Verification token entered is one sent on users registered email entered within 24 hrs         | Success |
| Verification token of already confirmed users account entered                                  | Success |
| Verification token of un-confirmed users account entered after 24 hrs of email being sent      | Fail    |
| Incorrect verification token entered in request body                                           | Fail    |                                                    
