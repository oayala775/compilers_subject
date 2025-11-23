from tkinter import ttk, scrolledtext
import tkinter as tk
import json
from analizador_lexico import StrictLexicalAnalyzer
from analizador_sintactico import Parser
from analizador_semantico import SemanticAnalyzer, CodeOptimizer

class ToolTip:
    """Clase para crear tooltips en widgets"""
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        
    def show_tip(self, text):
        """Muestra el tooltip con el texto"""
        if self.tip_window or not text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("Arial", 10))
        label.pack(ipadx=1)
        
    def hide_tip(self):
        """Oculta el tooltip"""
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

def crear_tooltips_para_treeview(treeview):
    """Crea tooltips para los items de un Treeview"""
    tooltip = ToolTip(treeview)
    
    def on_motion(event):
        item = treeview.identify_row(event.y)
        column = treeview.identify_column(event.x)
        if item and column:
            # Obtener el valor de la celda
            col_index = int(column[1:]) - 1
            value = treeview.set(item, treeview['columns'][col_index])
            if value and len(value) > 20:
                tooltip.show_tip(value)
            else:
                tooltip.hide_tip()
        else:
            tooltip.hide_tip()
    
    treeview.bind('<Motion>', on_motion)
    treeview.bind('<Leave>', lambda e: tooltip.hide_tip())

class CompactCompilerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Pixie - Analizador Léxico, Sintáctico y Semántico")
        self.window.geometry("1600x1000")

        self.lexer = StrictLexicalAnalyzer()
        self.optimizer = CodeOptimizer()
        self.original_code = ""
        
        # Color rosa uniforme para todos los botones
        self.button_color = "#FF69B4"
        self.button_active_color = "#FF1493"
        self.button_text_color = "white"
        
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # === LADO IZQUIERDO ===
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Frame para título y botones de control del editor
        editor_header = tk.Frame(left_frame)
        editor_header.pack(fill='x', pady=(0, 5))
        
        tk.Label(editor_header, text="Editor de Código Pixie:",
                 font=("Arial", 11, "bold")).pack(side='left', anchor='w')

        # Botones de control del editor
        control_frame = tk.Frame(editor_header)
        control_frame.pack(side='right', anchor='e')
        
        self.show_original_btn = tk.Button(control_frame, text="Mostrar Original", 
                                          command=self.show_original_code,
                                          bg=self.button_color, 
                                          fg=self.button_text_color, 
                                          font=("Arial", 9, "bold"),
                                          height=1, width=15,
                                          activebackground=self.button_active_color)
        self.show_original_btn.pack(side='left', padx=(5, 0))
        
        self.show_optimized_btn = tk.Button(control_frame, text="Mostrar Optimizado", 
                                           command=self.show_optimized_code,
                                           bg=self.button_color, 
                                           fg=self.button_text_color, 
                                           font=("Arial", 9, "bold"),
                                           height=1, width=15,
                                           activebackground=self.button_active_color)
        self.show_optimized_btn.pack(side='left', padx=(5, 0))

        # Editor de código
        self.editor = scrolledtext.ScrolledText(left_frame, width=60, height=25,
                                                font=("Consolas", 10))
        self.editor.pack(fill='both', expand=True)

        # Insertar código de prueba mejorado
        test_code = """# CÓDIGO CON MÚLTIPLES OPORTUNIDADES DE OPTIMIZACIÓN
let x be a Gem = 10;
let y be a Gem = 20;
let resultado a Gem = 20;
let z be a Gem = x + y;

# 1. ASIGNACIONES REDUNDANTES
let a be a Gem = 5;
let a be a Gem = a;           # Asignación redundante (debería eliminarse)
let b be a Gem = x + 0;       # Suma con cero (debería simplificarse a x)
let c be a Gem = y * 1;       # Multiplicación por uno (debería simplificarse a y)

# 2. EXPRESIONES CONSTANTES
let calculo1 be a Gem = 2 + 3 * 4;           # Debería calcularse a 14
let calculo2 be a Shimmer = 10.5 + 2.5;      # Debería calcularse a 13.0
let calculo3 be a Gem = (5 * 2) + (8 / 2);   # Debería calcularse a 14

# 3. CÓDIGO MUERTO
let variable_no_usada be a Gem = 100;        # Debería eliminarse
let otra_sin_uso be a Story = "hola";        # Debería eliminarse

# 4. EXPRESIONES IDÉNTICAS
let d be a Gem = x + y;
let e be a Gem = x + y;       # Expresión duplicada

# 5. OPERACIONES CON CONSTANTES BOOLEANAS
let condicion1 be a Truth_potion = sparkle_on and sparkle_off;
let condicion2 be a Truth_potion = sparkle_on or sparkle_off;

# 6. VARIABLES CON PROPAGACIÓN DE CONSTANTES
let base be a Gem = 5;
let altura be a Gem = 10;
let area be a Gem = base * altura;  # Debería propagarse 5 * 10 = 50

# 7. EXPRESIONES COMPLEJAS
let expresion_compleja be a Gem = ((x + y) * 0) + (z * 1);

# USO DE VARIABLES PARA EVITAR ELIMINACIÓN
share "Valor de x: " + x;
share "Valor de y: " + y;
share "Valor de z: " + z;
share "Cálculo 1: " + calculo1;
share "Cálculo 2: " + calculo2;
share "Cálculo 3: " + calculo3;
share "Área: " + area;
share "Condición 1: " + condicion1;
share "Condición 2: " + condicion2;

# ESTRUCTURA DE CONTROL CON EXPRESIONES CONSTANTES
if (sparkle_on) {
    let mensaje be a Story = "Siempre se ejecuta";
    share mensaje;
}

if (sparkle_off) {
    let mensaje2 be a Story = "Nunca se ejecuta";  # Código muerto
}

# CONSTANTES
forever PI be a Shimmer = 3.1416;
forever MAXIMO be a Gem = 100;

# USO DE CONSTANTES
let circulo be a Shimmer = PI * 10 * 10;
share "Área del círculo: " + circulo;

# FUNCION
charm sumar get_magic_from ( num1 be a Gem, num2 be a Gem ) returns Gem {
    let resultado be a Gem = num1 + num2;
    give_back resultado;
}
"""

        self.editor.insert('1.0', test_code)
        self.original_code = test_code
        self.optimized_code = ""

        # Botones principales
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill='x', pady=10)

        self.compile_btn = tk.Button(button_frame, text="Compilar", command=self.compile,
                                     bg=self.button_color, 
                                     fg=self.button_text_color, 
                                     font=("Arial", 11, "bold"),
                                     height=2, width=12,
                                     activebackground=self.button_active_color)
        self.compile_btn.pack(side='left', padx=(0, 10))

        self.optimize_btn = tk.Button(button_frame, text="Optimizar", command=self.optimize_code,
                                     bg=self.button_color, 
                                     fg=self.button_text_color, 
                                     font=("Arial", 11, "bold"),
                                     height=2, width=12,
                                     activebackground=self.button_active_color)
        self.optimize_btn.pack(side='left')

        # === LADO DERECHO ===
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)

        # Pestañas para resultados
        notebook = ttk.Notebook(right_frame)

        # Pestañas
        tokens_frame = ttk.Frame(notebook)
        symbols_frame = ttk.Frame(notebook)
        ast_frame = ttk.Frame(notebook)
        lexical_errors_frame = ttk.Frame(notebook)
        syntactic_errors_frame = ttk.Frame(notebook)
        semantic_errors_frame = ttk.Frame(notebook)
        optimization_frame = ttk.Frame(notebook)
        scope_visualization_frame = ttk.Frame(notebook)

        notebook.add(tokens_frame, text="Tokens")
        notebook.add(symbols_frame, text="Tabla de Símbolos")
        notebook.add(ast_frame, text="Árbol Sintáctico")
        notebook.add(lexical_errors_frame, text="Errores Léxicos")
        notebook.add(syntactic_errors_frame, text="Errores Sintácticos")
        notebook.add(semantic_errors_frame, text="Errores Semánticos")
        notebook.add(optimization_frame, text="Optimización")
        notebook.add(scope_visualization_frame, text="Búsqueda de Scope")

        notebook.pack(fill='both', expand=True)

        # Configuración de las pestañas
        self._setup_existing_tabs(tokens_frame, symbols_frame, ast_frame, 
                                 lexical_errors_frame, syntactic_errors_frame)

        # Configuración de pestaña de errores semánticos
        self.semantic_errors_text = scrolledtext.ScrolledText(semantic_errors_frame, 
                                                             width=50, height=15,
                                                             font=("Consolas", 9), 
                                                             state='disabled')
        self.semantic_errors_text.pack(fill='both', expand=True)

        # Configuración de pestaña de optimización
        optimization_main_frame = tk.Frame(optimization_frame)
        optimization_main_frame.pack(fill='both', expand=True)

        # Métricas de optimización
        self.optimization_info_label = tk.Label(optimization_main_frame, 
                                               text="Optimizaciones aplicadas: 0 | Reducción: 0%",
                                               font=("Arial", 10, "bold"),
                                               bg="#E6E6FA",
                                               relief="solid",
                                               padx=10,
                                               pady=5)
        self.optimization_info_label.pack(fill='x', padx=5, pady=5)

        # Lista de optimizaciones aplicadas
        tk.Label(optimization_main_frame, text="Optimizaciones Aplicadas:",
                font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 5))
        
        self.optimizations_list = scrolledtext.ScrolledText(optimization_main_frame, 
                                                           height=8,
                                                           font=("Consolas", 9),
                                                           state='disabled')
        self.optimizations_list.pack(fill='x', padx=5, pady=5)

        # Métricas detalladas
        tk.Label(optimization_main_frame, text="Métricas de Optimización:",
                font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 5))
        
        self.metrics_text = scrolledtext.ScrolledText(optimization_main_frame, 
                                                     height=8,
                                                     font=("Consolas", 9),
                                                     state='disabled')
        self.metrics_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Configuración de pestaña de búsqueda de scope
        scope_main_frame = tk.Frame(scope_visualization_frame)
        scope_main_frame.pack(fill='both', expand=True)

        # Visualización de scope antes/después
        scope_comparison_frame = tk.Frame(scope_main_frame)
        scope_comparison_frame.pack(fill='both', expand=True)

        # Antes de la optimización
        before_frame = tk.Frame(scope_comparison_frame)
        before_frame.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(before_frame, text="Ámbito de Variables - Antes",
                font=("Arial", 10, "bold")).pack(pady=5)

        # Frame para Treeview y scrollbars
        before_tree_container = tk.Frame(before_frame)
        before_tree_container.pack(fill='both', expand=True)

        self.before_scope_tree = ttk.Treeview(before_tree_container, 
                                             columns=('variable', 'ambito'), 
                                             show='headings', 
                                             height=12)
        self.before_scope_tree.heading('variable', text='Variable')
        self.before_scope_tree.heading('ambito', text='Ámbito')
        self.before_scope_tree.column('variable', width=150, minwidth=150)
        self.before_scope_tree.column('ambito', width=150, minwidth=150)

        # Scrollbar vertical para antes
        scrollbar_before_vertical = ttk.Scrollbar(before_tree_container, 
                                                 orient='vertical', 
                                                 command=self.before_scope_tree.yview)
        self.before_scope_tree.configure(yscrollcommand=scrollbar_before_vertical.set)

        # Scrollbar horizontal para antes
        scrollbar_before_horizontal = ttk.Scrollbar(before_tree_container, 
                                                   orient='horizontal', 
                                                   command=self.before_scope_tree.xview)
        self.before_scope_tree.configure(xscrollcommand=scrollbar_before_horizontal.set)

        # Empaquetar Treeview y scrollbars
        self.before_scope_tree.pack(side='left', fill='both', expand=True)
        scrollbar_before_vertical.pack(side='right', fill='y')
        scrollbar_before_horizontal.pack(side='bottom', fill='x')

        # Después de la optimización
        after_frame = tk.Frame(scope_comparison_frame)
        after_frame.pack(side='right', fill='both', expand=True, padx=5)

        tk.Label(after_frame, text="Ámbito de Variables - Después",
                font=("Arial", 10, "bold")).pack(pady=5)

        # Frame para Treeview y scrollbars
        after_tree_container = tk.Frame(after_frame)
        after_tree_container.pack(fill='both', expand=True)

        self.after_scope_tree = ttk.Treeview(after_tree_container, 
                                            columns=('variable', 'ambito'), 
                                            show='headings', 
                                            height=12)
        self.after_scope_tree.heading('variable', text='Variable')
        self.after_scope_tree.heading('ambito', text='Ámbito')
        self.after_scope_tree.column('variable', width=150, minwidth=150)
        self.after_scope_tree.column('ambito', width=150, minwidth=150)

        # Scrollbar vertical para después
        scrollbar_after_vertical = ttk.Scrollbar(after_tree_container, 
                                                orient='vertical', 
                                                command=self.after_scope_tree.yview)
        self.after_scope_tree.configure(yscrollcommand=scrollbar_after_vertical.set)

        # Scrollbar horizontal para después
        scrollbar_after_horizontal = ttk.Scrollbar(after_tree_container, 
                                                  orient='horizontal', 
                                                  command=self.after_scope_tree.xview)
        self.after_scope_tree.configure(xscrollcommand=scrollbar_after_horizontal.set)

        # Empaquetar Treeview y scrollbars
        self.after_scope_tree.pack(side='left', fill='both', expand=True)
        scrollbar_after_vertical.pack(side='right', fill='y')
        scrollbar_after_horizontal.pack(side='bottom', fill='x')

        # Crear tooltips para los Treeviews de scope
        crear_tooltips_para_treeview(self.before_scope_tree)
        crear_tooltips_para_treeview(self.after_scope_tree)

    def _setup_existing_tabs(self, tokens_frame, symbols_frame, ast_frame,
                            lexical_errors_frame, syntactic_errors_frame):
        """Configura las pestañas existentes con tabla de símbolos extendida"""
        # Tabla de tokens
        token_columns = ('linea', 'columna', 'token', 'tipo')
        self.tokens_table = ttk.Treeview(tokens_frame, columns=token_columns, show='headings', height=15)
        self.tokens_table.heading('linea', text='Línea')
        self.tokens_table.heading('columna', text='Columna')
        self.tokens_table.heading('token', text='Token')
        self.tokens_table.heading('tipo', text='Tipo')
        
        scrollbar_tokens = ttk.Scrollbar(tokens_frame, orient='vertical', command=self.tokens_table.yview)
        self.tokens_table.configure(yscrollcommand=scrollbar_tokens.set)
        self.tokens_table.pack(side='left', fill='both', expand=True)
        scrollbar_tokens.pack(side='right', fill='y')

        # TABLA DE SÍMBOLOS EXTENDIDA
        symbols_main_frame = tk.Frame(symbols_frame)
        symbols_main_frame.pack(fill='both', expand=True)
        
        self.symbols_info_label = tk.Label(symbols_main_frame, 
                                          text="Total de símbolos: 0 | Memoria usada: 0 bytes",
                                          font=("Arial", 10, "bold"),
                                          bg="#F0F0F0",
                                          relief="solid",
                                          padx=10,
                                          pady=5)
        self.symbols_info_label.pack(fill='x', padx=5, pady=5)

        # Columnas extendidas para tabla de símbolos
        symbol_columns = (
            'identificador', 'categoria', 'tipo', 'ambito', 
            'linea', 'estado', 'referencias', 'inicializado',
            'tamano_memoria', 'direccion_memoria', 'es_constante', 'modificable',
            'valor_actual', 'categoria_semantica', 'es_funcion', 'es_tipo_usuario'
        )
        
        self.symbols_table = ttk.Treeview(symbols_main_frame, columns=symbol_columns, show='headings', height=15)
        
        # Configurar encabezados
        column_headings = {
            'identificador': 'Identificador',
            'categoria': 'Categoría Léxica',
            'tipo': 'Tipo Dato',
            'ambito': 'Ámbito',
            'linea': 'Línea',
            'estado': 'Estado',
            'referencias': 'Refs',
            'inicializado': 'Inicializado',
            'tamano_memoria': 'Tamaño (bytes)',
            'direccion_memoria': 'Dirección Mem',
            'es_constante': 'Es Constante',
            'modificable': 'Modificable',
            'valor_actual': 'Valor Actual',
            'categoria_semantica': 'Categoría Semántica',
            'es_funcion': 'Es Función',
            'es_tipo_usuario': 'Es Tipo Usuario'
        }
        
        for col in symbol_columns:
            self.symbols_table.heading(col, text=column_headings.get(col, col))
            self.symbols_table.column(col, width=80)

        # Ajustar anchos específicos
        self.symbols_table.column('identificador', width=120)
        self.symbols_table.column('categoria_semantica', width=120)
        self.symbols_table.column('valor_actual', width=100)
        self.symbols_table.column('ambito', width=100)

        scrollbar_symbols = ttk.Scrollbar(symbols_main_frame, orient='vertical', command=self.symbols_table.yview)
        self.symbols_table.configure(yscrollcommand=scrollbar_symbols.set)
        self.symbols_table.pack(side='left', fill='both', expand=True)
        scrollbar_symbols.pack(side='right', fill='y')

        # Botón para exportar tabla de símbolos
        export_frame = tk.Frame(symbols_main_frame)
        export_frame.pack(fill='x', pady=5)
        
        self.export_btn = tk.Button(export_frame, text="Exportar Tabla de Símbolos",
                                   command=self.export_symbol_table,
                                   bg=self.button_color,
                                   fg=self.button_text_color,
                                   font=("Arial", 9, "bold"))
        self.export_btn.pack(side='right', padx=5)

        # Árbol sintáctico
        self.ast_tree = ttk.Treeview(ast_frame, columns=('valor', 'linea', 'columna'), show='tree headings', height=15)
        self.ast_tree.heading('#0', text='Nodo del Árbol Sintáctico')
        self.ast_tree.heading('valor', text='Valor')
        self.ast_tree.heading('linea', text='Línea')
        self.ast_tree.heading('columna', text='Columna')
        
        scrollbar_ast = ttk.Scrollbar(ast_frame, orient='vertical', command=self.ast_tree.yview)
        self.ast_tree.configure(yscrollcommand=scrollbar_ast.set)
        self.ast_tree.pack(side='left', fill='both', expand=True)
        scrollbar_ast.pack(side='right', fill='y')

        # Errores léxicos y sintácticos
        self.lexical_errors_text = scrolledtext.ScrolledText(lexical_errors_frame, width=50, height=15,
                                                             font=("Consolas", 9), state='disabled')
        self.lexical_errors_text.pack(fill='both', expand=True)

        self.syntactic_errors_text = scrolledtext.ScrolledText(syntactic_errors_frame, width=50, height=15,
                                                               font=("Consolas", 9), state='disabled')
        self.syntactic_errors_text.pack(fill='both', expand=True)

    def ajustar_ancho_columnas(self, treeview):
        """Ajusta automáticamente el ancho de las columnas al contenido"""
        treeview.update_idletasks()
        
        columns = treeview['columns']
        
        for col in columns:
            max_width = 100
            
            heading_text = treeview.heading(col)['text']
            max_width = max(max_width, len(heading_text) * 8)
            
            for item in treeview.get_children():
                cell_value = treeview.set(item, col)
                if cell_value:
                    cell_width = len(str(cell_value)) * 8
                    max_width = max(max_width, cell_width)
            
            max_width = min(max_width, 300)
            
            treeview.column(col, width=max_width)

    def show_original_code(self):
        """Muestra el código original en el editor"""
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', self.original_code)
        self.show_original_btn.config(bg=self.button_active_color)
        self.show_optimized_btn.config(bg=self.button_color)

    def show_optimized_code(self):
        """Muestra el código optimizado en el editor"""
        if hasattr(self, 'optimized_code') and self.optimized_code:
            self.editor.delete('1.0', tk.END)
            self.editor.insert('1.0', self.optimized_code)
            self.show_original_btn.config(bg=self.button_color)
            self.show_optimized_btn.config(bg=self.button_active_color)

    def compile(self):
        """Proceso de compilación completo con tabla de símbolos extendida"""
        code = self.editor.get("1.0", tk.END)
        self.original_code = code
        
        # Limpiar resultados anteriores
        self._clear_previous_results()
        
        # Análisis léxico
        tokens, lexical_errors = self.lexer.analyze(code)

        # Mostrar tokens
        for token in tokens:
            self.tokens_table.insert('', 'end', values=token)

        # Análisis sintáctico
        parser = Parser(tokens)
        syntactic_errors = parser.parse()
        
        # Mostrar tabla de símbolos EXTENDIDA
        all_symbols = parser.symbol_table.get_all_symbols()
        for symbol in all_symbols:
            self.symbols_table.insert('', 'end', values=(
                symbol['identificador'],
                symbol['categoria_lexica'],
                symbol['tipo_dato'] or 'N/A',
                symbol['ambito'],
                symbol['linea_declaracion'],
                symbol['estado'],
                symbol['contador_referencias'],
                'Sí' if symbol.get('inicializado', False) else 'No',
                symbol.get('tamano_memoria', 'N/A'),
                symbol.get('direccion_memoria', 'N/A'),
                'Sí' if symbol.get('es_constante', False) else 'No',
                'Sí' if symbol.get('modificable', True) else 'No',
                str(symbol.get('valor_actual', 'N/A'))[:20] + '...' if symbol.get('valor_actual') and len(str(symbol.get('valor_actual'))) > 20 else str(symbol.get('valor_actual', 'N/A')),
                symbol.get('categoria_semantica', 'N/A'),
                'Sí' if symbol.get('es_funcion', False) else 'No',
                'Sí' if symbol.get('es_tipo_usuario', False) else 'No'
            ))

        # Actualizar información de símbolos
        total_symbols = len(all_symbols)
        memory_used = parser.symbol_table.current_memory_usage
        self.symbols_info_label.config(
            text=f"Total de símbolos: {total_symbols} | Memoria usada: {memory_used} bytes | Memoria total asignada: {parser.symbol_table.next_memory_address} bytes"
        )

        # Mostrar árbol sintáctico
        if hasattr(parser, 'ast') and parser.ast:
            self.mostrar_arbol_sintactico(parser.ast)
            self.current_ast = parser.ast
            self.current_symbol_table = parser.symbol_table
        else:
            self.ast_tree.insert('', 'end', text='No se pudo generar el árbol sintáctico', values=('', '', ''))

        # Análisis semántico
        semantic_errors = []
        if hasattr(parser, 'ast') and parser.ast:
            semantic_analyzer = SemanticAnalyzer(parser.symbol_table)
            semantic_errors = semantic_analyzer.analyze(parser.ast)

        # Mostrar errores
        self._display_errors(lexical_errors, syntactic_errors, semantic_errors)

        # Visualización inicial de scope
        self._update_scope_visualization(all_symbols, all_symbols)

        # Configurar botones
        self.show_original_btn.config(bg=self.button_active_color)
        self.show_optimized_btn.config(bg=self.button_color)

    def optimize_code(self):
        """Aplica optimizaciones al código"""
        if not hasattr(self, 'current_ast') or not self.current_ast:
            return

        # Aplicar optimizaciones
        optimized_ast = self.optimizer.optimize(self.current_ast, self.current_symbol_table)
        
        # Generar código optimizado a partir del AST
        self.optimized_code = self._ast_to_code(optimized_ast)
        
        # Mostrar código optimizado en el editor
        self.show_optimized_code()
        
        # Mostrar reporte de optimización
        report = self.optimizer.get_optimization_report()
        
        # Actualizar información de optimización
        optimizations_count = len(report['optimizations_applied'])
        reduction_percentage = report['metrics']['reductions'].get('reduction_percentage', 0)
        
        self.optimization_info_label.config(
            text=f"Optimizaciones aplicadas: {optimizations_count} | Reducción: {reduction_percentage:.1f}%"
        )

        # Mostrar lista de optimizaciones
        self.optimizations_list.config(state='normal')
        self.optimizations_list.delete('1.0', tk.END)
        
        if report['optimizations_applied']:
            for i, optimization in enumerate(report['optimizations_applied'], 1):
                self.optimizations_list.insert('end', f"{i:2d}. {optimization}\n")
        else:
            self.optimizations_list.insert('end', "No se aplicaron optimizaciones\n")
        
        self.optimizations_list.config(state='disabled')

        # Mostrar métricas
        self.metrics_text.config(state='normal')
        self.metrics_text.delete('1.0', tk.END)
        
        metrics = report['metrics']
        self.metrics_text.insert('end', f"Instrucciones originales: {metrics['original_instructions']}\n")
        self.metrics_text.insert('end', f"Instrucciones optimizadas: {metrics['optimized_instructions']}\n")
        self.metrics_text.insert('end', f"Reducción total: {metrics['reductions']['total_instructions_reduced']} instrucciones\n")
        self.metrics_text.insert('end', f"Porcentaje de reducción: {metrics['reductions']['reduction_percentage']:.1f}%\n")
        self.metrics_text.insert('end', f"Optimizaciones aplicadas: {metrics['reductions']['optimizations_count']}\n")
        
        # Mostrar optimización de memoria si está disponible
        if 'memory_optimization' in metrics and metrics['memory_optimization']:
            memory_metrics = metrics['memory_optimization']
            self.metrics_text.insert('end', f"Memoria ahorrada: {memory_metrics.get('memory_saved_bytes', 0)} bytes\n")
            self.metrics_text.insert('end', f"Símbolos optimizados: {memory_metrics.get('optimized_symbols_count', 0)}\n")
        
        self.metrics_text.config(state='disabled')

        # Actualizar visualización de scope después de la optimización
        optimized_symbols = self.current_symbol_table.get_all_symbols()
        self._update_scope_visualization(
            self.current_symbol_table.get_all_symbols(), 
            optimized_symbols
        )

        # Mostrar árbol optimizado
        for item in self.ast_tree.get_children():
            self.ast_tree.delete(item)
        self.mostrar_arbol_sintactico(optimized_ast)

    def _ast_to_code(self, node, level=0):
        """Convierte el AST optimizado a código Pixie"""
        if node is None:
            return ""
        
        code = ""
        indent = "    " * level
        
        if node.tipo == 'PROGRAMA':
            for child in node.hijos:
                child_code = self._ast_to_code(child, level)
                if child_code:
                    code += child_code + "\n"
        elif node.tipo == 'DECLARACION_VARIABLE':
            if len(node.hijos) >= 2:
                identifier = self._ast_to_code(node.hijos[0], level)
                var_type = self._ast_to_code(node.hijos[1], level)
                code += f"{indent}let {identifier} be a {var_type}"
                if len(node.hijos) > 2 and node.hijos[2].tipo == 'ASIGNACION':
                    value = self._ast_to_code(node.hijos[2], level)
                    code += f" = {value}"
                code += ";"
        elif node.tipo == 'DECLARACION_CONSTANTE':
            if len(node.hijos) >= 1:
                identifier = self._ast_to_code(node.hijos[0], level)
                code += f"{indent}forever {identifier}"
                if len(node.hijos) > 1 and node.hijos[1].tipo == 'ASIGNACION':
                    value = self._ast_to_code(node.hijos[1], level)
                    code += f" = {value}"
                code += ";"
        elif node.tipo == 'IDENTIFICADOR':
            return node.valor if node.valor else ""
        elif node.tipo == 'TIPO':
            return node.valor if node.valor else ""
        elif node.tipo == 'ASIGNACION':
            if node.hijos:
                return self._ast_to_code(node.hijos[0], level)
        elif node.tipo == 'LITERAL':
            return node.valor if node.valor else ""
        elif node.tipo == 'EXPRESION_ARITMETICA':
            if len(node.hijos) >= 3:
                left = self._ast_to_code(node.hijos[0], level)
                operator = self._ast_to_code(node.hijos[1], level)
                right = self._ast_to_code(node.hijos[2], level)
                return f"{left} {operator} {right}"
        elif node.tipo == 'OPERADOR_ARITMETICO':
            return node.valor if node.valor else ""
        elif node.tipo == 'SENTENCIA_IF':
            if len(node.hijos) >= 2:
                condition = self._ast_to_code(node.hijos[0].hijos[0], level) if node.hijos[0].hijos else ""
                code += f"{indent}if ({condition}) {{\n"
                block_code = self._ast_to_code(node.hijos[1], level + 1)
                code += block_code
                code += f"\n{indent}}}"
        elif node.tipo == 'BLOQUE':
            for child in node.hijos:
                child_code = self._ast_to_code(child, level)
                if child_code:
                    code += child_code + "\n"
        
        return code

    def export_symbol_table(self):
        """Exporta la tabla de símbolos a un archivo JSON"""
        if hasattr(self, 'current_symbol_table'):
            all_symbols = self.current_symbol_table.get_all_symbols()
            filename = f"tabla_simbolos_{id(self)}.json"
            
            # Crear una versión serializable
            serializable_symbols = []
            for symbol in all_symbols:
                serializable_symbol = {}
                for key, value in symbol.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        serializable_symbol[key] = value
                    else:
                        serializable_symbol[key] = str(value)
                serializable_symbols.append(serializable_symbol)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_symbols, f, ensure_ascii=False, indent=2)
            
            # Mostrar mensaje de éxito
            success_label = tk.Label(self.window, 
                                   text=f"Tabla de símbolos exportada a {filename}", 
                                   fg="green", font=("Arial", 10))
            success_label.pack()
            self.window.after(3000, success_label.destroy)

    def _clear_previous_results(self):
        """Limpia los resultados anteriores"""
        for widget in [self.tokens_table, self.symbols_table, self.ast_tree, 
                      self.before_scope_tree, self.after_scope_tree]:
            for item in widget.get_children():
                widget.delete(item)
        
        for text_widget in [self.lexical_errors_text, self.syntactic_errors_text, 
                           self.semantic_errors_text, self.optimizations_list, self.metrics_text]:
            text_widget.config(state='normal')
            text_widget.delete('1.0', tk.END)
            text_widget.config(state='disabled')

    def _display_errors(self, lexical_errors, syntactic_errors, semantic_errors):
        """Muestra todos los tipos de errores"""
        self._display_error_list(self.lexical_errors_text, lexical_errors, "léxicos")
        self._display_error_list(self.syntactic_errors_text, syntactic_errors, "sintácticos")
        self._display_error_list(self.semantic_errors_text, semantic_errors, "semánticos")

    def _display_error_list(self, text_widget, errors, error_type):
        """Muestra una lista de errores en un widget de texto"""
        text_widget.config(state='normal')
        
        if errors:
            error_count = len(errors)
            text_widget.insert('end', f"Se encontraron {error_count} error(es) {error_type}:\n\n", 'error_title')
            
            for i, error in enumerate(errors, 1):
                if 'Advertencia' in error:
                    text_widget.insert('end', f"{i:2d}. {error}\n", 'warning')
                else:
                    text_widget.insert('end', f"{i:2d}. {error}\n", 'error_item')
        else:
            text_widget.insert('end', f'✓ No se encontraron errores {error_type}.', 'success')
        
        # Configurar tags
        text_widget.tag_configure('error_title', foreground='red', font=("Arial", 10, "bold"))
        text_widget.tag_configure('error_item', foreground='darkred')
        text_widget.tag_configure('warning', foreground='orange')
        text_widget.tag_configure('success', foreground='green', font=("Arial", 10, "bold"))
        text_widget.config(state='disabled')

    def _update_scope_visualization(self, original_symbols, optimized_symbols):
        """Actualiza la visualización de búsqueda de scope"""
        # Limpiar árboles
        for item in self.before_scope_tree.get_children():
            self.before_scope_tree.delete(item)
        for item in self.after_scope_tree.get_children():
            self.after_scope_tree.delete(item)
        
        # Mostrar scope antes de la optimización
        scope_groups = {}
        for symbol in original_symbols:
            scope = symbol['ambito']
            if scope not in scope_groups:
                scope_groups[scope] = []
            scope_groups[scope].append(symbol['identificador'])
    
        for scope, variables in scope_groups.items():
            for var in variables:
                self.before_scope_tree.insert('', 'end', values=(var, scope))
        
        # Mostrar scope después de la optimización
        scope_groups_opt = {}
        for symbol in optimized_symbols:
            scope = symbol['ambito']
            if scope not in scope_groups_opt:
                scope_groups_opt[scope] = []
            scope_groups_opt[scope].append(symbol['identificador'])
    
        for scope, variables in scope_groups_opt.items():
            for var in variables:
                self.after_scope_tree.insert('', 'end', values=(var, scope))
        
        # Ajustar automáticamente el ancho de columnas
        self.ajustar_ancho_columnas(self.before_scope_tree)
        self.ajustar_ancho_columnas(self.after_scope_tree)

    def mostrar_arbol_sintactico(self, nodo, parent=''):
        """Muestra recursivamente el árbol sintáctico en el Treeview"""
        if nodo is None:
            return
            
        texto_nodo = f"{nodo.tipo}"
        if nodo.valor:
            texto_nodo += f": {nodo.valor}"
            
        nodo_id = self.ast_tree.insert(
            parent, 'end', 
            text=texto_nodo,
            values=(nodo.valor or '', nodo.linea or '', nodo.columna or '')
        )
        
        for hijo in nodo.hijos:
            self.mostrar_arbol_sintactico(hijo, nodo_id)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = CompactCompilerGUI()
    app.run()