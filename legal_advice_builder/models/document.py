from django.db import models


class Document(models.Model):
    name = models.CharField(max_length=200)
    document_type = models.ForeignKey('legal_advice_builder.DocumentType',
                                      on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_value_for_field(self, field_type):
        try:
            return self.fields.get(field_type=field_type).content
        except DocumentField.DoesNotExist:
            return ''

    def get_initial_dict(self):
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
    help_text = models.CharField(max_length=500, blank=True)
    required = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class DocumentField(models.Model):
    field_type = models.ForeignKey('legal_advice_builder.DocumentFieldType',
                                   on_delete=models.CASCADE)
    document = models.ForeignKey('legal_advice_builder.Document',
                                 related_name='fields',
                                 on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content
