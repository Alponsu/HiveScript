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
                    if i == -1: i = length
                    tokens.append(f"COMMENT: {code[start:i]}")

                # Multi-line comments
                case _ if code.startswith(self.comments["multi_start"], i):
                    start = i
                    i = code.find(self.comments["multi_end"], i + 2)
                    if i == -1: i = length
                    else: i += 2
                    tokens.append(f"COMMENT: {code[start:i]}")

                # Identifiers and Keywords
                case _ if char.isalpha() or char == "_":
                    start = i
                    while i < length and (code[i].isalnum() or code[i] == "_"):
                        i += 1
                    value = code[start:i]
                    if value in self.keywords:
                        tokens.append(f"{self.keywords[value]} {value}")
                    elif value in self.reserved_words:
                        tokens.append(f"{self.reserved_words[value]} {value}")
                    else:
                        tokens.append(f"IDENTIFIER: {value}")

                # Numbers (Integer and Floating Point)
                case _ if char.isdigit() or (char == "." and i + 1 < length and code[i + 1].isdigit()):
                    start = i
                    is_float = False
                    while i < length and (code[i].isdigit() or code[i] == "."):
                        if code[i] == ".": is_float = True
                        i += 1
                    tokens.append(f"{'FLOAT:' if is_float else 'INTEGER:'} {code[start:i]}")

                # String Literals
                case _ if char in self.special_characters:
                    quote = char
                    start = i
                    i += 1
                    while i < length and code[i] != quote:
                        i += 1
                    i += 1  # Include closing quote
                    tokens.append(f"STRING: {code[start:i]}")

                # Operators and Delimiters
                case _:
                    matched = False
                    for op_type, op_set in self.operators.items():
                        if code.startswith(tuple(op_set), i):
                            match = max((op for op in op_set if code.startswith(op, i)), key=len)
                            tokens.append(f"{op_set[match]} {match}")
                            i += len(match)
                            matched = True
                            break
                    if not matched:
                        if char in self.delimiters:
                            tokens.append(f"{self.delimiters[char]} {char}")
                            i += 1
                        elif char == self.dot_operator:
                            tokens.append(f"DOT_OPERATOR: {char}")
                            i += 1
                        else:
                            tokens.append(f"INVALID TOKEN: {char}")
                            i += 1

        return tokens
