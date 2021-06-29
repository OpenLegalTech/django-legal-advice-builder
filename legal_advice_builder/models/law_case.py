from django.db import models
from django.template import Context
from django.template import Template
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from legal_advice_builder.utils import generate_answers_dict_for_template

from .document import Document
from .template import LawCaseTemplate


class LawCase(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    extra_help = models.TextField(blank=True)
    allow_download = models.BooleanField(default=False)
    save_answers = models.BooleanField(default=False)
    law_case_template = models.ForeignKey(LawCaseTemplate,
                                          null=True,
                                          blank=True,
                                          on_delete=models.SET_NULL)
    document = models.OneToOneField(Document,
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    def get_first_questionaire(self):
        return self.questionaire_set.first()

    def get_index_of_questionaire(self, questionaire):
        questionaire_ids = list(self.questionaire_set.values_list('id', flat=True))
        if questionaire.id in questionaire_ids:
            return questionaire_ids.index(questionaire.id)

    def questionaire_count(self):
        return self.questionaire_set.count()

    def generate_default_questionaires(self):
        from .questionaire import Questionaire
        questionaire_list = [{'title': _('verify')}, {'title': _('personal data')}]
        for index, questionaire in enumerate(questionaire_list):
            Questionaire.objects.create(
                law_case=self,
                title=questionaire.get('title'),
                order=index
            )

    def get_rendered_template(self, answers):
        template = get_template(
            'legal_advice_builder/law_case_base_template.html')
        context = {'object': self.law_case_template}
        base_template = template.render(context)
        result_template = Template(base_template)
        result = result_template.render(Context(
            {'answers': generate_answers_dict_for_template(answers)}
        ))
        return result

    @property
    def variables_for_template(self):
        from .question import Question
        variables = {}
        questions = Question.objects.filter(questionaire__law_case=self)
        for question in questions:
            variables[question.get_dict_key()[0]] = question.text
        return variables
