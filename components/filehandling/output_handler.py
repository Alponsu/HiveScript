import tkinter as tk
from tkinter import messagebox


class OutputHandler:
    @staticmethod
    def display_output(output_widget, content):
        output_widget.config(state="normal")
        output_widget.delete(1.0, tk.END)
        output_widget.insert(tk.END, content)
        output_widget.config(state="disabled")

    @staticmethod
    def execute_code(editor, output_widget):
        code = editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "No code to run.")
            return

        with open("temp_script.py", "w") as temp_file:
            temp_file.write(code)

