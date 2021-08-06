import json

from django.db import models
from django.template import Context
from django.template import Template
from django.utils.safestring import mark_safe

from legal_advice_builder.utils import clean_html_field
from legal_advice_builder.utils import generate_answers_dict_for_template


class Document(models.Model):
    name = models.CharField(max_length=200)
    recipient = models.TextField(blank=True)
    sender = models.TextField(blank=True)
    date = models.CharField(blank=True, max_length=50)
    subject = models.CharField(blank=True, max_length=200)
    signature = models.TextField(blank=True)

    sample_answers = models.JSONField(null=True, default=dict, blank=True)

    def __str__(self):
        return self.name

    def get_initial_fields_dict(self):
        '''Used to create vue components in edit mode of document for each field'''
        initial_data = []
        for text_block in self.document_text_blocks.all():
            initial_data.append(
                {
                    'textblock': text_block.id,
                    'content': text_block.content,
                    'document': self.id,
                    'name': 'name'
                }
            )
        return initial_data

    @property
    def fields_dict(self):
        return json.dumps(self.get_initial_fields_dict())

    def get_initial_questions_dict(self):
        '''Used to display sample answers in preview of document.'''
        from legal_advice_builder.models import Question
        initial_data = []
        lawcase = self.lawcase
        questions = Question.objects.filter(questionaire__law_case=lawcase)

        answers_questions = [int(answer.get('question')) for answer in self.sample_answers]

        for question in questions:
            if question.get_dict_key()[0] in self.template:
                if question.id not in answers_questions:
                    initial_data.append(
                        {
                            'question': question.id
                        }
                    )
                else:
                    index = answers_questions.index(question.id)
                    initial_data.append(
                        self.sample_answers[index]
                    )

        return initial_data

    @property
    def template(self):
        content = ' '.join([text_field.content for text_field in self.document_text_blocks.all()])
        return mark_safe(content)

    def template_with_answers(self, answers):
        content = ' '.join([text_field.content for text_field in self.document_text_blocks.all()])
        template = Template(mark_safe(content))
        result = template.render(Context(
            {'answers': generate_answers_dict_for_template(answers)}
        ))
        return result

    @property
    def template_with_sample_answers(self):
        return self.template_with_answers(self.sample_answers)


class TextBlock(models.Model):
    document = models.ForeignKey('legal_advice_builder.Document',
                                 related_name='document_text_blocks',
                                 on_delete=models.CASCADE)
    order = models.IntegerField()
    content = models.TextField(default='')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.content

    def save(self, *args, **kwargs):
        self.content = clean_html_field(self.content)
        return super().save(*args, **kwargs)
