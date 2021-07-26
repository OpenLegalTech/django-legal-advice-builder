import factory

from legal_advice_builder.models import Document
from legal_advice_builder.models import DocumentFieldType
from legal_advice_builder.models import DocumentType
from legal_advice_builder.models import LawCase
from legal_advice_builder.models import Questionaire


class DocumentTypeFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = DocumentType

    name = factory.Faker('text')
    document_template = factory.Faker('text')


class DocumentFieldTypeFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = DocumentFieldType

    document_type = factory.SubFactory(DocumentTypeFactory)
    name = factory.Faker('text')
    slug = factory.Faker('text')
    help_text = factory.Faker('text')
    required = True


class DocumentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Document

    name = factory.Faker('text')
    document_type = factory.SubFactory(DocumentTypeFactory)


class LawCaseFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = LawCase

    title = factory.Faker('text')


class QuestionaireFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Questionaire

    title = factory.Faker('text')
    short_title = factory.Faker('text')
    law_case = factory.SubFactory(LawCaseFactory)
    order = factory.Faker('random_int')
