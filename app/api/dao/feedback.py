from app.database.models.feedback import Feedback
from app.database.models.user import UserModel
from app import messages
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.models.tasks_list import TasksListModel
from app.utils.decorator_utils import email_verification_required
from app.utils.enum_utils import MentorshipRelationState
from app.utils.enum_utils import Rating


class FeedbackDAO:

    @email_verification_required
    def give_feedback(user_id, mentorship_relation_id, data):

        user = UserModel.find_by_id(user_id)
        relation = MentorshipRelationModel.find_by_id(mentorship_relation_id)
        if user.id != relation.mentee_id or user.id != relation.mentor_id:
            return messages.FEEDBACK_NOT_ALLOWED, 400

        feedback = data['feedback']
        rating = data['rating']
        now_timestamp = datetime.now().timestamp()
        relation.feedback.add_feedback(feedback=feedback, rating=rating, created_at=now_timestamp)
        relation.feedback.save_to_db()
