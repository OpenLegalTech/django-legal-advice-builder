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
        (SINGLE_LINE, _('Short single line text input')),
        (DATE, _('Date')),
        (YES_NO, _('Yes/No'))
    ]

    FIELD_ICONS = {
        TEXT: 'bi bi-blockquote-right',
        SINGLE_OPTION: 'bi bi-check2-square',
        MULTIPLE_OPTIONS: 'bi bi-ui-checks',
        SINGLE_LINE: 'bi bi-cursor-text',
        FILE_UPLOAD: 'bi bi-file-arrow-up',
        DATE: 'bi bi-calendar-event',
        YES_NO: 'bi bi-circle-half'
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
    next_question = models.ForeignKey('legal_advice_builder.Question', null=True,
                                      on_delete=models.SET_NULL)
    is_last = models.BooleanField(default=False)

    @property
    def conditions(self):
        return self.question_condition

    def is_option_question(self):
        return self.field_type in [self.SINGLE_OPTION, self.YES_NO, self.MULTIPLE_OPTIONS]

    def save(self, *args, **kwargs):
        if self.field_type == self.YES_NO:
            self.options = {
                'yes': str(_('yes')),
                'no': str(_('no'))
            }
        super().save(*args, **kwargs)

    def prepare_for_delete(self):
        if self.is_root():
            child = self.get_children().first()
            if child:
                new_root = Question.add_root()
                child.move(new_root, pos='first-child')
                child.refresh_from_db()
        else:
            new_parent = self.get_parent()
            children = self.get_children()
            for child in children:
                child.move(new_parent, pos='last-child')
                child.refresh_from_db()

    def check_for_success(self, option=None, text=None, date=None):
        if option or date or text:
            if self.is_status_by_conditions('success', option, date, text):
                if self.questionaire.next():
                    return self.questionaire.next().get_first_question()
                else:
                    return None
            if option or text:
                conditions = self.conditions.filter(
                    if_option='is',
                    if_value__in=[option, text],
                    then_value='question',
                    then_question__isnull=False)
                if conditions:
                    condition = conditions.first()
                    return condition.then_question
        return False

    def next(self, option=None, text=None, date=None):
        next_by_condition = self.check_for_success(option=option, text=text, date=date)
        if next_by_condition is not False:
            return next_by_condition
        if self.next_question:
            return self.next_question
        if self.is_last:
            if self.questionaire.next():
                return self.questionaire.next().get_first_question()
            else:
                return None
        if self.get_children():
            return self.get_children().first()
        elif self.questionaire.next():
            return self.questionaire.next().get_first_question()

    def is_status_by_conditions(self, status, option=None,
                                date=None, text=None):
        status_conditions = self.conditions.filter(then_value=status)
        if status_conditions.exists():
            if self.field_type in [self.SINGLE_OPTION,
                                   self.YES_NO, self.TEXT,
                                   self.SINGLE_LINE] and (option or text):
                types = [option, text]
                option_conditions = status_conditions.filter(
                    if_option='is',
                    if_value__in=types)
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
        next = self.next(option, text, date)
        if option or date or text:
            condition_success = self.is_status_by_conditions(
                'success', option=option, date=date, text=text)
            condition_failure = self.is_status_by_conditions(
                'failure', option=option, date=date, text=text)
            if (condition_success or
               (not next and not condition_failure and not self.questionaire.law_case.document) or
               self.is_last):
                return {
                    'success': True,
                    'message': self.questionaire.success_message,
                    'next': next
                }
            elif condition_failure:
                return {
                    'failure': True,
                    'message': condition_failure.message,
                }
        return {
            'ongoing': True,
            'next': next
        }

    @property
    def icon(self):
        return self.FIELD_ICONS.get(self.field_type)

    @property
    def has_error(self):
        return self.field_type in [self.SINGLE_OPTION, self.MULTIPLE_OPTIONS] and not self.options

    def get_unsure_message(self):
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

    def clean_up_conditions(self, options):
        self.conditions.exclude(if_value__in=options).delete()

    def get_if_text_by_type(self):
        if self.field_type in [self.SINGLE_OPTION,
                               self.MULTIPLE_OPTIONS,
                               self.YES_NO,
                               self.TEXT,
                               self.SINGLE_LINE]:
            return _('If the answer to this question is:')
        elif self.field_type == self.DATE:
            return _('If after the date given as answer a timespan of:')
        return ''

    def get_options_names(self):
        return ', '.join(list(self.options.keys()))

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
        return self.text
