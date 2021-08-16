# Django Legal Advice Builder
[![Coverage Status](https://coveralls.io/repos/github/OpenLegalTech/django-legal-advice-builder/badge.svg)](https://coveralls.io/github/OpenLegalTech/django-legal-advice-builder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/OpenLegalTech/django-legal-advice-builder/blob/main/LICENSE)

Django Legal Advice Builder is a django app the can be used to create, edit and display multi-step questionaires and display the answers to those questionaires in an predefined document template. Basically it implements the three following functionalities:

1. UI to create questionaires with questions and branching
2. UI to create documents with textblocks that can include answers of the users and that can be displayed or not displayed based on the user's answer.
3. UI to display questioniares

## How to get startet
For a quickstart just to see what the project is about you can pull and install the [demo repository](https://github.com/OpenLegalTech/legal-advice-demo).

To add the legal-advice-app to your Django Project you need to:

1) install the app to your projects environment
```
pip install git+https://github.com/OpenLegalTech/django-legal-advice-builder.git
```
2) Add the app and some other required apps to your django settings file
```
INSTALLED_APPS = [
    ...
    'treebeard',
    'legal_advice_builder.apps.LegalAdviceBuilderConfig',
    'tinymce'
    ...
]
```
3) Add the legal-advice-builder urls to your urls.py
```
urlpatterns = [
    ...
    path('advice-builder', include('legal_advice_builder.urls')),
    ...
]
```

4) To add Questionaire urls 
    * add a view that inherits from FormWizardView and 
    * overwrites `get_lawcase()`
    * overwrite `legal_advice_builder/form_wizard.html`


e.g. like this:
```
from legal_advice_builder.models import LawCase
from legal_advice_builder.views import FormWizardView
...
class LawCaseForm(FormWizardView):

    def get_lawcase(self):
        pk = self.kwargs.get('pk')
        return LawCase.objects.get(pk=pk)  
```






