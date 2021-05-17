from django.db import models
from django.template import Context
from django.template import Template
from django.template.loader import get_template

from legal_advice_builder.utils import generate_answers_dict_for_template

from .template import LawCaseTemplate


class LawCase(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    extra_help = models.TextField(blank=True)
    allow_download = models.BooleanField(default=False)
    save_answers = models.BooleanField(default=False)
    law_case_template = models.ForeignKey(LawCaseTemplate,
                                          null=True,
                                          on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    def get_first_questionaire(self):
        return self.questionaire_set.first()

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
