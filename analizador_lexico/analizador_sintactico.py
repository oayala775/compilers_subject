import json
import os


class ASTNode:
    """Nodo del Árbol de Análisis Sintáctico"""

    def __init__(self, tipo, valor=None, hijos=None, linea=None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos if hijos is not None else []
        self.linea = linea

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

    def to_dict(self):
        """Convierte el nodo a diccionario para serialización"""
        return {
            'tipo': self.tipo,
            'valor': self.valor,
            'linea': self.linea,
            'hijos': [hijo.to_dict() for hijo in self.hijos]
        }


class SymbolTable:
    def __init__(self, max_memory_bytes=100):
        self.max_memory_bytes = max_memory_bytes
        self.memory_table = []
        self.file_storage = "symbol_table.json"
        self.current_memory_usage = 0

    def calculate_symbol_size(self, symbol):
        """Calcula el tamaño aproximado en bytes de un símbolo"""
        size = 0
        for field in symbol.values():
            if isinstance(field, str):
                size += len(field.encode('utf-8'))
            elif isinstance(field, int):
                size += 4
            elif isinstance(field, float):
                size += 8
            elif field is None:
                size += 1
        return size

    def add_symbol(self, symbol_data):
        """Agrega un símbolo a la tabla"""
        symbol_size = self.calculate_symbol_size(symbol_data)

        if self.current_memory_usage + symbol_size > self.max_memory_bytes:
            self._handle_overflow(symbol_data)
        else:
            self.memory_table.append(symbol_data)
            self.current_memory_usage += symbol_size

    def _handle_overflow(self, symbol_data):
        """Maneja el desbordamiento guardando en archivo"""
        # Cargar símbolos existentes del archivo
        file_symbols = []
        if os.path.exists(self.file_storage):
            try:
                with open(self.file_storage, 'r', encoding='utf-8') as f:
                    file_symbols = json.load(f)
            except:
                file_symbols = []

        # Agregar nuevo símbolo
        file_symbols.append(symbol_data)

        # Guardar en archivo
        with open(self.file_storage, 'w', encoding='utf-8') as f:
            json.dump(file_symbols, f, ensure_ascii=False, indent=2)

    def search_symbol(self, identifier, scope=None):
        """Busca un símbolo por identificador y ámbito"""
        # Buscar en memoria primero
        for symbol in self.memory_table:
            if symbol['identificador'] == identifier:
                if scope is None or symbol['ambito'] == scope:
                    symbol['contador_referencias'] += 1
                    return symbol

        # Buscar en archivo si no se encuentra en memoria
        if os.path.exists(self.file_storage):
            try:
                with open(self.file_storage, 'r', encoding='utf-8') as f:
                    file_symbols = json.load(f)

                for symbol in file_symbols:
                    if symbol['identificador'] == identifier:
                        if scope is None or symbol['ambito'] == scope:
                            symbol['contador_referencias'] += 1
                            # Actualizar archivo con nuevo contador
                            self._update_file_symbols(file_symbols)
                            return symbol
            except:
                pass

        return None

    def _update_file_symbols(self, symbols):
        """Actualiza los símbolos en el archivo"""
        with open(self.file_storage, 'w', encoding='utf-8') as f:
            json.dump(symbols, f, ensure_ascii=False, indent=2)

    def get_all_symbols(self):
        """Obtiene todos los símbolos (memoria + archivo)"""
        all_symbols = self.memory_table.copy()

        if os.path.exists(self.file_storage):
            try:
                with open(self.file_storage, 'r', encoding='utf-8') as f:
                    file_symbols = json.load(f)
                all_symbols.extend(file_symbols)
            except:
                pass

        return all_symbols

    def clear(self):
        """Limpia la tabla de símbolos"""
        self.memory_table.clear()
        self.current_memory_usage = 0
        if os.path.exists(self.file_storage):
            os.remove(self.file_storage)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []
        self.symbol_table = SymbolTable()
        self.current_scope = "global"
        self.memory_address_counter = 0
        self.ast = None  # Árbol de Análisis Sintáctico

    def current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def next_token(self):
        self.current_token_index += 1
        return self.current_token()

    def expect(self, expected_type, expected_value=None):
        token = self.current_token()
        if not token:
            return False

        if token[2] == expected_type and (expected_value is None or token[1] == expected_value):
            self.next_token()
            return True
        return False

    def error(self, message, expected=None):
        token = self.current_token()
        line = token[0] if token else "?"
        column = token[3] if token and len(token) > 3 else "?"
        error_msg = f"Error sintáctico en línea {line}, columna {column}: {message}"
        if expected:
            error_msg += f". Se esperaba {expected}."
        self.errors.append(error_msg)

        # Recuperación: saltar hasta el siguiente punto y coma o llave de cierre
        self.synchronize()

    def synchronize(self):
        """Recuperación de errores: salta tokens hasta encontrar un sincronizador"""
        sync_tokens = [';', '}', '{']
        while self.current_token():
            if self.current_token()[1] in sync_tokens:
                return
            self.next_token()

    def parse(self):
        """Análisis sintáctico principal"""
        self.errors.clear()
        self.symbol_table.clear()

        # Crear nodo raíz del AST
        self.ast = ASTNode('PROGRAMA')

        while self.current_token():
            try:
                declaracion_node = self.declaracion()
                if declaracion_node:
                    self.ast.agregar_hijo(declaracion_node)
                else:
                    sentencia_node = self.sentencia_control()
                    if sentencia_node:
                        self.ast.agregar_hijo(sentencia_node)
                    else:
                        # Si no es una declaración ni sentencia de control, avanzamos
                        if self.current_token():
                            self.next_token()
            except Exception as e:
                self.error(f"Error inesperado: {str(e)}")
                self.synchronize()

        return self.errors

    def declaracion(self):
        """<declaracion_variable> | <declaracion_constante>"""
        token = self.current_token()
        if not token:
            return None

        if token[1] == 'let':
            return self.declaracion_variable()
        elif token[1] == 'forever':
            return self.declaracion_constante()
        elif token[1] == 'blueprint':
            return self.declaracion_clase()

        return None

    def declaracion_variable(self):
        """<declaracion_variable> ::= "let" <identificador> "be" "a" <tipo> ( "=" <expresion> )? ";" """
        start_index = self.current_token_index
        node = ASTNode('DECLARACION_VARIABLE', linea=self.current_token()[
                       0] if self.current_token() else None)

        if not self.expect('KEYWORD', 'let'):
            return None

        # Identificador
        ident_token = self.current_token()
        if not self.expect('IDENTIFIER'):
            self.error("Se esperaba un identificador")
            return None

        identifier = ident_token[1]
        node.agregar_hijo(
            ASTNode('IDENTIFICADOR', identifier, linea=ident_token[0]))

        if not self.expect('KEYWORD', 'be'):
            self.error("Se esperaba 'be'")
            return None

        if not self.expect('KEYWORD', 'a'):
            self.error("Se esperaba 'a'")
            return None

        # Tipo
        type_token = self.current_token()
        if not self.expect('TYPE'):
            self.error("Se esperaba un tipo de dato")
            return None

        data_type = type_token[1]
        node.agregar_hijo(ASTNode('TIPO', data_type, linea=type_token[0]))

        # Asignación opcional
        value = None
        if self.expect('OPERATOR', '='):
            expr_node = self.expresion()
            if expr_node:
                node.agregar_hijo(ASTNode('ASIGNACION', hijos=[expr_node]))
                value = "expresion"  # Placeholder para el valor

        if not self.expect('DELIMITER', ';'):
            self.error("Se esperaba ';'")
            return None

        # Agregar a tabla de símbolos
        symbol_data = {
            'identificador': identifier,
            'categoria_lexica': 'VARIABLE',
            'tipo_dato': data_type,
            'ambito': self.current_scope,
            'direccion_memoria': self.memory_address_counter,
            'linea_declaracion': ident_token[0],
            'valor': value,
            'estado': 'DECLARADA',
            'informacion_estructura': None,
            'contador_referencias': 0
        }

        self.symbol_table.add_symbol(symbol_data)
        self.memory_address_counter += 4  # Asumimos 4 bytes por variable

        return node

    def declaracion_constante(self):
        """<declaracion_constante> ::= "forever" <identificador> ("=" <expresion> )? ";" """
        start_index = self.current_token_index
        node = ASTNode('DECLARACION_CONSTANTE', linea=self.current_token()[
                       0] if self.current_token() else None)

        if not self.expect('KEYWORD', 'forever'):
            return None

        # Identificador
        ident_token = self.current_token()
        if not self.expect('IDENTIFIER'):
            self.error("Se esperaba un identificador")
            return None

        identifier = ident_token[1]
        node.agregar_hijo(
            ASTNode('IDENTIFICADOR', identifier, linea=ident_token[0]))

        # Asignación opcional
        value = None
        if self.expect('OPERATOR', '='):
            expr_node = self.expresion()
            if expr_node:
                node.agregar_hijo(ASTNode('ASIGNACION', hijos=[expr_node]))
                value = "expresion"  # Placeholder para el valor

        if not self.expect('DELIMITER', ';'):
            self.error("Se esperaba ';'")
            return None

        # Agregar a tabla de símbolos
        symbol_data = {
            'identificador': identifier,
            'categoria_lexica': 'CONSTANTE',
            'tipo_dato': None,  # Se inferirá del valor
            'ambito': self.current_scope,
            'direccion_memoria': self.memory_address_counter,
            'linea_declaracion': ident_token[0],
            'valor': value,
            'estado': 'DECLARADA',
            'informacion_estructura': None,
            'contador_referencias': 0
        }

        self.symbol_table.add_symbol(symbol_data)
        self.memory_address_counter += 4

        return node

    def sentencia_control(self):
        """Estructuras de control: if, while, etc."""
        token = self.current_token()
        if not token:
            return None

        if token[1] == 'if':
            return self.sentencia_if()

        return None

    def sentencia_if(self):
        """<condicional> ::= "if" "(" <expresion> ")" <bloque> ... """
        node = ASTNode('SENTENCIA_IF', linea=self.current_token()[
                       0] if self.current_token() else None)

        if not self.expect('KEYWORD', 'if'):
            return None

        if not self.expect('DELIMITER', '('):
            self.error("Se esperaba '('")
            return None

        # Expresión de condición
        cond_node = self.expresion()
        if cond_node:
            node.agregar_hijo(ASTNode('CONDICION', hijos=[cond_node]))
        else:
            self.error("Se esperaba una expresión")
            return None

        if not self.expect('DELIMITER', ')'):
            self.error("Se esperaba ')'")
            return None

        # Bloque
        bloque_node = self.bloque()
        if bloque_node:
            node.agregar_hijo(bloque_node)
        else:
            self.error("Se esperaba un bloque de código")
            return None

        return node

    def bloque(self):
        """<bloque> ::= "{" <lista_sentencias> "}" """
        node = ASTNode('BLOQUE', linea=self.current_token()[
                       0] if self.current_token() else None)

        if not self.expect('DELIMITER', '{'):
            return None

        # Cambiar ámbito
        old_scope = self.current_scope
        self.current_scope = f"bloque_{self.memory_address_counter}"

        # Procesar sentencias dentro del bloque
        while self.current_token() and self.current_token()[1] != '}':
            declaracion_node = self.declaracion()
            if declaracion_node:
                node.agregar_hijo(declaracion_node)
            else:
                sentencia_node = self.sentencia_control()
                if sentencia_node:
                    node.agregar_hijo(sentencia_node)
                else:
                    self.next_token()

        if not self.expect('DELIMITER', '}'):
            self.error("Se esperaba '}'")
            # Restaurar ámbito
            self.current_scope = old_scope
            return None

        # Restaurar ámbito
        self.current_scope = old_scope
        return node

    def expresion(self):
        """<expresion> ::= <expresion_logica>"""
        return self.expresion_logica()

    def expresion_logica(self):
        """<expresion_logica> ::= <termino_logico> <expresion_logica_cola>"""
        node = self.termino_logico()
        if not node:
            return None

        cola_node = self.expresion_logica_cola()
        if cola_node and cola_node.hijos:
            # Si hay operadores lógicos, crear un nodo para la expresión completa
            expr_node = ASTNode('EXPRESION_LOGICA', hijos=[node])
            expr_node.hijos.extend(cola_node.hijos)
            return expr_node

        return node

    def expresion_logica_cola(self):
        """<expresion_logica_cola> ::= "or" <termino_logico> <expresion_logica_cola> | ε"""
        node = ASTNode('EXPRESION_LOGICA_COLA')

        while self.expect('KEYWORD', 'or'):
            operador = 'OR'
            term_node = self.termino_logico()
            if term_node:
                node.agregar_hijo(ASTNode('OPERADOR_LOGICO', operador))
                node.agregar_hijo(term_node)
            else:
                self.error("Se esperaba un término lógico después de 'or'")
                return node

        return node

    def termino_logico(self):
        """<termino_logico> ::= <factor_logico> <termino_logico_cola>"""
        node = self.factor_logico()
        if not node:
            return None

        cola_node = self.termino_logico_cola()
        if cola_node and cola_node.hijos:
            # Si hay operadores lógicos, crear un nodo para el término completo
            term_node = ASTNode('TERMINO_LOGICO', hijos=[node])
            term_node.hijos.extend(cola_node.hijos)
            return term_node

        return node

    def termino_logico_cola(self):
        """<termino_logico_cola> ::= "and" <factor_logico> <termino_logico_cola> | ε"""
        node = ASTNode('TERMINO_LOGICO_COLA')

        while self.expect('KEYWORD', 'and'):
            operador = 'AND'
            factor_node = self.factor_logico()
            if factor_node:
                node.agregar_hijo(ASTNode('OPERADOR_LOGICO', operador))
                node.agregar_hijo(factor_node)
            else:
                self.error("Se esperaba un factor lógico después de 'and'")
                return node

        return node

    def factor_logico(self):
        """<factor_logico> ::= "not" <expresion_relacional> | <expresion_relacional>"""
        if self.expect('KEYWORD', 'not'):
            node = ASTNode('OPERADOR_LOGICO', 'NOT')
            expr_node = self.expresion_relacional()
            if expr_node:
                node.agregar_hijo(expr_node)
                return node
            else:
                self.error(
                    "Se esperaba una expresión relacional después de 'not'")
                return None

        return self.expresion_relacional()

    def expresion_relacional(self):
        """<expresion_relacional> ::= <expresion_aritmetica> <expresion_relacional_cola>"""
        node = self.expresion_aritmetica()
        if not node:
            return None

        cola_node = self.expresion_relacional_cola()
        if cola_node and cola_node.hijos:
            # Si hay operadores relacionales, crear un nodo para la expresión completa
            expr_node = ASTNode('EXPRESION_RELACIONAL', hijos=[node])
            expr_node.hijos.extend(cola_node.hijos)
            return expr_node

        return node

    def expresion_relacional_cola(self):
        """<expresion_relacional_cola> ::= <op_relacional> <expresion_aritmetica> | ε"""
        node = ASTNode('EXPRESION_RELACIONAL_COLA')

        token = self.current_token()
        if token and token[1] in ['<', '>', '<=', '>=', 'is', 'is_not']:
            operador = token[1]
            self.next_token()  # Consumir operador relacional
            expr_node = self.expresion_aritmetica()
            if expr_node:
                node.agregar_hijo(ASTNode('OPERADOR_RELACIONAL', operador))
                node.agregar_hijo(expr_node)
            else:
                self.error(
                    "Se esperaba una expresión aritmética después del operador relacional")

        return node

    def expresion_aritmetica(self):
        """<expresion_aritmetica> ::= <termino> <expresion_aritmetica_cola>"""
        node = self.termino()
        if not node:
            return None

        cola_node = self.expresion_aritmetica_cola()
        if cola_node and cola_node.hijos:
            # Si hay operadores, crear un nodo para la expresión completa
            expr_node = ASTNode('EXPRESION_ARITMETICA', hijos=[node])
            expr_node.hijos.extend(cola_node.hijos)
            return expr_node

        return node

    def expresion_aritmetica_cola(self):
        """<expresion_aritmetica_cola> ::= <op_suma> <termino> <expresion_aritmetica_cola> | ε"""
        node = ASTNode('EXPRESION_ARITMETICA_COLA')

        while self.current_token() and self.current_token()[1] in ['+', '-']:
            operador = self.current_token()[1]
            self.next_token()  # Consumir operador
            term_node = self.termino()
            if term_node:
                node.agregar_hijo(ASTNode('OPERADOR_ARITMETICO', operador))
                node.agregar_hijo(term_node)
            else:
                self.error("Se esperaba un término después del operador")
                return node

        return node

    def termino(self):
        """<termino> ::= <factor> <termino_cola>"""
        node = self.factor()
        if not node:
            return None

        cola_node = self.termino_cola()
        if cola_node and cola_node.hijos:
            # Si hay operadores, crear un nodo para el término completo
            term_node = ASTNode('TERMINO', hijos=[node])
            term_node.hijos.extend(cola_node.hijos)
            return term_node

        return node

    def termino_cola(self):
        """<termino_cola> ::= <op_multi> <factor> <termino_cola> | ε"""
        node = ASTNode('TERMINO_COLA')

        while self.current_token() and self.current_token()[1] in ['*', '/', '%']:
            operador = self.current_token()[1]
            self.next_token()  # Consumir operador
            factor_node = self.factor()
            if factor_node:
                node.agregar_hijo(ASTNode('OPERADOR_ARITMETICO', operador))
                node.agregar_hijo(factor_node)
            else:
                self.error("Se esperaba un factor después del operador")
                return node

        return node

    def factor(self):
        """<factor> ::= <primario> | <op_unario> <factor>"""
        # Operador unario
        token = self.current_token()
        if token and token[1] in ['+', '-']:
            operador = token[1]
            self.next_token()
            factor_node = self.factor()
            if factor_node:
                node = ASTNode('OPERADOR_UNARIO', operador)
                node.agregar_hijo(factor_node)
                return node
            else:
                self.error("Se esperaba un factor después del operador unario")
                return None

        return self.primario()

    def primario(self):
        """<primario> ::= <literal> | <identificador> | <llamada_funcion> | "(" <expresion> ")" """
        token = self.current_token()
        if not token:
            return None

        # Literales
        if token[2] in ['GEM', 'SHIMMER', 'BOOLEAN', 'LETTER', 'STORY']:
            node = ASTNode('LITERAL', token[1], linea=token[0])
            self.next_token()
            return node

        # Identificador
        elif token[2] == 'IDENTIFIER':
            # Verificar si el identificador existe en la tabla de símbolos
            symbol = self.symbol_table.search_symbol(
                token[1], self.current_scope)
            if not symbol:
                # Buscar en ámbito global
                symbol = self.symbol_table.search_symbol(token[1], "global")
                if not symbol:
                    self.error(f"Identificador '{token[1]}' no declarado")

            node = ASTNode('IDENTIFICADOR', token[1], linea=token[0])
            self.next_token()

            # Llamada a función?
            if self.current_token() and self.current_token()[1] == '(':
                llamada_node = self.llamada_funcion()
                if llamada_node:
                    # El identificador es el primer hijo
                    llamada_node.hijos.insert(0, node)
                    return llamada_node

            return node

        # Paréntesis
        elif token[1] == '(':
            self.next_token()
            expr_node = self.expresion()
            if expr_node:
                if not self.expect('DELIMITER', ')'):
                    self.error("Se esperaba ')'")
                    return expr_node
                return ASTNode('EXPRESION_PARENTESIS', hijos=[expr_node])
            else:
                self.error("Se esperaba una expresión dentro de paréntesis")
                return None

        self.error(
            "Se esperaba un literal, identificador o expresión entre paréntesis")
        return None

    def llamada_funcion(self):
        """<llamada_funcion> ::= <identificador> "(" <lista_expresiones_opcional> ")" """
        node = ASTNode('LLAMADA_FUNCION')

        if not self.expect('DELIMITER', '('):
            return None

        # Lista de expresiones opcional
        lista_node = self.lista_expresiones_opcional()
        if lista_node:
            node.agregar_hijo(lista_node)

        if not self.expect('DELIMITER', ')'):
            self.error("Se esperaba ')'")
            return None

        return node

    def lista_expresiones_opcional(self):
        """<lista_expresiones_opcional> ::= <lista_expresiones> | ε"""
        node = ASTNode('LISTA_EXPRESIONES')

        expr_node = self.expresion()
        if expr_node:
            node.agregar_hijo(expr_node)
            self.lista_expresiones_cola(node)

        return node if node.hijos else None

    def lista_expresiones_cola(self, node):
        """<lista_expresiones_cola> ::= "," <expresion> <lista_expresiones_cola> | ε"""
        while self.expect('DELIMITER', ','):
            expr_node = self.expresion()
            if expr_node:
                node.agregar_hijo(expr_node)
            else:
                self.error("Se esperaba una expresión después de ','")
                return

    def declaracion_clase(self):
        """<declaracion_clase> ::= "blueprint" <identificador> ( "follows_blueprint" <identificador> )? "{" <lista_miembros> "}" """

        linea_inicio = self.current_token(
        )[0] if self.current_token() else None
        node = ASTNode('DECLARACION_BLUEPRINT', linea=linea_inicio)

        # 1. Esperar "blueprint"
        if not self.expect('KEYWORD', 'blueprint'):
            # Esto no debería pasar si se llama desde declaracion(), pero es una buena práctica
            return None

        # 2. Esperar Identificador (Nombre de la clase)
        ident_token = self.current_token()
        if not self.expect('IDENTIFIER'):
            self.error("Se esperaba un identificador (nombre del blueprint)")
            return None

        class_name = ident_token[1]
        node.agregar_hijo(
            ASTNode('IDENTIFICADOR', class_name, linea=ident_token[0]))

        parent_name = None  # Para la tabla de símbolos

        # 3. (Opcional) Herencia: "follows_blueprint" <identificador>
        if self.expect('KEYWORD', 'follows_blueprint'):
            parent_token = self.current_token()
            if not self.expect('IDENTIFIER'):
                self.error(
                    "Se esperaba un identificador (blueprint padre) después de 'follows_blueprint'")
                return None

            parent_name = parent_token[1]
            # Añadir nodo de herencia al AST
            herencia_node = ASTNode('HERENCIA', linea=parent_token[0])
            herencia_node.agregar_hijo(
                ASTNode('IDENTIFICADOR', parent_name, linea=parent_token[0]))
            node.agregar_hijo(herencia_node)

        # 4. Esperar "{" (Inicio del cuerpo)
        if not self.expect('DELIMITER', '{'):
            self.error("Se esperaba '{' para iniciar el cuerpo del blueprint")
            return None

        # 5. Parsear Cuerpo: <lista_miembros>
        body_node = ASTNode('CUERPO_BLUEPRINT', linea=self.current_token()[
                            0] if self.current_token() else linea_inicio)

        # --- Manejo de Ámbito (Scope) ---
        # Un blueprint define un nuevo ámbito para sus miembros
        old_scope = self.current_scope
        self.current_scope = class_name  # El ámbito es el nombre de la clase

        # Iterar hasta encontrar "}"
        while self.current_token() and self.current_token()[1] != '}':
            # Por ahora, solo permitimos declaraciones de variables (miembros)
            # Reutilizamos la gramática de variables
            miembro_node = self.declaracion_variable()

            if miembro_node:
                body_node.agregar_hijo(miembro_node)
            else:
                # Si no es una variable, es un error
                self.error(f"Sentencia no válida dentro del blueprint. Solo se permiten declaraciones 'let'. Token encontrado: {self.current_token()[1]}",
                           expected="'let' o '}'")
                self.synchronize()  # Intentar recuperarse

                # Seguridad para evitar bucle infinito si synchronize() falla
                if not self.current_token() or self.current_token()[1] == '}':
                    break

        node.agregar_hijo(body_node)

        # 6. Esperar "}" (Fin del cuerpo)
        if not self.expect('DELIMITER', '}'):
            self.error(
                f"Se esperaba '}}' para cerrar el blueprint '{class_name}'")
            self.current_scope = old_scope  # Restaurar ámbito incluso si hay error
            return None

        # --- Entrada en la Tabla de Símbolos (para la clase misma) ---
        self.current_scope = old_scope  # Restaurar ámbito ANTES de añadir la clase

        symbol_data = {
            'identificador': class_name,
            'categoria_lexica': 'BLUEPRINT',  # Nueva categoría
            'tipo_dato': class_name,  # El tipo de una clase es su propio nombre
            # Se añade al ámbito exterior (ej. "global")
            'ambito': self.current_scope,
            'direccion_memoria': self.memory_address_counter,
            'linea_declaracion': ident_token[0],
            'valor': None,
            'estado': 'DECLARADA',
            'informacion_estructura': f"Parent: {parent_name if parent_name else 'None'}",
            'contador_referencias': 0
        }

        self.symbol_table.add_symbol(symbol_data)
        self.memory_address_counter += 4  # Tamaño de referencia a la estructura

        return node
