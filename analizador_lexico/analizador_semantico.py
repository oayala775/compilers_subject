import json
import os
from analizador_sintactico import ASTNode, SymbolTable

class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []
        self.current_scope = "global"
        self.scope_stack = ["global"]
        self.function_return_stack = []
        self.initialized_vars = set()
        self.constant_vars = set()
        self.declared_vars_in_scope = set()
        
    def analyze(self, ast):
        """Análisis semántico principal que utiliza la información extendida de la tabla de símbolos"""
        self.errors.clear()
        self.scope_stack = ["global"]
        self.current_scope = "global"
        self.function_return_stack = []
        self.initialized_vars.clear()
        self.constant_vars.clear()
        self.declared_vars_in_scope.clear()
        
        self._analyze_node(ast)
        
        # Verificaciones semánticas extendidas
        self._check_semantic_constraints()
        
        return self.errors
    
    def _check_semantic_constraints(self):
        """Realiza verificaciones semánticas utilizando la información extendida"""
        all_symbols = self.symbol_table.get_all_symbols()
        
        for symbol in all_symbols:
            # Verificar constantes no modificadas
            if symbol.get('es_constante', False) and symbol.get('modificable', True):
                self.errors.append(f"Advertencia semántica: La constante '{symbol['identificador']}' no debería ser modificable")
            
            # Verificar variables no inicializadas
            if (symbol.get('es_variable', False) and 
                not symbol.get('inicializado', False) and
                symbol.get('contador_referencias', 0) > 0):
                self.errors.append(f"Advertencia semántica: Variable '{symbol['identificador']}' usada pero puede no estar inicializada")
            
            # Verificar tipos de datos
            self._validate_data_type(symbol)
    
    def _validate_data_type(self, symbol):
        """Valida la consistencia de tipos de datos"""
        tipo_dato = symbol.get('tipo_dato')
        valor_actual = symbol.get('valor_actual')
        
        if tipo_dato and valor_actual:
            if tipo_dato == 'Gem' and not self._is_integer_value(valor_actual):
                self.errors.append(f"Error de tipo: '{symbol['identificador']}' debe ser Gem (entero)")
            elif tipo_dato == 'Shimmer' and not self._is_float_value(valor_actual):
                self.errors.append(f"Error de tipo: '{symbol['identificador']}' debe ser Shimmer (flotante)")
            elif tipo_dato == 'Truth_potion' and valor_actual not in ['sparkle_on', 'sparkle_off']:
                self.errors.append(f"Error de tipo: '{symbol['identificador']}' debe ser Truth_potion (sparkle_on/sparkle_off)")
    
    def _is_integer_value(self, value):
        """Verifica si un valor es entero"""
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_float_value(self, value):
        """Verifica si un valor es flotante"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def _analyze_node(self, node):
        """Analiza recursivamente un nodo del AST"""
        if not node:
            return None
            
        method_name = f'_analyze_{node.tipo}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            for child in node.hijos:
                self._analyze_node(child)
            return None
    
    def _analyze_PROGRAMA(self, node):
        """Análisis del programa completo"""
        for child in node.hijos:
            self._analyze_node(child)
    
    def _analyze_DECLARACION_VARIABLE(self, node):
        """Análisis de declaración de variable"""
        if len(node.hijos) < 2:
            return
            
        identifier_node = node.hijos[0]
        type_node = node.hijos[1]
        
        var_name = identifier_node.valor
        var_type = type_node.valor
        
        # Verificar si la variable ya fue declarada en este ámbito
        var_key = f"{self.current_scope}::{var_name}"
        if var_key in self.declared_vars_in_scope:
            self.errors.append(f"Error semántico en línea {identifier_node.linea}: La variable '{var_name}' ya está declarada en este ámbito")
            return
        
        # Marcar como declarada en este ámbito
        self.declared_vars_in_scope.add(var_key)
        
        # Buscar en tabla de símbolos
        symbol = self._find_symbol_in_scope(var_name)
        if not symbol:
            self.errors.append(f"Error semántico en línea {identifier_node.linea}: Variable '{var_name}' no encontrada en tabla de símbolos")
            return

        # Verificar asignación si existe
        if len(node.hijos) > 2 and node.hijos[2].tipo == 'ASIGNACION':
            assignment_node = node.hijos[2]
            expr_type = self._analyze_node(assignment_node.hijos[0])
            
            # Verificar compatibilidad de tipos
            if expr_type and not self._check_type_compatibility(var_type, expr_type):
                self.errors.append(f"Error semántico en línea {identifier_node.linea}: No se puede asignar tipo '{expr_type}' a variable de tipo '{var_type}'")
            else:
                # Marcar como inicializada si la asignación es compatible
                self.initialized_vars.add(var_key)
    
    def _analyze_DECLARACION_FUNCION(self, node):
            """Análisis semántico de declaración de función"""
            if len(node.hijos) < 3: return

            # 1. Obtener datos básicos
            id_node = node.hijos[0]
            func_name = id_node.valor
            
            # Buscar el nodo de retorno (puede variar posición dependiendo de params)
            # Asumimos estructura fija: ID, PARAMETROS, TIPO_RETORNO, BLOQUE
            return_type_node = node.hijos[2]
            block_node = node.hijos[3]
            
            expected_type = return_type_node.valor

            # 2. Manejo de Scope
            # El parser ya creó los símbolos en el scope correcto, pero el analizador
            # semántico necesita actualizar su puntero 'current_scope' para analizar el bloque
            old_scope = self.current_scope
            func_scope = f"func_{func_name}"
            self._enter_scope(func_scope)
            
            # Apilamos el tipo de retorno esperado para validar los 'give_back' dentro
            self.function_return_stack.append(expected_type)

            # 3. Analizar el bloque de la función
            self._analyze_node(block_node)

            # 4. Limpieza
            self.function_return_stack.pop()
            self._exit_scope(old_scope)

    def _analyze_SENTENCIA_RETORNO(self, node):
        """Valida que el tipo de retorno coincida con la función"""
        if not node.hijos: return
        
        # Analizar la expresión a devolver
        expr_type = self._analyze_node(node.hijos[0])
        
        if not self.function_return_stack:
            self.errors.append(f"Error semántico línea {node.linea}: 'give_back' fuera de una función")
            return

        expected_type = self.function_return_stack[-1]
        
        if expr_type and not self._check_type_compatibility(expected_type, expr_type):
             self.errors.append(f"Error de tipo línea {node.linea}: La función espera devolver '{expected_type}' pero se devuelve '{expr_type}'")
    
    def _analyze_DECLARACION_CONSTANTE(self, node):
        """Análisis de declaración de constante"""
        if not node.hijos:
            return
            
        identifier_node = node.hijos[0]
        const_name = identifier_node.valor
        
        # Verificar si la constante ya fue declarada
        const_key = f"{self.current_scope}::{const_name}"
        if const_key in self.declared_vars_in_scope:
            self.errors.append(f"Error semántico en línea {identifier_node.linea}: La constante '{const_name}' ya está declarada en este ámbito")
            return
        
        # Marcar como declarada
        self.declared_vars_in_scope.add(const_key)
        
        # Buscar en tabla de símbolos
        symbol = self._find_symbol_in_scope(const_name)
        if not symbol:
            self.errors.append(f"Error semántico en línea {identifier_node.linea}: Constante '{const_name}' no encontrada en tabla de símbolos")
            return
        
        # Verificar que tenga asignación
        if len(node.hijos) < 2 or node.hijos[1].tipo != 'ASIGNACION':
            self.errors.append(f"Error semántico en línea {identifier_node.linea}: La constante '{const_name}' debe tener una asignación inicial")
            return
        
        # Analizar la expresión de asignación
        assignment_node = node.hijos[1]
        expr_type = self._analyze_node(assignment_node.hijos[0])
        
        if expr_type:
            const_type = symbol.get('tipo_dato')
            if const_type and not self._check_type_compatibility(const_type, expr_type):
                self.errors.append(f"Error semántico en línea {identifier_node.linea}: No se puede asignar tipo '{expr_type}' a constante de tipo '{const_type}'")
        
        # Marcar como constante e inicializada
        self.constant_vars.add(const_key)
        self.initialized_vars.add(const_key)
    
    def _analyze_SENTENCIA_IF(self, node):
        """Análisis de sentencia if"""
        if len(node.hijos) < 2:
            return
            
        # Analizar condición
        condition_node = node.hijos[0]
        condition_type = self._analyze_node(condition_node.hijos[0])
        
        # Verificar que la condición sea booleana
        if condition_type and condition_type != 'Truth_potion':
            self.errors.append(f"Error semántico en línea {condition_node.linea}: La condición del 'if' debe ser de tipo Truth_potion")
        
        # Analizar bloque
        block_node = node.hijos[1]
        old_scope = self.current_scope
        self._enter_scope(f"if_block_{block_node.linea}")
        self._analyze_node(block_node)
        self._exit_scope(old_scope)
    
    def _analyze_BLOQUE(self, node):
        """Análisis de bloque de código"""
        for child in node.hijos:
            self._analyze_node(child)
    
    def _analyze_ASIGNACION(self, node):
        """Análisis de asignación"""
        if not node.hijos:
            return None
        expr_node = node.hijos[0]
        return self._analyze_node(expr_node)
    
    def _analyze_EXPRESION_LOGICA(self, node):
        """Análisis de expresión lógica"""
        if not node.hijos:
            return None
            
        for i, child in enumerate(node.hijos):
            if i % 2 == 0:
                operand_type = self._analyze_node(child)
                if operand_type and operand_type != 'Truth_potion':
                    self.errors.append(f"Error semántico en línea {child.linea}: Operando en expresión lógica debe ser Truth_potion")
        
        return 'Truth_potion'
    
    def _analyze_EXPRESION_RELACIONAL(self, node):
        """Análisis de expresión relacional"""
        if len(node.hijos) < 1:
            return None
            
        left_type = self._analyze_node(node.hijos[0])
        
        # Si hay operador relacional
        if len(node.hijos) > 1:
            operator_node = node.hijos[1]
            right_type = self._analyze_node(node.hijos[2])
            
            # Verificar compatibilidad de tipos para comparación
            if left_type and right_type and not self._check_comparison_compatibility(left_type, right_type):
                self.errors.append(f"Error semántico en línea {operator_node.linea}: No se pueden comparar tipos '{left_type}' y '{right_type}'")
        
        return 'Truth_potion'
    
    def _analyze_EXPRESION_ARITMETICA(self, node):
        """Análisis de expresión aritmética"""
        if not node.hijos:
            return None
            
        result_type = None
        
        for i, child in enumerate(node.hijos):
            if i % 2 == 0:
                operand_type = self._analyze_node(child)
                
                if operand_type and operand_type not in ['Gem', 'Shimmer']:
                    self.errors.append(f"Error semántico en línea {child.linea}: Operando en expresión aritmética debe ser Gem o Shimmer")
                
                # Determinar tipo resultante
                if operand_type == 'Shimmer':
                    result_type = 'Shimmer'
                elif operand_type == 'Gem' and result_type is None:
                    result_type = 'Gem'
        
        return result_type
    
    def _analyze_IDENTIFICADOR(self, node):
        """Análisis de identificador"""
        var_name = node.valor
        
        # Buscar el símbolo en la tabla
        symbol = self._find_symbol_in_scope(var_name)
        
        if not symbol:
            self.errors.append(f"Error semántico en línea {node.linea}: Variable '{var_name}' no declarada")
            return None
        
        # Incrementar contador de referencias
        self._increment_reference_count(symbol)
        
        # Verificar si está inicializada
        var_key = f"{symbol['ambito']}::{var_name}"
        if var_key not in self.initialized_vars and var_key not in self.constant_vars:
            self.errors.append(f"Advertencia semántica en línea {node.linea}: Variable '{var_name}' puede no estar inicializada")
        
        return symbol['tipo_dato']
    
    def _analyze_LITERAL(self, node):
        """Análisis de literal"""
        value = node.valor
        
        # Determinar tipo basado en el valor
        if value in ['sparkle_on', 'sparkle_off']:
            return 'Truth_potion'
        elif '.' in str(value):
            return 'Shimmer'
        elif value.isdigit() or (value[0] == '-' and value[1:].isdigit()):
            return 'Gem'
        elif value.startswith('"') and value.endswith('"'):
            return 'Story'
        elif value.startswith("'") and value.endswith("'"):
            return 'Letter'
        
        return None
    
    def _analyze_OPERADOR_ARITMETICO(self, node):
        return None
    
    def _analyze_OPERADOR_RELACIONAL(self, node):
        return 'Truth_potion'
    
    def _analyze_OPERADOR_LOGICO(self, node):
        return 'Truth_potion'
    
    def _enter_scope(self, scope_name):
        """Entra en un nuevo ámbito"""
        self.scope_stack.append(scope_name)
        self.current_scope = scope_name
    
    def _exit_scope(self, old_scope):
        """Sale del ámbito actual"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def _find_symbol_in_scope(self, identifier):
        """Busca un símbolo en el ámbito actual y padres"""
        for scope in reversed(self.scope_stack):
            symbol = self.symbol_table.search_symbol(identifier, scope)
            if symbol:
                return symbol
        return None
    
    def _increment_reference_count(self, symbol):
        """Incrementa el contador de referencias de un símbolo"""
        # Buscar y actualizar en memoria
        for s in self.symbol_table.memory_table:
            if (s['identificador'] == symbol['identificador'] and 
                s['ambito'] == symbol['ambito']):
                s['contador_referencias'] += 1
                return
        
        # Si no está en memoria, buscar en archivo
        if os.path.exists(self.symbol_table.file_storage):
            try:
                with open(self.symbol_table.file_storage, 'r', encoding='utf-8') as f:
                    file_symbols = json.load(f)
                
                for s in file_symbols:
                    if (s['identificador'] == symbol['identificador'] and 
                        s['ambito'] == symbol['ambito']):
                        s['contador_referencias'] += 1
                        self.symbol_table._update_file_symbols(file_symbols)
                        return
            except:
                pass
    
    def _check_type_compatibility(self, target_type, source_type):
        """Verifica compatibilidad de tipos para asignación"""
        if target_type == source_type:
            return True
        if target_type == 'Shimmer' and source_type == 'Gem':
            return True
        return False
    
    def _check_comparison_compatibility(self, type1, type2):
        """Verifica compatibilidad de tipos para comparación"""
        if type1 in ['Gem', 'Shimmer'] and type2 in ['Gem', 'Shimmer']:
            return True
        return type1 == type2

