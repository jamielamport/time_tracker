import pdfkit


path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

breakdown = '''
<table>
				<tr class="heading">
					<td>Item</td>

					<td>Price</td>
				</tr>

				<tr class="item">
					<td>Website design</td>

					<td>$300.00</td>
				</tr>

				<tr class="item">
					<td>Hosting (3 months)</td>

					<td>$75.00</td>
				</tr>

				<tr class="item last">
					<td>Domain name (1 year)</td>

					<td>$10.00</td>
				</tr>

				<tr class="total">
					<td></td>

					<td>Total: $385.00</td>
				</tr>
			</table>
'''

with open('invoice.html', "r") as file:
    file_content = str(file.read())
file_content = file_content.replace('\r', '').replace('\n', '')

# Replace placeholders with correct content
file_content = file_content.replace('{{breakdown_table}}', breakdown)

#print(file_content)

pdfkit.from_string(file_content, 'out.pdf', configuration=config)