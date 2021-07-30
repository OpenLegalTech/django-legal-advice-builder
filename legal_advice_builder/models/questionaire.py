from django.db import models
from django.utils.translation import gettext_lazy as _

from . import LawCase


class Questionaire(models.Model):
    law_case = models.ForeignKey(LawCase,
                                 on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    short_title = models.CharField(max_length=50, blank=True)
    success_message = models.TextField(blank=True, help_text=_('This message is '
                                                               'shown if the user has '
                                                               'reached the end '
                                                               'of this questionaire '
                                                               'successfully.'))
    unsure_message = models.TextField(blank=True)
    order = models.IntegerField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

    def get_first_question(self):
        return self.questions.first()

    def get_last_question(self):
        return self.questions.last()

    def add_new_after_question(self, data, parent_question=None):
        from . import Question
        if parent_question:
            question = self.questions.get(id=parent_question)
            children = question.get_children()
            new_question = question.add_child(**data)
            for child in children:
                if not child == new_question:
                    child.move(new_question, pos='last-child')
                    child.refresh_from_db()
            return new_question
        else:
            return Question.add_root(**data)

    def next(self):
        return Questionaire.objects.filter(
            law_case=self.law_case, order__gt=self.order).first()

    @property
    def has_error(self):
        from . import Question
        fields = [Question.SINGLE_OPTION, Question.MULTIPLE_OPTIONS]
        return self.question_set.filter(field_type__in=fields, options={}).exists()

    @property
    def questions(self):
        return self.question_set.all().order_by('path')
