from django.urls import path

from .admin_views import DocumentCreateView
from .admin_views import DocumentFormView
from .admin_views import DocumentPreviewView
from .admin_views import LawCaseDelete
from .admin_views import LawCaseEdit
from .admin_views import LawCaseList
from .admin_views import LawCasePreview
from .admin_views import QuestionaireCreate
from .admin_views import QuestionaireDeleteView
from .admin_views import QuestionaireDetail
from .admin_views import QuestionDelete
from .admin_views import QuestionUpdate
from .admin_views import AnswerEditView
from .admin_views import DownloadAnswerAsPDFView
from .admin_views import DownloadAnswerAsWordView
from .admin_views import DownloadAnswerAsHTMLView

app_name = 'legal_advice_builder'
urlpatterns = [
    path('', LawCaseList.as_view(), name='law-case-list'),
    path('<int:pk>/edit/', LawCaseEdit.as_view(), name='law-case-edit'),
    path('<int:pk>/delete/', LawCaseDelete.as_view(), name='law-case-delete'),
    path('<int:pk>/preview/', LawCasePreview.as_view(), name='law-case-preview'),
    path('<int:pk>/document/create/', DocumentCreateView.as_view(), name='document-create'),
    path('<int:pk>/questionaire/create/', QuestionaireCreate.as_view(), name='questionaire-create'),
    path('questionaire/<int:pk>/', QuestionaireDetail.as_view(), name='questionaire-detail'),
    path('questionaire/<int:pk>/delete', QuestionaireDeleteView.as_view(), name='questionaire-delete'),
    path('question/<int:pk>/edit', QuestionUpdate.as_view(), name='question-update'),
    path('question/<int:pk>/delete', QuestionDelete.as_view(), name='question-delete'),
    path('document/<int:pk>/edit/', DocumentFormView.as_view(), name='document-update'),
    path('document/<int:pk>/preview/', DocumentPreviewView.as_view(), name='document-detail'),
    path('answer/<int:pk>/edit/', AnswerEditView.as_view(), name='answer-update'),
    path('answer/<int:pk>/pdfdownload/', DownloadAnswerAsPDFView.as_view(), name='answer-pdf-download'),
    path('answer/<int:pk>/worddownload/', DownloadAnswerAsWordView.as_view(), name='answer-word-download'),
    path('answer/<int:pk>/htmldownload/', DownloadAnswerAsHTMLView.as_view(), name='answer-html-download')
]
