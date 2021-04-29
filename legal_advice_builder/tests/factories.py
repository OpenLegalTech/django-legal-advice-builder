import factory

from legal_advice_builder.models import LawCase, Questionaire


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
