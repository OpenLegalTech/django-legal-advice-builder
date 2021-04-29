from pytest_factoryboy import register

from .factories import LawCaseFactory, QuestionaireFactory

register(LawCaseFactory)
register(QuestionaireFactory)
