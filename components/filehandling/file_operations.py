from tkinter import filedialog
import tkinter as tk
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

class FileOperations:
    @staticmethod
    def open_file(editor):
        file_path = filedialog.askopenfilename(filetypes=[("Hivescript Files", "*.hst")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
            editor.delete(1.0, tk.END)
            editor.insert(1.0, content)
            return file_path

    @staticmethod
    def save_file(editor, file_path):
        if file_path:
            with open(file_path, "w") as file:
                file.write(editor.get(1.0, tk.END))
        else:
            FileOperations.save_file_as(editor)

    @staticmethod
    def save_file_as(editor):
        file_path = filedialog.asksaveasfilename(defaultextension=".hst", filetypes=[("Hivescript Files", "*.hst")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(editor.get(1.0, tk.END))
            return file_path

    @staticmethod
    def save_lexical_output_to_pdf(tokens, file_path=None):
        if not file_path:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])

        if file_path:
            # Create the PDF document
            pdf = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []

            # Prepare table data
            table_data = [["Lexeme", "Token"]]  # Header row
            for token in tokens:
                lexeme, token_type = token.split(maxsplit=1)
                table_data.append([lexeme, token_type])

            # Create the table
            table = Table(table_data, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(table)

            pdf.build(elements)
            return file_path
