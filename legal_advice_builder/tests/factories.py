import factory

from legal_advice_builder.models import Answer
from legal_advice_builder.models import Condition
from legal_advice_builder.models import Document
from legal_advice_builder.models import LawCase
from legal_advice_builder.models import Questionaire
from legal_advice_builder.models import TextBlock


class DocumentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Document

    name = factory.Faker('text')


class TextBlockFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = TextBlock

    document = factory.SubFactory(DocumentFactory)
    order = factory.Faker('random_int')
    content = factory.Faker('text')


class LawCaseFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = LawCase

    title = factory.Faker('text')


class AnswerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Answer

    law_case = factory.SubFactory(LawCaseFactory)


class QuestionaireFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Questionaire

    title = factory.Faker('text')
    short_title = factory.Faker('text')
    law_case = factory.SubFactory(LawCaseFactory)
    order = factory.Faker('random_int')


class ConditionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Condition