class CodeOptimizer:
    def __init__(self):
        self.optimizations_applied = []
        self.metrics = {
            'original_instructions': 0,
            'optimized_instructions': 0,
            'reductions': {},
            'scope_search_visualization': {},
            'memory_optimization': {}
        }
    
    def optimize(self, ast, symbol_table):
        """Aplica optimizaciones utilizando la información extendida de la tabla de símbolos"""
        if not ast:
            return ast
            
        self.optimizations_applied.clear()
        self.metrics['original_instructions'] = self._count_instructions(ast)
        
        # Aplicar optimizaciones
        optimized_ast = self._copy_ast(ast)
        
        # Optimización de memoria basada en información de símbolos
        self._memory_optimization(symbol_table)
        
        # Optimización local
        self._local_optimization(optimized_ast)
        
        # Optimización global
        self._global_optimization(optimized_ast, symbol_table)
        
        self.metrics['optimized_instructions'] = self._count_instructions(optimized_ast)
        self._calculate_reductions()
        
        return optimized_ast
    
    def _memory_optimization(self, symbol_table):
        """Optimización de memoria basada en información extendida de símbolos"""
        all_symbols = symbol_table.get_all_symbols()
        memory_saved = 0
        
        for symbol in all_symbols:
            # Optimizar tamaño de memoria para constantes
            if symbol.get('es_constante', False):
                original_size = symbol.get('tamano_memoria', 0)
                # Las constantes pueden usar menos memoria
                optimized_size = max(1, original_size // 2)
                memory_saved += original_size - optimized_size
                self.optimizations_applied.append(f"Optimizada memoria de constante '{symbol['identificador']}'")
        
        self.metrics['memory_optimization'] = {
            'memory_saved_bytes': memory_saved,
            'optimized_symbols_count': len([s for s in all_symbols if s.get('es_constante', False)])
        }
    
    def _local_optimization(self, ast):
        """Optimización a nivel de bloques básicos"""
        self._remove_redundant_code(ast)
        self._algebraic_simplification(ast)
    
    def _global_optimization(self, ast, symbol_table):
        """Optimización a nivel global"""
        self._dead_code_elimination(ast)
        self._analyze_scope_usage(ast, symbol_table)
    
    def _remove_redundant_code(self, node):
        """Elimina código redundante"""
        if not node.hijos:
            return
            
        new_children = []
        i = 0
        while i < len(node.hijos):
            child = node.hijos[i]
            
            # Eliminar asignaciones redundantes (x = x)
            if (child.tipo == 'DECLARACION_VARIABLE' and len(child.hijos) > 2 and
                child.hijos[2].tipo == 'ASIGNACION'):
                assignment = child.hijos[2]
                if (len(assignment.hijos) > 0 and assignment.hijos[0].tipo == 'IDENTIFICADOR' and
                    child.hijos[0].valor == assignment.hijos[0].valor):
                    self.optimizations_applied.append("Eliminada asignación redundante")
                    i += 1
                    continue
            
            self._remove_redundant_code(child)
            new_children.append(child)
            i += 1
        
        node.hijos = new_children
    
    def _algebraic_simplification(self, node):
        """Simplificación algebraica de expresiones"""
        if node.tipo in ['EXPRESION_ARITMETICA', 'TERMINO']:
            self._simplify_arithmetic(node)
        
        for child in node.hijos:
            self._algebraic_simplification(child)
    
    def _simplify_arithmetic(self, node):
        """Simplifica expresiones aritméticas"""
        if len(node.hijos) != 3:
            return
            
        left = node.hijos[0]
        operator = node.hijos[1]
        right = node.hijos[2]
        
        if (operator.tipo == 'OPERADOR_ARITMETICO' and 
            left.tipo == 'LITERAL' and right.tipo == 'LITERAL'):
            try:
                left_val = eval(left.valor)
                right_val = eval(right.valor)
                result = None
                
                if operator.valor == '+': result = left_val + right_val
                elif operator.valor == '-': result = left_val - right_val
                elif operator.valor == '*': result = left_val * right_val
                elif operator.valor == '/': result = left_val / right_val if right_val != 0 else left_val
                
                if result is not None:
                    node.tipo = 'LITERAL'
                    node.valor = str(result)
                    node.hijos = []
                    self.optimizations_applied.append("Simplificación algebraica aplicada")
            except:
                pass
    
    def _dead_code_elimination(self, node):
        """Elimina código inalcanzable"""
        new_children = []
        for child in node.hijos:
            # Eliminar variables declaradas pero no usadas
            if (child.tipo == 'DECLARACION_VARIABLE' and 
                len(child.hijos) > 0 and
                child.hijos[0].tipo == 'IDENTIFICADOR'):
                
                var_name = child.hijos[0].valor
                # Buscamos en todo el nodo padre (scope actual)
                usage_count = self._count_variable_usage(var_name, node)
                
                # Si solo aparece 1 vez (su propia declaración), se borra
                if usage_count <= 1:
                    self.optimizations_applied.append(f"Eliminada variable no usada: {var_name}")
                    continue
            
            self._dead_code_elimination(child)
            new_children.append(child)
        
        node.hijos = new_children

    def _count_variable_usage(self, var_name, node):
        """Cuenta cuántas veces se usa una variable en el árbol"""
        count = 0
        if node.tipo == 'IDENTIFICADOR' and node.valor == var_name:
            count = 1
        
        for child in node.hijos:
            count += self._count_variable_usage(var_name, child)
        
        return count
    
    def _analyze_scope_usage(self, ast, symbol_table):
        """Analiza el uso de variables por ámbito para visualización"""
        scope_usage = {}
        
        def analyze_node_scope(node, current_scope):
            if node.tipo == 'IDENTIFICADOR':
                var_name = node.valor
                if current_scope not in scope_usage:
                    scope_usage[current_scope] = set()
                scope_usage[current_scope].add(var_name)
            
            for child in node.hijos:
                analyze_node_scope(child, current_scope)
        
        analyze_node_scope(ast, 'global')
        self.metrics['scope_search_visualization'] = scope_usage
    
    def _copy_ast(self, node):
        """Crea una copia del AST"""
        if not node:
            return None
        
        new_node = ASTNode(node.tipo, node.valor, linea=node.linea, columna=node.columna)
        new_node.hijos = [self._copy_ast(child) for child in node.hijos]
        
        return new_node
    
    def _count_instructions(self, node):
        """Cuenta el número de instrucciones en el AST"""
        count = 1
        
        for child in node.hijos:
            count += self._count_instructions(child)
        
        return count
    
    def _calculate_reductions(self):
        """Calcula métricas de reducción"""
        original = self.metrics['original_instructions']
        optimized = self.metrics['optimized_instructions']
        
        if original > 0:
            reduction = ((original - optimized) / original) * 100
            self.metrics['reductions'] = {
                'total_instructions_reduced': original - optimized,
                'reduction_percentage': reduction,
                'optimizations_count': len(self.optimizations_applied)
            }

    def get_optimization_report(self):
        """Genera reporte de optimizaciones aplicadas"""
        return {
            'metrics': self.metrics,
            'optimizations_applied': self.optimizations_applied,
            'scope_visualization': self.metrics['scope_search_visualization'],
            'memory_optimization': self.metrics.get('memory_optimization', {})
        }