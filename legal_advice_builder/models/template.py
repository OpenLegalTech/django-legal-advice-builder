from django.db import models


class LawCaseTemplate(models.Model):

    name = models.CharField(max_length=50)
    recipient = models.TextField(blank=True)
    sender = models.TextField(blank=True)
    date = models.CharField(blank=True, max_length=50)
    subject = models.CharField(blank=True, max_length=200)
    body = models.TextField()
    signature = models.TextField(blank=True)

    def __str__(self):
        return self.name
