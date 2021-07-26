import pytest


@pytest.mark.django_db
def test_save(answer_factory):

    html_with_script = '<script>alert("hallo")</script>'
    answer = answer_factory(
        rendered_document=html_with_script,
    )

    assert answer.rendered_document == 'alert("hallo")'

    html_with_h1 = '<h1>hallo</h1>'
    answer = answer_factory(
        rendered_document=html_with_h1,
    )

    assert answer.rendered_document == html_with_h1
