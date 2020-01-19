from app.database.models.user import UserModel
from app.messages_enums import Message
from app.messenger import Lang
from app.utils.decorator_utils import email_verification_required


class AdminDAO:
    """Data Access Object for Admin functionalities."""

    @staticmethod
    @email_verification_required
    def assign_new_user(user_id, data, lang: Lang):
        """Creates a new admin.

        Creates a new admin if the assigned user exists and is assigned by another user. Otherwise returns a message.

        Args:
            user_id: The user id of the assigner.
            data: A list containing the details of the assigned user.
            lang: Language to be used in response.

        Returns:
            message: A message corresponding to the completed action.
        """
        new_admin_user_id = data['user_id']

        if user_id == new_admin_user_id:
            return lang.map(Message.USER_CANNOT_BE_ASSIGNED_ADMIN_BY_USER), 403

        admin_user = UserModel.find_by_id(user_id)

        if admin_user:
            if not admin_user.is_admin:
                return lang.map(Message.USER_ASSIGN_NOT_ADMIN), 403
        else:
            return lang.map(Message.USER_NOT_FOUND), 404

        new_admin_user = UserModel.find_by_id(new_admin_user_id)

        if new_admin_user:

            if new_admin_user.is_admin:
                return lang.map(Message.USER_IS_ALREADY_AN_ADMIN), 400

            new_admin_user.is_admin = True
            new_admin_user.save_to_db()

            return lang.map(Message.USER_IS_NOW_AN_ADMIN), 200

        return lang.map(Message.USER_DOES_NOT_EXIST), 404

    @staticmethod
    @email_verification_required
    def revoke_admin_user(user_id, data, lang: Lang):
        """Revokes the admin status of an user.

        Revokes the admin status of an user if the user exists, is an admin and another user requests for this action. Otherwise returns a message.

        Args:
            user_id: The user id of the revoker.
            data: A list containing the details of the user whose admin status is to be revoked.
            lang: Language to be used in response.

        Returns:
            message: A message corresponding to the completed action.
        """
        admin_user_id = data['user_id']

        if user_id == admin_user_id:
            return lang.map(Message.USER_CANNOT_REVOKE_ADMIN_STATUS), 403

        new_admin_user = UserModel.find_by_id(admin_user_id)

        admin_user = UserModel.find_by_id(user_id)

        if admin_user:
            if not admin_user.is_admin:
                return lang.map(Message.USER_REVOKE_NOT_ADMIN), 403
        else:
            return lang.map(Message.USER_NOT_FOUND), 404

        if new_admin_user:

            if not new_admin_user.is_admin:
                return lang.map(Message.USER_IS_NOT_AN_ADMIN), 400

            new_admin_user.is_admin = False
            new_admin_user.save_to_db()

            return lang.map(Message.USER_ADMIN_STATUS_WAS_REVOKED), 200

        return lang.map(Message.USER_DOES_NOT_EXIST), 404
