import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import io

#colores
BG_DARK    = "#0d0d1a"
BG_PANEL   = "#12122a"
BG_EDITOR  = "#0a0a18"
NEON_CYAN  = "#00f0ff"
NEON_PINK  = "#ff2d78"
NEON_GREEN = "#39ff14"
NEON_YELL  = "#ffe600"
TEXT_WHITE = "#e0e0ff"
TEXT_MUTED = "#6666aa"
BORDER     = "#2a2a5a"

#compilador importado
try:
    import ply.lex as lex_module
    import ply.yacc as yacc_module
    from Lexer import lexer, error_table, find_column
    from Parser import parser, symbol_table
    COMPILER_OK = True
except Exception as e:
    COMPILER_OK = False
    IMPORT_ERROR = str(e)

# ─────────────────────────────────────────────
#  FUNCIÓN COMPILAR
# ─────────────────────────────────────────────
def compile_code(code):
    if not COMPILER_OK:
        return [], "(no se pudo cargar el compilador)", [], [{"tipo": "Sistema", "linea": "-", "columna": "-", "descripcion": IMPORT_ERROR}]

    error_table.clear()
    symbol_table.clear()

    # tokens
    lexer.lineno = 1
    lexer.input(code)
    tokens_list = []
    for tok in lexer:
        tokens_list.append((tok.type, str(tok.value), tok.lineno))

    # ast
    lexer.lineno = 1
    try:
        tree = parser.parse(code, lexer=lexer)
        ast_text = format_ast(tree) if tree else "(no se pudo construir el árbol)"
    except Exception as ex:
        ast_text = f"Error: {ex}"

    syms   = list(symbol_table)
    errors = list(error_table)
    return tokens_list, ast_text, syms, errors

def format_ast(tree, indent=0):
    prefix = "    " * indent + "└─ "
    result = ""
    if isinstance(tree, tuple):
        result += f"{prefix}{tree[0]}\n"
        for child in tree[1:]:
            result += format_ast(child, indent + 1)
    elif isinstance(tree, list):
        for item in tree:
            result += format_ast(item, indent)
    else:
        result += f"{prefix}{repr(tree)}\n"
    return result
