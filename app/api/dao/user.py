from datetime import datetime
from operator import itemgetter

from app import messages
from app.api.email_utils import confirm_token
from app.api.models.user import full_user_api_model
from app.database.models.user import UserModel
from app.api.dao.task import TaskDAO
from app.utils.decorator_utils import email_verification_required
from app.utils.enum_utils import MentorshipRelationState
from app.utils.validation_utils import is_email_valid
from flask_restplus import marshal

class UserDAO:
    """Data Access Object for User functionalities"""

    FAIL_USER_ALREADY_EXISTS = "FAIL_USER_ALREADY_EXISTS"
    SUCCESS_USER_CREATED = "SUCCESS_USER_CREATED"
    MIN_NUMBER_OF_ADMINS = 1

    @staticmethod
    def create_user(data):
        """Creates a new user.
        
        Creates a new user with provided data.
        
        Arguments:
            data: A list containing the user's name, username, password, and email, as well as recognition that they have read and agree to the Terms and Conditions.
            
        Returns:
            A tuple with two elements. The first element is a dictionary containing a key 'message' containing a string which indicates whether or not the user was created successfully. The second is the HTTP response code.
        """

        name = data['name']
        username = data['username']
        password = data['password']
        email = data['email']
        terms_and_conditions_checked = data['terms_and_conditions_checked']

        existing_user = UserModel.find_by_username(data['username'])
        if existing_user:
            return messages.USER_USES_A_USERNAME_THAT_ALREADY_EXISTS, 400
        else:
            existing_user = UserModel.find_by_email(data['email'])
            if existing_user:
                return messages.USER_USES_AN_EMAIL_ID_THAT_ALREADY_EXISTS, 400

        user = UserModel(name, username, password, email, terms_and_conditions_checked)
        if 'need_mentoring' in data:
            user.need_mentoring = data['need_mentoring']

        if 'available_to_mentor' in data:
            user.available_to_mentor = data['available_to_mentor']

        user.save_to_db()

        return messages.USER_WAS_CREATED_SUCCESSFULLY, 200

    @staticmethod
    @email_verification_required
    def delete_user(user_id):
        """ Deletes a user.
        
        Deletes the specified user and removes them from the directory, with checks to make sure that the user exists and is not the only administrator.
        
        Arguments:
            user_id: The ID of the user to be deleted.
            
        Returns: 
            A tuple with two elements. The first element is a dictionary containing a key 'message' containing a string which indicates whether or not the user was created successfully. The second is the HTTP response code.
        """

        user = UserModel.find_by_id(user_id)

        # check if this user is the only admin
        if user.is_admin:

            admins_list_count = len(UserModel.get_all_admins())
            if admins_list_count <= UserDAO.MIN_NUMBER_OF_ADMINS:
                return messages.USER_CANT_DELETE, 400

        if user:
            user.delete_from_db()
            return messages.USER_SUCCESSFULLY_DELETED, 200

        return messages.USER_DOES_NOT_EXIST, 404

    @staticmethod
    @email_verification_required
    def get_user(user_id):
        """ Retrieves a user's profile information using a specified ID.
        
        Provides the user profile of the user whose ID matches the one specified.
        
        Arguments:
            user_id: The ID of the user to be searched.
        
        Returns:
            The UserModel class of the user whose ID was searched, containing the public information of their profile such as bio, location, etc.
        
        """

        return UserModel.find_by_id(user_id)

    @staticmethod
    def get_user_by_email(email):
        """ Retrieves a user's profile information using a specified email.
        
        Provides the user profile of the user whose email matches the one specified.
        
        Arguments:
            email: The email of the user to be searched.
        
        Returns:
            The UserModel class of the user whose email was searched, containing the public information of their profile such as bio, location, etc.
        
        """

        return UserModel.find_by_email(email)

    @staticmethod
    def get_user_by_username(username):
        """ Retrieves a user's profile information using a specified username.
        
        Provides the user profile of the user whose username matches the one specified.
        
        Arguments:
            username: The ID of the user to be searched.
        
        Returns:
            The UserModel class of the user whose username was searched, containing the public information of their profile such as bio, location, etc.
        
        """

        return UserModel.find_by_username(username)

    @staticmethod
    def list_users(user_id, is_verified=None):
        """ Retrieves a list of verified users with the specified ID.
        
        Arguments:
            user_id: The ID of the user to be listed.
            is_verified: Status of the user's verification; None when provided as an argument.
        
        Returns:
            A list of users matching conditions and the HTTP response code.
        
        """

        users_list = UserModel.query.filter(UserModel.id != user_id).all()
        list_of_users = []
        if is_verified:
            for user in users_list:
                if user.is_email_verified:
                    list_of_users += [user.json()]
        else:
            list_of_users = [user.json() for user in users_list]

        return list_of_users, 200

    @staticmethod
    @email_verification_required
    def update_user_profile(user_id, data):
        """ Updates the profile of a specified user with new data.
        
        Replaces old data items with new ones in the provided data list, with a check for overlap between users in username and a check that a user with the specified ID exists
        
        Arguments:
            user_id: The ID of the user whose data will be updated.
            data: A list containing the user's information such as name, bio, location, etc.
        
        Returns:
            A message that indicates whether the update was successful or not and a second element which is the HTTP response code.
        
        """

        user = UserModel.find_by_id(user_id)
        if not user:
            return messages.USER_DOES_NOT_EXIST, 404

        username = data.get('username', None)
        if username:
            user_with_same_username = UserModel.find_by_username(username)

            # username should be unique
            if user_with_same_username:
                return messages.USER_USES_A_USERNAME_THAT_ALREADY_EXISTS, 400

            user.username = username

        if 'name' in data and data['name']:
            user.name = data['name']

        if 'bio' in data:
            if data['bio']:
                user.bio = data['bio']
            else:
                user.bio = None

        if 'location' in data:
            if data['location']:
                user.location = data['location']
            else:
                user.location = None
            
        if 'occupation' in data:
            if data['occupation']:
                user.occupation = data['occupation']
            else:
                user.occupation = None

        if 'organization' in data:
            if data['organization']:
                user.organization = data['organization']
            else:
                user.organization = None

        if 'slack_username' in data:
            if data['slack_username']:
                user.slack_username = data['slack_username']
            else:
                user.slack_username = None

        if 'social_media_links' in data:
            if data['social_media_links']:
                user.social_media_links = data['social_media_links']
            else:
                user.social_media_links = None

        if 'skills' in data:
            if data['skills']:
                user.skills = data['skills']
            else:
                user.skills = None

        if 'interests' in data:
            if data['interests']:
                user.interests = data['interests']
            else:
                user.interests = None

        if 'resume_url' in data:
            if data['resume_url']:
                user.resume_url = data['resume_url']
            else:
                user.resume_url = None

        if 'photo_url' in data:
            if data['photo_url']:
                user.photo_url = data['photo_url']
            else:
                user.photo_url = None

        if 'need_mentoring' in data:
            user.need_mentoring = data['need_mentoring']

        if 'available_to_mentor' in data:
            user.available_to_mentor = data['available_to_mentor']

        user.save_to_db()

        return messages.USER_SUCCESSFULLY_UPDATED, 200

    @staticmethod
    @email_verification_required
    def change_password(user_id, data):
        """ Changes the user's password.
        
        Finds the user with the given ID, checks their current password, and then updates to the new one.
        
        Arguments:
            user_id: The ID of the user to be searched.
            data: The user's current and new password.
        
        Returns:
            A message that indicates whether the password change was successful or not and a second element which is the HTTP response code.
        
        """

        current_password = data['current_password']
        new_password = data['new_password']

        user = UserModel.find_by_id(user_id)
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save_to_db()
            return messages.PASSWORD_SUCCESSFULLY_UPDATED, 201

        return messages.USER_ENTERED_INCORRECT_PASSWORD, 400

    @staticmethod
    def confirm_registration(token):
        """ Determines whether a user's email registration has been confirmed.
        
        Determines whether a user's email registration was invalid, previously confirmed, or just confirmed.
        
        Arguments:
            token: Serialized and signed email address as a URL safe string.
        
        Returns:
            A message that indicates if the confirmation was invalid, already happened, or just happened, and the HTTP response code.
        
        """

        email_from_token = confirm_token(token)

        if not email_from_token or email_from_token is None:
            return messages.EMAIL_EXPIRED_OR_TOKEN_IS_INVALID, 400

        user = UserModel.find_by_email(email_from_token)
        if user.is_email_verified:
            return messages.ACCOUNT_ALREADY_CONFIRMED, 200
        else:
            user.is_email_verified = True
            user.email_verification_date = datetime.now()
            user.save_to_db()
            return messages.ACCOUNT_ALREADY_CONFIRMED_AND_THANKS, 200

    @staticmethod
    def authenticate(username_or_email, password):
        """ User login process.
        
        The user can login with two options:
        -> username + password
        -> email + password
        
        Arguments:
            username_or_email: The username or email associated with the account being authenticated.
            password: The password associated with the account being authenticated.
            
        Returns:
            Returns authenticated user if username and password are valid, otherwise returns None.
        """

        if is_email_valid(username_or_email):
            user = UserModel.find_by_email(username_or_email)
        else:
            user = UserModel.find_by_username(username_or_email)

        if user and user.check_password(password):
            return user

        return None

    @staticmethod
    @email_verification_required
    def get_achievements(user_id):
        """Shows a subset of the user's achievements

        Gets all the completed tasks of the user and
        return them in a list. Achievements are completed tasks

        Args:
            user_id: The ID of the user for whom tasks are
                requested.

        Returns:
            achievements: A list containing the user's achievements
        """
        user = UserModel.find_by_id(user_id)
        all_relations = user.mentor_relations + user.mentee_relations
        tasks = []
        for relation in all_relations:
            tasks += relation.tasks_list.tasks
        achievements = [task for task in tasks if task.get("is_done")]
        return achievements

    @staticmethod
    def get_user_statistics(user_id):
        """Shows some basic user statistics

        Gets the following statistics of the user:
        -> Pending Requests
        -> Accepted Requests
        -> Rejected Requests
        -> Completed Relations
        -> Cancelled Relations
        -> Up to 3 recent achievements

        Args:
            user_id: The id of the user for whom stats are requested

        Returns:
            A dict containing the stats (if the user ID is valid)
            If user ID is invalid, returns None
        """
        user = UserModel.find_by_id(user_id)

        if not user:
            return None

        all_relations = user.mentor_relations + user.mentee_relations
        (pending_requests, accepted_requests, rejected_requests, completed_relations, cancelled_relations) = (
            0, 0, 0, 0, 0)
        for relation in all_relations:
            if relation.state == MentorshipRelationState.PENDING:
                pending_requests += 1
            elif relation.state == MentorshipRelationState.ACCEPTED:
                accepted_requests += 1
            elif relation.state == MentorshipRelationState.REJECTED:
                rejected_requests += 1
            elif relation.state == MentorshipRelationState.COMPLETED:
                completed_relations += 1
            elif relation.state == MentorshipRelationState.CANCELLED:
                cancelled_relations += 1

        achievements = UserDAO.get_achievements(user_id)
        if achievements:
            # We only need the first three of these achievements
            achievements = achievements[0:3]
            sorted(achievements, key=itemgetter("created_at"))

        response = {
            'name': user.name,
            'pending_requests': pending_requests,
            'accepted_requests': accepted_requests,
            'rejected_requests': rejected_requests,
            'completed_relations': completed_relations,
            'cancelled_relations': cancelled_relations,
            'achievements': achievements
        }
        return response

    @staticmethod
    def get_user_dashboard(user_id):
        """Shows user dashboard statistics

        Gets the following statistics of the user:
        -> user_details
            - id, name, username, email, password_hash, terms_and_conditions_checked, is_admin,
            registration_date, is_email_verified, email_verification_date, bio, location,
            occupation, organization, slack_username, social_media_links, skills, interests,
            resume_url, photo_url, need_mentoring, available_to_mentor,
            current_mentorship_role, membership_status
        -> Mentorship relations
            - received_as_mentee, sent_as_mentee, received_as_mentor, sent_as_mentor
                - states: PENDING, ACCEPTED, REJECTED, CANCELLED, COMPLETED
                    - id, username, photo_url, creation_date, accept_date, start_date, end_date, notes
        -> Tasks: todo, done
            - id, description, is_done, created_at, completed_at

        Args:
            user_id: The id of the user for whom stats are requested

        Returns:
            A dict containing the stats (if the user ID is valid)
            If user ID is invalid, returns None
        """
        user = UserModel.find_by_id(user_id)

        if not user:
            return None

        user_details = marshal(UserDAO.get_user(user_id), full_user_api_model)

        received_as_mentee = {'PENDING': [], 'ACCEPTED': [], 'REJECTED': [], 'CANCELLED': [], 'COMPLETED': []}
        sent_as_mentee = {'PENDING': [], 'ACCEPTED': [], 'REJECTED': [], 'CANCELLED': [], 'COMPLETED': []}

        received_as_mentor = {'PENDING': [], 'ACCEPTED': [], 'REJECTED': [], 'CANCELLED': [], 'COMPLETED': []}
        sent_as_mentor = {'PENDING': [], 'ACCEPTED': [], 'REJECTED': [], 'CANCELLED': [], 'COMPLETED': []}

        tasks_sorted = {'todo':[], 'done': []}

        # user as mentee
        for relation in user.mentee_relations:
            relation_field = {
                'id': 0, 'mentor_id': '', 'username': '', 'photo_url': '', 'creation_date': 0,
                'accept_date': 0, 'start_date': 0, 'end_date': 0, 'notes': ''
                }
            mentor_user = UserModel.find_by_id(relation.mentor_id)
            relation_field['id'] = relation.id
            relation_field['user_id'] = mentor_user.id
            relation_field['username'] = mentor_user.username
            relation_field['photo_url'] = mentor_user.photo_url
            relation_field['creation_date'] = relation.creation_date
            relation_field['accept_date'] = relation.accept_date
            relation_field['start_date'] = relation.start_date
            relation_field['end_date'] = relation.end_date
            relation_field['notes'] = relation.notes

            #user is mentee and sender
            if user_id == relation.action_user_id:
                sent_as_mentee[str(UserDAO.mapState(relation.state))].append(relation_field)

            #user is mentee and reciever
            else:
                received_as_mentee[str(UserDAO.mapState(relation.state))].append(relation_field)

            task_list = TaskDAO.list_tasks(user_id=user_id, mentorship_relation_id=relation.id)
            for task in task_list:
                # tasks are identified by request_id and task_id
                # Two tasks can have same task_id so request_id is also added
                task['request_id'] = relation.id
                if task['is_done'] == True:
                    tasks_sorted['done'].append(task)
                else:
                    tasks_sorted['todo'].append(task)

        # user as mentor
        for relation in user.mentor_relations:
            relation_field = {
                'id': 0, 'mentee_id': '', 'username': '', 'photo_url': '', 'creation_date': 0,
                'accept_date': 0, 'start_date': 0, 'end_date': 0, 'notes': ''
                }
            mentee_user = UserModel.find_by_id(relation.mentee_id)
            relation_field['id'] = relation.id
            relation_field['user_id'] = mentee_user.id
            relation_field['username'] = mentee_user.username
            relation_field['photo_url'] = mentee_user.photo_url
            relation_field['creation_date'] = relation.creation_date
            relation_field['accept_date'] = relation.accept_date
            relation_field['start_date'] = relation.start_date
            relation_field['end_date'] = relation.end_date
            relation_field['notes'] = relation.notes

            #user is mentor and sender
            if user_id == relation.action_user_id:
                sent_as_mentor[str(UserDAO.mapState(relation.state))].append(relation_field)

            #user is mentor and reciever
            else:
                received_as_mentor[str(UserDAO.mapState(relation.state))].append(relation_field)

            task_list = TaskDAO.list_tasks(user_id=user_id, mentorship_relation_id=relation.id)
            for task in task_list:
                # tasks are identified by request_id and task_id
                # Two tasks can have same task_id so request_id is also added
                task['request_id'] = relation.id
                if task['is_done'] == True:
                    tasks_sorted['done'].append(task)
                else:
                    tasks_sorted['todo'].append(task)

        response = {
            'user_details': user_details,
            'mentorship_relations': {
                'received_as_mentee': received_as_mentee,
                'sent_as_mentee': sent_as_mentee,
                'received_as_mentor': received_as_mentor,
                'sent_as_mentor': sent_as_mentor,
            },
            'tasks': tasks_sorted
        }
        return response

    @staticmethod
    def mapState(state):
        if state == 1:
            return "PENDING"
        elif state == 2:
            return "ACCEPTED"
        elif state == 3:
            return "REJECTED"
        elif state == 4:
            return "CANCELLED"
        elif state == 5:
            return "COMPLETED"
