import factory

from legal_advice_builder.models import Question


def get_question(questionaire=None, short_title=None):
    res_dict = {
        'text': factory.Faker('text'),
    }
    if questionaire:
        res_dict.update({
            'questionaire': questionaire
        })
    if short_title:
        res_dict.update({
            'short_title': short_title
        })
    return res_dict


def get_single_option_question(questionaire=None, short_title=None):
    res_dict = {
        'text': factory.Faker('text'),
        'field_type': Question.SINGLE_OPTION,
        'options': {
            'yes': 'Yes',
            'no': 'No',
            'maybe': 'Maybe'
        }
    }
    if questionaire:
        res_dict.update({
            'questionaire': questionaire
        })
    if short_title:
        res_dict.update({
            'short_title': short_title
        })
    return res_dict


def get_yes_no_question(questionaire=None, short_title=None):
    res_dict = {
        'text': factory.Faker('text'),
        'field_type': Question.YES_NO
    }
    if questionaire:
        res_dict.update({
            'questionaire': questionaire
        })
    if short_title:
        res_dict.update({
            'short_title': short_title
        })
    return res_dict


def get_text_question(questionaire=None, short_title=None):
    res_dict = {
        'text': factory.Faker('text'),
        'field_type': Question.TEXT,
    }
    if questionaire:
        res_dict.update({
            'questionaire': questionaire
        })
    if short_title:
        res_dict.update({
            'short_title': short_title
        })
    return res_dict


def get_date_question(questionaire=None):
    res_dict = {
        'text': factory.Faker('text'),
        'field_type': Question.DATE,
    }

    if questionaire:
        res_dict.update({
            'questionaire': questionaire
        })
    return res_dict
