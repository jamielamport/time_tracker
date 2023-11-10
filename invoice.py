import pandas as pd
import glob
import datetime
from fpdf import FPDF
#from pathlib import Path
from dbconnection import DBConnection
from configdata import ConfigData
from collections import defaultdict


class Invoice:
    def __init__(self, client_id):
        self.client_id = client_id
        settingsobj = ConfigData()
        self.client_data = settingsobj.getClientData(self.client_id)
        self.settings = settingsobj.getSettings()

    def getInvoiceData(self):
        connection = DBConnection().connect()
        result = connection.execute("select ID, project, date, time_spent from recorded_time WHERE client_id=? AND invoiced=0", (self.client_id, ))
        time_data = {}
        for row in result:
            if row['project'] in time_data:
                time_spent = float(time_data[row['project']]) + float(row['time_spent'])
            else:
                time_spent = float(row['time_spent'])
            time_data[row['project']] = time_spent
        connection.close()
        return time_data

    def addInvoice(self, total):
        connection = DBConnection().connect()
        result = connection.execute("INSERT INTO invoices (invoice_total) VALUES (?)", (total, ))

        # Get our new invoice id
        #lastidresult = connection.execute("select last_insert_rowid() as invoice_id")

        invoice_id = result.lastrowid
        connection.commit()
        connection.close()
        return invoice_id


    def generateCurrentInvoice(self):
        current_date = datetime.datetime.now()
        current_date_string = current_date.strftime("%Y.%m.%d")

        # Get our time data from the database
        time_data = self.getInvoiceData()
        total = 0
        for time_row in time_data:
            print(time_row)
            print(time_data[time_row])
            project_total = time_data[time_row] * self.client_data['hourly_rate']
            total = total + project_total

        # Add our new invoice
        invoice_id = self.addInvoice(total)

        # Setup the invoice layout
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        pdf.set_font(family="Arial", size=24, style="B")
        pdf.cell(w=100, h=8, txt=f"INVOICE {invoice_id}", border=0, ln=1)

        # Freelancer Address Details here


        pdf.set_font(family="Arial", size=24, style="B")
        pdf.cell(w=100, h=8, txt=f"Date {current_date_string}", ln=1)

        # Add headers
        pdf.set_font(family="Arial", size=10, style="B")
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=50, h=8, txt='Project', border=1)
        pdf.cell(w=30, h=8, txt='Time Spent', border=1)
        pdf.cell(w=30, h=8, txt='Total', border=1, ln=1)

        # Add rows
        for time_row in time_data:
            print(time_row)
            print(time_data[time_row])
            project_total = time_data[time_row] * self.client_data['hourly_rate']
            pdf.set_font(family="Arial", size=10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(w=50, h=8, txt=str(time_row), border=1)
            pdf.cell(w=30, h=8, txt=str(time_data[time_row]), border=1)
            pdf.cell(w=30, h=8, txt=f"£ {project_total}", border=1, ln=1)

        # Add total row
        pdf.cell(w=50, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="Total", border=1)
        pdf.cell(w=30, h=8, txt=f"£ {total}", border=1, ln=1)

        # Add company name and logo
        #pdf.set_font(family="Arial", size=10, style="B")
        #pdf.cell(w=30, h=8, txt=f"PythonHow")
        #pdf.image("pythonhow.png", w=10)

        pdf.output(f"pdf_invoices/{invoice_id}_JamieLamport.pdf")

if __name__ == '__main__':
    invoiceobj = Invoice(client_id=1)
    invoiceobj.generateCurrentInvoice()
