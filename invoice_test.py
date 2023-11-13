from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


styles = getSampleStyleSheet()
import os

def invoice_content(c, doc):
    c.saveState()
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 24)
    c.drawString(50, 770, "INVOICE NR")

    # Address next
    c.setFont("Helvetica", 10)
    c.drawRightString(550, 740, "Jamie Lamport")
    c.drawRightString(550, 720, "13 Rowan Avenue")
    c.drawRightString(550, 700, "Basingstoke")
    c.drawRightString(550, 680, "RG23 7FP")

    c.drawRightString(550, 650, "Tel: 07810898194")
    c.drawRightString(550, 630, "Email: jamie.lamport@gmail.com")

    # Invoice details and date
    c.drawString(50, 600, "Invoice Number: 1234")
    c.drawString(50, 580, "Invoice Date: 10/11/2023")

    # Client details
    c.drawString(50, 550, "To: client name")

    # Electronic payment block
    c.line(50, 520, 560, 520)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(300, 505, "Electronic Transfer Information")
    c.line(50, 495, 560, 495)

    c.setFont("Helvetica", 10)
    c.drawCentredString(300, 481, "Jamie Lamport – A/C No. 80243223– Sort Code: 60-02-49")
    c.drawCentredString(300, 461, "Thank you for your business.")

    # Work and pricing breakdown here
    data = [['Project', 'Time (hours)', 'Total (£)'],
        ['Meeting Center', '17.5', '£45'],
        ['Test', '10', '£21'],
        ['', 'Total', '£66']]
    # Need to add table styles here
    t = Table(data, colWidths=[3*inch,2*inch,2*inch])
    t.wrapOn(c, 800, 800)
    t.drawOn(c, 50, 370)

    c.restoreState()

def breakdown_table(c):
    c.saveState()

    c.restoreState()

def create_pdf():
    doc = SimpleDocTemplate("phello.pdf")
    #c = canvas.Canvas("content_pdf.pdf", pagesize=A4)
    Story = [Spacer(1,2*inch)]
    style = styles["Normal"]
    #for i in range(100):
    #    bogustext = ("This is Paragraph number %s. " % i) * 20
    #p = Paragraph(bogustext, style)
    #Story.append(p)
    Story.append(Spacer(1, 0.2 * inch))

    doc.build(Story, onFirstPage=invoice_content)



    #c.setFillColor(colors.black)
    #c.setFont("Helvetica", 14)
    #c.drawString(50, 660, "In this tutorial, we will demonstrate how to create PDF files using Python.")
    #c.drawString(50, 640, "Python is a versatile programming language that can be used to create different types of files, including PDFs.")
    #c.drawString(50, 620, "By the end of this tutorial, you will be able to generate PDF files using Python and the ReportLab library.")

    #image_path = os.path.join(os.getcwd(), "python_logo.png")
    #c.drawImage(image_path, 50, 400, width=150, height=150)

    #c.save()

if __name__ == "__main__":
    create_pdf()