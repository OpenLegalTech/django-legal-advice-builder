function showForm() {
    document.getElementById('questionaire_form').style.display = 'block';
    document.getElementById('questionaire_detail').style.display = 'none';
    document.getElementById('showFormButton').style.display = 'none';
    document.getElementById('showDetailButton').style.display = 'inline-block'
}

function showDetail() {
    document.getElementById('questionaire_form').style.display = 'none';
    document.getElementById('questionaire_detail').style.display = 'flex';
    document.getElementById('showFormButton').style.display = 'inline-block';
    document.getElementById('showDetailButton').style.display = 'none'
}