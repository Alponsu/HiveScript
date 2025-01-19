from tkinter import filedialog
import tkinter as tk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


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
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            y_position = height - 40  # Start from the top of the page
            c.setFont("Helvetica", 10)

            # Write the tokens to the PDF
            for token in tokens:
                if y_position <= 40:  # Check if space is running out
                    c.showPage()  # Create a new page
                    c.setFont("Helvetica", 10)
                    y_position = height - 40  # Reset position to top of new page
                c.drawString(40, y_position, token)
                y_position -= 12  # Move down for the next line

            c.save()
            return file_path
