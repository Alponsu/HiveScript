from tkinter import filedialog
import tkinter as tk


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
