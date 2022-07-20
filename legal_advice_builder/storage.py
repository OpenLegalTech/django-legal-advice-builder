import json

from django.core.serializers.json import DjangoJSONEncoder

from .models import Question
from .utils import get_answer_from_list


class SessionStorage:
    current_questionaire = 'questionaire_id'
    current_question = 'question_id'
    answers = 'answers'

    def __init__(self, prefix, request=None):
        self.prefix = prefix
        self.request = request

        if self.prefix not in self.request.session:
            self.init_data()
            self.request.session[self.prefix] = self.data

    def init_data(self):
        self.data = {
            self.current_questionaire: None,
            self.current_question: None,
            self.answers: [],
        }

    def get_data(self):
        self.request.session.modified = True
        return json.loads(self.request.session[self.prefix])

    def set_data(self, value):
        self.request.session[self.prefix] = json.dumps(value, cls=DjangoJSONEncoder)
        self.request.session.modified = True

    def reset(self):
        self.init_data()

    def get_answer_for_questions(self, question_id):
        answers = self.get_data().get('answers')
        if answers:
            return get_answer_from_list(answers, question_id)
        return ""

    def get_current_question(self):
        try:
            return Question.objects.get(id=self.get_data().get('current_question'))
        except Question.DoesNotExist:
            return None

    def has_previuos_question(self):
        return not len(self.get_data().get('answers', [])) == 0
