class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index] if self.tokens else None

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
        """Match the current token with an expected type."""
        if not self.current_token:
            raise SyntaxError("Unexpected end of input")

        if self.current_token[1] == expected_type:
            self.advance()
            return True
        raise SyntaxError(f"Expected {expected_type}, got {self.current_token}")

    def parse(self):
        """Parse the entire input."""
        while self.current_token:
            self.statement()

    def statement(self):
        """Identify and parse different statements."""
        try:
            if self.current_token[1] in ["INT", "FLOAT", "DOUBLE", "STRING", "BOOL"]:
                self.declaration_statement()
            elif self.current_token[1] == "IDENTIFIER":
                # Check if it's a function call or assignment
                if self.peek() and self.peek()[1] == "DEL_LPAREN":
                    self.function_call_statement()
                else:
                    self.assignment_statement()
            elif self.current_token[1] == "IF_KEYWORD":
                self.conditional_statement()
            elif self.current_token[1] in ["FOR_KEYWORD", "WHILE_KEYWORD", "DO_KEYWORD"]:
                self.loop_statement()
            elif self.current_token[1] == "RETURN_KEYWORD":
                self.return_statement()
            else:
                raise SyntaxError(f"Unexpected token: {self.current_token}")
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            # Skip to next statement to continue parsing
            while self.current_token and self.current_token[1] != "DEL_SEMICOLON":
                self.advance()
            if self.current_token:
                self.advance()

    def declaration_statement(self):
        """Parse variable declarations with optional initialization."""
        # Match data type
        data_type = self.current_token[1]
        self.match(data_type)

        # Handle multiple variable declarations
        while True:
            # Match variable name
            self.match("IDENTIFIER")

            # Optional initialization
            if self.current_token and self.current_token[1] == "ASSIGNMENT":
                self.match("ASSIGNMENT")
                self.expression()

            # Check for multiple declarations or end of statement
            if not self.current_token or self.current_token[1] != "DEL_COMMA":
                break
            self.match("DEL_COMMA")

        # Match terminating semicolon
        self.match("DEL_SEMICOLON")

    def assignment_statement(self):
        """Parse assignment statements with complex expressions."""
        self.match("IDENTIFIER")
        self.match("ASSIGNMENT")
        self.expression()
        self.match("DEL_SEMICOLON")

    def function_call_statement(self):
        """Parse function call statements."""
        self.match("IDENTIFIER")
        self.match("DEL_LPAREN")

        # Handle optional arguments
        if self.current_token and self.current_token[1] != "DEL_RPAREN":
            while True:
                self.expression()
                if not self.current_token or self.current_token[1] != "DEL_COMMA":
                    break
                self.match("DEL_COMMA")

        self.match("DEL_RPAREN")
        self.match("DEL_SEMICOLON")

    def conditional_statement(self):
        """Parse if-else conditions with optional else clause."""
        self.match("IF_KEYWORD")
        self.match("DEL_LPAREN")
        self.expression()
        self.match("DEL_RPAREN")
        self.match("DEL_LCURLY")

        # Parse if block statements
        while self.current_token and self.current_token[1] != "DEL_RCURLY":
            self.statement()
        self.match("DEL_RCURLY")

        # Optional else clause
        if self.current_token and self.current_token[1] == "ELSE_KEYWORD":
            self.match("ELSE_KEYWORD")
            self.match("DEL_LCURLY")
            while self.current_token and self.current_token[1] != "DEL_RCURLY":
                self.statement()
            self.match("DEL_RCURLY")

    def loop_statement(self):
        """Parse various loop constructs with more robust parsing."""
        keyword = self.current_token[1]
        self.match(keyword)

        if keyword == "FOR_KEYWORD":
            self.match("DEL_LPAREN")
            # Initialization
            if self.current_token and self.current_token[1] != "DEL_SEMICOLON":
                self.declaration_statement()
            else:
                self.match("DEL_SEMICOLON")

            # Condition
            if self.current_token and self.current_token[1] != "DEL_SEMICOLON":
                self.expression()
            self.match("DEL_SEMICOLON")

            # Increment/Update
            if self.current_token and self.current_token[1] != "DEL_RPAREN":
                self.expression()
            self.match("DEL_RPAREN")
        else:
            # While and do-while loops
            self.match("DEL_LPAREN")
            self.expression()
            self.match("DEL_RPAREN")

        # Loop body
        self.match("DEL_LCURLY")
        while self.current_token and self.current_token[1] != "DEL_RCURLY":
            self.statement()
        self.match("DEL_RCURLY")

    def return_statement(self):
        """Parse return statements."""
        self.match("RETURN_KEYWORD")
        if self.current_token and self.current_token[1] != "DEL_SEMICOLON":
            self.expression()
        self.match("DEL_SEMICOLON")

    def expression(self):
        """
        Parse complex expressions supporting:
        - Literals (int, float, string)
        - Identifiers
        - Arithmetic operations
        - Comparison operations
        - Parenthesized sub-expressions
        """

        def parse_primary():
            if self.current_token[1] in ["IDENTIFIER", "INT_LITERAL", "FLO_LITERAL", "STR_LITERAL"]:
                self.advance()
            elif self.current_token[1] == "DEL_LPAREN":
                self.match("DEL_LPAREN")
                self.expression()
                self.match("DEL_RPAREN")
            else:
                raise SyntaxError(f"Unexpected token in expression: {self.current_token}")

        def parse_multiplicative():
            parse_primary()
            while self.current_token and self.current_token[1] in ["MUL_OP", "DIV_OP"]:
                self.advance()
                parse_primary()

        def parse_additive():
            parse_multiplicative()
            while self.current_token and self.current_token[1] in ["ADD_OP", "SUB_OP"]:
                self.advance()
                parse_multiplicative()

        def parse_comparison():
            parse_additive()
            while self.current_token and self.current_token[1] in ["LT_OP", "GT_OP", "LTE_OP", "GTE_OP", "EQ_OP",
                                                                   "NEQ_OP"]:
                self.advance()
                parse_additive()

        parse_comparison()