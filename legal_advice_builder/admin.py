from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import Answer
from .models import Condition
from .models import Document
from .models import LawCase
from .models import Question
from .models import Questionaire
from .models import TextBlock
from .models import TextBlockCondition


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


class TextBlockInline(admin.TabularInline):
    model = TextBlock


class DocumentAdmin(admin.ModelAdmin):
    inlines = [
        TextBlockInline,
    ]
    model = Document


class TextBlockConditionInline(admin.TabularInline):
    model = TextBlockCondition


class TextBlockAdmin(admin.ModelAdmin):
    list_filter = ('document', )
    inlines = [
        TextBlockConditionInline,
    ]
    model = TextBlock


admin.site.register(Questionaire, QuestionaireAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(TextBlock, TextBlockAdmin)
admin.site.register(Answer)
admin.site.register(LawCase)
