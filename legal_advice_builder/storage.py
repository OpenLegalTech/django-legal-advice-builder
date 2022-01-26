import json

from django.core.serializers.json import DjangoJSONEncoder


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
