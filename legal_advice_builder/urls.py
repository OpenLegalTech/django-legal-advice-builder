from django.urls import path

from .views import LawCaseDetail
from .views import LawCaseList
from .views import QuestionaireDetail
from .views import QuestionUpdate

app_name = 'legal_advice_builder'
urlpatterns = [
    path('', LawCaseList.as_view(), name='law-case-list'),
    path('<int:pk>/', LawCaseDetail.as_view(), name='law-case-detail'),
    path('questionaire/<int:pk>/', QuestionaireDetail.as_view(), name='questionaire-detail'),
    path('question/<int:pk>/', QuestionUpdate.as_view(), name='question-update')

]
