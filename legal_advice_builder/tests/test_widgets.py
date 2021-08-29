import pytest

from legal_advice_builder.models import Question
from legal_advice_builder.widgets import ConditionsWidget

from .helpers import get_text_question


@pytest.mark.django_db
def test_conditions_widget(questionaire_factory):

    qn = questionaire_factory()
    q_1 = Question.add_root(
        **get_text_question(questionaire=qn)
    )
    q_2 = q_1.add_child(
        **get_text_question(questionaire=qn)
    )

    cw = ConditionsWidget(question=q_1)
    assert len(cw.get_other_questions()) == 1
    assert cw.create_conditions_dict() == []
    assert not cw.get_if_options() == ''
    assert list(cw.get_then_options().keys()) == ['failure', 'question', 'success']
    assert list(cw.get_period_options().keys()) == ['days', 'months', 'years']
    assert cw.get_default_next() == q_2.id

    qn = questionaire_factory()
    q_1 = Question.add_root(
        **get_text_question(questionaire=qn)
    )

    cw = ConditionsWidget(question=q_1)
    assert cw.get_default_next() == ''

    assert 'initial' in cw.get_context('conditions', None, {'id': 'id_conditions'})
