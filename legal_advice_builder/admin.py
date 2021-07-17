from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import Answer
from .models import Condition
from .models import Document
from .models import DocumentField
from .models import DocumentFieldType
from .models import DocumentType
from .models import LawCase
from .models import LawCaseTemplate
from .models import Question
from .models import Questionaire


class ConditionInline(admin.TabularInline):
    model = Condition
    fk_name = 'question'


class QuestionAdmin(TreeAdmin):
    form = movenodeform_factory(Question)
    list_filter = ('questionaire__law_case', 'questionaire')

    inlines = [
        ConditionInline,
    ]


class QuestionaireAdmin(admin.ModelAdmin):
    list_filter = ('law_case', )


class DocumentFieldTypeInline(admin.TabularInline):
    model = DocumentFieldType


class DocumentTypeAdmin(admin.ModelAdmin):
    inlines = [
        DocumentFieldTypeInline,
    ]


class DocumentFieldInline(admin.TabularInline):
    model = DocumentField


class DocumentAdmin(admin.ModelAdmin):
    inlines = [
        DocumentFieldInline,
    ]


admin.site.register(Questionaire, QuestionaireAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(Answer)
admin.site.register(LawCase)
admin.site.register(LawCaseTemplate)
