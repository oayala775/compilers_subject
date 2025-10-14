import re

class StrictLexicalAnalyzer:
    def __init__(self):
        self.symbols_table: list[tuple[int, str, str]] = []
        self.correct_tokens = []
        self.errors = []
        self.keywords = {
            'let', 'be', 'a', 'forever', 'if', 'or_if', 'otherwise', 'as_long_as',
            'for_every', 'dream', 'break_free', 'next_please', 'give_back', 'charm',
            'returns', 'design', 'inspired_by', 'follows_blueprint', 'for_everyone',
            'my_secrets', 'for_my_circle', 'blueprint', 'oopsie', 'recover_with',
            'panic', 'with', 'get_magic_from', 'share', 'magic_closet'
        }
        
        self.types = {
            'Gem', 'Shimmer', 'Truth_potion', 'Letter', 'Story', 'Collection', 'Ensemble'
        }
        
        self.boolean_values = {
            'sparkle_on', 'sparkle_off'
        }
        
        self.valid_operators = {'=', '+', '-', '*', '/', '%', '(', ')', '{', '}', 
                               '[', ']', ',', ';', ':', '.', '<', '>', '!', '&', '|'}
        
        self.valid_multi_char_operators = {'<=', '>=', '==', '!=', '&&', '||'}

    def is_logic_operator(self, token: str) -> str:
        for valid_operator in self.valid_multi_char_operators:
            match = re.match(f'{valid_operator}', token)
            if match:
                return True
        return False

    def is_keyword(self, token: str) -> str:
        for keyword in self.keywords:
            match = re.match(f'{keyword}', token)
            if match:
                return True
        return False

    def is_valid_var_name(self, token: str) -> str:
        match = re.match(r'^[a-zA-Z_-][a-zA-Z_0-9]+$', token)
        if match:
            return True
        return False

    def check_var_declaration(self, tokens: list[str], line_num: int):
        while len(tokens) > 0:
            keyword = tokens.pop(0)
            self.symbols_table.append((line_num, keyword, 'Identificador'))
            self.correct_tokens.append(keyword)
            # Check if next to a keyword is a valid var name
            if not self.is_valid_var_name(tokens[0]):
                self.errors.append(f"Nombre de variable inválido en línea {line_num}: {tokens[0]}")
                # return False
            var_name: str = tokens.pop(0)
            self.correct_tokens.append(var_name)
            self.symbols_table.append((line_num, var_name, 'Nombre de variable'))
            # Check if next to a var name is the 'be a' syntax
            match_be = re.fullmatch('be', tokens[0])
            if not match_be:
                self.errors.append(f"Sentencia de asignación incompleta en línea {line_num}")
                # return False
            tokens.pop(0)
            match_a = re.fullmatch('a', tokens[0])
            if not match_a:
                self.errors.append(f"Sentencia de asignación incompleta en línea {line_num}")
                # return False
            tokens.pop(0)
            self.correct_tokens.append("be a")
            self.symbols_table.append((line_num, 'be a', 'Asignación'))
            # Check if next to be a is a valid data type
            if not self.is_valid_datatype(tokens[0]):
                # If it's not a valid datatype, then it could be a declaration
                match_semicolon = re.match(r'^.*;$', tokens[0])
                if match_semicolon:
                    separated_lines = match_semicolon.group(0).split(';')
                    data_type = separated_lines[0]
                    if self.is_valid_datatype(data_type):
                        self.correct_tokens.append(data_type)
                        self.symbols_table.append((line_num, data_type, 'Tipo de dato'))
                        self.correct_tokens.append(";")
                        self.symbols_table.append((line_num, ";", 'Fin de linea'))
                        return
                # If semicolon can't be found then it's an error
                else: 
                    self.errors.append(f"No se encontró caracter de fin de línea ';' en la línea {line_num}")
                    # return False
            # If a valid data type is found it's then added to the results
            type: str = tokens.pop(0)
            self.correct_tokens.append(type)
            self.symbols_table.append((line_num, type, 'Tipo de dato'))
            # After data type must come an assignation
            if tokens[0] == '=':
                match_eq = re.match('=', tokens[0])
                if not match_eq:
                    self.errors.append(f"No se encontró asignación en la línea {line_num}")
                    # return False
                tokens.pop(0)
                self.correct_tokens.append("=")
                self.symbols_table.append((line_num, "=", 'Asignación'))
                # Searches for semicolon
                match_semicolon = re.match(r'^.*;$', tokens[0])
                if not match_semicolon:
                    self.errors.append(f"No se encontró caracter de fin de línea ';' en la línea {line_num}")
                    # return False
                # if semicolon is found then it's splitted and then obtained the assignation value
                separated_lines = match_semicolon.group(0).split(';')
                assignation_value = separated_lines[0]
                was_assignation_correct: bool = self.check_correct_assignation(type, assignation_value)
                if not was_assignation_correct:
                    self.errors.append(f"El tipo de dato y su valor no son correspondientes, en línea {line_num}")
                    # return False
                tokens.pop(0)
                self.correct_tokens.append(assignation_value)
                self.symbols_table.append((line_num, assignation_value, 'Valor'))
                self.correct_tokens.append(';')
                self.symbols_table.append((line_num, ';', 'Fin de línea'))
    
    def check_correct_assignation(self, data_type: str, token: str):
        expected_result_for_each_datatype = { 'Gem': r'[0-9]+', 'Shimmer': r'[0-9]+\.[0-9]+', 'Truth_potion': r'(sparkle_on|sparkle_off)', 'Letter': r"\'\w\'"}
        match = re.match(expected_result_for_each_datatype[data_type], token)
        return True if match else False

    def is_valid_datatype(self, token: str) -> bool:
        return token in self.types
    
    def remove_comments(self, line: str) -> str:
        return re.sub(r'#.*', '',line).rstrip()

    def separate_line_by_tokens(self, line: str) -> list[str]:
        return re.findall(r"\S+",line)

    def analyze(self, code: str):
        lines: list[str] = code.splitlines()
        comments = []
        
        for line_num, line in enumerate(lines, 1):

            line = self.remove_comments(line)
            tokens = self.separate_line_by_tokens(line)
                
            print(f"TOKENS: {tokens}")
            if tokens:
                while len(tokens) > 0:
                    if not self.is_keyword(tokens[0]):
                        break
                    if tokens[0] == 'let':
                        if not self.check_var_declaration(tokens, line_num):
                            break
                    break

            print(f"CORRECT VALUES: \n{self.correct_tokens}")
            print(f"ERRORS: \n{self.errors}")
            print(f"SYMBOLS TABLE: \n{self.errors}")

        return self.symbols_table, self.errors

            



            # pos: int = 0
            # if len(token) > 0:
            #     while pos < len(line):
            #         if line[pos].isspace():
            #             pos += 1
            #             continue
                    
            #         # Operadores multi-carácter
            #         if pos + 1 < len(line):
            #             two_char = line[pos:pos+2]
            #             if two_char in self.valid_multi_char_operators:
            #                 tokens.append((line_num, two_char, 'Operador'))
            #                 pos += 2
            #                 continue
                    
            #         # Operadores de un carácter
            #         if line[pos] in self.valid_operators:
            #             tokens.append((line_num, line[pos], 'Operador'))
            #             pos += 1
            #             continue
                    
            #         # Números decimales
            #         decimal_match = re.match(r'[+-]?(\d+\.\d+|\.\d+|\d+\.)', line[pos:])
            #         if decimal_match:
            #             token = decimal_match.group()
            #             # Verificar formato válido
            #             if token.count('.') != 1:
            #                 errors.append(f"Línea {line_num}: Número decimal mal formado '{token}'")
            #             elif token.startswith('.') or token.endswith('.'):
            #                 errors.append(f"Línea {line_num}: Número decimal mal formado '{token}'")
            #             else:
            #                 tokens.append((line_num, token, 'Decimal'))
            #             pos += len(token)
            #             continue
                    
            #         # Números enteros
            #         int_match = re.match(r'[+-]?\d+', line[pos:])
            #         if int_match:
            #             token = int_match.group()
            #             # Verificar que no sea parte de identificador
            #             next_pos = pos + len(token)
            #             if next_pos < len(line) and (line[next_pos].isalpha() or line[next_pos] == '_'):
            #                 # Es un identificador que empieza con número
            #                 identifier = token
            #                 while next_pos < len(line) and (line[next_pos].isalnum() or line[next_pos] in ['_', '-', '!', '@']):
            #                     identifier += line[next_pos]
            #                     next_pos += 1
            #                 errors.append(f"Línea {line_num}: Identificador inválido que comienza con número '{identifier}'")
            #                 pos = next_pos
            #             else:
            #                 tokens.append((line_num, token, 'Entero'))
            #                 pos += len(token)
            #             continue
                    
            #         # Cadenas
            #         if line[pos] == '"':
            #             end_quote = line.find('"', pos + 1)
            #             if end_quote == -1:
            #                 errors.append(f"Línea {line_num}: Cadena sin cerrar")
            #                 break
            #             token = line[pos:end_quote + 1]
            #             tokens.append((line_num, token, 'Cadena'))
            #             pos = end_quote + 1
            #             continue
                    
            #         # Caracteres
            #         if line[pos] == "'":
            #             if pos + 2 >= len(line) or line[pos + 2] != "'":
            #                 errors.append(f"Línea {line_num}: Carácter mal formado")
            #                 pos += 1
            #                 continue
            #             token = line[pos:pos + 3]
            #             # Verificar que tenga exactamente un carácter entre comillas
            #             if len(token) != 3 or token[1] == "'":
            #                 errors.append(f"Línea {line_num}: Carácter mal formado '{token}'")
            #             else:
            #                 tokens.append((line_num, token, 'Caracter'))
            #             pos += 3
            #             continue
                    
            #         # Identificadores - método más estricto
            #         if line[pos].isalpha() or line[pos] == '_':
            #             start = pos
            #             # Consumir hasta encontrar un delimitador
            #             while pos < len(line) and (line[pos].isalnum() or line[pos] in ['_', '-', '!', '@', '$']):
            #                 pos += 1
                        
            #             token = line[start:pos]
                        
            #             # Verificar caracteres inválidos en identificador
            #             invalid_chars = [c for c in token if not c.isalnum() and c != '_']
            #             if invalid_chars:
            #                 errors.append(f"Línea {line_num}: Identificador con caracteres inválidos '{token}' - caracteres no permitidos: {invalid_chars}")
            #                 continue
                        
            #             # Clasificar token
            #             if token in self.keywords:
            #                 tokens.append((line_num, token, 'Palabra clave'))
            #             elif token in self.types:
            #                 tokens.append((line_num, token, 'Tipo de dato'))
            #             elif token in self.boolean_values:
            #                 tokens.append((line_num, token, 'Valor booleano'))
            #             else:
            #                 # Verificar si es un valor no reconocido
            #                 if token in ['true', 'false', 'integer']:
            #                     errors.append(f"Línea {line_num}: Valor no reconocido en Pixie '{token}'")
            #                 else:
            #                     tokens.append((line_num, token, 'Identificador'))
            #             continue
                    
            #         # Operadores no válidos
            #         if pos + 1 < len(line) and line[pos:pos+2] == '<>':
            #             errors.append(f"Línea {line_num}: Operador no válido '<>'")
            #             pos += 2
            #             continue
                    
            #         # Carácter no válido
            #         errors.append(f"Línea {line_num}: Carácter no válido '{line[pos]}'")
            #         pos += 1
            
            # return tokens, errors
