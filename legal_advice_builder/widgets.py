from django import forms


class OptionsWidget(forms.TextInput):
    template_name = 'legal_advice_builder/admin/options_widget_template.html'

    class Media:
        js = ('options_field.js',)
