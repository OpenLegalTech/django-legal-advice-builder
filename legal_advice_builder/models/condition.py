from django.db import models


class Condition(models.Model):
    question = models.ForeignKey('legal_advice_builder.Question',
                                 on_delete=models.CASCADE)
    if_option = models.CharField(max_length=500)
    if_value = models.CharField(max_length=500)
    then_value = models.CharField(max_length=500)

    class Meta:
        unique_together = ['question', 'if_value', 'then_value']

    def __str__(self):
        return 'if answer {} "{}" then {}'.format(self.if_option,
                                                  self.if_value,
                                                  self.then_value)
