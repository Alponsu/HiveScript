class SyntaxAnalyzer:
    def __init__(self):
        # Define grammar rules
        self.data_types = {"int", "float", "double", "char", "string", "bool"}
        self.keywords = {
            "if", "else", "elif", "for", "while", "do", "skip", "stop",
            "return", "main", "struct", "ptr", "address", "deref",
            "allocate", "free", "print", "scan"
        }
        self.operators = {"+", "-", "*", "/", "%", "&&", "||", "!", "==", "!=", "<", ">", "<=", ">="}
        self.assignment_operators = {"=", "+=", "-=", "*=", "/=", "%="}
        self.delimiters = {";", ",", "(", ")", "[", "]", "{", "}"}

    def analyze(self, tokens):
        self.tokens = tokens
        self.current_token = 0
        self.errors = []

        # Start parsing from the main program structure
        if not self.parse_program():
            self.errors.append("Syntax Error: Invalid program structure.")

        if self.errors:
            return f"Syntax Analysis Failed:\n" + "\n".join(self.errors)
        return "Syntax Analysis Passed: No errors found."

    def parse_program(self):
        """
        Parse the main program structure.
        Example:
        main {
            <statements>
        }
        """
        if self.match("KEYWORD", "main"):
            if self.match("DELIMITER", "{"):
                while not self.match("DELIMITER", "}"):
                    if not self.parse_statement():
                        return False
                return True
        return False

    def parse_statement(self):
        """
        Parse different types of statements.
        """
        # Declaration statement
        if self.lookahead_type() == "KEYWORD" and self.lookahead_value() in self.data_types:
            return self.parse_declaration()

        # Conditional statements
        if self.lookahead_type() == "KEYWORD" and self.lookahead_value() in {"if", "else", "elif"}:
            return self.parse_conditional()

        # Loop statements
        if self.lookahead_type() == "KEYWORD" and self.lookahead_value() in {"for", "while", "do"}:
            return self.parse_loop()

        # Input/Output statements
        if self.lookahead_type() == "KEYWORD" and self.lookahead_value() in {"print", "scan"}:
            return self.parse_io()

        # Assignment statement
        if self.lookahead_type() == "IDENTIFIER":
            return self.parse_assignment()

        # Skip and Stop (loop control)
        if self.match("KEYWORD", "skip") or self.match("KEYWORD", "stop"):
            return self.match("DELIMITER", ";")

        # Return statement
        if self.match("KEYWORD", "return"):
            return self.match("DELIMITER", ";")

        return False

    def parse_declaration(self):
        """
        Parse variable declarations.
        Example:
        int a;
        float x = 10.5;
        """
        if self.match("KEYWORD", self.data_types):
            if self.match("IDENTIFIER"):
                if self.match("ASSIGNMENT_OPERATOR"):
                    if not self.match_any(["INTEGER", "FLOAT", "STRING", "CHARACTER", "BOOLEAN"]):
                        return False
                return self.match("DELIMITER", ";")
        return False

    def parse_conditional(self):
        """
        Parse conditional statements.
        Example:
        if (x > 5) { ... }
        else if (y < 10) { ... }
        else { ... }
        """
        if self.match("KEYWORD", {"if", "elif"}):
            if self.match("DELIMITER", "("):
                if self.parse_expression():
                    if self.match("DELIMITER", ")"):
                        if self.match("DELIMITER", "{"):
                            while not self.match("DELIMITER", "}"):
                                if not self.parse_statement():
                                    return False
                            return True
        elif self.match("KEYWORD", "else"):
            if self.match("DELIMITER", "{"):
                while not self.match("DELIMITER", "}"):
                    if not self.parse_statement():
                        return False
                return True
        return False

    def parse_loop(self):
        """
        Parse loop statements.
        Example:
        for (int i = 0; i < 10; i++) { ... }
        while (x > 5) { ... }
        do { ... } while (x < 5);
        """
        if self.match("KEYWORD", "for"):
            if self.match("DELIMITER", "("):
                if self.parse_declaration():
                    if self.parse_expression():
                        if self.match("DELIMITER", ";"):
                            if self.parse_expression():
                                if self.match("DELIMITER", ")"):
                                    if self.match("DELIMITER", "{"):
                                        while not self.match("DELIMITER", "}"):
                                            if not self.parse_statement():
                                                return False
                                        return True
        elif self.match("KEYWORD", "while"):
            if self.match("DELIMITER", "("):
                if self.parse_expression():
                    if self.match("DELIMITER", ")"):
                        if self.match("DELIMITER", "{"):
                            while not self.match("DELIMITER", "}"):
                                if not self.parse_statement():
                                    return False
                            return True
        elif self.match("KEYWORD", "do"):
            if self.match("DELIMITER", "{"):
                while not self.match("DELIMITER", "}"):
                    if not self.parse_statement():
                        return False
                if self.match("KEYWORD", "while"):
                    if self.match("DELIMITER", "("):
                        if self.parse_expression():
                            return self.match("DELIMITER", ");")
        return False

    def parse_io(self):
        """
        Parse input/output statements.
        Example:
        print("Hello");
        scan("%d", &x);
        """
        if self.match("KEYWORD", "print"):
            if self.match("DELIMITER", "("):
                if self.match_any(["STRING", "IDENTIFIER", "INTEGER", "FLOAT"]):
                    if self.match("DELIMITER", ")"):
                        return self.match("DELIMITER", ";")
        elif self.match("KEYWORD", "scan"):
            if self.match("DELIMITER", "("):
                if self.match_any(["STRING", "IDENTIFIER"]):
                    if self.match("DELIMITER", ")"):
                        return self.match("DELIMITER", ";")
        return False

    def parse_assignment(self):
        """
        Parse assignment statements.
        Example:
        x = 10;
        y += 5;
        """
        if self.match("IDENTIFIER"):
            if self.match("ASSIGNMENT_OPERATOR"):
                if self.parse_expression():
                    return self.match("DELIMITER", ";")
        return False

    def parse_expression(self):
        """
        Parse expressions (arithmetic, relational, boolean).
        """
        if self.match_any(["IDENTIFIER", "INTEGER", "FLOAT", "STRING"]):
            while self.lookahead_type() == "OPERATOR":
                self.advance()
                if not self.match_any(["IDENTIFIER", "INTEGER", "FLOAT"]):
                    return False
            return True
        return False

    def match(self, token_type, value=None):
        """
        Match the current token with the given type and optional value.
        """
        if self.current_token < len(self.tokens):
            token_type_actual, token_value_actual = self.tokens[self.current_token].split(": ", 1)
            if token_type_actual == token_type and (value is None or token_value_actual in value):
                self.current_token += 1
                return True
        return False

    def match_any(self, token_types):
        """
        Match the current token with any of the given types.
        """
        if self.current_token < len(self.tokens):
            token_type_actual, _ = self.tokens[self.current_token].split(": ", 1)
            if token_type_actual in token_types:
                self.current_token += 1
                return True
        return False

    def lookahead_type(self):
        """
        Get the type of the current token.
        """
        if self.current_token < len(self.tokens):
            return self.tokens[self.current_token].split(": ", 1)[0]
        return None

    def lookahead_value(self):
        """
        Get the value of the current token.
        """
        if self.current_token < len(self.tokens):
            return self.tokens[self.current_token].split(": ", 1)[1]
        return None

    def advance(self):
        """
        Advance to the next token.
        """
        if self.current_token < len(self.tokens):
            self.current_token += 1
