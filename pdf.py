from django.template.loader import render_to_string
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration


class PDFGenerator:
    """
    A reusable class to generate PDF files.
    """

    def _init_(self, template_name, context, base_url=None, css_path=None):
        """
        Initialize the PDF generator.
        :param template_name: The template file name to use for the PDF.
        :param context: Context data for rendering the template.
        :param base_url: Base URL for assets like images in the template.
        :param css_path: Path to a custom CSS file.
        """
        self.template_name = template_name
        self.context = context
        self.base_url = base_url
        self.css_path = css_path
        self.font_config = FontConfiguration()

    def generate_pdf(self, output_path=None):
        """
        Generates a PDF from the provided template and context.
        :return: PDF binary content.
        """
        # Render HTML string from the template
        html_string = render_to_string(self.template_name, self.context)

        # Convert the HTML to a PDF
        pdf_file = HTML(string=html_string, base_url=self.base_url).write_pdf(
            font_config=self.font_config,
            presentational_hints=True,
            stylesheets=[CSS(self.css_path, font_config=self.font_config)]
            if self.css_path
            else [],
        )

        # Save to file or return bytes
        if output_path:
            with open(output_path, "wb") as pdf_file:
                pdf_file.write(pdf_file)
            return output_path

        return pdf_file
