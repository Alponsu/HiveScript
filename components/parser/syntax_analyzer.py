class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index] if self.tokens else None
        self.errors = []  # Store syntax errors

    def advance(self):
        """Move to the next token."""
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None

    def peek(self):
        """Look at the next token without consuming it."""
        if self.current_token_index + 1 < len(self.tokens):
            return self.tokens[self.current_token_index + 1]
        return None

    def match(self, expected_type):
        """Match the current token with an expected type and report precise line number."""
        if not self.current_token:
            self.errors.append(f"Syntax Error (Line Unknown): Unexpected end of input, expected {expected_type}")
            return False

        lexeme, token_type, line = self.current_token
        if token_type == expected_type:
            self.advance()
            return True
        else:
            self.errors.append(
                f"Syntax Error (Line {line}): Expected {expected_type} before '{lexeme}' ({token_type})"
            )
            return False

    def parse(self):
        """Parse the entire input, ensuring the main function exists."""
        self.errors.clear()  # Reset errors before parsing

        if self.current_token and self.current_token[1] == "INTEGER_KEYWORD":
            self.parse_main_function()
        else:
            self.errors.append("Syntax Error: Program must start with 'int main'")

    def parse_main_function(self):
        """Parse the main function."""
        self.match("INTEGER_KEYWORD")  # int
        self.match("MAIN_KEYWORD")     # main
        self.match("DEL_LCURLY")       # {

        # Parse statements inside the main function
        while self.current_token and self.current_token[1] != "DEL_RCURLY":
            self.statement()

        self.match("DEL_RCURLY")       # }

    def assignment_statement(self):
        """Parse assignment statements, including unary operations."""
        self.match("IDENTIFIER")

        # Handle `i++` or `i--`
        if self.current_token and self.current_token[1] in ["UNARY_INCREMENT", "UNARY_DECREMENT"]:
            self.match(self.current_token[1])
        else:
            self.match("ASSIGNMENT")
            self.expression()

        self.match("DEL_SEMICOLON")

    def statement(self):
        """Identify and parse different statements, including loops."""
        try:
            if self.current_token[1] in [
                "INTEGER_KEYWORD", "FLOAT_KEYWORD", "DOUBLE_KEYWORD", "STRING_KEYWORD", "BOOL_KEYWORD", "CHAR_KEYWORD"
            ]:
                self.declaration_statement()
            elif self.current_token[1] == "IDENTIFIER":
                if self.peek() and self.peek()[1] == "DEL_LPAREN":
                    self.function_call_statement()
                else:
                    self.assignment_statement()
            elif self.current_token[1] in ["FOR_KEYWORD", "WHILE_KEYWORD", "DO_KEYWORD"]:
                self.loop_statement()
            elif self.current_token[1] == "RETURN_KEYWORD":
                self.return_statement()
            else:
                self.errors.append(f"Syntax Error: Unexpected token {self.current_token}")
                self.skip_to_next_statement()
        except Exception as e:
            self.errors.append(f"Syntax Error: {str(e)}")
            self.skip_to_next_statement()

    def loop_statement(self):
        """Parse for, while, and do-while loops."""
        loop_type = self.current_token[1]

        if loop_type == "FOR_KEYWORD":
            self.match("FOR_KEYWORD")
            self.match("DEL_LPAREN")

            # Initialization (either declaration or assignment)
            if self.current_token and self.current_token[1] != "DEL_SEMICOLON":
                if self.current_token[1] in ["INTEGER_KEYWORD", "FLOAT_KEYWORD", "DOUBLE_KEYWORD"]:
                    self.declaration_statement()
                else:
                    self.assignment_statement()
            self.match("DEL_SEMICOLON")

            # Condition expression (optional)
            if self.current_token and self.current_token[1] != "DEL_SEMICOLON":
                self.expression()
            self.match("DEL_SEMICOLON")

            # Update expression (handles `i++`, `i--`, `i = i + 1`)
            if self.current_token and self.current_token[1] != "DEL_RPAREN":
                if self.current_token[1] == "IDENTIFIER":
                    self.assignment_statement()
                else:
                    self.expression()
            self.match("DEL_RPAREN")

        elif loop_type == "WHILE_KEYWORD":
            self.match("WHILE_KEYWORD")
            self.match("DEL_LPAREN")
            self.expression()
            self.match("DEL_RPAREN")

        elif loop_type == "DO_KEYWORD":
            self.match("DO_KEYWORD")

        # Loop body must be enclosed in {}
        self.match("DEL_LCURLY")
        while self.current_token and self.current_token[1] != "DEL_RCURLY":
            self.statement()
        self.match("DEL_RCURLY")

        # For do-while, match `while (condition);`
        if loop_type == "DO_KEYWORD":
            self.match("WHILE_KEYWORD")
            self.match("DEL_LPAREN")
            self.expression()
            self.match("DEL_RPAREN")
            self.match("DEL_SEMICOLON")

    def return_statement(self):
        """Parse return statements."""
        self.match("RETURN_KEYWORD")
        if self.current_token and self.current_token[1] != "DEL_SEMICOLON":
            self.expression()
        self.match("DEL_SEMICOLON")

    def declaration_statement(self):
        """Parse variable declarations."""
        self.match(self.current_token[1])  # Match data type
        if not self.match("IDENTIFIER"):
            return

        if self.current_token and self.current_token[1] == "ASSIGNMENT":
            self.match("ASSIGNMENT")
            self.expression()

        while self.current_token and self.current_token[1] == "DEL_COMMA":
            self.match("DEL_COMMA")
            if not self.match("IDENTIFIER"):
                return

            if self.current_token and self.current_token[1] == "ASSIGNMENT":
                self.match("ASSIGNMENT")
                self.expression()

        self.match("DEL_SEMICOLON")

    def expression(self):
        """Parse expressions including relational and arithmetic operations."""

        def parse_primary():
            """Parse numbers, variables, and parenthesized expressions."""
            if self.current_token[1] in ["IDENTIFIER", "INT_LITERAL", "FLO_LITERAL", "STRING_LIT"]:
                self.advance()
            elif self.current_token[1] == "DEL_LPAREN":
                self.match("DEL_LPAREN")
                self.expression()
                self.match("DEL_RPAREN")
            else:
                self.errors.append(f"Syntax Error: Unexpected token in expression {self.current_token}")

        def parse_multiplicative():
            """Handle multiplication and division operations."""
            parse_primary()
            while self.current_token and self.current_token[1] in ["ARITHMETIC_MULTIPLY", "ARITHMETIC_DIVIDE"]:
                self.advance()
                parse_primary()

        def parse_additive():
            """Handle addition and subtraction operations."""
            parse_multiplicative()
            while self.current_token and self.current_token[1] in ["ARITHMETIC_PLUS", "ARITHMETIC_MINUS"]:
                self.advance()
                parse_multiplicative()

        def parse_comparison():
            """Handle relational comparisons (e.g., <, >, ==, !=)."""
            parse_additive()
            while self.current_token and self.current_token[1] in [
                "RELATIONAL_LESS_THAN", "RELATIONAL_GREATER_THAN",
                "RELATIONAL_LESS_EQUAL", "RELATIONAL_GREATER_EQUAL",
                "RELATIONAL_EQUALS", "RELATIONAL_NOT_EQUALS"
            ]:
                self.advance()
                parse_additive()

        parse_comparison()  # Start parsing the full expression

    def skip_to_next_statement(self):
        """Skip tokens until a semicolon is found to recover from an error."""
        while self.current_token and self.current_token[1] != "DEL_SEMICOLON":
            self.advance()
        if self.current_token:
            self.advance()
