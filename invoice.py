import pandas as pd
import glob
import datetime
from fpdf import FPDF
from dbconnection import DBConnection
from configdata import ConfigData
from reportlab.pdfgen import canvas
import pdfkit

path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)


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
        id_data = []
        for row in result:
            if row['project'] in time_data:
                time_spent = float(time_data[row['project']]) + float(row['time_spent'])
            else:
                time_spent = float(row['time_spent'])
            time_data[row['project']] = time_spent
            id_data.append(row['ID'])
        connection.close()
        return [id_data, time_data]

    def addInvoice(self, total):
        connection = DBConnection().connect()
        result = connection.execute("INSERT INTO invoices (invoice_total) VALUES (?)", (total, ))

        # Get our new invoice id
        #lastidresult = connection.execute("select last_insert_rowid() as invoice_id")

        invoice_id = result.lastrowid
        connection.commit()
        connection.close()
        return invoice_id

    # Set all the invoiced time slots as invoiced
    def setAsInvoiced(self, id_list):
        connection = DBConnection().connect()
        print(id_list)
        sql = "UPDATE recorded_time SET invoiced=1 WHERE ID in ({seq})".format(
            seq=','.join(['?'] * len(id_list)))
        result = connection.execute(sql, id_list)
        connection.commit()
        connection.close()

    def generateCurrentInvoice(self):
        current_date = datetime.datetime.now()
        current_date_string = current_date.strftime("%d/%m/%Y")

        end_date = current_date + datetime.timedelta(days=14)
        end_date = end_date.strftime("%d/%m/%Y")

        # Get our time data from the database
        invoice_data = self.getInvoiceData()
        time_data = invoice_data[1]
        id_data = invoice_data[0]

        if len(id_data):
            total = 0
            total_time = 0
            breakdown_html = '<table><tr class="heading"><td></td><td>Time</td><td>Cost</td></tr>'
            for time_row in time_data:
                print(time_row)
                print(time_data[time_row])
                project_total = time_data[time_row] * self.client_data['hourly_rate']
                breakdown_html += f"<tr class='item'><td>{time_row}</td><td>{time_data[time_row]}</td><td>£{'%.2f' % project_total}</td></tr>"
                total = total + project_total
                total_time = total_time + time_data[time_row]
            breakdown_html += f'<tr class="item"><td>VAT @ 20%</td><td></td><td>£0</td></tr>'
            breakdown_html += f"<tr class='total'><td>Totals</td><td>{total_time} x £{'%.2f' % self.client_data['hourly_rate']} ph</td><td>£{'%.2f' % total}</td></tr></table>"

            # Add our new invoice
            invoice_id = self.addInvoice(total)

            # Setup the invoice layout
            with open('invoice.html', "r") as file:
                file_content = str(file.read())
            file_content = file_content.replace('\r', '').replace('\n', '')

            # Replace placeholders with correct content
            file_content = file_content.replace('{{breakdown_table}}', breakdown_html)
            file_content = file_content.replace('{{total_string}}', '£' + str('%.2f' % total))
            file_content = file_content.replace('{{invoice_number}}', str(invoice_id))
            file_content = file_content.replace('{{invoice_date}}', current_date_string)
            file_content = file_content.replace('{{due_date}}', end_date)
            file_content = file_content.replace('{{client_details}}', 'WebEvents Global')
            file_content = file_content.replace('{{freelancer_details}}', 'Jamie Lamport<br />13 Rowan Avenue<br />Basingstoke<br />RG23 7FP'
                                                                          '<br /><br />Tel: 07810 898194<br />Email: jamie.lamport@gmail.com')
            pdfkit.from_string(file_content, f"pdf_invoices/{invoice_id}_JamieLamport.pdf", configuration=config)

            self.setAsInvoiced(id_data)
            return 1
        else:
            return 0


if __name__ == '__main__':
    invoiceobj = Invoice(client_id=1)
    invoiceobj.generateCurrentInvoice()
