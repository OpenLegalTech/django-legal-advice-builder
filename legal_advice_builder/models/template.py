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


class Template(models.Model):
    name = models.CharField(max_length=50)
    law_case = models.ForeignKey(LawCaseTemplate,
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Lawsuit(Template):

    plaintiff = models.TextField(blank=True)
    defendant = models.TextField(blank=True)
    reason = models.TextField(blank=True)
    amount_in_dispute = models.TextField(blank=True)
    claims = models.TextField(blank=True)
    facts_of_the_case = models.TextField(blank=True)
    justification = models.TextField(blank=True)

    def __str__(self):
        return self.name
