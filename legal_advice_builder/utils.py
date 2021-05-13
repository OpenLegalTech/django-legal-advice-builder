def generate_answers_dict_for_template(answers):
    from .models import Question

    answers_dict = {}
    for answer in answers:
        question = Question.objects.get(id=answer.get('question'))
        option = answer.get('option')
        text = answer.get('text')
        date = answer.get('date')
        key, value = question.get_dict_key(option, text, date)
        answers_dict[key] = value
    return answers_dict
