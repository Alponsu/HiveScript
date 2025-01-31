import re

class LexicalAnalyzer:
    def __init__(self):
        self.patterns = [
            (r'//.*', 'COMMENT'),
            (r'/\*.*?\*/', 'COMMENT'),

            (r'%d', 'FORMSPECIF_DEC'),
            (r'%f', 'FORMSPECIF_FLO'),
            (r'%lf', 'FORMSPECIF_DOU'),
            (r'%s', 'FORMSPECIF_STR'),
            (r'%c', 'FORMSPECIF_CHAR'),
            (r'%p', 'FORMSPECIF_PTR'),

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

            (r'\b(int|float|double|bool|char|string|if|else|elif|for|while|do|skip|stop|return|import|from|print|scan|struct|ptr|address|deref|allocate|free|val|main)\b', 'KEYWORD'),

            (r'\b(True|False|None)\b', 'RESERVED'),

            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),

            (r'\d+\.\d+', 'FLO_LITERAL'),
            (r'\d+', 'INT_LITERAL'),

            (r'"[^"]*"', 'STRING_LIT'),
            (r"'[^']*'", 'STRING_LIT'),

            (r';', 'DEL_SEMICOLON'),
            (r',', 'DEL_COMMA'),
            (r'\(', 'DEL_LPAREN'),
            (r'\)', 'DEL_RPAREN'),
            (r'\[', 'DEL_LBRACK'),
            (r'\]', 'DEL_RBRACK'),
            (r'\{', 'DEL_LCURLY'),
            (r'\}', 'DEL_RCURLY'),

            (r'\.', 'DOT_OPERATOR'),

            (r'\s+', None),

            (r'.', 'INVALID_TOKEN')
        ]

        self.regex_patterns = [(re.compile(pattern, re.DOTALL), token_type) for pattern, token_type in self.patterns]

    def tokenize(self, code):
        tokens = []
        position = 0

        while position < len(code):
            matched = False
            for regex, token_type in self.regex_patterns:
                match = regex.match(code, position)
                if match:
                    lexeme = match.group(0)
                    if token_type:  # Skip whitespace
                        # Handle string literals separately
                        if token_type == 'STRING_LIT':
                            tokens.extend(self.tokenize_string_content(lexeme))
                        else:
                            tokens.append((lexeme, token_type))
                    position = match.end()
                    matched = True
                    break

            if not matched:
                raise ValueError(f"Unexpected character at position {position}: {code[position]}")

        return tokens

    def tokenize_string_content(self, string_literal):
        tokens = []
        content = string_literal[1:-1]  # Remove the quotes
        i = 0
        while i < len(content):
            if content[i] == '%' and i + 1 < len(content):
                specifier = content[i:i+2]
                if specifier in {'%d', '%f', '%lf', '%s', '%c', '%p'}:
                    if i > 0:
                        tokens.append((content[:i], 'STRING_LIT'))
                    tokens.append((specifier, f'FORMSPECIF_{specifier[1:].upper()}'))
                    content = content[i+2:]  # Remove processed part
                    i = 0
                    continue
            i += 1

        if content:
            tokens.append((content, 'STRING_LIT'))

        return tokens