from django.db import models
from django.template import Context
from django.template import Template
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from legal_advice_builder.utils import clean_html_field
from legal_advice_builder.utils import generate_answers_dict_for_template


class Document(models.Model):
    name = models.CharField(max_length=200)
    document_type = models.ForeignKey('legal_advice_builder.DocumentType',
                                      on_delete=models.CASCADE)

    recipient = models.TextField(blank=True)
    sender = models.TextField(blank=True)
    date = models.CharField(blank=True, max_length=50)
    subject = models.CharField(blank=True, max_length=200)
    signature = models.TextField(blank=True)

    sample_answers = models.JSONField(null=True, default=dict, blank=True)

    def __str__(self):
        return self.name

    def get_value_for_field(self, field_type):
        try:
            return self.fields.get(field_type=field_type).content
        except DocumentField.DoesNotExist:
            return ''

    def get_initial_fields_dict(self):
        initial_data = []
        for field_type in self.document_type.field_types.all():
            initial_data.append(
                {
                    'field_type': field_type.id,
                    'document': self.id,
                    'content': self.get_value_for_field(field_type)
                }
            )
        return initial_data

    def get_initial_questions_dict(self):
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

    def fields_for_context(self):
        context = {}
        for field in self.fields.all():
            dict_key = field.field_type.slug
            context[dict_key] = mark_safe(field.content)
        return context

    @property
    def template(self):
        template = Template(self.document_type.document_template)
        context = self.fields_for_context()
        return template.render(Context(
            context
        ))

    def template_with_answers(self, answers):
        template = Template(mark_safe(self.document_type.document_template))
        context = self.fields_for_context()
        base_template = template.render(Context(context))
        result_template = Template(mark_safe(base_template))
        result = result_template.render(Context(
            {'answers': generate_answers_dict_for_template(answers)}
        ))
        return result

    @property
    def template_with_sample_answers(self):
        return self.template_with_answers(self.sample_answers)


class DocumentType(models.Model):
    name = models.CharField(max_length=200)
    document_template = models.TextField()

    def __str__(self):
        return self.name


class DocumentFieldType(models.Model):
    document_type = models.ForeignKey('legal_advice_builder.DocumentType',
                                      related_name='field_types',
                                      on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    help_text = models.CharField(max_length=500, blank=True)
    required = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name).replace("-", "_")
        super().save(*args, **kwargs)


class DocumentField(models.Model):
    field_type = models.ForeignKey('legal_advice_builder.DocumentFieldType',
                                   on_delete=models.CASCADE)
    document = models.ForeignKey('legal_advice_builder.Document',
                                 related_name='fields',
                                 on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content

    def save(self, *args, **kwargs):
        self.content = clean_html_field(self.content)
        return super().save(*args, **kwargs)
