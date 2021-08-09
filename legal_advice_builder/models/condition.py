from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone


class AbstractCondition(models.Model):
    question = models.ForeignKey('legal_advice_builder.Question',
                                 on_delete=models.CASCADE)
    if_option = models.CharField(max_length=500)
    if_value = models.CharField(max_length=500)

    class Meta:
        abstract = True

    def __str__(self):
        return 'if answer {} "{}"'.format(self.if_option,
                                          self.if_value)

    def evaluate_date(self, date):
        condition_type = self.if_option
        if condition_type in ['deadline_expired', 'deadline_running']:
            unit = self.if_value.split('_')[0]
            period = self.if_value.split('_')[1]
            now = timezone.now().date()
            kwargs = {}
            kwargs[unit] = int(period)
            date_to_validate = date + relativedelta(**kwargs)
            if condition_type == 'deadline_expired':
                return date_to_validate <= now
            if condition_type == 'deadline_running':
                return date_to_validate >= now
        return False


class Condition(AbstractCondition):
    then_value = models.CharField(max_length=500)
    then_question = models.ForeignKey('legal_advice_builder.Question',
                                      related_name='then_question_conditions',
                                      null=True,
                                      blank=True,
                                      on_delete=models.SET_NULL)
    message = models.TextField(blank=True)

    class Meta:
        unique_together = ['question', 'if_value', 'then_value']
        default_related_name = 'question_condition'

    def __str__(self):
        return 'if answer {} "{}" then {}'.format(self.if_option,
                                                  self.if_value,
                                                  self.then_value)


class TextBlockCondition(AbstractCondition):
    text_block = models.ForeignKey('legal_advice_builder.TextBlock',
                                   related_name='text_block_conditions',
                                   on_delete=models.CASCADE)

    class Meta:
        unique_together = ['question', 'if_value']
        default_related_name = 'text_block_condition'

    def __str__(self):
        return 'Display textblock if answer "{}" "{}"'.format(self.if_option,
                                                              self.if_value)
