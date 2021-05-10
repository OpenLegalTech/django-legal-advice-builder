from pytest_factoryboy import register

from .factories import LawCaseFactory
from .factories import QuestionaireFactory

register(LawCaseFactory)
register(QuestionaireFactory)
