import re

class StrictLexicalAnalyzer:
    def __init__(self):
        self.symbols_table: list[tuple[int, str, str | None]] = []
        self.errors = []

    def analyze(self, code: str):
        self.token_rules = [
            ('COMMENT',       r'#.*'),
            ('KEYWORD',       r'\b(let|be|a|forever|if|or_if|otherwise|as_long_as|for_every|dream|break_free|next_please|give_back|charm|returns|design|inspired_by|follows_blueprint|for_everyone|my_secrets|for_my_circle|blueprint|oopsie|recover_with|panic|with|get_magic_from|share|magic_closet|is|is_not|and|or|not)\b'),
            ('TYPE',          r'\b(Gem|Shimmer|Truth_potion|Letter|Story|Collection|Ensemble)\b'),
            ('BOOLEAN',       r'\b(sparkle_on|sparkle_off)\b'),
            ('SHIMMER',       r'[+-]?\d+\.\d+'),      # Verificación de floats antes que enteros
            ('IDENTIFIER',    r'^[a-zA-Z][a-zA-Z0-9]*$'), # Identifiers
            ('GEM',           r'[+-]?\d+'),           # Integers
            ('STORY',         r'"[^"]*"'),           # Strings
            ('LETTER',        r'\'[^\']\''),          # Chars
            ('MULTI_OP',      r'<=|>='),               # Multi-char operators
            ('OPERATOR',      r'[=+\-*/%<>]'),          # Single-char operators
            ('DELIMITER',     r'[(){}\[\];,:]'),
            ('WHITESPACE',    r'\s+'),
            ('MISMATCH',      r'.'),                  # Un comodín para cualquier otro carácter
        ]
        
        # * Compilar para hacer más eficiente la expresión regular
        self.master_regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_rules))

        # Otra forma de realizar la sentencia de regex completa
        # self.master_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_rules)
        
        for line_num, line in enumerate(code.splitlines(), 0):
            for match in re.finditer(self.master_regex, line):
                token_type = match.lastgroup
                token_value = match.group()

                if token_type == 'WHITESPACE' or token_type == 'COMMENT':
                    continue  
                
                if token_type == 'MISMATCH':
                    self.errors.append(f"Línea {line_num}: Carácter inesperado '{token_value}'")
                else:
                    self.symbols_table.append((line_num, token_value, token_type))

        return self.symbols_table, self.errors
