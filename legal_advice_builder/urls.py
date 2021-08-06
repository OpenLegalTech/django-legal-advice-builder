from django.urls import path

from .views import DocumentCreateView
from .views import DocumentFormView
from .views import DocumentPreviewView
from .views import LawCaseDelete
from .views import LawCaseEdit
from .views import LawCaseList
from .views import LawCasePreview
from .views import QuestionaireDeleteView
from .views import QuestionaireDetail
from .views import QuestionDelete
from .views import QuestionUpdate

app_name = 'legal_advice_builder'
urlpatterns = [
    path('', LawCaseList.as_view(), name='law-case-list'),
    path('<int:pk>/edit/', LawCaseEdit.as_view(), name='law-case-edit'),
    path('<int:pk>/delete/', LawCaseDelete.as_view(), name='law-case-delete'),
    path('<int:pk>/preview/', LawCasePreview.as_view(), name='law-case-preview'),
    path('<int:pk>/document/create/', DocumentCreateView.as_view(), name='document-create'),
    path('questionaire/<int:pk>/', QuestionaireDetail.as_view(), name='questionaire-detail'),
    path('questionaire/<int:pk>/delete', QuestionaireDeleteView.as_view(), name='questionaire-delete'),
    path('question/<int:pk>/edit', QuestionUpdate.as_view(), name='question-update'),
    path('question/<int:pk>/delete', QuestionDelete.as_view(), name='question-delete'),
    path('document/<int:pk>/edit/', DocumentFormView.as_view(), name='document-update'),
    path('document/<int:pk>/preview/', DocumentPreviewView.as_view(), name='document-detail')
]
