from django.db import models
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node

from .questionaire import Questionaire


class Question(MP_Node):

    TEXT = 'TX'
    SINGLE_LINE = 'SL'
    SINGLE_OPTION = 'SO'
    MULTIPLE_OPTIONS = 'MO'
    FILE_UPLOAD = 'FU'
    DATE = 'DT'
    YES_NO = 'YN'

    FIELD_TYPES = [
        (TEXT, _('Long multiline Text input')),
        (SINGLE_OPTION, _('Pick one of multiple options')),
        (MULTIPLE_OPTIONS, _('Pick several of multiple options')),
        (SINGLE_LINE, _('Short single line text input')),
        (FILE_UPLOAD, _('File Upload')),
        (DATE, _('Date')),
        (YES_NO, _('Yes/No'))
    ]

    FIELD_ICONS = {
        TEXT: 'bi bi-blockquote-right',
        SINGLE_OPTION: 'bi bi-check2-square',
        MULTIPLE_OPTIONS: 'bi bi-ui-checks',
        SINGLE_LINE: 'bi bi-cursor-text',
        FILE_UPLOAD: 'bi bi-file-arrow-up',
        DATE: 'bi bi-calendar-event'
    }

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

    information = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.field_type == self.YES_NO:
            self.options = {
                'yes': str(_('yes')),
                'no': str(_('no'))
            }
        super().save(*args, **kwargs)

    def next(self, option=None, text=None, date=None):
        if option or date:
            if self.is_status_by_conditions('success', option, date):
                if self.questionaire.next():
                    return self.questionaire.next().get_first_question()
                else:
                    return None
            if option:
                conditions = self.conditions.filter(
                    if_option='is',
                    if_value=option,
                    then_value='question',
                    then_question__isnull=False)
                if conditions:
                    condition = conditions.first()
                    return condition.then_question
        if self.get_children():
            return self.get_children().first()
        elif self.questionaire.next():
            return self.questionaire.next().get_first_question()

    def is_status_by_conditions(self, status, option=None, date=None):
        status_conditions = self.conditions.filter(then_value=status)
        if status_conditions.exists():
            if self.field_type in [self.SINGLE_OPTION, self.YES_NO] and option:
                option_conditions = status_conditions.filter(if_option='is',
                                                             if_value=option)
                if option_conditions.exists():
                    return option_conditions.first()
            elif self.field_type == self.DATE and date:
                date_conditions = status_conditions.filter(
                    if_option__in=['deadline_expired', 'deadline_running']
                )
                for condition in date_conditions:
                    res = condition.evaluate_date(date)
                    if res:
                        return condition
        return False

    def get_status(self, option=None, text=None, date=None):
        if option or date:
            condition_success = self.is_status_by_conditions(
                'success', option=option, date=date)
            condition_failure = self.is_status_by_conditions(
                'failure', option=option, date=date)
            if condition_success:
                return {
                    'success': True,
                    'message': self.questionaire.success_message,
                    'next': self.next(option, text, date)
                }
            elif condition_failure:
                return {
                    'failure': True,
                    'message': condition_failure.message,
                }
        return {
            'ongoing': True,
            'next': self.next(option, text)
        }

    @property
    def icon(self):
        return self.FIELD_ICONS.get(self.field_type)

    @property
    def has_error(self):
        return self.field_type in [self.SINGLE_OPTION, self.MULTIPLE_OPTIONS] and not self.options

    def get_unsure_message(self):
        if self.unsure_message:
            return self.unsure_message
        return self.questionaire.unsure_message

    def get_options_by_type(self):
        if self.field_type in [self.SINGLE_OPTION, self.MULTIPLE_OPTIONS, self.YES_NO]:
            return {
                'is': _('is')
            }
        elif self.field_type == self.DATE:
            return {
                'deadline_expired': _('is expired.'),
                'deadline_running': _('is still running.')
            }
        return {}

    def get_if_text_by_type(self):
        if self.field_type in [self.SINGLE_OPTION, self.MULTIPLE_OPTIONS, self.YES_NO]:
            return _('If the answer to this question is:')
        elif self.field_type == self.DATE:
            return _('If after the date given as answer a timespan of:')
        return ''

    def get_options_names(self):
        return ', '.join([key for key, value in self.options.items()])

    def get_dict_key(self, option=None, text=None, date=None):
        qn = self.questionaire
        qn_key = qn.short_title if qn.short_title else 'questionaire_{}'.format(qn.id)
        question_key = self.short_title if self.short_title else 'question_{}'.format(self.id)
        value = ''
        if option:
            if self.field_type in [self.SINGLE_OPTION, self.YES_NO]:
                value = self.options.get(option)
            elif self.field_type == self.MULTIPLE_OPTIONS:
                value = [self.options.get(opt) for opt in option]
        elif text:
            value = text
        elif date:
            value = date
        return '{}_{}'.format(qn_key, question_key), value

    def __str__(self):
        short_title = self.short_title if self.short_title else ''
        if self.field_type == self.SINGLE_OPTION:
            return '{} {} ({})'.format(
                short_title,
                self.text,
                self.get_options_names())
        else:
            return '{}: {}'.format(short_title, self.text)
