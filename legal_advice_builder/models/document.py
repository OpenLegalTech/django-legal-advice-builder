import datetime
import json

from django.db import models
from django.template import Context
from django.template import Template
from django.utils.functional import cached_property
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
        '''Used to create vue component in edit mode of document for each textblock'''
        initial_data = []
        for text_block in self.document_text_blocks.all():
            text_block_dict = {
                'textblock': text_block.id,
                'content': text_block.content,
                'document': self.id,
                'name': 'name',
                'question': '',
                'if_option': '',
                'if_value': ''
            }
            if text_block.text_block_conditions.all():
                condition = text_block.text_block_conditions.first()
                text_block_dict.update({
                    'question': condition.question.id,
                    'if_option': condition.if_option,
                    'if_value': condition.if_value
                })
            initial_data.append(text_block_dict)
        return initial_data

    @cached_property
    def fields_dict(self):
        return json.dumps(self.get_initial_fields_dict())

    @cached_property
    def questions(self):
        from legal_advice_builder.models import Question
        return Question.objects.filter(questionaire__law_case=self.lawcase)

    @property
    def options_questions(self):
        from legal_advice_builder.models import Question
        questions = self.questions.filter(
            field_type__in=[Question.SINGLE_OPTION, Question.YES_NO, Question.MULTIPLE_OPTIONS]
        )
        return list(questions.values('id', 'text', 'options'))

    def get_initial_questions_dict(self):
        '''Used to display sample answers in preview of document.'''
        initial_data = []
        answers_questions = [int(answer.get('question')) for answer in self.sample_answers]

        for question in self.questions:
            if question.get_dict_key()[0] in self.template:
                if question.id not in answers_questions:
                    initial_data.append(
                        {
                            'question': question.id
                        }
                    )
                else:
                    index = answers_questions.index(question.id)
                    answer = self.sample_answers[index]
                    if 'date' in answer and answer.get('date'):
                        date = datetime.datetime.strptime(answer.get('date'), '%d.%m.%Y').date()
                        answer['date'] = date.strftime('%Y-%m-%d')
                    initial_data.append(
                        answer
                    )
        return initial_data

    @cached_property
    def template(self):
        content = ' '.join([text_field.content_with_condition for text_field in self.document_text_blocks.all()])
        return mark_safe(content)

    def template_with_answers(self, answers):
        content = ' '.join([text_field.content_with_condition for text_field in self.document_text_blocks.all()])
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

    @property
    def content_with_condition(self):
        if self.text_block_conditions.first():
            condition = self.text_block_conditions.first()
            question_string = condition.question.get_dict_key()[0]
            string_with_condition = '{{% if answers.{} == "{}" %}} {} {{% endif %}}'.format(
                question_string, condition.if_value, self.content)
            return string_with_condition
        else:
            return self.content
