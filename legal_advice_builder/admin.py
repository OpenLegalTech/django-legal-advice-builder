import os.path
import tempfile

from django.contrib import admin
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import re_path
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


class LawcaseAdmin(admin.ModelAdmin):
    model = LawCase

    def get_urls(self):
        urls = super().get_urls()
        upload_urls = [
            re_path(r'^upload/$',
                    self.admin_site.admin_view(self.upload_lawcase),
                    name='legal_advice_builder-admin_upload'),
        ]
        return upload_urls + urls

    actions = [
        'export_lawcase'
    ]

    def export_lawcase(self, request, queryset):
        lawcases = queryset
        lawcase_ids = lawcases.values_list('id', flat=True)
        questionaires = Questionaire.objects.filter(
            law_case__id__in=lawcase_ids)
        questionaire_ids = questionaires.values_list('id', flat=True)
        questions = Question.objects.filter(
            questionaire__id__in=questionaire_ids)
        question_ids = questions.values_list('id', flat=True)
        conditions = Condition.objects.filter(
            question__id__in=question_ids)
        text_block_conditions = TextBlockCondition.objects.filter(
            question__id__in=question_ids
        )
        document_ids = lawcases.values_list('document', flat=True)
        documents = Document.objects.filter(id__in=document_ids)
        textblocks = TextBlock.objects.filter(document__id__in=document_ids)

        all_objects = [*lawcases, *questionaires, *questions,
                       *conditions, *text_block_conditions,
                       *documents, *textblocks]
        export_json = serializers.serialize('json', all_objects)
        response = HttpResponse(export_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=export.json'
        return response

    def upload_lawcase(self, request):
        if not request.method == 'POST':
            raise PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied
        uploaded_file = request.FILES['file']
        prefix, suffix = os.path.splitext(uploaded_file.name)
        destination_path = tempfile.mkstemp(
            suffix=suffix, prefix=prefix + "_")[1]
        with open(destination_path, "wb") as fp:
            for chunk in uploaded_file.chunks():
                fp.write(chunk)
        tmp_fixtures = [destination_path]
        fixtures = [destination_path]
        call_command(
            "loaddata",
            *fixtures,
        )
        for tmp_file in tmp_fixtures:
            os.unlink(tmp_file)
        return redirect('admin:legal_advice_builder_lawcase_changelist')


admin.site.register(Questionaire, QuestionaireAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(TextBlock, TextBlockAdmin)
admin.site.register(Answer)
admin.site.register(LawCase, LawcaseAdmin)
