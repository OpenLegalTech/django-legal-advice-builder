import datetime

import bleach


def generate_answers_dict_for_template(answers):
    from .models import Question

    answers_dict = {}
    for answer in answers:
        question = Question.objects.get(id=answer.get('question'))
        option = answer.get('option')
        text = answer.get('text')
        date = answer.get('date')
        if date:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        key, value = question.get_dict_key(option, text, date)
        answers_dict[key] = value
    return answers_dict


def clean_html_field(text, setting='default'):
    allowed_tags = ['p', 'strong', 'em',
                    'u', 'ol', 'li', 'ul', 'h1',
                    'h2', 'h3', 'h4', 'h5']
    allowed_attrs = {'*': ['style']}
    allowed_styles = ['text-align']
    return bleach.clean(text,
                        tags=allowed_tags,
                        attributes=allowed_attrs,
                        styles=allowed_styles,
                        strip=True)
