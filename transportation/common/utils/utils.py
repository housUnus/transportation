from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile


def generate_pdf(path, context):

    # Rendered
    html_string = render_to_string(path, context)
    html = HTML(string=html_string)
    result = html.write_pdf()

    # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=rappor2t.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output.seek(0)
        print(output.name)
        response.write(output.read())

    return response
