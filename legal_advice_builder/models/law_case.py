from django.db import models
from django.utils.translation import gettext_lazy as _

from .document import Document
from .question import Question
from .questionaire import Questionaire


class LawCase(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    allow_download = models.BooleanField(default=True)
    save_answers = models.BooleanField(default=True)
    document = models.OneToOneField(Document,
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    def get_first_questionaire(self):
        return self.questionaire_set.first()

    def get_first_question(self):
        return self.questionaire_set.first().get_first_question()

    @property
    def first_questionaire(self):
        return self.get_first_questionaire()

    def get_index_of_questionaire(self, questionaire):
        questionaire_ids = list(
            self.questionaire_set.values_list('id', flat=True))
        if questionaire.id in questionaire_ids:
            return questionaire_ids.index(questionaire.id)

    def questionaire_count(self):
        return self.questionaire_set.count()

    def questions_count(self):
        return Question.objects.filter(questionaire__law_case=self).count()

    def generate_default_questionaires(self):
        Questionaire.objects.create(
            law_case=self,
            title=_('Unnamed Questionaire'),
            order=0
        )

    @property
    def placeholders_for_template(self):
        """Returns placeholders used in documentform for vue component."""
        variables = {}
        questions = Question.objects.filter(questionaire__law_case=self)
        for question in questions:
            variables[question.get_dict_key()[0]] = question.text
        return variables
