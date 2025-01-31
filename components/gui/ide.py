import tkinter as tk
from tkinter import filedialog, messagebox
from components.lexer import LexicalAnalyzer
from components.parser.syntax_analyzer import SyntaxAnalyzer
from components.filehandling.file_operations import FileOperations
from components.filehandling.output_handler import OutputHandler


class HiveScriptIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("HiveScript IDE")
        self.file_path = None

        self.lexical_analyzer = LexicalAnalyzer()
        self.syntax_analyzer = SyntaxAnalyzer([])

        # Main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Editor frame
        editor_frame = tk.Frame(main_frame)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame, width=4, padx=3, takefocus=0, border=0,
            background="lightgray", state="disabled", font=("Courier", 12)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Editor
        self.editor = tk.Text(editor_frame, wrap="none", undo=True, font=("Courier", 12))
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.bind("<KeyRelease>", self.update_line_numbers)
        self.editor.bind("<MouseWheel>", self.sync_scroll)

        # Scrollbars
        y_scroll = tk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.editor.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=y_scroll.set)

        # Console frame
        console_frame = tk.Frame(main_frame)
        console_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(console_frame, text="Output", font=("Arial", 14, "bold")).pack(anchor="nw")

        self.output = tk.Text(console_frame, state="disabled", bg="white", fg="black", font=("Courier", 12))
        self.output.pack(fill=tk.BOTH, expand=True)

        # Menu bar
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit)
        self.menu.add_cascade(label="File", menu=file_menu)

        run_menu = tk.Menu(self.menu, tearoff=0)
        run_menu.add_command(label="Lexical Analysis", command=self.lexical_analysis)
        run_menu.add_command(label="Save Lexical Analysis to PDF", command=self.save_lexical_to_pdf)
        run_menu.add_command(label="Syntax Analysis", command=self.syntax_analysis)
        self.menu.add_cascade(label="Run", menu=run_menu)

        self.update_line_numbers()

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)
        line_count = self.editor.index(tk.END).split(".")[0]
        self.line_numbers.insert(1.0, "\n".join(str(i) for i in range(1, int(line_count))))
        self.line_numbers.config(state="disabled")

    def sync_scroll(self, event):
        self.line_numbers.yview_scroll(event.delta, "units")

    def open_file(self):
        content = FileOperations.open_file(self.editor)
        if content:
            self.file_path = content

    def save_file(self):
        FileOperations.save_file(self.editor, self.file_path)

    def lexical_analysis(self):
        code = self.editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "No code to analyze.")
            return

        tokens = self.lexical_analyzer.tokenize(code)
        formatted_tokens = [f"{lexeme.ljust(20)} {token}" for lexeme, token in tokens]
        OutputHandler.display_output(self.output, "Lexical Analysis:\n" + "\n".join(formatted_tokens))

    def save_lexical_to_pdf(self):
        code = self.editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "No code to analyze for PDF output.")
            return

        tokens = self.lexical_analyzer.tokenize(code)
        formatted_tokens = [f"{lexeme.ljust(20)} {token}" for lexeme, token in tokens]
        file_path = FileOperations.save_lexical_output_to_pdf(formatted_tokens)

        if file_path:
            messagebox.showinfo("Success", f"Lexical Analysis saved as PDF at {file_path}")
        else:
            messagebox.showerror("Error", "Failed to save the output as PDF.")

    def syntax_analysis(self):
        code = self.editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "No code to analyze.")
            return

        # Tokenize the code
        tokens = self.lexical_analyzer.tokenize(code)

        # Pass the tokens to the SyntaxAnalyzer
        try:
            self.syntax_analyzer.tokens = tokens  # Set the tokens for syntax analysis
            self.syntax_analyzer.current_token_index = 0
            self.syntax_analyzer.current_token = self.syntax_analyzer.tokens[
                self.syntax_analyzer.current_token_index] if self.syntax_analyzer.tokens else None

            # Perform the syntax analysis
            self.syntax_analyzer.parse()  # This will raise SyntaxError if there's a parsing issue

            # If successful, display the result in the output
            OutputHandler.display_output(self.output, "Syntax Analysis: Success")
        except SyntaxError as e:
            # Display any syntax errors in the output
            OutputHandler.display_output(self.output, f"Syntax Error: {str(e)}")

    def exit(self):
        self.root.quit()