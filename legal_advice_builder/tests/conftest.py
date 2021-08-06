import pytest
from pytest_factoryboy import register

from .factories import AnswerFactory
from .factories import ConditionFactory
from .factories import DocumentFactory
from .factories import LawCaseFactory
from .factories import QuestionaireFactory
from .factories import TextBlockFactory

register(AnswerFactory)
register(ConditionFactory)
register(TextBlockFactory)
register(DocumentFactory)
register(LawCaseFactory)
register(QuestionaireFactory)


@pytest.fixture
def create_user(db, django_user_model):
    def make_user(**kwargs):
        return django_user_model.objects.create_user(**kwargs)
    return make_user
