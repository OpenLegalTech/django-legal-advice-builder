function showQuestionaireForm() {
    document.getElementById('questionaire_form').style.display = 'block';
    document.getElementById('questionaire_detail').style.display = 'none';
    document.getElementById('showFormButton').style.display = 'none';
    document.getElementById('showDetailButton').style.display = 'inline-block'
}

function showQuestionaireDetail() {
    document.getElementById('questionaire_form').style.display = 'none';
    document.getElementById('questionaire_detail').style.display = 'flex';
    document.getElementById('showFormButton').style.display = 'inline-block';
    document.getElementById('showDetailButton').style.display = 'none'
}

function showQuestionForm() {
    document.getElementById('question_form').style.display = 'block';
    document.getElementById('question_detail').style.display = 'none';
    document.getElementById('showQuestionFormButton').style.display = 'none';
    document.getElementById('showQuestionDetailButton').style.display = 'inline-block'
}

function showQuestionDetail() {
    document.getElementById('question_form').style.display = 'none';
    document.getElementById('question_detail').style.display = 'block';
    document.getElementById('showQuestionFormButton').style.display = 'inline-block';
    document.getElementById('showQuestionDetailButton').style.display = 'none'
}