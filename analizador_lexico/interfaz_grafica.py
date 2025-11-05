from tkinter import ttk, scrolledtext
import tkinter as tk
from analizador_lexico import StrictLexicalAnalyzer
from analizador_sintactico import Parser, ASTNode

class CompactCompilerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Pixie - Analizador Léxico y Sintáctico")
        self.window.geometry("1200x800")

        self.lexer = StrictLexicalAnalyzer()
        self.create_widgets()

    def create_widgets(self):
        # Frame principal dividido en izquierda y derecha
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # === LADO IZQUIERDO ===
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Editor de código
        tk.Label(left_frame, text="Editor de Código Pixie:",
                 font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))

        self.editor = scrolledtext.ScrolledText(left_frame, width=60, height=25,
                                                font=("Consolas", 10))
        self.editor.pack(fill='both', expand=True)

        # Insertar código de prueba
        test_code = """# ERRORES: Identificadores mal formados
let 2edad be a Gem = 25;
let nombre-usuario be a Letter = "Juan";
let @variable be a Gem = 10;
let var!able be a Gem = 15;

# ERRORES: Números inválidos
let decimal1 be a Shimmer = 12..34;
let decimal2 be a Shimmer = .99;

# ERRORES: Incoherencia entre tipo de dato y asignación
let nombre be a Letter = 'María';
let valor be a Shimmer = 'True';
let entero1 be a Gem = 123abc;

# ERRORES: Valores no reconocidos
let estado be a Truth_potion = true;
let tipo be a Gem = integer;

# CÓDIGO VÁLIDO
let edad be a Gem = 25;
let precio be a Shimmer = 99.99;
let activo be a Truth_potion = sparkle_on;
let nombre be a Letter = "María";

if (edad >= 18) {
    share nombre + " es mayor de edad";
}"""

        self.editor.insert('1.0', test_code)

        # Botón Compilar (color rosa)
        self.compile_btn = tk.Button(left_frame, text="Compilar", command=self.compile,
                                     bg="#FF69B4", fg="white", font=("Arial", 11, "bold"),
                                     height=2, width=15)
        self.compile_btn.pack(pady=10)

        # === LADO DERECHO ===
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)

        # Pestañas para resultados
        notebook = ttk.Notebook(right_frame)

        # Pestaña de tokens
        tokens_frame = ttk.Frame(notebook)
        notebook.add(tokens_frame, text="Tokens")

        # Pestaña de tabla de símbolos
        symbols_frame = ttk.Frame(notebook)
        notebook.add(symbols_frame, text="Tabla de Símbolos")

        # Pestaña de árbol sintáctico
        ast_frame = ttk.Frame(notebook)
        notebook.add(ast_frame, text="Árbol Sintáctico")

        # Pestaña de errores léxicos
        lexical_errors_frame = ttk.Frame(notebook)
        notebook.add(lexical_errors_frame, text="Errores Léxicos")

        # Pestaña de errores sintácticos
        syntactic_errors_frame = ttk.Frame(notebook)
        notebook.add(syntactic_errors_frame, text="Errores Sintácticos")

        notebook.pack(fill='both', expand=True)

        # Tabla de tokens
        token_columns = ('linea', 'token', 'descripcion')
        self.tokens_table = ttk.Treeview(
            tokens_frame, columns=token_columns, show='headings', height=15)
        self.tokens_table.heading('linea', text='Línea')
        self.tokens_table.heading('token', text='Token')
        self.tokens_table.heading('descripcion', text='Descripción')

        # Scrollbar para la tabla de tokens
        scrollbar_tokens = ttk.Scrollbar(
            tokens_frame, orient='vertical', command=self.tokens_table.yview)
        self.tokens_table.configure(yscrollcommand=scrollbar_tokens.set)

        self.tokens_table.pack(side='left', fill='both', expand=True)
        scrollbar_tokens.pack(side='right', fill='y')

        # Configurar columnas de tokens
        self.tokens_table.column('linea', width=80)
        self.tokens_table.column('token', width=150)
        self.tokens_table.column('descripcion', width=200)

        # Frame para tabla de símbolos con información adicional
        symbols_main_frame = tk.Frame(symbols_frame)
        symbols_main_frame.pack(fill='both', expand=True)
        
        # Información de la tabla de símbolos
        self.symbols_info_label = tk.Label(symbols_main_frame, 
                                          text="Total de símbolos: 0 | Memoria usada: 0 bytes",
                                          font=("Arial", 10, "bold"),
                                          bg="#F0F0F0",
                                          relief="solid",
                                          padx=10,
                                          pady=5)
        self.symbols_info_label.pack(fill='x', padx=5, pady=5)

        # Tabla de símbolos con todas las columnas requeridas
        symbol_columns = ('identificador', 'categoria', 'tipo', 'ambito', 'direccion', 
                         'linea', 'valor', 'estado', 'estructura', 'referencias')
        self.symbols_table = ttk.Treeview(
            symbols_main_frame, columns=symbol_columns, show='headings', height=15)
        
        # Configurar encabezados
        self.symbols_table.heading('identificador', text='Identificador')
        self.symbols_table.heading('categoria', text='Categoría Léxica')
        self.symbols_table.heading('tipo', text='Tipo de Dato')
        self.symbols_table.heading('ambito', text='Ámbito')
        self.symbols_table.heading('direccion', text='Dirección Memoria')
        self.symbols_table.heading('linea', text='Línea Declaración')
        self.symbols_table.heading('valor', text='Valor')
        self.symbols_table.heading('estado', text='Estado')
        self.symbols_table.heading('estructura', text='Información Estructura')
        self.symbols_table.heading('referencias', text='Contador Referencias')

        # Scrollbar para la tabla de símbolos
        scrollbar_symbols = ttk.Scrollbar(
            symbols_main_frame, orient='vertical', command=self.symbols_table.yview)
        self.symbols_table.configure(yscrollcommand=scrollbar_symbols.set)

        self.symbols_table.pack(side='left', fill='both', expand=True)
        scrollbar_symbols.pack(side='right', fill='y')

        # Configurar anchos de columna
        self.symbols_table.column('identificador', width=120)
        self.symbols_table.column('categoria', width=120)
        self.symbols_table.column('tipo', width=100)
        self.symbols_table.column('ambito', width=100)
        self.symbols_table.column('direccion', width=120)
        self.symbols_table.column('linea', width=100)
        self.symbols_table.column('valor', width=100)
        self.symbols_table.column('estado', width=100)
        self.symbols_table.column('estructura', width=140)
        self.symbols_table.column('referencias', width=120)

        # Árbol sintáctico
        self.ast_tree = ttk.Treeview(ast_frame, columns=('valor', 'linea'), show='tree headings', height=15)
        self.ast_tree.heading('#0', text='Nodo del Árbol Sintáctico')
        self.ast_tree.heading('valor', text='Valor')
        self.ast_tree.heading('linea', text='Línea')
        
        self.ast_tree.column('#0', width=300)
        self.ast_tree.column('valor', width=150)
        self.ast_tree.column('linea', width=80)

        scrollbar_ast = ttk.Scrollbar(ast_frame, orient='vertical', command=self.ast_tree.yview)
        self.ast_tree.configure(yscrollcommand=scrollbar_ast.set)

        self.ast_tree.pack(side='left', fill='both', expand=True)
        scrollbar_ast.pack(side='right', fill='y')

        # Área de errores léxicos
        self.lexical_errors_text = scrolledtext.ScrolledText(lexical_errors_frame, width=50, height=15,
                                                             font=("Consolas", 9), state='disabled')
        self.lexical_errors_text.pack(fill='both', expand=True)

        # Área de errores sintácticos
        self.syntactic_errors_text = scrolledtext.ScrolledText(syntactic_errors_frame, width=50, height=15,
                                                               font=("Consolas", 9), state='disabled')
        self.syntactic_errors_text.pack(fill='both', expand=True)

    def compile(self):
        code = self.editor.get("1.0", tk.END)
        
        # Análisis léxico
        tokens, lexical_errors = self.lexer.analyze(code)

        # Limpiar resultados anteriores
        for item in self.tokens_table.get_children():
            self.tokens_table.delete(item)
            
        for item in self.symbols_table.get_children():
            self.symbols_table.delete(item)
            
        for item in self.ast_tree.get_children():
            self.ast_tree.delete(item)

        self.lexical_errors_text.config(state='normal')
        self.lexical_errors_text.delete('1.0', tk.END)
        
        self.syntactic_errors_text.config(state='normal')
        self.syntactic_errors_text.delete('1.0', tk.END)
        
        self.window.update_idletasks()

        # Mostrar tokens
        for token in tokens:
            self.tokens_table.insert('', 'end', values=token)

        # Análisis sintáctico
        parser = Parser(tokens)
        syntactic_errors = parser.parse()
        
        # Mostrar tabla de símbolos con todas las columnas
        all_symbols = parser.symbol_table.get_all_symbols()
        for symbol in all_symbols:
            self.symbols_table.insert('', 'end', values=(
                symbol['identificador'],
                symbol['categoria_lexica'],
                symbol['tipo_dato'] or 'N/A',
                symbol['ambito'],
                symbol['direccion_memoria'],
                symbol['linea_declaracion'],
                str(symbol['valor'])[:50] + '...' if symbol['valor'] and len(str(symbol['valor'])) > 50 else str(symbol['valor'] or 'N/A'),
                symbol['estado'],
                symbol['informacion_estructura'] or 'N/A',
                symbol['contador_referencias']
            ))

        # Actualizar información de la tabla de símbolos
        total_symbols = len(all_symbols)
        memory_used = parser.symbol_table.current_memory_usage
        self.symbols_info_label.config(
            text=f"Total de símbolos: {total_symbols} | Memoria usada: {memory_used} bytes | "
                 f"Límite: {parser.symbol_table.max_memory_bytes} bytes"
        )

        # Mostrar árbol sintáctico
        if hasattr(parser, 'ast') and parser.ast:
            self.mostrar_arbol_sintactico(parser.ast)
        else:
            self.ast_tree.insert('', 'end', text='No se pudo generar el árbol sintáctico', values=('', ''))

        # Mostrar errores léxicos
        if lexical_errors:
            error_count = len(lexical_errors)
            self.lexical_errors_text.insert(
                'end', f"Se encontraron {error_count} error(es) léxico(s):\n\n", 'error_title')
            
            for i, error in enumerate(lexical_errors, 1):
                self.lexical_errors_text.insert(
                    'end', f"{i:2d}. {error}\n", 'error_item')

            # Configurar tags para colores
            self.lexical_errors_text.tag_configure(
                'error_title', foreground='red', font=("Arial", 10, "bold"))
            self.lexical_errors_text.tag_configure('error_item', foreground='darkred')
        else:
            self.lexical_errors_text.insert(
                'end', '✓ No se encontraron errores léxicos.', 'success')
            self.lexical_errors_text.tag_configure(
                'success', foreground='green', font=("Arial", 10, "bold"))

        # Mostrar errores sintácticos
        if syntactic_errors:
            error_count = len(syntactic_errors)
            self.syntactic_errors_text.insert(
                'end', f"Se encontraron {error_count} error(es) sintáctico(s):\n\n", 'error_title')
            
            for i, error in enumerate(syntactic_errors, 1):
                self.syntactic_errors_text.insert(
                    'end', f"{i:2d}. {error}\n", 'error_item')

            # Configurar tags para colores
            self.syntactic_errors_text.tag_configure(
                'error_title', foreground='red', font=("Arial", 10, "bold"))
            self.syntactic_errors_text.tag_configure('error_item', foreground='darkred')
        else:
            self.syntactic_errors_text.insert(
                'end', '✓ No se encontraron errores sintácticos.', 'success')
            self.syntactic_errors_text.tag_configure(
                'success', foreground='green', font=("Arial", 10, "bold"))

        self.lexical_errors_text.config(state='disabled')
        self.syntactic_errors_text.config(state='disabled')

    def mostrar_arbol_sintactico(self, nodo, parent=''):
        """Muestra recursivamente el árbol sintáctico en el Treeview"""
        if nodo is None:
            return
            
        # Crear texto para mostrar
        texto_nodo = f"{nodo.tipo}"
        if nodo.valor:
            texto_nodo += f": {nodo.valor}"
            
        # Insertar nodo en el árbol
        nodo_id = self.ast_tree.insert(
            parent, 'end', 
            text=texto_nodo,
            values=(nodo.valor or '', nodo.linea or '')
        )
        
        # Insertar hijos recursivamente
        for hijo in nodo.hijos:
            self.mostrar_arbol_sintactico(hijo, nodo_id)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = CompactCompilerGUI()
    app.run()