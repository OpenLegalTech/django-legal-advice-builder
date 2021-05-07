import weasyprint as wp
from django.http import HttpResponse

from .forms import DocumentForm
from .models import Answer


class GenerateEditableDocumentMixin:

    def save_answers(self, answers):
        answer = Answer.objects.create(
            law_case=self.get_lawcase(),
            answers=answers,
        )
        if self.request.user.is_authenticated:
            answer.creator = self.request.user
            answer.save()
        return answer

    def render_done(self, answers=None, **kwargs):
        answer = self.save_answers(answers)
        answer.save_rendered_document()
        form = DocumentForm(instance=answer)
        context = self.get_template_with_context(answer.answers)
        context.update({
            'form': form
        })
        return self.render_to_response(context)


class GeneratePDFDownloadMixin:

    def get_filename(self):
        return 'download.pdf'

    def get_pdf_bytes(self, html_string):
        doc = wp.HTML(string=html_string)
        return doc.write_pdf()

    def generate_pdf_download(self, html_string):
        response = HttpResponse(
            self.get_pdf_bytes(html_string),
            content_type='application/pdf'
        )
        filename = self.get_filename()
        attachment = 'attachment; filename="{}"'.format(filename)
        response['Content-Disposition'] = attachment
        return response
