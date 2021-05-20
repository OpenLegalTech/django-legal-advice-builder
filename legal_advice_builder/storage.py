class SessionStorage:
    current_questionaire = 'questionaire_id'
    current_question = 'question_id'
    answers = 'answers'

    def __init__(self, prefix, request=None, file_storage=None):
        self.prefix = prefix
        self.request = request
        self.file_storage = file_storage
        self._files = {}
        self._tmp_files = []

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
        return self.request.session[self.prefix]

    def set_data(self, value):
        self.request.session[self.prefix] = value
        self.request.session.modified = True

    def reset(self):
        self.init_data()
