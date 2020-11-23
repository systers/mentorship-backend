from datetime import datetime
from operator import itemgetter
from http import HTTPStatus
from typing import Dict
from flask_restx import marshal
from sqlalchemy import func

from app import messages
from app.api.dao.mentorship_relation import MentorshipRelationDAO
from app.api.email_utils import confirm_token
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.models.user import UserModel
from app.utils.decorator_utils import email_verification_required
from app.utils.enum_utils import MentorshipRelationState
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.api.models.mentorship_relation import (
    list_tasks_response_body,
    mentorship_request_response_body_for_user_dashboard_body,
)
from app.api.dao.mentorship_relation import MentorshipRelationDAO
from app.utils.validation_utils import is_email_valid


class UserDAO:
    """Data Access Object for User functionalities"""

    FAIL_USER_ALREADY_EXISTS = "FAIL_USER_ALREADY_EXISTS"
    SUCCESS_USER_CREATED = "SUCCESS_USER_CREATED"
    MIN_NUMBER_OF_ADMINS = 1
    DEFAULT_PAGE = 1
    DEFAULT_USERS_PER_PAGE = 10
    MAX_USERS_PER_PAGE = 50

    @staticmethod
    def create_user(data: Dict[str, str]):
        """Creates a new user.

        Creates a new user with provided data.

        Arguments:
            data: A list containing the user's name, username, password, and email, as well as recognition that they have read and agree to the Terms and Conditions.

        Returns:
            A tuple with two elements. The first element is a dictionary containing a key 'message' containing a string which indicates whether or not the user was created successfully. The second is the HTTP response code.
        """

        name = data["name"]
        username = data["username"]
        password = data["password"]
        email = data["email"]
        terms_and_conditions_checked = data["terms_and_conditions_checked"]

        existing_user = UserModel.find_by_username(data["username"])
        if existing_user:
            return messages.USER_USES_A_USERNAME_THAT_ALREADY_EXISTS, HTTPStatus.CONFLICT
        else:
            existing_user = UserModel.find_by_email(data["email"])
            if existing_user:
                return messages.USER_USES_AN_EMAIL_ID_THAT_ALREADY_EXISTS, HTTPStatus.CONFLICT

        user = UserModel(name, username, password, email, terms_and_conditions_checked)
        if "need_mentoring" in data:
            user.need_mentoring = data["need_mentoring"]

        if "available_to_mentor" in data:
            user.available_to_mentor = data["available_to_mentor"]

        user.save_to_db()

        return messages.USER_WAS_CREATED_SUCCESSFULLY, HTTPStatus.CREATED

    @staticmethod
    @email_verification_required
    def delete_user(user_id: int):
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
                return messages.USER_CANT_DELETE, HTTPStatus.BAD_REQUEST

        if user:
            user.delete_from_db()
            return messages.USER_SUCCESSFULLY_DELETED, HTTPStatus.OK

        return messages.USER_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND

    @staticmethod
    @email_verification_required
    def get_user(user_id: int):
        """ Retrieves a user's profile information using a specified ID.

        Provides the user profile of the user whose ID matches the one specified.

        Arguments:
            user_id: The ID of the user to be searched.

        Returns:
            The UserModel class of the user whose ID was searched, containing the public information of their profile such as bio, location, etc.

        """

        return UserModel.find_by_id(user_id)

    @staticmethod
    def get_user_by_email(email: str):
        """ Retrieves a user's profile information using a specified email.

        Provides the user profile of the user whose email matches the one specified.

        Arguments:
            email: The email of the user to be searched.

        Returns:
            The UserModel class of the user whose email was searched, containing the public information of their profile such as bio, location, etc.

        """

        return UserModel.find_by_email(email)

    @staticmethod
    def get_user_by_username(username: str):
        """ Retrieves a user's profile information using a specified username.

        Provides the user profile of the user whose username matches the one specified.

        Arguments:
            username: The ID of the user to be searched.

        Returns:
            The UserModel class of the user whose username was searched, containing the public information of their profile such as bio, location, etc.

        """

        return UserModel.find_by_username(username)

    @staticmethod
    def list_users(user_id: int, search_query: str = "", page: int = DEFAULT_PAGE, per_page: int = DEFAULT_USERS_PER_PAGE, is_verified = None, location = None):
        """ Retrieves a list of verified users with the specified ID.

        Arguments:
            user_id: The ID of the user to be listed.
            search_query: The search query for name of the users to be found.
            is_verified: Status of the user's verification; None when provided as an argument.
            page: The page of users to be returned
            per_page: The number of users to return per page
            location: The location of users to be listed

        Returns:
            A list of users matching conditions and the HTTP response code.

        """

        users_list = UserModel.query.filter(
            UserModel.id != user_id,
            not is_verified or UserModel.is_email_verified,
            not location or (UserModel.location and func.lower(UserModel.location).contains(location.lower())) ,
            func.lower(UserModel.name).contains(search_query.lower())
        ).order_by(UserModel.id).paginate(page=page,
                                          per_page=per_page,
                                          error_out=False,
                                          max_per_page=UserDAO.MAX_USERS_PER_PAGE).items

        list_of_users = [
            user.json()
            for user in users_list
        ]

        for user in list_of_users:
            relation = MentorshipRelationDAO.list_current_mentorship_relation(
                user["id"]
            )
            if isinstance(relation, MentorshipRelationModel):
                user["is_available"] = False
            else:
                # we don't need if statement for this case
                # is_available is true
                # when either need_mentoring or available_to_mentor is true
                user["is_available"] = (
                    user["need_mentoring"] or user["available_to_mentor"]
                )

        return list_of_users, HTTPStatus.OK

    @staticmethod
    @email_verification_required
    def update_user_profile(user_id: int, data: Dict[str, str]):
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
            return messages.USER_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND

        username = data.get("username", None)
        if username:
            user_with_same_username = UserModel.find_by_username(username)

            # username should be unique
            if user_with_same_username:
                return messages.USER_USES_A_USERNAME_THAT_ALREADY_EXISTS, HTTPStatus.BAD_REQUEST

            user.username = username

        if "name" in data and data["name"]:
            user.name = data["name"]

        if "bio" in data:
            if data["bio"]:
                user.bio = data["bio"]
            else:
                user.bio = None

        if "location" in data:
            if data["location"]:
                user.location = data["location"]
            else:
                user.location = None

        if "occupation" in data:
            if data["occupation"]:
                user.occupation = data["occupation"]
            else:
                user.occupation = None

        if "organization" in data:
            if data["organization"]:
                user.organization = data["organization"]
            else:
                user.organization = None

        if "slack_username" in data:
            if data["slack_username"]:
                user.slack_username = data["slack_username"]
            else:
                user.slack_username = None

        if "social_media_links" in data:
            if data["social_media_links"]:
                user.social_media_links = data["social_media_links"]
            else:
                user.social_media_links = None

        if "skills" in data:
            if data["skills"]:
                user.skills = data["skills"]
            else:
                user.skills = None

        if "interests" in data:
            if data["interests"]:
                user.interests = data["interests"]
            else:
                user.interests = None

        if "resume_url" in data:
            if data["resume_url"]:
                user.resume_url = data["resume_url"]
            else:
                user.resume_url = None

        if "photo_url" in data:
            if data["photo_url"]:
                user.photo_url = data["photo_url"]
            else:
                user.photo_url = None

        if "need_mentoring" in data:
            user.need_mentoring = data["need_mentoring"]

        if "available_to_mentor" in data:
            user.available_to_mentor = data["available_to_mentor"]

        user.save_to_db()

        return messages.USER_SUCCESSFULLY_UPDATED, HTTPStatus.OK

    @staticmethod
    @email_verification_required
    def change_password(user_id: int, data: Dict[str, str]):
        """ Changes the user's password.

        Finds the user with the given ID, checks their current password, and then updates to the new one.

        Arguments:
            user_id: The ID of the user to be searched.
            data: The user's current and new password.

        Returns:
            A message that indicates whether the password change was successful or not and a second element which is the HTTP response code.

        """

        current_password = data["current_password"]
        new_password = data["new_password"]

        user = UserModel.find_by_id(user_id)
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save_to_db()
            return messages.PASSWORD_SUCCESSFULLY_UPDATED, HTTPStatus.CREATED

        return messages.USER_ENTERED_INCORRECT_PASSWORD, HTTPStatus.BAD_REQUEST

    @staticmethod
    def confirm_registration(token: str):
        """ Determines whether a user's email registration has been confirmed.

        Determines whether a user's email registration was invalid, previously confirmed, or just confirmed.

        Arguments:
            token: Serialized and signed email address as a URL safe string.

        Returns:
            A message that indicates if the confirmation was invalid, already happened, or just happened, and the HTTP response code.

        """

        email_from_token = confirm_token(token)

        if not email_from_token or email_from_token is None:
            return messages.EMAIL_EXPIRED_OR_TOKEN_IS_INVALID, HTTPStatus.BAD_REQUEST

        user = UserModel.find_by_email(email_from_token)
        if user.is_email_verified:
            return messages.ACCOUNT_ALREADY_CONFIRMED, HTTPStatus.OK
        else:
            user.is_email_verified = True
            user.email_verification_date = datetime.now()
            user.save_to_db()
            return messages.ACCOUNT_ALREADY_CONFIRMED_AND_THANKS, HTTPStatus.OK

    @staticmethod
    def authenticate(username_or_email: str, password: str):
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
    def get_achievements(user_id: int):
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
    def get_user_statistics(user_id: int):
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
        (
            pending_requests,
            accepted_requests,
            rejected_requests,
            completed_relations,
            cancelled_relations,
        ) = (0, 0, 0, 0, 0)
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
            "name": user.name,
            "pending_requests": pending_requests,
            "accepted_requests": accepted_requests,
            "rejected_requests": rejected_requests,
            "completed_relations": completed_relations,
            "cancelled_relations": cancelled_relations,
            "achievements": achievements,
        }
        return response

    @staticmethod
    def get_user_dashboard(user_id):
        """
        returns user dashboard: relations received. sent as mentor or mentee for all states.
        Also returns all done, to be done tasks if in a relation

        Args:
            user_id: id of the user whose dashboard is to be returned
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return None

        response = {}

        all_user_relations = user.mentee_relations + user.mentor_relations
        relations_in_response_form = [
            DashboardRelationResponseModel(relation) for relation in all_user_relations
        ]

        mentor_sent_relations = [
            relation
            for relation in relations_in_response_form
            if relation.action_user_id == user_id and relation.mentor_id == user_id
        ]
        mentor_received_relations = [
            relation
            for relation in relations_in_response_form
            if relation.action_user_id != user_id and relation.mentor_id == user_id
        ]
        mentee_sent_relations = [
            relation
            for relation in relations_in_response_form
            if relation.action_user_id == user_id and relation.mentee_id == user_id
        ]
        mentee_received_relations = [
            relation
            for relation in relations_in_response_form
            if relation.action_user_id != user_id and relation.mentee_id == user_id
        ]

        as_mentee = {
            "sent": {
                "accepted": [],
                "rejected": [],
                "completed": [],
                "cancelled": [],
                "pending": [],
            },
            "received": {
                "accepted": [],
                "rejected": [],
                "completed": [],
                "cancelled": [],
                "pending": [],
            },
        }
        as_mentor = {
            "sent": {
                "accepted": [],
                "rejected": [],
                "completed": [],
                "cancelled": [],
                "pending": [],
            },
            "received": {
                "accepted": [],
                "rejected": [],
                "completed": [],
                "cancelled": [],
                "pending": [],
            },
        }

        as_mentee["received"]["accepted"] = [
            relation.response
            for relation in mentee_received_relations
            if relation.state == MentorshipRelationState.ACCEPTED
        ]
        as_mentee["received"]["rejected"] = [
            relation.response
            for relation in mentee_received_relations
            if relation.state == MentorshipRelationState.REJECTED
        ]
        as_mentee["received"]["completed"] = [
            relation.response
            for relation in mentee_received_relations
            if relation.state == MentorshipRelationState.COMPLETED
        ]
        as_mentee["received"]["cancelled"] = [
            relation.response
            for relation in mentee_received_relations
            if relation.state == MentorshipRelationState.CANCELLED
        ]
        as_mentee["received"]["pending"] = [
            relation.response
            for relation in mentee_received_relations
            if relation.state == MentorshipRelationState.PENDING
        ]

        as_mentor["received"]["accepted"] = [
            relation.response
            for relation in mentor_received_relations
            if relation.state == MentorshipRelationState.ACCEPTED
        ]
        as_mentor["received"]["rejected"] = [
            relation.response
            for relation in mentor_received_relations
            if relation.state == MentorshipRelationState.REJECTED
        ]
        as_mentor["received"]["completed"] = [
            relation.response
            for relation in mentor_received_relations
            if relation.state == MentorshipRelationState.COMPLETED
        ]
        as_mentor["received"]["cancelled"] = [
            relation.response
            for relation in mentor_received_relations
            if relation.state == MentorshipRelationState.CANCELLED
        ]
        as_mentor["received"]["pending"] = [
            relation.response
            for relation in mentor_received_relations
            if relation.state == MentorshipRelationState.PENDING
        ]

        as_mentee["sent"]["accepted"] = [
            relation.response
            for relation in mentee_sent_relations
            if relation.state == MentorshipRelationState.ACCEPTED
        ]
        as_mentee["sent"]["rejected"] = [
            relation.response
            for relation in mentee_sent_relations
            if relation.state == MentorshipRelationState.REJECTED
        ]
        as_mentee["sent"]["completed"] = [
            relation.response
            for relation in mentee_sent_relations
            if relation.state == MentorshipRelationState.COMPLETED
        ]
        as_mentee["sent"]["cancelled"] = [
            relation.response
            for relation in mentee_sent_relations
            if relation.state == MentorshipRelationState.CANCELLED
        ]
        as_mentee["sent"]["pending"] = [
            relation.response
            for relation in mentee_sent_relations
            if relation.state == MentorshipRelationState.PENDING
        ]

        as_mentor["sent"]["accepted"] = [
            relation.response
            for relation in mentor_sent_relations
            if relation.state == MentorshipRelationState.ACCEPTED
        ]
        as_mentor["sent"]["rejected"] = [
            relation.response
            for relation in mentor_sent_relations
            if relation.state == MentorshipRelationState.REJECTED
        ]
        as_mentor["sent"]["completed"] = [
            relation.response
            for relation in mentor_sent_relations
            if relation.state == MentorshipRelationState.COMPLETED
        ]
        as_mentor["sent"]["cancelled"] = [
            relation.response
            for relation in mentor_sent_relations
            if relation.state == MentorshipRelationState.CANCELLED
        ]
        as_mentor["sent"]["pending"] = [
            relation.response
            for relation in mentor_sent_relations
            if relation.state == MentorshipRelationState.PENDING
        ]

        response["as_mentor"] = as_mentor
        response["as_mentee"] = as_mentee

        current_relation = MentorshipRelationDAO.list_current_mentorship_relation(
            user_id=user_id
        )

        if current_relation != (messages.NOT_IN_MENTORED_RELATION_CURRENTLY, HTTPStatus.OK):
            response["tasks_todo"] = marshal(
                [
                    task
                    for task in current_relation.tasks_list.tasks
                    if not task["is_done"]
                ],
                list_tasks_response_body,
            )
            response["tasks_done"] = marshal(
                [task for task in current_relation.tasks_list.tasks if task["is_done"]],
                list_tasks_response_body,
            )

        return response


class DashboardRelationResponseModel:
    """temp class used for storing mentorship_request_response_body_for_user_dashboard_body values"""

    def __init__(self, relation: MentorshipRelationModel):
        self.state = relation.state
        self.mentor_id = relation.mentor_id
        self.mentee_id = relation.mentee_id
        self.action_user_id = relation.action_user_id
        self.response = {
            "id": relation.id,
            "action_user_id": relation.action_user_id,
            "mentor": {
                "id": relation.mentor_id,
                "user_name": relation.mentor.name,
                "photo_url": relation.mentor.photo_url,
            },
            "mentee": {
                "id": relation.mentee_id,
                "user_name": relation.mentee.name,
                "photo_url": relation.mentee.photo_url,
            },
            "creation_date": relation.creation_date,
            "accept_date": relation.accept_date,
            "start_date": relation.start_date,
            "end_date": relation.end_date,
            "state": relation.state,
            "notes": relation.notes,
        }
