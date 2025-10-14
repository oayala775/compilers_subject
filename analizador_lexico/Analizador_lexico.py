import tkinter as tk
from tkinter import ttk, scrolledtext
import re

class StrictLexicalAnalyzer:
    def __init__(self):
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

    def analyze(self, code: str):
        tokens = []
        errors = []
        lines: list[str] = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Eliminar comentarios
            comment_pos = line.find('#')
            if comment_pos != -1:
                line = line[:comment_pos]
            
            line = line.rstrip()
            if not line:
                continue
                
            pos: int = 0
            while pos < len(line):
                if line[pos].isspace():
                    pos += 1
                    continue
                
                # Operadores multi-carácter
                if pos + 1 < len(line):
                    two_char = line[pos:pos+2]
                    if two_char in self.valid_multi_char_operators:
                        tokens.append((line_num, two_char, 'Operador'))
                        pos += 2
                        continue
                
                # Operadores de un carácter
                if line[pos] in self.valid_operators:
                    tokens.append((line_num, line[pos], 'Operador'))
                    pos += 1
                    continue
                
                # Números decimales
                decimal_match = re.match(r'[+-]?(\d+\.\d+|\.\d+|\d+\.)', line[pos:])
                if decimal_match:
                    token = decimal_match.group()
                    # Verificar formato válido
                    if token.count('.') != 1:
                        errors.append(f"Línea {line_num}: Número decimal mal formado '{token}'")
                    elif token.startswith('.') or token.endswith('.'):
                        errors.append(f"Línea {line_num}: Número decimal mal formado '{token}'")
                    else:
                        tokens.append((line_num, token, 'Decimal'))
                    pos += len(token)
                    continue
                
                # Números enteros
                int_match = re.match(r'[+-]?\d+', line[pos:])
                if int_match:
                    token = int_match.group()
                    # Verificar que no sea parte de identificador
                    next_pos = pos + len(token)
                    if next_pos < len(line) and (line[next_pos].isalpha() or line[next_pos] == '_'):
                        # Es un identificador que empieza con número
                        identifier = token
                        while next_pos < len(line) and (line[next_pos].isalnum() or line[next_pos] in ['_', '-', '!', '@']):
                            identifier += line[next_pos]
                            next_pos += 1
                        errors.append(f"Línea {line_num}: Identificador inválido que comienza con número '{identifier}'")
                        pos = next_pos
                    else:
                        tokens.append((line_num, token, 'Entero'))
                        pos += len(token)
                    continue
                
                # Cadenas
                if line[pos] == '"':
                    end_quote = line.find('"', pos + 1)
                    if end_quote == -1:
                        errors.append(f"Línea {line_num}: Cadena sin cerrar")
                        break
                    token = line[pos:end_quote + 1]
                    tokens.append((line_num, token, 'Cadena'))
                    pos = end_quote + 1
                    continue
                
                # Caracteres
                if line[pos] == "'":
                    if pos + 2 >= len(line) or line[pos + 2] != "'":
                        errors.append(f"Línea {line_num}: Carácter mal formado")
                        pos += 1
                        continue
                    token = line[pos:pos + 3]
                    # Verificar que tenga exactamente un carácter entre comillas
                    if len(token) != 3 or token[1] == "'":
                        errors.append(f"Línea {line_num}: Carácter mal formado '{token}'")
                    else:
                        tokens.append((line_num, token, 'Caracter'))
                    pos += 3
                    continue
                
                # Identificadores - método más estricto
                if line[pos].isalpha() or line[pos] == '_':
                    start = pos
                    # Consumir hasta encontrar un delimitador
                    while pos < len(line) and (line[pos].isalnum() or line[pos] in ['_', '-', '!', '@', '$']):
                        pos += 1
                    
                    token = line[start:pos]
                    
                    # Verificar caracteres inválidos en identificador
                    invalid_chars = [c for c in token if not c.isalnum() and c != '_']
                    if invalid_chars:
                        errors.append(f"Línea {line_num}: Identificador con caracteres inválidos '{token}' - caracteres no permitidos: {invalid_chars}")
                        continue
                    
                    # Clasificar token
                    if token in self.keywords:
                        tokens.append((line_num, token, 'Palabra clave'))
                    elif token in self.types:
                        tokens.append((line_num, token, 'Tipo de dato'))
                    elif token in self.boolean_values:
                        tokens.append((line_num, token, 'Valor booleano'))
                    else:
                        # Verificar si es un valor no reconocido
                        if token in ['true', 'false', 'integer']:
                            errors.append(f"Línea {line_num}: Valor no reconocido en Pixie '{token}'")
                        else:
                            tokens.append((line_num, token, 'Identificador'))
                    continue
                
                # Operadores no válidos
                if pos + 1 < len(line) and line[pos:pos+2] == '<>':
                    errors.append(f"Línea {line_num}: Operador no válido '<>'")
                    pos += 2
                    continue
                
                # Carácter no válido
                errors.append(f"Línea {line_num}: Carácter no válido '{line[pos]}'")
                pos += 1
        
        return tokens, errors

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

# ERRORES: Valores no reconocidos
let estado be a Truth_potion = true;
let tipo be a Gem = integer;

# CÓDIGO VÁLIDO
let edad be a Gem = 25;
let nombre be a Letter = "María";
let precio be a Shimmer = 99.99;
let activo be a Truth_potion = sparkle_on;

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