#interfaz
class NetRunnerIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Cybercode")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.build_ui()

    def build_ui(self):
        # ── HEADER ──────────────────────────────
        header = tk.Frame(self.root, bg=BG_DARK, pady=8)
        header.pack(fill="x", padx=16)

        tk.Label(header, text="CYBERCODE", font=("Courier New", 18, "bold"),
                 fg=NEON_CYAN, bg=BG_DARK).pack(side="left")
        tk.Label(header, text="",
                 font=("Courier New", 11), fg=TEXT_MUTED, bg=BG_DARK).pack(side="left", padx=8)

        self.status_lbl = tk.Label(header, text="LISTO", font=("Courier New", 10, "bold"),
                                   fg=NEON_GREEN, bg=BG_DARK)
        self.status_lbl.pack(side="right")

        # separador
        tk.Frame(self.root, bg=NEON_CYAN, height=1).pack(fill="x", padx=16)

       
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=16, pady=10)

        # columna izquierda — editor
        left = tk.Frame(body, bg=BG_DARK)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="// EDITOR", font=("Courier New", 9, "bold"),
                 fg=NEON_PINK, bg=BG_DARK).pack(anchor="w")

        self.editor = scrolledtext.ScrolledText(
            left, font=("Courier New", 12), bg=BG_EDITOR,
            fg=NEON_CYAN, insertbackground=NEON_CYAN,
            selectbackground=NEON_PINK, relief="flat",
            bd=0, padx=10, pady=10
        )
        self.editor.pack(fill="both", expand=True)
        self.editor.insert("1.0", 'init\n    jack hp := 100;\n    transmit("Night City");\nshutdown')

        # botón compilar
        btn_frame = tk.Frame(left, bg=BG_DARK, pady=8)
        btn_frame.pack(fill="x")

        self.btn = tk.Button(
            btn_frame, text="COMPILAR",
            font=("Courier New", 12, "bold"),
            bg=NEON_PINK, fg=BG_DARK,
            activebackground="#ff6fa3", activeforeground=BG_DARK,
            relief="flat", padx=20, pady=8, cursor="hand2",
            command=self.run_compiler
        )
        self.btn.pack(fill="x")

        tk.Button(
            btn_frame, text="LIMPIAR",
            font=("Courier New", 10),
            bg=BG_PANEL, fg=TEXT_MUTED,
            activebackground=BORDER, activeforeground=TEXT_WHITE,
            relief="flat", padx=10, pady=4, cursor="hand2",
            command=self.clear_all
        ).pack(fill="x", pady=(4, 0))

        # columna derecha — resultados
        right = tk.Frame(body, bg=BG_DARK)
        right.pack(side="right", fill="both", expand=True, padx=(12, 0))

        # notebook de tabs
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Cyber.TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("Cyber.TNotebook.Tab",
                        background=BG_PANEL, foreground=TEXT_MUTED,
                        font=("Courier New", 9, "bold"),
                        padding=[12, 6])
        style.map("Cyber.TNotebook.Tab",
                  background=[("selected", BG_DARK)],
                  foreground=[("selected", NEON_CYAN)])

        results_header = tk.Frame(right, bg=BG_DARK)
        results_header.pack(fill="x", pady=(0, 4))

        tk.Button(
            results_header, text=" LIMPIAR RESULTADOS",
            font=("Courier New", 9, "bold"),
            bg=BG_PANEL, fg=NEON_YELL,
            activebackground=BORDER, activeforeground=TEXT_WHITE,
            relief="flat", padx=10, pady=4, cursor="hand2",
            command=self.clear_results
        ).pack(side="right")

        self.nb = ttk.Notebook(right, style="Cyber.TNotebook")
        self.nb.pack(fill="both", expand=True)

        # Tab Tokens
        self.tab_tokens = tk.Frame(self.nb, bg=BG_DARK)
        self.nb.add(self.tab_tokens, text="  TOKENS  ")
        self._build_token_tab()

        # Tab AST
        self.tab_ast = tk.Frame(self.nb, bg=BG_DARK)
        self.nb.add(self.tab_ast, text="  ARBOL ")
        self._build_ast_tab()

        # Tab Símbolos
        self.tab_sym = tk.Frame(self.nb, bg=BG_DARK)
        self.nb.add(self.tab_sym, text="  SÍMBOLOS  ")
        self._build_sym_tab()

        # Tab Errores
        self.tab_err = tk.Frame(self.nb, bg=BG_DARK)
        self.nb.add(self.tab_err, text="  ERRORES  ")
        self._build_err_tab()

    # ── TABS ────────────────────────────────────
    def _build_token_tab(self):
        cols = ("Tipo", "Valor", "Línea")
        self.token_tree = self._make_treeview(self.tab_tokens, cols)

    def _build_ast_tab(self):
        self.ast_text = scrolledtext.ScrolledText(
            self.tab_ast, font=("Courier New", 11),
            bg=BG_EDITOR, fg=NEON_GREEN,
            relief="flat", bd=0, padx=10, pady=10,
            state="disabled"
        )
        self.ast_text.pack(fill="both", expand=True)

    def _build_sym_tab(self):
        cols = ("Nombre", "Tipo", "Valor", "Línea")
        self.sym_tree = self._make_treeview(self.tab_sym, cols)

    def _build_err_tab(self):
        cols = ("Tipo", "Línea", "Col", "Descripción")
        self.err_tree = self._make_treeview(self.tab_err, cols)

    def _make_treeview(self, parent, cols):
        style = ttk.Style()
        style.configure("Cyber.Treeview",
                        background=BG_PANEL, foreground=TEXT_WHITE,
                        fieldbackground=BG_PANEL, rowheight=24,
                        font=("Courier New", 10))
        style.configure("Cyber.Treeview.Heading",
                        background=BG_DARK, foreground=NEON_CYAN,
                        font=("Courier New", 9, "bold"))
        style.map("Cyber.Treeview",
                  background=[("selected", NEON_PINK)],
                  foreground=[("selected", BG_DARK)])

        frame = tk.Frame(parent, bg=BG_DARK)
        frame.pack(fill="both", expand=True)

        tv = ttk.Treeview(frame, columns=cols, show="headings",
                          style="Cyber.Treeview")
        for col in cols:
            tv.heading(col, text=col)
            tv.column(col, width=120, anchor="w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return tv

    # ── ACCIONES ────────────────────────────────
    def run_compiler(self):
        code = self.editor.get("1.0", "end-1c")
        if not code.strip():
            return

        self.status_lbl.config(text=" COMPILANDO...", fg=NEON_YELL)
        self.root.update()

        tokens_list, ast_text, syms, errors = compile_code(code)

        # llenar tokens
        self.token_tree.delete(*self.token_tree.get_children())
        for i, (tipo, valor, linea) in enumerate(tokens_list):
            tag = "even" if i % 2 == 0 else "odd"
            self.token_tree.insert("", "end", values=(tipo, valor, linea), tags=(tag,))
        self.token_tree.tag_configure("even", background=BG_PANEL)
        self.token_tree.tag_configure("odd",  background=BG_EDITOR)

        # llenar ast
        self.ast_text.config(state="normal")
        self.ast_text.delete("1.0", "end")
        self.ast_text.insert("1.0", ast_text)
        self.ast_text.config(state="disabled")

        # llenar símbolos
        self.sym_tree.delete(*self.sym_tree.get_children())
        for i, s in enumerate(syms):
            tag = "even" if i % 2 == 0 else "odd"
            self.sym_tree.insert("", "end",
                values=(s['nombre'], s['tipo'], str(s['valor']), s['linea']),
                tags=(tag,))
        self.sym_tree.tag_configure("even", background=BG_PANEL)
        self.sym_tree.tag_configure("odd",  background=BG_EDITOR)

        # llenar errores
        self.err_tree.delete(*self.err_tree.get_children())
        for i, e in enumerate(errors):
            tag = "err"
            self.err_tree.insert("", "end",
                values=(e['tipo'], e['linea'], e['columna'], e['descripcion']),
                tags=(tag,))
        self.err_tree.tag_configure("err", foreground=NEON_PINK)

        # status
        if errors:
            self.status_lbl.config(
                text=f"● {len(errors)} ERROR(ES)", fg=NEON_PINK)
            self.nb.select(self.tab_err)
        else:
            self.status_lbl.config(text=" SIN ERRORES", fg=NEON_GREEN)
            self.nb.select(self.tab_tokens)

    def clear_results(self):
        self.token_tree.delete(*self.token_tree.get_children())
        self.sym_tree.delete(*self.sym_tree.get_children())
        self.err_tree.delete(*self.err_tree.get_children())
        self.ast_text.config(state="normal")
        self.ast_text.delete("1.0", "end")
        self.ast_text.config(state="disabled")
        self.status_lbl.config(text="LISTO", fg=NEON_GREEN)

    def clear_all(self):
        self.editor.delete("1.0", "end")
        self.token_tree.delete(*self.token_tree.get_children())
        self.sym_tree.delete(*self.sym_tree.get_children())
        self.err_tree.delete(*self.err_tree.get_children())
        self.ast_text.config(state="normal")
        self.ast_text.delete("1.0", "end")
        self.ast_text.config(state="disabled")
        self.status_lbl.config(text="LISTO", fg=NEON_GREEN)

#main
if __name__ == "__main__":
    root = tk.Tk()
    app = NetRunnerIDE(root)
    root.mainloop()