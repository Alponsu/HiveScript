import re

class LexicalAnalyzer:
    def __init__(self):
        self.patterns = [
            (r'//.*', 'COMMENT'),
            (r'/\*.*?\*/', 'COMMENT'),

            # Format Specifiers (No longer handled separately)
            (r'%d', 'FORMSPECIF_INT'),
            (r'%f', 'FORMSPECIF_FLOAT'),
            (r'%lf', 'FORMSPECIF_DOUBLE'),
            (r'%s', 'FORMSPECIF_STRING'),
            (r'%c', 'FORMSPECIF_CHAR'),
            (r'%p', 'FORMSPECIF_PTR'),

            # Operators
            (r'<=', 'RELATIONAL_LESS_EQUAL'),
            (r'>=', 'RELATIONAL_GREATER_EQUAL'),
            (r'==', 'RELATIONAL_EQUALS'),
            (r'!=', 'RELATIONAL_NOT_EQUALS'),
            (r'\+\+', 'UNARY_INCREMENT'),
            (r'--', 'UNARY_DECREMENT'),
            (r'\+=', 'ASSIGNMENT_ADD'),
            (r'-=', 'ASSIGNMENT_SUBTRACT'),
            (r'\*=', 'ASSIGNMENT_MULTIPLY'),
            (r'/=', 'ASSIGNMENT_DIVIDE'),
            (r'%=', 'ASSIGNMENT_MODULUS'),
            (r'&&', 'BOOLEAN_AND'),
            (r'\|\|', 'BOOLEAN_OR'),

            (r'<', 'RELATIONAL_LESS_THAN'),
            (r'>', 'RELATIONAL_GREATER_THAN'),
            (r'=', 'ASSIGNMENT'),
            (r'\+', 'ARITHMETIC_PLUS'),
            (r'-', 'ARITHMETIC_MINUS'),
            (r'\*', 'ARITHMETIC_MULTIPLY'),
            (r'/', 'ARITHMETIC_DIVIDE'),
            (r'%', 'ARITHMETIC_MODULUS'),
            (r'!', 'BOOLEAN_NOT'),

            # Keywords (Refactored)
            (r'\bint\b', 'INTEGER_KEYWORD'),
            (r'\bfloat\b', 'FLOAT_KEYWORD'),
            (r'\bdouble\b', 'DOUBLE_KEYWORD'),
            (r'\bbool\b', 'BOOL_KEYWORD'),
            (r'\bchar\b', 'CHAR_KEYWORD'),
            (r'\bstring\b', 'STRING_KEYWORD'),

            (r'\bif\b', 'IF_KEYWORD'),
            (r'\belse\b', 'ELSE_KEYWORD'),
            (r'\belif\b', 'ELIF_KEYWORD'),
            (r'\bfor\b', 'FOR_KEYWORD'),
            (r'\bwhile\b', 'WHILE_KEYWORD'),
            (r'\bdo\b', 'DO_KEYWORD'),
            (r'\bskip\b', 'SKIP_KEYWORD'),
            (r'\bstop\b', 'STOP_KEYWORD'),
            (r'\breturn\b', 'RETURN_KEYWORD'),
            (r'\bimport\b', 'IMPORT_KEYWORD'),
            (r'\bfrom\b', 'FROM_KEYWORD'),
            (r'\bprint\b', 'PRINT_KEYWORD'),
            (r'\bscan\b', 'SCAN_KEYWORD'),
            (r'\bstruct\b', 'STRUCT_KEYWORD'),
            (r'\bptr\b', 'POINTER_KEYWORD'),
            (r'\baddress\b', 'ADDRESS_KEYWORD'),
            (r'\bderef\b', 'DEREF_KEYWORD'),
            (r'\ballocate\b', 'ALLOCATE_KEYWORD'),
            (r'\bfree\b', 'FREE_KEYWORD'),
            (r'\bval\b', 'VAL_KEYWORD'),
            (r'\bmain\b', 'MAIN_KEYWORD'),

            # Reserved Words
            (r'\b(True|False|None)\b', 'RESERVED'),

            # Identifiers
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),

            # Literals
            (r'\d+\.\d+', 'FLO_LITERAL'),
            (r'\d+', 'INT_LITERAL'),

            # String Literals
            (r'"[^"]*"', 'STRING_LIT'),
            (r"'[^']*'", 'STRING_LIT'),

            # Delimiters
            (r';', 'DEL_SEMICOLON'),
            (r',', 'DEL_COMMA'),
            (r'\(', 'DEL_LPAREN'),
            (r'\)', 'DEL_RPAREN'),
            (r'\[', 'DEL_LBRACK'),
            (r'\]', 'DEL_RBRACK'),
            (r'\{', 'DEL_LCURLY'),
            (r'\}', 'DEL_RCURLY'),

            (r'\.', 'DOT_OPERATOR'),

            # Ignore whitespace
            (r'\s+', None),

            # Catch all invalid tokens
            (r'.', 'INVALID_TOKEN')
        ]

        self.regex_patterns = [(re.compile(pattern, re.DOTALL), token_type) for pattern, token_type in self.patterns]

    def tokenize(self, code):
        tokens = []
        position = 0
        line = 1

        while position < len(code):
            matched = False
            for regex, token_type in self.regex_patterns:
                match = regex.match(code, position)
                if match:
                    lexeme = match.group(0)
                    if token_type:
                        if token_type == 'STRING_LIT':
                            tokens.append((lexeme, 'STRING_LIT', line))  # No special handling for format specifiers
                        else:
                            tokens.append((lexeme, token_type, line))
                    position = match.end()
                    matched = True

                    # Track line numbers
                    line += lexeme.count("\n")
                    break

            if not matched:
                tokens.append((code[position], "INVALID_TOKEN", line))
                position += 1

        return tokens
