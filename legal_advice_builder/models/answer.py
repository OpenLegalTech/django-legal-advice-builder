from django.conf import settings
from django.db import models
from .law_case import LawCase


class Answer(models.Model):
    law_case = models.ForeignKey(LawCase, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                null=True, on_delete=models.SET_NULL)
    answers = models.JSONField(null=True, default=dict, blank=True)
    message = models.TextField(blank=True)
    rendered_document = models.TextField(blank=True)

    def __str__(self):
        return self.law_case.title

    def save_rendered_document(self):
        self.rendered_document = self.template
        self.save()

    @property
    def template(self):
        return self.law_case.get_rendered_template(self.answers)
