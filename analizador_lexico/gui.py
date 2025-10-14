from Analizador_lexico import StrictLexicalAnalyzer
from tkinter import ttk, scrolledtext
import tkinter as tk

class CompactCompilerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Pixie - Analizador Léxico")
        self.window.geometry("1000x700")
        
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
let entero1 be a Gem = 123abc;

# ERRORES: Usa un tipo de dato diferente al esperado
let nombre be a Letter = "María";

# ERRORES: Valores no reconocidos
let estado be a Truth_potion = true;
let tipo be a Gem = integer;

# CÓDIGO VÁLIDO
let edad be a Gem = 25;
let precio be a Shimmer = 99.99;
let activo be a Truth_potion = sparkle_on;
let activo be a Truth_potion;

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
        
        # Pestaña de tabla de símbolos
        tokens_frame = ttk.Frame(notebook)
        notebook.add(tokens_frame, text="Tabla de Símbolos")
        
        # Pestaña de errores
        errors_frame = ttk.Frame(notebook)
        notebook.add(errors_frame, text="Errores Léxicos")
        
        notebook.pack(fill='both', expand=True)
        
        # Tabla de símbolos
        columns = ('linea', 'token', 'descripcion')
        self.tokens_table = ttk.Treeview(tokens_frame, columns=columns, show='headings', height=15)
        self.tokens_table.heading('linea', text='Línea')
        self.tokens_table.heading('token', text='Token')
        self.tokens_table.heading('descripcion', text='Descripción')
        
        # Scrollbar para la tabla
        scrollbar_tokens = ttk.Scrollbar(tokens_frame, orient='vertical', command=self.tokens_table.yview)
        self.tokens_table.configure(yscrollcommand=scrollbar_tokens.set)
        
        self.tokens_table.pack(side='left', fill='both', expand=True)
        scrollbar_tokens.pack(side='right', fill='y')
        
        # Configurar columnas
        self.tokens_table.column('linea', width=80)
        self.tokens_table.column('token', width=150)
        self.tokens_table.column('descripcion', width=200)
        
        # Área de errores
        self.errors_text = scrolledtext.ScrolledText(errors_frame, width=50, height=15, 
                                                   font=("Consolas", 9))
        self.errors_text.pack(fill='both', expand=True)
        
    def compile(self):
        code = self.editor.get("1.0", tk.END)
        tokens, errors = self.lexer.analyze(code)
        
        # Limpiar resultados anteriores
        for item in self.tokens_table.get_children():
            self.tokens_table.delete(item)
        
        self.errors_text.delete('1.0', tk.END)
        
        # Mostrar tokens
        for token in tokens:
            self.tokens_table.insert('', 'end', values=token)
        
        # Mostrar errores
        if errors:
            error_count = len(errors)
            self.errors_text.insert('end', f"Se encontraron {error_count} error(es) léxico(s):\n\n", 'error_title')
            for i, error in enumerate(errors, 1):
                self.errors_text.insert('end', f"{i:2d}. {error}\n", 'error_item')
            
            # Configurar tags para colores
            self.errors_text.tag_configure('error_title', foreground='black', font=("Arial", 10, "bold"))
            self.errors_text.tag_configure('error_item', foreground='black')
        else:
            self.errors_text.insert('end', '✓ No se encontraron errores léxicos. El código es válido.', 'success')
            self.errors_text.tag_configure('success', foreground='green', font=("Arial", 10, "bold"))
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = CompactCompilerGUI()
    app.run()