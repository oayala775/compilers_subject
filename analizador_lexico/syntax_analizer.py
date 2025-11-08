import re

class StrictLexicalAnalyzer:
    def __init__(self):
        self.symbols_table: list[tuple[int, str, str | None]] = []
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
                                '[', ']', ',', ';', ':', '.', '<', '>', 'not', '&', '|'}

        self.valid_multi_char_operators = {'<=', '>=', 'is', 'is_not', 'and', 'or'}

    def is_logic_operator(self, token: str) -> bool:
        for valid_operator in self.valid_multi_char_operators:
            match = re.match(f'{valid_operator}', token)
            if match:
                return True
        return False

    def is_keyword(self, token: str) -> bool:
        for keyword in self.keywords:
            match = re.match(f'{keyword}', token)
            if match:
                return True
        return False

    def is_valid_var_name(self, token: str) -> bool:
        match = re.match(r'^[a-zA-Z_-][a-zA-Z_0-9]+$', token)
        if match:
            return True
        return False

    def check_var_declaration(self, tokens: list[str], line_num: int):
        while len(tokens) > 0:
            keyword = tokens.pop(0)
            self.symbols_table.append((line_num, keyword, 'Identificador'))
            # Check if next to a keyword is a valid var name
            if not self.is_valid_var_name(tokens[0]):
                self.append_error(f"Nombre de variable inválido {tokens[0]}", tokens, line_num)
            else:
                var_name: str = tokens.pop(0)
                self.symbols_table.append(
                    (line_num, var_name, 'Nombre de variable'))
            # Check if next to a var name is the 'be a' syntax
            match_be = re.fullmatch('be', tokens[0])
            if not match_be:
                self.append_error("Sentencia de asignación incompleta", tokens, line_num)
            else:
                tokens.pop(0)
                match_a = re.fullmatch('a', tokens[0])
                if not match_a:
                    self.append_error("Sentencia de asignación incompleta", tokens, line_num)
                else:
                    tokens.pop(0)
                    self.symbols_table.append((line_num, 'be a', 'Asignación'))
            # Check if next to be a is a valid data type
            if not self.is_valid_datatype(tokens[0]):
                # If it's not a valid datatype, then it could be a declaration
                match_semicolon = re.match(r'^.*;$', tokens[0])
                if match_semicolon:
                    separated_lines = match_semicolon.group(0).split(';')
                    data_type = separated_lines[0]
                    if self.is_valid_datatype(data_type):
                        self.symbols_table.append(
                            (line_num, data_type, 'Tipo de dato'))
                        self.symbols_table.append(
                            (line_num, ";", 'Fin de linea'))
                        return
                # If semicolon can't be found then it's an error
                else:
                    self.append_error("No se encontró caracter de fin de línea ';'", tokens, line_num)
            # If a valid data type is found it's then added to the results
            else:
                type: str = tokens.pop(0)
                self.symbols_table.append((line_num, type, 'Tipo de dato'))
            # After data type must come an assignation
            if tokens[0] == '=':
                match_eq = re.match('=', tokens[0])
                if not match_eq:
                    self.append_error("No se encontró asignación", tokens, line_num)
                else:
                    tokens.pop(0)
                    self.symbols_table.append((line_num, "=", 'Asignación'))
                # Searches for semicolon
                match_semicolon = re.match(r'^.*;$', tokens[0])
                if not match_semicolon:
                    self.append_error("No se encontró caracter de fin de línea", tokens, line_num)
                # if semicolon is found then it's splitted and then obtained the assignation value
                else:
                    separated_lines = match_semicolon.group(0).split(';')
                    assignation_value = separated_lines[0]
                    was_assignation_correct: bool = self.check_correct_assignation(
                        type, assignation_value)
                    if not was_assignation_correct:
                        self.append_error("El tipo de dato y su valor no son correspondientes", tokens, line_num)
                    else:
                        tokens.pop(0)
                        self.symbols_table.append(
                            (line_num, assignation_value, 'Valor'))
                        self.symbols_table.append(
                            (line_num, ';', 'Fin de línea'))

    def check_if_structure(self, tokens: list[str], line_num: int):
        while len(tokens) > 0:
            if_keyword = tokens.pop(0)
            self.symbols_table.append((line_num, if_keyword, "Identificador"))
            if len(tokens) > 0:
                operators = self.separate_operators(tokens[0],line_num)
                # for operator in operators:
                #     self.symbols_table.append((line_num, operator, 'Caliz'))
            # if not self.check_condition(tokens[0]):
            #     self.append_error("Caliz",tokens, line_num)
            # else:
            #     self.symbols_table.append((line_num, tokens[0], "Resultado correcto"))
            
            pass
    
    def separate_operators(self, token: str, line_num: int) -> list[str]:
        found_operators: list[str] = []
        for operator in self.valid_operators:
            if operator in token:
                self.symbols_table.append((line_num, operator, 'Operador'))
                found_operators.append(operator)
                value_without_operator: str = token.replace(operator, '')
                found_operators.append(value_without_operator)
        return found_operators

    def check_condition(self, token: str):
        match = re.match(r'\(\w+[\s]?\)', token)
        if match:
            return True
        return False

    def append_error(self, message: str, tokens: list[str], line_num: int):
        self.errors.append(f"Línea {line_num}: {message}")
        tokens.pop(0)

    def check_correct_assignation(self, data_type: str, token: str):
        expected_result_for_each_datatype = {'Gem': r'[+-]?\d+', 'Shimmer': r'[0-9]+\.[0-9]+',
                                             'Truth_potion': r'(sparkle_on|sparkle_off)', 'Letter': (r"\'\w\'", r"\".+\"")}
        if data_type == 'Letter':
            match = re.match(
                expected_result_for_each_datatype[data_type][0], token)
            if not match:
                match = re.match(
                    expected_result_for_each_datatype[data_type][1], token)
        else:
            match = re.match(
                expected_result_for_each_datatype[data_type], token)
        return True if match else False

    def is_valid_datatype(self, token: str) -> bool:
        return token in self.types

    def remove_comments(self, line: str) -> str:
        return re.sub(r'#.*', '', line).rstrip()

    def separate_line_by_tokens(self, line: str) -> list[str]:
        return re.findall(r"\S+", line)

