from django.conf import settings
from django.db import models
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node


class LawCase(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    result_template = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def get_first_questionaire(self):
        return self.questionaire_set.first()


class Questionaire(models.Model):
    law_case = models.ForeignKey(LawCase,
                                 on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    short_title = models.CharField(max_length=50, blank=True)
    success_message = models.TextField()
    failure_message = models.TextField()
    unsure_message = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

    def get_first_question(self):
        return self.questions.first()

    def next(self):
        return Questionaire.objects.filter(
            law_case=self.law_case, order__gt=self.order).first()

    @property
    def questions(self):
        return self.question_set.all().order_by('path')


class Question(MP_Node):

    TEXT = 'TX'
    SINGLE_LINE = 'SL'
    SINGLE_OPTION = 'SO'
    FILE_UPLOAD = 'FU'

    FIELD_TYPES = [
        (TEXT, _('Long multiline Text input')),
        (SINGLE_OPTION, _('Pick one of multiple options')),
        (SINGLE_LINE, _('Short single line text input')),
        (FILE_UPLOAD, _('File Upload'))
    ]

    questionaire = models.ForeignKey(Questionaire,
                                     null=True,
                                     on_delete=models.CASCADE)
    short_title = models.CharField(max_length=50, blank=True)
    text = models.CharField(max_length=200)
    options = models.JSONField(default=dict, blank=True, null=True)
    field_type = models.CharField(
        max_length=2,
        choices=FIELD_TYPES,
        default=SINGLE_OPTION,
    )
    help_text = models.CharField(max_length=200, blank=True)
    parent_option = models.CharField(max_length=200, blank=True)
    failure_options = models.JSONField(default=list, null=True, blank=True)
    success_options = models.JSONField(default=list, null=True, blank=True)
    unsure_options = models.JSONField(default=list, null=True, blank=True)
    information = models.TextField(blank=True)
    success_message = models.TextField(blank=True)
    failure_message = models.TextField(blank=True)
    unsure_message = models.TextField(blank=True)

    def next(self, option=None, text=None):
        if option:
            try:
                return self.get_children().get(parent_option=option)
            except Question.DoesNotExist:
                if option in self.success_options:
                    if self.questionaire.next():
                        return self.questionaire.next().get_first_question()
                    else:
                        return None
        return self.get_children().first()

    def is_success(self, option=None, text=None):
        if option:
            return option in self.success_options
        elif text:
            return False
        return False

    def is_failure(self, option=None, text=None):
        if option:
            return option in self.failure_options
        elif text:
            return False
        return False

    def is_unsure(self, option=None, text=None):
        if option:
            return option in self.unsure_options
        elif text:
            return False
        return False

    def get_success_message(self):
        if self.success_message:
            return self.success_message
        return self.questionaire.success_message

    def get_failure_message(self):
        if self.failure_message:
            return self.failure_message
        return self.questionaire.failure_message

    def get_unsure_message(self):
        if self.unsure_message:
            return self.unsure_message
        return self.questionaire.unsure_message

    def get_options_names(self):
        return ', '.join([key for key, value in self.options.items()])

    def get_dict_key(self, option=None, text=None):
        qn = self.questionaire
        qn_key = qn.short_title if qn.short_title else 'questionaire_{}'.format(qn.id)
        question_key = self.short_title if self.short_title else 'question_{}'.format(self.id)
        value = ''
        if option:
            value = self.options.get(option)
        elif text:
            value = text
        return '{}_{}'.format(qn_key, question_key), value

    def __str__(self):
        short_title = self.short_title if self.short_title else ''
        if self.field_type == self.SINGLE_OPTION:
            return '{}: {} {} ({})'.format(
                self.parent_option,
                short_title,
                self.text,
                self.get_options_names())
        else:
            return '{}: {}'.format(short_title, self.text)


class Answer(models.Model):
    law_case = models.ForeignKey(LawCase, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                null=True, on_delete=models.SET_NULL)
    answers = models.JSONField(null=True, default=dict, blank=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return self.law_case.title

    def answers_dict(self):
        answers_dict = {}
        for answer in self.answers:
            question = Question.objects.get(id=answer.get('question'))
            option = answer.get('option')
            text = answer.get('text')
            key, value = question.get_dict_key(option, text)
            answers_dict[key] = value
        return answers_dict

    @property
    def template(self):
        template = Template(self.law_case.result_template)
        result = template.render(Context(
            {'answers': self.answers_dict()}
        ))
        return result
