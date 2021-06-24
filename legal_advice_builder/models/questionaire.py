from django.db import models

from . import LawCase


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

    def get_last_question(self):
        return self.questions.last()

    def next(self):
        return Questionaire.objects.filter(
            law_case=self.law_case, order__gt=self.order).first()

    @property
    def questions(self):
        return self.question_set.all().order_by('path')
