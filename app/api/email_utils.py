import datetime
from itsdangerous import URLSafeTimedSerializer, BadSignature

from flask_mail import Message
from flask import render_template

import config
from app.api.mail_extension import mail


def generate_confirmation_token(email):
    """Serializes and signs an email address into token with an expiry."""
    from run import application

    serializer = URLSafeTimedSerializer(application.config["SECRET_KEY"])
    return serializer.dumps(email, salt=application.config["SECURITY_PASSWORD_SALT"])


def confirm_token(token, expiration=config.BaseConfig.UNVERIFIED_USER_THRESHOLD):
    """Confirms the token matches the expected email address.

    Args:
        token: Serialized and signed email address as a URL safe string.
        expiration: Maximum age of the token before expiration.

    Returns:
        email: Deserialized email address with verified signature.
        False: If the token signature does not match.

    Raises:
        SignatureExpired: Raised if the token's signature timestamp is older
            than the specified maximum age.
    """
    from run import application

    serializer = URLSafeTimedSerializer(application.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token, salt=application.config["SECURITY_PASSWORD_SALT"], max_age=expiration
        )
    except BadSignature:
        return False
    return email


def mock_send_email(recipient,subject,template):
    """Mocks the email sending behaviour by printing it as terminal output."""

    print("Mock Email Service")
    print(f"Subject: {subject}")
    print(f"Recipient: {recipient}")
    print(template)


def send_email(recipient, subject, template):
    """Sends a html email message with a subject to the specified recipient."""
    from run import application

    if application.config["MOCK_EMAIL"]:
        mock_send_email(recipient,subject,template)
    else:
        msg = Message(
            subject,
            recipients=[recipient],
            html=template,
            sender=application.config["MAIL_DEFAULT_SENDER"],
        )
        mail.send(msg)


def send_email_verification_message(user_name, email):
    """Sends a verification html email message to the specified user.

    First, the email address is serialized and signed for safety into a token.
    A confirmation url is generated using the token and a custom html email
    message containing the user's name and confirmation url is built and sent
    to the user.

    Args:
        user_name: User's name.
        email: User email address.
    """
    confirmation_token = generate_confirmation_token(email)
    from app.api.resources.user import (
        UserEmailConfirmation,
    )  # import here to avoid circular imports
    from app.api.api_extension import api

    confirm_url = api.url_for(
        UserEmailConfirmation, token=confirmation_token, _external=True
    )
    html = render_template(
        "email_confirmation.html",
        confirm_url=confirm_url,
        user_name=user_name,
        threshold=config.BaseConfig.UNVERIFIED_USER_THRESHOLD,
    )
    subject = "Mentorship System - Please confirm your email"
    send_email(email, subject, html)


def send_email_mentorship_relation_accepted(request_id):
    """
    Sends a notification email to the sender of the mentorship relation request,
    stating that his request has been accepted.

    Args:
        request_id: Request id of the mentorship request.
    """

    from app.database.models.user import UserModel
    from app.database.models.mentorship_relation import MentorshipRelationModel

    # Getting the request from id.
    request = MentorshipRelationModel.find_by_id(request_id)

    # Getting the sender and receiver of the mentorship request from their ids.
    if request.action_user_id == request.mentor_id:
        request_sender = UserModel.find_by_id(request.mentor_id)
        request_receiver = UserModel.find_by_id(request.mentee_id)
        role = "mentee"
    else:
        request_sender = UserModel.find_by_id(request.mentee_id)
        request_receiver = UserModel.find_by_id(request.mentor_id)
        role = "mentor"

    end_date = request.end_date
    date = datetime.datetime.fromtimestamp(end_date).strftime("%d-%m-%Y")

    subject = "Mentorship relation accepted!"
    html = render_template(
        "mentorship_relation_accepted.html",
        request_sender=request_sender.name,
        request_receiver=request_receiver.name,
        role=role,
        end_date=date,
    )
    send_email(request_sender.email, subject, html)


def send_email_new_request(user_sender, user_recipient, notes, sender_role):
    """Sends a notification html email message to the user_recipient user.

    First, the email address is serialized and signed for safety into a token.
    A confirmation url is generated using the token and a custom html email
    message containing the user's name and confirmation url is built and sent
    to the user.

    Args:
        user_sender: User who sent a relation request.
        user_recipient: User to which a relation request is addressed.
        note: Note from user_sender.
        sender_role: Role of the sender_user in the relationship. Must be either "mentee" or "mentor"
    """
    html = render_template(
        "email_relation_request.html",
        user_recipient_name=user_recipient.name,
        user_sender_name=user_sender.name,
        notes=notes,
        sender_role=sender_role,
    )
    subject = "Mentorship System - You have got new relation request"
    send_email(user_recipient.email, subject, html)

def send_email_reset_password_message(user_name, email):
 
    from run import application
    import config
    serializer = URLSafeTimedSerializer(application.config["SECRET_KEY"])
    confirmation_token = serializer.dumps(email, salt=application.config["SECURITY_RESET_SALT"])
    from app.api.dao.user import UserDAO
    from app.api.resources.user import ResetPassword # import here to avoid circular imports
    from app.api.api_extension import api
 
    DAO = UserDAO()
    confirm_url = api.url_for(ResetPassword, token=confirmation_token, _external=True)
    
    html = render_template(
        "email_reset_password.html",
        confirm_url=confirm_url,
        user_name=user_name,
        token_expiry=1, # hours
    )
    subject = "Mentorship System - Password Reset Request!"
    send_email(email, subject, html)

