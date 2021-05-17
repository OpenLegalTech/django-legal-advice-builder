from django.db import models

from legal_advice_builder.utils import clean_html_field


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

    def save(self, *args, **kwargs):
        self.recipient = clean_html_field(self.recipient)
        self.sender = clean_html_field(self.sender)
        self.date = clean_html_field(self.date)
        self.subject = clean_html_field(self.subject)
        self.body = clean_html_field(self.body)
        self.signature = clean_html_field(self.signature)
        return super().save(*args, **kwargs)
