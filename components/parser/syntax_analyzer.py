class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index] if self.tokens else None
        self.errors = []  # Store syntax errors

    def advance(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None

    def peek(self):
        if self.current_token_index + 1 < len(self.tokens):
            return self.tokens[self.current_token_index + 1]
        return None

    def match(self, expected_type):
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
        """Ensures the program starts with `int main()`, otherwise stops parsing immediately."""
        self.errors.clear()

        # Allow struct declarations before main function
        while self.current_token and self.current_token[1] == "STRUCT_KEYWORD":
            self.struct_statement()

        # If main function is missing, report error and stop parsing
        if not self.current_token or self.current_token[1] != "INTEGER_KEYWORD" or self.peek()[1] != "MAIN_KEYWORD":
            self.errors.append("Syntax Error: Program must have a main function")
            return  # **Stop parsing immediately**

        self.parse_main_function()

    def parse_main_function(self):
        """Parse the main function."""
        self.match("INTEGER_KEYWORD")
        self.match("MAIN_KEYWORD")
        self.match("DEL_LPAREN")
        self.match("DEL_RPAREN")
        self.match("DEL_LCURLY")

        # Parse statements inside the main function
        while self.current_token and self.current_token[1] != "DEL_RCURLY":
            self.statement()

        self.match("DEL_RCURLY")

    def assignment_statement(self):
        self.match("IDENTIFIER")

        # Handle `i++` or `i--`
        if self.current_token and self.current_token[1] in ["UNARY_INCREMENT", "UNARY_DECREMENT"]:
            self.match(self.current_token[1])
        else:
            self.match("ASSIGNMENT")
            self.expression()

        self.match("DEL_SEMICOLON")

    def unary_increment(self):
        self.match("IDENTIFIER")
        if self.current_token and self.current_token[1] in ["UNARY_INCREMENT", "UNARY_DECREMENT"]:
            self.match(self.current_token[1])
        else:
            self.match("ASSIGNMENT")
            self.expression()

    def statement(self):
        try:
            if self.current_token[1] in ["INTEGER_KEYWORD", "FLOAT_KEYWORD", "DOUBLE_KEYWORD",
                                         "STRING_KEYWORD", "BOOL_KEYWORD", "CHAR_KEYWORD"]:
                self.declaration_statement()
            elif self.current_token[1] == "IDENTIFIER":
                if self.peek() and self.peek()[1] == "DEL_LPAREN":
                    self.function_call_statement()
                elif self.peek() and self.peek()[1] == "DOT_OPERATOR":
                    self.struct_member_assignment()
                else:
                    self.assignment_statement()
            elif self.current_token[1] in ["IF_KEYWORD", "ELSE_KEYWORD", "ELIF_KEYWORD"]:
                self.conditional_statement()
            elif self.current_token[1] in ["FOR_KEYWORD", "WHILE_KEYWORD", "DO_KEYWORD"]:
                self.loop_statement()
            elif self.current_token[1] == "RETURN_KEYWORD":
                self.return_statement()
            elif self.current_token[1] in ["PRINT_KEYWORD", "SCAN_KEYWORD"]:
                self.io_statement()
            elif self.current_token[1] == "STRUCT_KEYWORD":
                if self.peek() and self.peek()[1] == "IDENTIFIER" and self.tokens[self.current_token_index + 2][
                    1] == "DEL_LCURLY":
                    self.struct_statement()
                else:
                    self.declaration_statement()
            elif self.current_token[1] == "POINTER_KEYWORD":
                self.pointer_declaration()
            elif self.current_token[1] in ["ALLOCATE_KEYWORD", "FREE_KEYWORD", "ADDRESS_KEYWORD",
                                           "DEREF_KEYWORD", "VAL_KEYWORD"]:
                self.memory_management_statement()
            elif self.current_token[1] in ["INT_LITERAL", "FLO_LITERAL", "STRING_LIT", "CHAR_LIT"]:
                # **New Fix:** Prevent standalone literals from being treated as statements
                self.errors.append(
                    f"Syntax Error (Line {self.current_token[2]}): Unexpected literal '{self.current_token[0]}'")
                self.skip_to_next_statement()
            else:
                self.skip_to_next_statement()
        except Exception as e:
            self.errors.append(f"Syntax Error: {str(e)}")
            self.skip_to_next_statement()

    def pointer_statement(self):
        """Recursively parse multiple levels of pointer types like ptr[ptr[int]]."""
        if self.current_token[1] == "POINTER_KEYWORD":
            self.match("POINTER_KEYWORD")  # Match 'ptr'
            self.match("DEL_LBRACK")  # Match '['

            # Recursively parse the inner type (could be another pointer or a base type)
            self.pointer_statement()

            self.match("DEL_RBRACK")  # Match ']'
        else:
            # Base type (e.g., int, float, etc.)
            if self.current_token[1] in ["INTEGER_KEYWORD", "FLOAT_KEYWORD", "DOUBLE_KEYWORD", "STRING_KEYWORD",
                                         "BOOL_KEYWORD", "CHAR_KEYWORD", "IDENTIFIER"]:
                self.match(self.current_token[1])  # Match base type (e.g., int, string)
            else:
                self.errors.append(
                    f"Syntax Error (Line {self.current_token[2]}): pointer declaration must have a type'")

    def conditional_statement(self):
        self.match("IF_KEYWORD")
        self.match("DEL_LPAREN")
        self.expression()
        self.match("DEL_RPAREN")
        self.match("DEL_LCURLY")

        while self.current_token and self.current_token[1] != "DEL_RCURLY":
            self.statement()
        self.match("DEL_RCURLY")

        if self.current_token and self.current_token[1] == "ELSE_KEYWORD":
            self.match("ELSE_KEYWORD")
            self.match("DEL_LCURLY")
            while self.current_token and self.current_token[1] != "DEL_RCURLY":
                self.statement()
            self.match("DEL_RCURLY")

    def loop_statement(self):
        if self.current_token[1] == "FOR_KEYWORD":
            self.match("FOR_KEYWORD")
            self.match("DEL_LPAREN")

            # Step 1: Initialization (Must be a variable declaration or assignment)
            if self.current_token and self.current_token[1] != "DEL_SEMICOLON":
                if self.current_token[1] in ["INTEGER_KEYWORD", "FLOAT_KEYWORD", "DOUBLE_KEYWORD"]:
                    self.declaration_statement()
                elif self.current_token[1] == "IDENTIFIER":
                    self.assignment_statement()
                else:
                    self.errors.append(
                        f"Syntax Error (Line {self.current_token[2]}): Expected variable initialization")
                    self.skip_to_next_statement()
                    return


            # Step 2: Condition (Must be a boolean expression)
            if self.current_token and self.current_token[1] not in [
                "IDENTIFIER", "INT_LITERAL", "FLO_LITERAL", "RELATIONAL_LESS_THAN",
                "RELATIONAL_GREATER_THAN", "RELATIONAL_LESS_EQUAL", "RELATIONAL_GREATER_EQUAL",
                "RELATIONAL_EQUALS", "RELATIONAL_NOT_EQUALS"
            ]:
                self.errors.append(
                    f"Syntax Error (Line {self.current_token[2]}): Expected boolean expression as loop condition")
                self.skip_to_next_statement()
                return
            self.expression()  # Parse condition
            self.match("DEL_SEMICOLON")  # Match second semicolon

            # Step 3: Change (Must be an increment, decrement, or assignment)
            if self.current_token and self.current_token[1] != "DEL_RPAREN":
                if self.current_token[1] == "IDENTIFIER":
                    if self.peek() and self.peek()[1] in ["UNARY_INCREMENT", "UNARY_DECREMENT"]:
                        self.unary_increment()
                    else:
                        self.assignment_statement()
                else:
                    self.errors.append(
                        f"Syntax Error (Line {self.current_token[2]}): Expected increment, decrement, or assignment in change statement")
                    self.skip_to_next_statement()
                    return
            self.match("DEL_RPAREN")  # Match closing parenthesis

            # Loop body must be enclosed in `{}`
            self.match("DEL_LCURLY")
            while self.current_token and self.current_token[1] != "DEL_RCURLY":
                self.statement()
            self.match("DEL_RCURLY")


        elif loop_type == "WHILE_KEYWORD":
            self.match("WHILE_KEYWORD")
            self.match("DEL_LPAREN")
            self.expression()
            self.match("DEL_RPAREN")

            self.match("DEL_LCURLY")
            while self.current_token and self.current_token[1] != "DEL_RCURLY":
                self.statement()
            self.match("DEL_RCURLY")

        elif loop_type == "DO_KEYWORD":
            self.match("DO_KEYWORD")
            self.match("DEL_LCURLY")
            while self.current_token and self.current_token[1] != "DEL_RCURLY":
                self.statement()
            self.match("DEL_RCURLY")

            self.match("WHILE_KEYWORD")
            self.match("DEL_LPAREN")
            self.expression()
            self.match("DEL_RPAREN")
            self.match("DEL_SEMICOLON")

    def return_statement(self):
        self.match("RETURN_KEYWORD")
        if self.current_token and self.current_token[1] != "DEL_SEMICOLON":
            self.expression()
        self.match("DEL_SEMICOLON")

    def pointer_declaration(self):
        if self.current_token[1] == "POINTER_KEYWORD":
            self.pointer_statement()  # Parse pointer declaration
            self.match("IDENTIFIER")  # Match the pointer variable name

            if self.current_token[1] == "ASSIGNMENT":
                self.match("ASSIGNMENT")
                self.match("ADDRESS_KEYWORD")
                self.match("DEL_LPAREN")
                self.match("IDENTIFIER")  # Match the variable being referenced
                self.match("DEL_RPAREN")

            self.match("DEL_SEMICOLON")  # Ensure semicolon at the end
            return

        # Handle other types (e.g., int, float, etc.)
        self.match(self.current_token[1])  # Match the base type keyword
        self.match("IDENTIFIER")  # Match the variable name
        self.match("DEL_SEMICOLON")

    def declaration_statement(self):

        if self.current_token[1] == "STRUCT_KEYWORD":
            self.match("STRUCT_KEYWORD")
            if self.current_token and self.current_token[1] == "POINTER_KEYWORD":
                self.match("POINTER_KEYWORD")
                self.match("DEL_LBRACK")
                self.match("IDENTIFIER")
                self.match("DEL_RBRACK")
                self.match("IDENTIFIER")

                if self.current_token and self.current_token[1] == "ASSIGNMENT":
                    self.match("ASSIGNMENT")
                    self.match("ALLOCATE_KEYWORD")
                    self.match("DEL_LPAREN")
                    if self.current_token and self.current_token[1] in ["INT_LITERAL", "IDENTIFIER"]:
                        self.match(self.current_token[1])
                        if self.current_token and self.current_token[1] == "DEL_COMMA":
                            self.match("DEL_COMMA")
                            self.match("INT_LITERAL")
                    self.match("DEL_RPAREN")

                self.match("DEL_SEMICOLON")
                return

        if self.current_token[1] == "STRUCT_KEYWORD":
            self.match("STRUCT_KEYWORD")
            self.match("IDENTIFIER")
            self.match("IDENTIFIER")

            if self.current_token and self.current_token[1] == "ASSIGNMENT":
                self.match("ASSIGNMENT")
                self.match("DEL_LCURLY")
                while self.current_token and self.current_token[1] != "DEL_RCURLY":
                    self.expression()
                    if self.current_token and self.current_token[1] == "DEL_COMMA":
                        self.match("DEL_COMMA")
                self.match("DEL_RCURLY")

            self.match("DEL_SEMICOLON")
            return
            # Match the type keyword (e.g., int, float, etc.)
        self.match(self.current_token[1])

        # Match the first variable name
        if not self.match("IDENTIFIER"):
            return

        # Check for initialization (`=`)
        if self.current_token and self.current_token[1] == "ASSIGNMENT":
            self.match("ASSIGNMENT")

            # **Check if a value exists**
            if not self.current_token or self.current_token[1] in ["DEL_SEMICOLON", "DEL_COMMA"]:
                self.errors.append(f"Syntax Error (Line {self.current_token[2]}): Expected a value after '='")

                # **Force token advancement to prevent infinite loops**
                self.advance()
                return  # **Don't skip the whole statement, just handle the error**

            self.expression()  # Parse the assigned value

        # Handle multiple variable declarations (e.g., int a, b = 5, c;)
        while self.current_token and self.current_token[1] == "DEL_COMMA":
            self.match("DEL_COMMA")

            # Ensure the next token is an identifier
            if not self.match("IDENTIFIER"):
                return

            # Check if the variable has an assignment
            if self.current_token and self.current_token[1] == "ASSIGNMENT":
                self.match("ASSIGNMENT")

                # **Check if a value exists**
                if not self.current_token or self.current_token[1] in ["DEL_SEMICOLON", "DEL_COMMA"]:
                    self.errors.append(f"Syntax Error (Line {self.current_token[2]}): Expected a value after '='")

                    # **Force token advancement to prevent infinite loops**
                    self.advance()
                    return  # **Don't skip the whole statement, just handle the error**

                self.expression()  # Parse the assigned value

        self.match("DEL_SEMICOLON")  # Ensure semicolon at the end

    def io_statement(self):
        """Parse print and scan statements, ensuring correct format string handling."""
        if self.current_token[1] == "PRINT_KEYWORD":
            self.match("PRINT_KEYWORD")
            self.match("DEL_LPAREN")

            # First argument (can be a string or expression)
            if self.current_token and self.current_token[1] == "STRING_LIT":
                self.match("STRING_LIT")
            elif self.current_token and self.current_token[1] == "DEREF_KEYWORD":
                self.dereference_statement()  # Handle deref(identifier)
            else:
                self.errors.append(
                    f"Syntax Error (Line {self.current_token[2]}): Expected format string or valid expression in print statement"
                )
                self.skip_to_next_statement()
                return

            # Handle additional arguments separated by commas
            while self.current_token and self.current_token[1] == "DEL_COMMA":
                self.match("DEL_COMMA")

                if self.current_token and self.current_token[1] == "IDENTIFIER":
                    if self.peek() and self.peek()[1] == "DOT_OPERATOR":
                        self.struct_member_access()
                    else:
                        self.expression()
                elif self.current_token and self.current_token[1] == "DEREF_KEYWORD":
                    self.dereference_statement()  # Handle deref(identifier)
                else:
                    self.errors.append(
                        f"Syntax Error (Line {self.current_token[2]}): Unexpected token '{self.current_token[0]}' in print statement"
                    )
                    self.skip_to_next_statement()
                    return

            self.match("DEL_RPAREN")
            self.match("DEL_SEMICOLON")

        elif self.current_token[1] == "SCAN_KEYWORD":
            self.match("SCAN_KEYWORD")
            self.match("DEL_LPAREN")

            # Handle the format string (e.g., "Enter your age: %d")
            if self.current_token and self.current_token[1] == "STRING_LIT":
                self.match("STRING_LIT")
            else:
                self.errors.append("Syntax Error: Expected format string in scan statement")
                self.skip_to_next_statement()
                return

            # Handle the variable to store the input (e.g., `age`)
            if self.current_token and self.current_token[1] == "DEL_COMMA":
                self.match("DEL_COMMA")
                if self.current_token and self.current_token[1] == "IDENTIFIER":
                    self.match("IDENTIFIER")
                else:
                    self.errors.append("Syntax Error: Expected identifier after comma in scan statement")
                    self.skip_to_next_statement()
                    return
            else:
                self.errors.append("Syntax Error: Expected comma after format string in scan statement")
                self.skip_to_next_statement()
                return

            self.match("DEL_RPAREN")
            self.match("DEL_SEMICOLON")

        else:
            self.errors.append("Syntax Error: Expected PRINT_KEYWORD or SCAN_KEYWORD")

    def dereference_statement(self):
        """Parses deref(identifier) expressions."""
        self.match("DEREF_KEYWORD")
        self.match("DEL_LPAREN")
        self.match("IDENTIFIER")  # Match the identifier inside deref()
        self.match("DEL_RPAREN")

    def memory_management_statement(self):
        if self.current_token[1] == "ALLOCATE_KEYWORD":
            self.match("ALLOCATE_KEYWORD")
            self.match("DEL_LPAREN")
            if self.current_token and self.current_token[1] in ["INT_LITERAL", "IDENTIFIER"]:
                self.match(self.current_token[1])
                if self.current_token and self.current_token[1] == "DEL_COMMA":
                    self.match("DEL_COMMA")
                    self.match("INT_LITERAL")
            self.match("DEL_RPAREN")

        elif self.current_token[1] == "FREE_KEYWORD":
            self.match("FREE_KEYWORD")
            self.match("DEL_LPAREN")
            self.match("IDENTIFIER")
            self.match("DEL_RPAREN")
            self.match("DEL_SEMICOLON")

        elif self.current_token[1] == "DEREF_KEYWORD":
            self.match("DEREF_KEYWORD")
            self.match("DEL_LPAREN")
            self.match("IDENTIFIER")
            self.match("DEL_RPAREN")

        elif self.current_token[1] == "VAL_KEYWORD":
            self.match("VAL_KEYWORD")
            self.match("DEL_LPAREN")
            self.match("IDENTIFIER")
            self.match("DEL_RPAREN")

    def struct_statement(self):
        """Parse struct definitions, ensuring members are declared but not initialized."""
        self.match("STRUCT_KEYWORD")
        self.match("IDENTIFIER")  # Match struct name
        self.match("DEL_LCURLY")  # Match `{` opening brace

        while self.current_token and self.current_token[1] != "DEL_RCURLY":
            if self.current_token[1] in ["INTEGER_KEYWORD", "FLOAT_KEYWORD", "DOUBLE_KEYWORD",
                                         "STRING_KEYWORD", "BOOL_KEYWORD", "CHAR_KEYWORD", "IDENTIFIER"]:
                # Match base type
                data_type = self.current_token[0]
                self.match(self.current_token[1])

                # Match variable name
                if self.current_token[1] == "IDENTIFIER":
                    var_name = self.current_token[0]
                    self.match("IDENTIFIER")
                else:
                    self.errors.append(
                        f"Syntax Error (Line {self.current_token[2]}): Expected identifier for struct member")
                    self.skip_to_next_statement()
                    continue

                # Check if initialization (`=`) is attempted, which is **not allowed**
                if self.current_token and self.current_token[1] == "ASSIGNMENT":
                    self.errors.append(
                        f"Syntax Error (Line {self.current_token[2]}): Initialization of '{var_name}' in struct '{data_type}' is not allowed"
                    )
                    self.skip_to_next_statement()
                    continue

                self.match("DEL_SEMICOLON")  # Ensure `;` at end of declaration

            elif self.current_token[1] == "POINTER_KEYWORD":
                # Match pointer declaration (ptr[type] identifier;)
                self.match("POINTER_KEYWORD")
                self.match("DEL_LBRACK")  # Match `[`
                if self.current_token[1] in ["INTEGER_KEYWORD", "FLOAT_KEYWORD", "DOUBLE_KEYWORD",
                                             "STRING_KEYWORD", "BOOL_KEYWORD", "CHAR_KEYWORD", "IDENTIFIER"]:
                    self.match(self.current_token[1])  # Match base type inside `ptr[type]`
                else:
                    self.errors.append(
                        f"Syntax Error (Line {self.current_token[2]}): Expected base type inside 'ptr[...]'"
                    )
                    self.skip_to_next_statement()
                    continue
                self.match("DEL_RBRACK")  # Match `]`

                # Match pointer variable name
                if self.current_token[1] == "IDENTIFIER":
                    self.match("IDENTIFIER")
                else:
                    self.errors.append(f"Syntax Error (Line {self.current_token[2]}): Expected identifier for pointer")
                    self.skip_to_next_statement()
                    continue

                # Check for assignment (`=`), which **is not allowed** inside structs
                if self.current_token and self.current_token[1] == "ASSIGNMENT":
                    self.errors.append(
                        f"Syntax Error (Line {self.current_token[2]}): Initialization of pointer inside struct is not allowed"
                    )
                    self.skip_to_next_statement()
                    continue

                self.match("DEL_SEMICOLON")  # Ensure `;` at end of pointer declaration

            else:
                self.errors.append(f"Syntax Error (Line {self.current_token[2]}): Invalid struct member declaration")
                self.skip_to_next_statement()

        self.match("DEL_RCURLY")  # Closing `}`
        self.match("DEL_SEMICOLON")  # Ensure `;` at the end of the struct

    def struct_pointer_statement(self):
        """Parse struct pointer assignments."""
        self.match("STRUCT_KEYWORD")
        self.match("POINTER_KEYWORD")
        self.match("DEL_LBRACK")
        self.match("IDENTIFIER")
        self.match("DEL_RBRACK")
        self.match("IDENTIFIER")
        self.match("ASSIGNMENT")
        self.match("ADDRESS_KEYWORD")
        self.match("DEL_LPAREN")
        self.match("IDENTIFIER")
        self.match("DEL_RPAREN")
        self.match("DEL_SEMICOLON")

    def struct_member_assignment(self):
        self.match("IDENTIFIER")
        self.match("DOT_OPERATOR")
        self.match("VAL_KEYWORD")
        self.match("DEL_LPAREN")
        self.match("IDENTIFIER")
        self.match("DEL_RPAREN")
        self.match("ASSIGNMENT")
        self.expression()
        self.match("DEL_SEMICOLON")

    def struct_member_access(self):
        """Handle struct member access inside print statements."""
        self.match("IDENTIFIER")  # Match struct name
        self.match("DOT_OPERATOR")  # Match dot operator
        self.match("VAL_KEYWORD")  # Match member name
        self.match("DEL_LPAREN")
        self.match("IDENTIFIER")
        self.match("DEL_RPAREN")

    def expression(self):
        def parse_primary():
            if self.current_token[1] == "STRING_LIT":
                self.match("STRING_LIT")
            elif self.current_token[1] in ["IDENTIFIER", "INT_LITERAL", "FLO_LITERAL"]:
                if self.current_token[1] == "IDENTIFIER" and self.peek() and self.peek()[1] == "DOT_OPERATOR":
                    self.struct_member_access()
                else:
                    self.match(self.current_token[1])
            elif self.current_token[1] == "DEREF_KEYWORD":
                self.match("DEREF_KEYWORD")
                self.match("DEL_LPAREN")
                self.match("IDENTIFIER")
                self.match("DEL_RPAREN")
            elif self.current_token[1] == "DEL_LPAREN":
                self.match("DEL_LPAREN")
                self.expression()
                self.match("DEL_RPAREN")
            elif self.current_token[1] == "SCAN_KEYWORD":
                self.match("SCAN_KEYWORD")
                self.match("DEL_LPAREN")
                if self.current_token and self.current_token[1] == "STRING_LIT":
                    self.match("STRING_LIT")
                else:
                    self.errors.append(
                        f"Syntax Error (Line {self.current_token[2]}): Expected format string inside scan()")
                    self.skip_to_next_statement()
                    return
                self.match("DEL_RPAREN")
            else:
                self.errors.append(f"Syntax Error (Line {self.current_token[2]}): String is not formatted correctly")
                self.skip_to_next_statement()

        def parse_multiplicative():
            parse_primary()
            while self.current_token and self.current_token[1] in ["ARITHMETIC_MULTIPLY", "ARITHMETIC_DIVIDE"]:
                self.advance()
                parse_primary()

        def parse_additive():
            parse_multiplicative()
            while self.current_token and self.current_token[1] in ["ARITHMETIC_PLUS", "ARITHMETIC_MINUS"]:
                self.advance()
                parse_multiplicative()

        def parse_comparison():
            parse_additive()
            while self.current_token and self.current_token[1] in [
                "RELATIONAL_LESS_THAN", "RELATIONAL_GREATER_THAN",
                "RELATIONAL_LESS_EQUAL", "RELATIONAL_GREATER_EQUAL",
                "RELATIONAL_EQUALS", "RELATIONAL_NOT_EQUALS"
            ]:
                self.advance()
                parse_additive()

        parse_comparison()

    def skip_to_next_statement(self):
        """Skip tokens until a semicolon (;) is found, ensuring proper resumption."""
        while self.current_token and self.current_token[1] != "DEL_SEMICOLON":
            self.advance()

        # **Advance past the semicolon to resume parsing**
        if self.current_token and self.current_token[1] == "DEL_SEMICOLON":
            self.advance()

        # **Ensure parsing continues if tokens remain**
        if self.current_token:
            self.statement()

