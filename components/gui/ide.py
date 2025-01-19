import tkinter as tk
from tkinter import filedialog, messagebox
from components.lexer import LexicalAnalyzer
#from components.parser import SyntaxAnalyzer
from components.filehandling.file_operations import FileOperations
from components.filehandling.output_handler import OutputHandler


class HiveScriptIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("HiveScript IDE")
        self.file_path = None

        self.lexical_analyzer = LexicalAnalyzer()
        #self.syntax_analyzer = SyntaxAnalyzer()

        # Main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Line numbers
        self.line_numbers = tk.Text(
            main_frame, width=4, padx=3, takefocus=0, border=0, background="lightgray", state="disabled", font=("Courier", 12)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Editor frame
        editor_frame = tk.Frame(main_frame)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.editor = tk.Text(editor_frame, wrap="none", undo=True, font=("Courier", 12))
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.editor.bind("<KeyRelease>", self.update_line_numbers)
        self.editor.bind("<MouseWheel>", self.sync_scroll)

        # Scrollbars for editor
        y_scroll = tk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.on_editor_scroll)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=y_scroll.set)

        x_scroll = tk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.editor.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor.config(xscrollcommand=x_scroll.set)

        # Output frame
        self.output_frame = tk.Frame(root)
        self.output_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.output = tk.Text(
            self.output_frame, height=10, state="disabled", bg="black", fg="white", font=("Courier", 12)
        )
        self.output.pack(side=tk.BOTTOM, fill=tk.X)

        # Menubar
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        # File menu
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit)
        self.menu.add_cascade(label="File", menu=file_menu)

        # Run menu
        run_menu = tk.Menu(self.menu, tearoff=0)
        run_menu.add_command(label="Lexical Analysis", command=self.lexical_analysis)
        run_menu.add_command(label="Syntax Analysis", command=self.syntax_analysis)
        self.menu.add_cascade(label="Run", menu=run_menu)

        self.update_line_numbers()

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)
        line_count = self.editor.index(tk.END).split(".")[0]
        lines = "\n".join(str(i) for i in range(1, int(line_count)))
        self.line_numbers.insert(1.0, lines)
        self.line_numbers.config(state="disabled")

    def on_editor_scroll(self, *args):
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def sync_scroll(self, event):
        self.line_numbers.yview_scroll(event.delta, "units")

    def open_file(self):
        content = FileOperations.open_file(self.editor)
        if content:
            self.file_path = content

    def save_file(self):
        FileOperations.save_file(self.editor, self.file_path)

    def save_file_as(self):
        self.file_path = FileOperations.save_file_as(self.editor)

    def run_code(self):
        OutputHandler.execute_code(self.editor, self.output)

    def lexical_analysis(self):
        code = self.editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "No code to analyze.")
            return

        tokens = self.lexical_analyzer.tokenize(code)
        result = "\n".join(tokens)

        OutputHandler.display_output(self.output, "Lexical Analysis:\n" + result)

    def syntax_analysis(self):
        code = self.editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "No code to analyze.")
            return

        tokens = self.lexical_analyzer.tokenize(code)
        analysis_result = self.syntax_analyzer.analyze(tokens)

        OutputHandler.display_output(self.output, "Syntax Analysis:\n" + analysis_result)

    def exit(self):
        self.root.quit()
