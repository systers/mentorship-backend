from flask_restplus import fields, Model
from app.utils.enum_utils import Rating


def add_models_to_namespace(api_namespace):
    api_namespace.models[feedback_model.name] = feedback_model
    api_namespace.models[give_feedback_response_body.name] = give_feedback_response_body

feedback_model = Model(
    "Feedback Model",
    {
        "id": fields.Integer(required=True, description="Feedback's id"),
        "user_id": fields.Integer(required=True, description="User's id"),
        "relation_id": fields.Integer(required=True, description="Relation's id"),
        "feedback": fields.String(required=True, description="Feedback"),
        "rating": fields.Integer(required=True, enum=Rating.values, description="Rating of the application"),
        "submission_date": fields.Float(
            required=True,
            description="Feedback submission date",
        ),
    },

)

give_feedback_response_body = Model(
    "Give feedback response model",
    {
        "feedback": fields.String(required=True, description="feedback of the application"),
        "rating": fields.Integer(required=True, enum=Rating.values, description="Rating of the application"),
        "now_timestamp": fields.Float(required=True, description="Feedback submission date")
    },

)
