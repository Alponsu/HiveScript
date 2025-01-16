class LexicalAnalyzer:
    def __init__(self):
        self.keywords = {
            "int", "float", "double", "bool", "char", "string",
            "if", "else", "elif", "for", "while", "do", "skip", "stop",
            "return", "import", "from", "print", "scan", "struct",
            "ptr", "address", "deref", "allocate", "free", "val", "main"
        }
        self.reserved_words = {"True", "False", "None"}
        self.arithmetic_operators = {"+", "-", "*", "/", "%"}
        self.boolean_operators = {"&&", "||", "!"}
        self.relational_operators = {"==", "!=", "<", ">", "<=", ">="}
        self.assignment_operators = {"=", "+=", "-=", "*=", "/=", "%="}
        self.unary_operators = {"+", "-", "++", "--"}
        self.delimiters = {";", ",", "(", ")", "[", "]", "{", "}"}
        self.special_characters = {"'", '"'}
        self.comment_start_single = "//"
        self.comment_start_multi = "/*"
        self.comment_end_multi = "*/"
        self.dot_operator = "."

    def tokenize(self, code):
        tokens = []
        i = 0
        length = len(code)

        while i < length:
            char = code[i]

            # Skip whitespace
            if char.isspace():
                i += 1
                continue

            # Single-line comments
            if code[i:i + 2] == self.comment_start_single:
                start = i
                while i < length and code[i] != "\n":
                    i += 1
                tokens.append(f"COMMENT: {code[start:i]}")  # Token for single-line comment
                continue

            # Multi-line comments
            if code[i:i + 2] == self.comment_start_multi:
                start = i
                i += 2
                while i < length and code[i:i + 2] != self.comment_end_multi:
                    i += 1
                i += 2  # Skip closing */
                tokens.append(f"COMMENT: {code[start:i]}")  # Token for multi-line comment
                continue

            # Identifiers and Keywords
            if char.isalpha() or char == "_":
                start = i
                while i < length and (code[i].isalnum() or code[i] == "_"):
                    i += 1
                value = code[start:i]
                if value in self.keywords:
                    tokens.append(f"KEYWORD: {value}")
                elif value in self.reserved_words:
                    tokens.append(f"RESERVED_WORD: {value}")
                else:
                    tokens.append(f"IDENTIFIER: {value}")
                continue

            # Numbers (Integer and Floating Point)
            if char.isdigit() or (char == "." and i + 1 < length and code[i + 1].isdigit()):
                start = i
                is_float = False
                while i < length and (code[i].isdigit() or code[i] == "."):
                    if code[i] == ".":
                        is_float = True
                    i += 1
                value = code[start:i]
                if is_float:
                    tokens.append(f"FLOAT: {value}")
                else:
                    tokens.append(f"INTEGER: {value}")
                continue

            # String Literals
            if char in self.special_characters:
                quote = char
                start = i
                i += 1
                while i < length and code[i] != quote:
                    i += 1
                i += 1  # Skip closing quote
                tokens.append(f"STRING: {code[start:i]}")
                continue

            # Check for two-character operators first (+=, -=, *=, /=, etc.)
            if i + 1 < length:
                two_char_operator = code[i:i + 2]
                if two_char_operator in self.arithmetic_operators.union(self.assignment_operators,
                                                                        self.unary_operators):
                    tokens.append(f"OPERATOR: {two_char_operator}")
                    i += 2
                    continue

            # Then check for single-character operators (like +, -, *, /)
            if char in self.arithmetic_operators or char in self.unary_operators:
                tokens.append(f"OPERATOR: {char}")
                i += 1
                continue

            # Check for boolean operators
            if code[i:i + 2] in self.boolean_operators:
                tokens.append(f"BOOLEAN_OPERATOR: {code[i:i + 2]}")
                i += 2
                continue

            # Check for relational operators
            if code[i:i + 2] in self.relational_operators or char in self.relational_operators:
                start = i
                if i + 1 < length and code[i:i + 2] in self.relational_operators:
                    i += 2
                else:
                    i += 1
                tokens.append(f"RELATIONAL_OPERATOR: {code[start:i]}")
                continue

            # Check for assignment operators
            if char in self.assignment_operators or code[i:i + 2] in self.assignment_operators:
                start = i
                if i + 1 < length and code[i:i + 2] in self.assignment_operators:
                    i += 2
                else:
                    i += 1
                tokens.append(f"ASSIGNMENT_OPERATOR: {code[start:i]}")
                continue

            # Delimiters
            if char in self.delimiters:
                tokens.append(f"DELIMITER: {char}")
                i += 1
                continue

            if char in self.dot_operator:
                tokens.append(f"DOT_OPERATOR: {char}")
                i += 1
                continue

            # Unknown Characters
            tokens.append(f"UNKNOWN: {char}")
            i += 1

        return tokens


