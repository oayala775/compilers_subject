import json
import os

class ASTNode:
    """Nodo del Árbol de Análisis Sintáctico"""
    def __init__(self, tipo, valor=None, hijos=None, linea=None, columna=None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos if hijos is not None else []
        self.linea = linea
        self.columna = columna
    
    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)
    
    def to_dict(self):
        """Convierte el nodo a diccionario para serialización"""
        return {
            'tipo': self.tipo,
            'valor': self.valor,
            'linea': self.linea,
            'columna': self.columna,
            'hijos': [hijo.to_dict() for hijo in self.hijos]
        }

class SymbolTable:
    def __init__(self, max_memory_bytes=1000):
        self.max_memory_bytes = max_memory_bytes
        self.memory_table = []
        self.file_storage = "symbol_table.json"
        self.current_memory_usage = 0
        self.next_memory_address = 0
        
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
            elif isinstance(field, bool):
                size += 1
            elif field is None:
                size += 1
            elif isinstance(field, list) or isinstance(field, dict):
                size += len(str(field).encode('utf-8'))
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
        self.next_memory_address = 0
        if os.path.exists(self.file_storage):
            os.remove(self.file_storage)
    
    def get_next_memory_address(self, size):
        """Obtiene la siguiente dirección de memoria disponible"""
        address = self.next_memory_address
        self.next_memory_address += size
        return address

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []
        self.symbol_table = SymbolTable()
        self.current_scope = "global"
        self.ast = None
        
        # Contadores para tipos de datos
        self.type_sizes = {
            'Gem': 4,        # int - 4 bytes
            'Shimmer': 8,    # float - 8 bytes  
            'Truth_potion': 1, # boolean - 1 byte
            'Letter': 2,     # char - 2 bytes (UTF-16)
            'Story': 256,    # string - 256 bytes por defecto
            'Collection': 64, # array - 64 bytes base
            'Ensemble': 128  # struct - 128 bytes base
        }

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
        
        # token[3] es el tipo, token[2] es el valor
        if token[3] == expected_type and (expected_value is None or token[2] == expected_value):
            self.next_token()
            return True
        return False
    
    def error(self, message, expected=None):
        token = self.current_token()
        if token:
            line = token[0]
            column = token[1]
        else:
            line = "?"
            column = "?"
        
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
            if self.current_token()[2] in sync_tokens:
                return
            self.next_token()
    
    def parse(self):
        """Análisis sintáctico principal"""
        self.errors.clear()
        self.symbol_table.clear()
        
        # Agregar todos los tokens a la tabla de símbolos
        for token in self.tokens:
            self._add_token_to_symbol_table(token)
        
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
    
    def _add_token_to_symbol_table(self, token):
        """Agrega un token a la tabla de símbolos con información semántica completa"""
        token_type = token[3]
        token_value = token[2]
        
        # Solo agregar identificadores, tipos y literales relevantes
        if token_type not in ['IDENTIFIER', 'TYPE', 'GEM', 'SHIMMER', 'BOOLEAN', 'LETTER', 'STORY']:
            return
        
        # No agregar palabras clave como identificadores
        if token_value in ['let', 'be', 'a', 'forever', 'if', 'or', 'and', 'not', 'is', 'is_not']:
            return
        
        # Determinar información semántica básica
        categoria_lexica = token_type
        tipo_dato = self._get_data_type_for_token(token)
        tamano_memoria = self.type_sizes.get(tipo_dato, 4)
        direccion_memoria = self.symbol_table.get_next_memory_address(tamano_memoria)
        
        # Información semántica extendida
        symbol_data = {
            # Información básica del identificador
            'identificador': token_value,
            'categoria_lexica': categoria_lexica,
            'tipo_dato': tipo_dato,
            'ambito': self.current_scope,
            'linea_declaracion': token[0],
            'estado': 'DECLARADO',
            'contador_referencias': 0,
            
            # Información de memoria
            'tamano_memoria': tamano_memoria,
            'direccion_memoria': direccion_memoria,
            'direccion_relativa': direccion_memoria,
            
            # Estado de inicialización
            'inicializado': False,
            'valor_inicial': None,
            
            # Para variables
            'es_variable': categoria_lexica == 'IDENTIFIER',
            'es_constante': False,
            'modificable': True,
            'visibilidad': 'publico',
            
            # Para funciones (inicializado para posibles funciones futuras)
            'es_funcion': False,
            'firma_funcion': None,
            'lista_parametros': [],
            'tipo_retorno': None,
            'variables_locales': [],
            'implementada': False,
            'parametros_detallados': [],
            
            # Para tipos definidos por el usuario
            'es_tipo_usuario': token_type == 'TYPE' and token_value in ['Collection', 'Ensemble'],
            'estructura_interna': None,
            'metodos_asociados': [],
            'jerarquia_herencia': [],
            'restricciones_aplicables': [],
            
            # Información adicional
            'valor_actual': self._get_value_for_token(token),
            'informacion_estructura': None,
            'alcance_temporal': 'programa',
            'categoria_semantica': self._get_semantic_category(token),
            'nivel_anidamiento': 0,
            'bloque_pertenencia': self.current_scope
        }
        
        # Ajustes específicos por tipo de token
        if token_type in ['GEM', 'SHIMMER', 'BOOLEAN', 'LETTER', 'STORY']:
            symbol_data.update({
                'es_constante': True,
                'modificable': False,
                'inicializado': True,
                'valor_inicial': token_value,
                'categoria_semantica': 'LITERAL'
            })
        elif token_type == 'TYPE':
            symbol_data.update({
                'es_tipo_usuario': True,
                'categoria_semantica': 'TIPO_DATO'
            })
        
        self.symbol_table.add_symbol(symbol_data)
    
    def _get_semantic_category(self, token):
        """Determina la categoría semántica del token"""
        token_type = token[3]
        if token_type == 'IDENTIFIER':
            return 'VARIABLE'
        elif token_type == 'TYPE':
            return 'TIPO_DATO'
        elif token_type in ['GEM', 'SHIMMER', 'BOOLEAN', 'LETTER', 'STORY']:
            return 'LITERAL'
        else:
            return 'DESCONOCIDO'
    
    def _get_data_type_for_token(self, token):
        """Determina el tipo de dato basado en el tipo de token"""
        token_type = token[3]
        if token_type == 'GEM':
            return 'Gem'
        elif token_type == 'SHIMMER':
            return 'Shimmer'
        elif token_type == 'BOOLEAN':
            return 'Truth_potion'
        elif token_type == 'LETTER':
            return 'Letter'
        elif token_type == 'STORY':
            return 'Story'
        elif token_type == 'TYPE':
            return token[2]
        else:
            return 'Desconocido'
    
    def _get_value_for_token(self, token):
        """Obtiene el valor para el token"""
        token_type = token[3]
        if token_type in ['GEM', 'SHIMMER', 'BOOLEAN', 'LETTER', 'STORY']:
            return token[2]
        else:
            return None
    
    def declaracion(self):
        """<declaracion_variable> | <declaracion_constante>"""
        token = self.current_token()
        if not token:
            return None
        
        match token[2]:
            case 'let':
                return self.declaracion_variable()
            case 'forever':
                return self.declaracion_constante()
            case 'charm':
                return self.declaracion_funcion()
            case _:
                return None

        # if token[2] == 'let':
        # elif token[2] == 'forever':
        #     return self.declaracion_constante()
        # elif token[2] == 'charm':
        #     return self.declaracion_funcion()
    
    def declaracion_funcion(self):
            """<decl_funcion> ::= "charm" <id> "get_magic_from" "(" <params> ")" "returns" <tipo> <bloque>"""
            token = self.current_token()
            node = ASTNode('DECLARACION_FUNCION', linea=token[0], columna=token[1])
            
            # 1. Palabra clave 'charm'
            if not self.expect('KEYWORD', 'charm'):
                return None
                
            # 2. Identificador de la función
            ident_token = self.current_token()
            if not self.expect('IDENTIFIER'):
                self.error("Se esperaba nombre de la función")
                return None
            
            func_name = ident_token[2]
            node.agregar_hijo(ASTNode('IDENTIFICADOR', func_name, linea=ident_token[0]))

            # Actualizar símbolo a tipo FUNCION
            symbol = self.symbol_table.search_symbol(func_name, self.current_scope)
            if symbol:
                symbol.update({
                    'es_funcion': True,
                    'es_variable': False,
                    'categoria_semantica': 'FUNCION'
                })

            # 3. Palabra clave 'get_magic_from' (opcional o mandatoria según diseño, aquí mandatoria)
            if not self.expect('KEYWORD', 'get_magic_from'):
                self.error("Se esperaba 'get_magic_from' para definir parámetros")
                return None

            # 4. Parámetros: "(" ... ")"
            if not self.expect('DELIMITER', '('):
                self.error("Se esperaba '('")
                return None
                
            params_node = self.parametros_funcion() # Método definido abajo
            node.agregar_hijo(params_node)
            
            # Guardar parámetros en la tabla de símbolos (para validación semántica futura)
            if symbol and params_node.hijos:
                symbol['lista_parametros'] = [p.hijos[1].valor for p in params_node.hijos] # Guardamos los tipos

            if not self.expect('DELIMITER', ')'):
                self.error("Se esperaba ')'")
                return None

            # 5. Tipo de retorno: "returns" <tipo>
            if not self.expect('KEYWORD', 'returns'):
                self.error("Se esperaba 'returns' y el tipo de dato")
                return None
                
            type_token = self.current_token()
            if not self.expect('TYPE'):
                self.error("Se esperaba un tipo de retorno válido")
                return None
            
            return_type = type_token[2]
            node.agregar_hijo(ASTNode('TIPO_RETORNO', return_type, linea=type_token[0]))
            
            if symbol:
                symbol['tipo_retorno'] = return_type

            # 6. El cuerpo de la función
            # Importante: Cambiamos el scope ANTES de entrar al bloque para que los params sean locales
            old_scope = self.current_scope
            self.current_scope = f"func_{func_name}" 
            
            # Reinscribimos los parámetros en el nuevo scope local
            for param in params_node.hijos:
                p_name = param.hijos[0].valor
                p_type = param.hijos[1].valor
                # Creamos manualmente el símbolo en el scope local
                self.symbol_table.add_symbol({
                    'identificador': p_name,
                    'categoria_lexica': 'IDENTIFIER',
                    'tipo_dato': p_type,
                    'ambito': self.current_scope,
                    'es_variable': True,
                    'inicializado': True,
                    'linea_declaracion': token[0],
                    'estado': 'DECLARADO',
                    'contador_referencias': 0,
                    'tamano_memoria': self.type_sizes.get(p_type, 4),
                    'direccion_memoria': self.symbol_table.get_next_memory_address(self.type_sizes.get(p_type, 4)),
                    'es_constante': False,
                    'modificable': True,
                    'valor_actual': None,
                    'categoria_semantica': 'PARAMETRO',
                    'es_funcion': False,
                    'es_tipo_usuario': False
                })

            bloque_node = self.bloque()
            if bloque_node:
                node.agregar_hijo(bloque_node)
            
            # Regresar al scope anterior
            self.current_scope = old_scope
            
            return node

    def parametros_funcion(self):
        """<parametros> ::= <param> ("," <param>)* | epsilon"""
        node = ASTNode('PARAMETROS')
        
        # Si el siguiente token es ')', no hay parámetros
        if self.current_token()[2] == ')':
            return node
            
        while True:
            # Sintaxis de param: "nombre be a Tipo"
            p_ident = self.current_token()
            if not self.expect('IDENTIFIER'):
                self.error("Se esperaba nombre del parámetro")
                break
                
            if not self.expect('KEYWORD', 'be'):
                self.error("Se esperaba 'be'")
                break
            if not self.expect('KEYWORD', 'a'):
                self.error("Se esperaba 'a'")
                break
                
            p_type = self.current_token()
            if not self.expect('TYPE'):
                self.error("Se esperaba tipo del parámetro")
                break
                
            param_node = ASTNode('PARAMETRO')
            param_node.agregar_hijo(ASTNode('IDENTIFICADOR', p_ident[2]))
            param_node.agregar_hijo(ASTNode('TIPO', p_type[2]))
            node.agregar_hijo(param_node)
            
            if self.current_token()[2] == ',':
                self.next_token()
            else:
                break
                
        return node

    def sentencia_retorno(self):
        """<retorno> ::= "give_back" <expresion> ";" """
        token = self.current_token()
        node = ASTNode('SENTENCIA_RETORNO', linea=token[0], columna=token[1])
        
        if not self.expect('KEYWORD', 'give_back'):
            return None
            
        expr = self.expresion()
        if expr:
            node.agregar_hijo(expr)
        else:
            self.error("Se esperaba una expresión para devolver")
            
        if not self.expect('DELIMITER', ';'):
            self.error("Se esperaba ';'")
            
        return node

    def declaracion_variable(self):
        """<declaracion_variable> ::= "let" <identificador> "be" "a" <tipo> ( "=" <expresion> )? ";" """
        start_index = self.current_token_index
        token = self.current_token()
        node = ASTNode('DECLARACION_VARIABLE', linea=token[0] if token else None, columna=token[1] if token else None)
        
        if not self.expect('KEYWORD', 'let'):
            return None
        
        # Identificador
        ident_token = self.current_token()
        if not self.expect('IDENTIFIER'):
            self.error("Se esperaba un identificador")
            return None
        
        identifier = ident_token[2]
        node.agregar_hijo(ASTNode('IDENTIFICADOR', identifier, linea=ident_token[0], columna=ident_token[1]))
        
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
        
        data_type = type_token[2]
        node.agregar_hijo(ASTNode('TIPO', data_type, linea=type_token[0], columna=type_token[1]))
        
        # Actualizar información semántica en tabla de símbolos
        tamano = self.type_sizes.get(data_type, 4)

        # 2. Buscar si ya existe el símbolo EXACTAMENTE en el ámbito actual
        #    (No usamos search_symbol estándar porque ese busca en los padres/globales)
        symbol = None
        for s in self.symbol_table.memory_table:
            if s['identificador'] == identifier and s['ambito'] == self.current_scope:
                symbol = s
                break
        
        if symbol:
            # CASO A: Ya existe en este ámbito local (re-declaración o actualización)
            symbol.update({
                'tipo_dato': data_type,
                'tamano_memoria': tamano,
                'es_variable': True,
                'es_constante': False,
                'modificable': True,
                'categoria_semantica': 'VARIABLE'
            })
        else:
            # CASO B: No existe en este ámbito local (aunque exista en global).
            # Creamos un NUEVO símbolo local que hace "shadowing" al global.
            new_symbol_data = {
                'identificador': identifier,
                'categoria_lexica': 'IDENTIFIER',
                'tipo_dato': data_type,
                'ambito': self.current_scope,     # <--- AQUÍ SE GUARDA EL SCOPE CORRECTO
                'linea_declaracion': ident_token[0],
                'estado': 'DECLARADO',
                'contador_referencias': 0,
                
                # Memoria
                'tamano_memoria': tamano,
                'direccion_memoria': self.symbol_table.get_next_memory_address(tamano),
                'direccion_relativa': 0,
                
                # Estado
                'inicializado': False,
                'valor_inicial': None,
                'valor_actual': None,
                
                # Propiedades
                'es_variable': True,
                'es_constante': False,
                'modificable': True,
                'visibilidad': 'privado' if self.current_scope != 'global' else 'publico',
                
                # Metadatos extra para evitar errores de clave
                'es_funcion': False,
                'es_tipo_usuario': False,
                'categoria_semantica': 'VARIABLE'
            }
            
            self.symbol_table.add_symbol(new_symbol_data)
            symbol = new_symbol_data
        
        # Asignación opcional
        if self.expect('OPERATOR', '='):
            expr_node = self.expresion()
            if expr_node:
                node.agregar_hijo(ASTNode('ASIGNACION', hijos=[expr_node]))
                # Marcar como inicializado
                if symbol:
                    symbol['inicializado'] = True
                    symbol['valor_inicial'] = "expresion"
        
        if not self.expect('DELIMITER', ';'):
            self.error("Se esperaba ';'")
            return None
        
        return node
    
    def declaracion_constante(self):
        """<declaracion_constante> ::= "forever" <identificador> ("=" <expresion> )? ";" """
        token = self.current_token()
        node = ASTNode('DECLARACION_CONSTANTE', linea=token[0] if token else None, columna=token[1] if token else None)
        
        if not self.expect('KEYWORD', 'forever'):
            return None
        
        # Identificador
        ident_token = self.current_token()
        if not self.expect('IDENTIFIER'):
            self.error("Se esperaba un identificador")
            return None
        
        identifier = ident_token[2]
        node.agregar_hijo(ASTNode('IDENTIFICADOR', identifier, linea=ident_token[0], columna=ident_token[1]))
        
        # Actualizar información semántica en tabla de símbolos
        symbol = self.symbol_table.search_symbol(identifier, self.current_scope)
        if symbol:
            symbol.update({
                'es_constante': True,
                'modificable': False,
                'categoria_semantica': 'CONSTANTE'
            })
        
        # Asignación obligatoria para constantes
        if not self.expect('OPERATOR', '='):
            self.error("Las constantes deben tener una asignación inicial")
            return None
        
        expr_node = self.expresion()
        if expr_node:
            node.agregar_hijo(ASTNode('ASIGNACION', hijos=[expr_node]))
            # Marcar como inicializado
            if symbol:
                symbol['inicializado'] = True
                symbol['valor_inicial'] = "expresion_constante"
        
        if not self.expect('DELIMITER', ';'):
            self.error("Se esperaba ';'")
            return None
        
        return node
    
    def sentencia_control(self):
        """Estructuras de control: if, while, etc."""
        token = self.current_token()
        if not token:
            return None
        
        if token[2] == 'if':
            return self.sentencia_if()
        
        return None
    
    def sentencia_if(self):
        """<condicional> ::= "if" "(" <expresion> ")" <bloque> ... """
        token = self.current_token()
        node = ASTNode('SENTENCIA_IF', linea=token[0] if token else None, columna=token[1] if token else None)
        
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
        token = self.current_token()
        node = ASTNode('BLOQUE', linea=token[0] if token else None, columna=token[1] if token else None)
        
        if not self.expect('DELIMITER', '{'):
            return None
        
        # Cambiar ámbito
        old_scope = self.current_scope
        self.current_scope = f"bloque_{self.symbol_table.next_memory_address}"
        
        # Procesar sentencias dentro del bloque
        while self.current_token() and self.current_token()[2] != '}':
                    declaracion_node = self.declaracion()
                    if declaracion_node:
                        node.agregar_hijo(declaracion_node)
                        continue # Importante saltar al siguiente ciclo

                    # Verificar si es retorno
                    if self.current_token()[2] == 'give_back':
                        ret_node = self.sentencia_retorno()
                        if ret_node:
                            node.agregar_hijo(ret_node)
                        continue

                    # Verificar si es estructura de control (If, y ahora llamadas sueltas)
                    sentencia_node = self.sentencia_control()
                    if sentencia_node:
                        node.agregar_hijo(sentencia_node)
                    else:
                        # Si no reconocemos nada, avanzamos para evitar bucle infinito
                        self.error(f"Sentencia no reconocida: {self.current_token()[2]}")
                        self.next_token()
        # while self.current_token() and self.current_token()[2] != '}':
        #     declaracion_node = self.declaracion()
        #     if declaracion_node:
        #         node.agregar_hijo(declaracion_node)
        #     else:
        #         sentencia_node = self.sentencia_control()
        #         if sentencia_node:
        #             node.agregar_hijo(sentencia_node)
        #         else:
        #             self.next_token()
        
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
            token = self.current_token()
            node = ASTNode('OPERADOR_LOGICO', 'NOT', linea=token[0] if token else None, columna=token[1] if token else None)
            expr_node = self.expresion_relacional()
            if expr_node:
                node.agregar_hijo(expr_node)
                return node
            else:
                self.error("Se esperaba una expresión relacional después de 'not'")
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
        if token and token[2] in ['<', '>', '<=', '>=', 'is', 'is_not']:
            operador = token[2]
            self.next_token()
            expr_node = self.expresion_aritmetica()
            if expr_node:
                node.agregar_hijo(ASTNode('OPERADOR_RELACIONAL', operador))
                node.agregar_hijo(expr_node)
            else:
                self.error("Se esperaba una expresión aritmética después del operador relacional")
        
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
        
        while self.current_token() and self.current_token()[2] in ['+', '-']:
            operador = self.current_token()[2]
            self.next_token()
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
        
        while self.current_token() and self.current_token()[2] in ['*', '/', '%']:
            operador = self.current_token()[2]
            self.next_token()
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
        if token and token[2] in ['+', '-']:
            operador = token[2]
            self.next_token()
            factor_node = self.factor()
            if factor_node:
                node = ASTNode('OPERADOR_UNARIO', operador, linea=token[0], columna=token[1])
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
        if token[3] in ['GEM', 'SHIMMER', 'BOOLEAN', 'LETTER', 'STORY']:
            node = ASTNode('LITERAL', token[2], linea=token[0], columna=token[1])
            self.next_token()
            return node
        
        # Identificador
        elif token[3] == 'IDENTIFIER':
            node = ASTNode('IDENTIFICADOR', token[2], linea=token[0], columna=token[1])
            self.next_token()
            
            # Llamada a función?
            if self.current_token() and self.current_token()[2] == '(':
                llamada_node = self.llamada_funcion()
                if llamada_node:
                    llamada_node.hijos.insert(0, node)
                    return llamada_node
            
            return node
        
        # Paréntesis
        elif token[2] == '(':
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
        
        self.error("Se esperaba un literal, identificador o expresión entre paréntesis")
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