from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import Answer
from .models import LawCase
from .models import LawCaseTemplate
from .models import Lawsuit
from .models import Question
from .models import Questionaire
from .models import Template


class QuestionAdmin(TreeAdmin):
    form = movenodeform_factory(Question)
    list_filter = ('questionaire__law_case', 'questionaire')


class QuestionaireAdmin(admin.ModelAdmin):
    list_filter = ('law_case', )


admin.site.register(Questionaire, QuestionaireAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(LawCase)
admin.site.register(LawCaseTemplate)
admin.site.register(Template)
admin.site.register(Lawsuit)
