from pytest_factoryboy import register

from .factories import AnswerFactory
from .factories import DocumentFactory
from .factories import DocumentFieldTypeFactory
from .factories import DocumentTypeFactory
from .factories import LawCaseFactory
from .factories import QuestionaireFactory

register(AnswerFactory)
register(DocumentTypeFactory)
register(DocumentFieldTypeFactory)
register(DocumentFactory)
register(LawCaseFactory)
register(QuestionaireFactory)
