from django import forms


class OptionsWidget(forms.HiddenInput):
    template_name = 'legal_advice_builder/admin/options_widget_template.html'

    class Media:
        js = ('options_field.js',)
