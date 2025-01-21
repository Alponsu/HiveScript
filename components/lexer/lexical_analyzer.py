class LexicalAnalyzer:
    def __init__(self):
        self.keywords = {
            "int": "INTEGER_KEYWORD",
            "float": "FLOAT_KEYWORD",
            "double": "DOUBLE_KEYWORD",
            "bool": "BOOL_KEYWORD",
            "char": "CHAR_KEYWORD",
            "string": "STRING_KEYWORD",
            "if": "IF_KEYWORD",
            "else": "ELSE_KEYWORD",
            "elif": "ELIF_KEYWORD",
            "for": "FOR_KEYWORD",
            "while": "WHILE_KEYWORD",
            "do": "DO_KEYWORD",
            "skip": "SKIP_KEYWORD",
            "stop": "STOP_KEYWORD",
            "return": "RETURN_KEYWORD",
            "import": "IMPORT_KEYWORD",
            "from": "FROM_KEYWORD",
            "print": "PRINT_KEYWORD",
            "scan": "SCAN_KEYWORD",
            "struct": "STRUCT_KEYWORD",
            "ptr": "PTR_KEYWORD",
            "address": "ADDRESS_KEYWORD",
            "deref": "DEREF_KEYWORD",
            "allocate": "ALLOCATE_KEYWORD",
            "free": "FREE_KEYWORD",
            "val": "VAL_KEYWORD",
            "main": "MAIN_KEYWORD"
        }
        self.reserved_words = {
            "True": "TRUE_RESERVED",
            "False": "FALSE_RESERVED",
            "None": "NONE_RESERVED"
        }
        self.operators = {
            "arithmetic": {
                "+": "ARITHMETIC_PLUS",
                "-": "ARITHMETIC_MINUS",
                "*": "ARITHMETIC_MULTIPLY",
                "/": "ARITHMETIC_DIVIDE",
                "%": "ARITHMETIC_MODULUS"
            },
            "boolean": {
                "&&": "BOOLEAN_AND",
                "||": "BOOLEAN_OR",
                "!": "BOOLEAN_NOT"
            },
            "relational": {
                "==": "RELATIONAL_EQUALS",
                "!=": "RELATIONAL_NOT_EQUALS",
                "<": "RELATIONAL_LESS_THAN",
                ">": "RELATIONAL_GREATER_THAN",
                "<=": "RELATIONAL_LESS_EQUAL",
                ">=": "RELATIONAL_GREATER_EQUAL"
            },
            "assignment": {
                "=": "ASSIGNMENT",
                "+=": "ASSIGNMENT_ADD",
                "-=": "ASSIGNMENT_SUBTRACT",
                "*=": "ASSIGNMENT_MULTIPLY",
                "/=": "ASSIGNMENT_DIVIDE",
                "%=": "ASSIGNMENT_MODULUS"
            },
            "unary": {
                "+": "UNARY_PLUS",
                "-": "UNARY_MINUS",
                "++": "UNARY_INCREMENT",
                "--": "UNARY_DECREMENT"
            }
        }
        self.delimiters = {
            ";": "DEL_SEMICOLON",
            ",": "DEL_COMMA",
            "(": "DEL_LPAREN",
            ")": "DEL_RPAREN",
            "[": "DEL_LBRACK",
            "]": "DEL_RBRACK",
            "{": "DEL_LCURLY",
            "}": "DEL_RCURLY"
        }
        self.format_specifiers = {
            "%d": "FORMSPECIF_DEC",
            "%f": "FORMSPECIF_FLO",
            "lf": "FORMSPECIF_DOU",
            "%s": "FORMSPECIF_STR",
            "%c": "FORMSPECIF_CHAR",
            "%p": "FORMSPECIF_PTR"
        }
        self.special_characters = {"'", '"'}
        self.comments = {"single": "//", "multi_start": "/*", "multi_end": "*/"}
        self.dot_operator = "."

    def tokenize(self, code):
        tokens = []
        i, length = 0, len(code)

        while i < length:
            char = code[i]

            match char:
                # Skip whitespace
                case _ if char.isspace():
                    i += 1

                # Single-line comments
                case _ if code.startswith(self.comments["single"], i):
                    start = i
                    i = code.find("\n", i)
                    if i == -1:
                        i = length
                    tokens.append((code[start:i], "COMMENT"))

                # Multi-line comments
                case _ if code.startswith(self.comments["multi_start"], i):
                    start = i
                    i = code.find(self.comments["multi_end"], i + 2)
                    if i == -1:
                        i = length
                    else:
                        i += 2
                    tokens.append((code[start:i], "COMMENT"))

                # Identifiers and Keywords
                case _ if char.isalpha() or char == "_":
                    start = i
                    while i < length and (code[i].isalnum() or code[i] == "_"):
                        i += 1
                    value = code[start:i]
                    if value in self.keywords:
                        tokens.append((value, self.keywords[value]))
                    elif value in self.reserved_words:
                        tokens.append((value, self.reserved_words[value]))
                    else:
                        tokens.append((value, "IDENTIFIER"))

                # Numbers (Integer and Floating Point)
                case _ if char.isdigit() or (char == "." and i + 1 < length and code[i + 1].isdigit()):
                    start = i
                    is_float = False
                    while i < length and (code[i].isdigit() or code[i] == "."):
                        if code[i] == ".":
                            is_float = True
                        i += 1
                    tokens.append((code[start:i], "FLO_LITERAL" if is_float else "INT_LITERAL"))

                # String Literals with Embedded Format Specifiers
                case _ if char in self.special_characters:
                    quote = char
                    tokens.append((quote, "SINGLE_QUO" if quote == '\'' else "DOUBLE_QUO"))  # Opening quote
                    i += 1
                    start = i
                    while i < length and code[i] != quote:
                        # Check for format specifiers
                        if code[i:i + 2] in self.format_specifiers:
                            if start < i:
                                tokens.append((code[start:i], "STRING_LIT"))  # Add string literal before %
                            tokens.append((code[i:i + 2], self.format_specifiers[code[i:i + 2]]))  # Format specifier
                            i += 2
                            start = i
                        else:
                            i += 1
                    if start < i:
                        tokens.append((code[start:i], "STRING_LIT"))  # Remaining string literal
                    tokens.append((quote, "SINGLE_QUO" if quote == '\'' else "DOUBLE_QUO"))  # Closing quote
                    i += 1  # Move past the closing quote

                # Operators and Delimiters
                case _:
                    matched = False
                    for op_type, op_set in self.operators.items():
                        if code.startswith(tuple(op_set), i):
                            match = max((op for op in op_set if code.startswith(op, i)), key=len)
                            tokens.append((match, op_set[match]))
                            i += len(match)
                            matched = True
                            break
                    if not matched:
                        if char in self.delimiters:
                            tokens.append((char, self.delimiters[char]))
                            i += 1
                        elif char == self.dot_operator:
                            tokens.append((char, "DOT_OPERATOR"))
                            i += 1
                        else:
                            tokens.append((char, "INVALID_TOKEN"))
                            i += 1

        # Format tokens for aligned output
        max_lexeme_length = max(len(lexeme) for lexeme, _ in tokens)
        formatted_tokens = [
            f"{lexeme.ljust(max_lexeme_length)} {token}" for lexeme, token in tokens
        ]

        return formatted_tokens



