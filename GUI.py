import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import io
import re

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

        btn_err_frame = tk.Frame(self.tab_err, bg=BG_DARK, pady=6)
        btn_err_frame.pack(fill="x", padx=8)

        tk.Button(
            btn_err_frame, text="🔍 DETALLES DEL ERROR",
            font=("Courier New", 10, "bold"),
            bg=NEON_YELL, fg=BG_DARK,
            activebackground="#fff176", activeforeground=BG_DARK,
            relief="flat", padx=14, pady=6, cursor="hand2",
            command=self.show_error_details
        ).pack(side="left", padx=(0, 8))

    def _make_treeview(self, parent, cols):
        style = ttk.Style()
        style.configure("Cyber.Treeview",
                        background=BG_PANEL, foreground=TEXT_WHITE,
                        fieldbackground=BG_PANEL, rowheight=28,
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
            # Columna Descripción mucho más ancha; el resto estándar
            if col == "Descripción":
                tv.column(col, width=500, minwidth=300, anchor="w")
            elif col in ("Línea", "Col"):
                tv.column(col, width=70, minwidth=50, anchor="center")
            else:
                tv.column(col, width=110, minwidth=80, anchor="w")

        # Scrollbar vertical
        sb_y = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb_y.set)
        # Scrollbar horizontal
        sb_x = ttk.Scrollbar(frame, orient="horizontal", command=tv.xview)
        tv.configure(xscrollcommand=sb_x.set)

        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        tv.pack(side="left", fill="both", expand=True)
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

        # llenar errores — deduplicar primero (el lexer corre 2 veces internamente)
        self.err_tree.delete(*self.err_tree.get_children())
        seen_errors = set()
        unique_errors = []
        for e in errors:
            key = (e['tipo'], str(e['linea']), str(e['columna']), e['descripcion'])
            if key not in seen_errors:
                seen_errors.add(key)
                unique_errors.append(e)

        for i, e in enumerate(unique_errors):
            self.err_tree.insert("", "end",
                values=(e['tipo'], e['linea'], e['columna'], e['descripcion']),
                tags=("err",))
        self.err_tree.tag_configure("err", foreground=NEON_PINK)

        # Resaltar líneas con error en el editor
        self.editor.tag_remove("error_line", "1.0", "end")
        if unique_errors:
            self.editor.tag_configure("error_line",
                                      background="#3a0010",
                                      foreground=NEON_PINK,
                                      underline=True)
            for e in unique_errors:
                try:
                    ln = int(e['linea'])
                    desc_lower = e['descripcion'].lower()
                    # Para errores sintácticos de token inesperado, el parser
                    # reporta la línea del token siguiente al error real.
                    # El error real (;  faltante) está en la línea anterior.
                    if e['tipo'] == 'Sintáctico' and 'token inesperado' in desc_lower:
                        real_ln = max(1, ln - 1)
                        self.editor.tag_add("error_line", f"{real_ln}.0", f"{real_ln}.end")
                    else:
                        self.editor.tag_add("error_line", f"{ln}.0", f"{ln}.end")
                except (ValueError, TypeError):
                    pass

        # status
        if unique_errors:
            self.status_lbl.config(
                text=f"● {len(unique_errors)} ERROR(ES)", fg=NEON_PINK)
            self.nb.select(self.tab_err)
        else:
            self.editor.tag_remove("error_line", "1.0", "end")
            self.status_lbl.config(text=" SIN ERRORES", fg=NEON_GREEN)
            self.nb.select(self.tab_tokens)


    # ── ERROR DETAILS ────────────────────────────
    def _get_error_explanation(self, tipo, descripcion):
        desc = descripcion.lower()

        if tipo == "Lexico":
            parts = descripcion.split()
            char = parts[-1] if parts else "?"
            return (
                f"El carácter '{char}' no pertenece al alfabeto de CyberCode.\n"
                "El lexer no puede convertirlo en un token válido.",
                f"Elimina o reemplaza el carácter '{char}'.\n"
                "CyberCode solo acepta letras, dígitos y operadores como:\n"
                "  :=  ;  ()  {}  +  -  *  /  %  ==  !=  <  >  <=  >="
            )

        if tipo == "Sintáctico":
            if "fin de archivo" in desc:
                return (
                    "El código terminó antes de lo esperado.\n"
                    "Probablemente falta cerrar un bloque con 'shutdown', '}' o ';'.",
                    "Asegúrate de que el programa inicie con 'init' y cierre con 'shutdown'.\n"
                    "Verifica que cada bloque {} esté correctamente cerrado."
                )
            tok = descripcion.split("'")[1] if "'" in descripcion else "desconocido"
            return (
                f"El parser encontró '{tok}' cuando esperaba otra cosa.\n"
                "⚠ IMPORTANTE: el error real está en la línea ANTERIOR a la indicada.\n"
                "El parser solo detecta el problema cuando ve el siguiente token inesperado.",
                f"Revisa la línea ANTERIOR a la señalada buscando:\n"
                f"  • ';' faltante al final de esa línea (causa más común)\n"
                "  • Paréntesis o llaves sin cerrar en esa línea\n"
                "  • Una declaración incompleta (falta valor, operador, etc.)\n"
                f"  Ejemplo: 'jack vida := 50' sin ';' al final → el parser\n"
                f"  falla cuando ve '{tok}' en la línea siguiente."
            )

        if tipo == "Sistema":
            return (
                "Error al cargar los módulos del compilador.",
                "Instala PLY con:  pip install ply\n"
                "y asegúrate de que Lexer.py y Parser.py estén en el mismo directorio."
            )

        return ("Error desconocido.", "Revisa el código manualmente.")

    def show_error_details(self):
        # Recopilar TODOS los errores de la tabla (no requiere selección)
        all_items = self.err_tree.get_children()
        if not all_items:
            messagebox.showinfo("Sin errores",
                                "No hay errores registrados en la tabla.\n"
                                "Compila primero tu código.")
            return

        errors_data = []
        for item in all_items:
            vals = self.err_tree.item(item, "values")
            if vals and len(vals) >= 4:
                errors_data.append(vals)

        win = tk.Toplevel(self.root)
        win.title(f"Detalles de Errores ({len(errors_data)}) — CyberCode")
        win.configure(bg=BG_DARK)
        win.geometry("1020x760")
        win.minsize(800, 550)
        win.resizable(True, True)
        win.grab_set()

        # Header
        hdr = tk.Frame(win, bg=NEON_PINK, pady=6)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"⚠  ANÁLISIS DE ERRORES  ({len(errors_data)} encontrado{'s' if len(errors_data) != 1 else ''})",
                 font=("Courier New", 12, "bold"),
                 fg=BG_DARK, bg=NEON_PINK).pack()

        # Canvas scrollable para mostrar todos los errores
        canvas = tk.Canvas(win, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        scroll_frame = tk.Frame(canvas, bg=BG_DARK)
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _on_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_resize)

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scroll_frame.bind("<Configure>", _on_frame_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def section(parent, label, value, fg=TEXT_WHITE):
            """Crea un bloque label + contenido con Text auto-ajustable."""
            tk.Label(parent, text=label,
                     font=("Courier New", 9, "bold"),
                     fg=NEON_CYAN, bg=BG_DARK, anchor="w").pack(fill="x", pady=(8, 0))
            tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")
            # Text widget: se ajusta al ancho real, nunca corta el texto
            num_lines = value.count("\n") + 1
            txt = tk.Text(parent,
                          font=("Courier New", 10),
                          fg=fg, bg=BG_PANEL,
                          height=num_lines,
                          wrap="word",
                          relief="flat", bd=0,
                          padx=14, pady=10,
                          cursor="arrow",
                          state="normal")
            txt.insert("1.0", value)
            txt.config(state="disabled")
            txt.pack(fill="x", pady=(2, 6))

        for idx, (tipo, linea, col, desc) in enumerate(errors_data):
            causa, solucion = self._get_error_explanation(tipo, desc)

            # Para errores sintácticos de token inesperado, la línea real del
            # problema es la anterior a la reportada por el parser.
            if tipo == "Sintáctico" and "token inesperado" in desc.lower():
                try:
                    linea_real = max(1, int(linea) - 1)
                    ubicacion_str = (f"Línea {linea_real}  ← ERROR REAL  "
                                     f"(parser reportó línea {linea}, col {col})")
                except (ValueError, TypeError):
                    ubicacion_str = f"Línea {linea}  |  Columna {col}"
            else:
                ubicacion_str = f"Línea {linea}  |  Columna {col}"

            card = tk.Frame(scroll_frame, bg=BG_PANEL,
                            highlightbackground=NEON_PINK, highlightthickness=1)
            card.pack(fill="x", padx=14, pady=8)

            # Número de error
            tk.Label(card, text=f"  ERROR #{idx + 1}",
                     font=("Courier New", 10, "bold"),
                     fg=NEON_PINK, bg=BG_PANEL, anchor="w").pack(fill="x", pady=(6, 2))

            inner = tk.Frame(card, bg=BG_DARK, padx=10, pady=6)
            inner.pack(fill="x")

            section(inner, "TIPO", tipo, fg=NEON_PINK)
            section(inner, "UBICACIÓN", ubicacion_str)

            section(inner, "DESCRIPCIÓN", desc)
            section(inner, "CAUSA", causa)
            section(inner, "✅ SOLUCIÓN SUGERIDA", solucion, fg=NEON_GREEN)

        # Botón barra inferior
        btn_bar = tk.Frame(win, bg=BG_DARK)
        btn_bar.pack(pady=10, side="bottom", fill="x", padx=20)

        tk.Button(btn_bar, text="⚡ ARREGLAR",
                  font=("Courier New", 10, "bold"),
                  bg=NEON_GREEN, fg=BG_DARK,
                  activebackground="#80ff60", activeforeground=BG_DARK,
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  command=lambda: [canvas.unbind_all("<MouseWheel>"),
                                   win.destroy(),
                                   self.auto_fix_code()]
                  ).pack(side="left", padx=(0, 8))

        tk.Button(btn_bar, text="CERRAR",
                  font=("Courier New", 10, "bold"),
                  bg=BG_PANEL, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  command=lambda: [canvas.unbind_all("<MouseWheel>"), win.destroy()]
                  ).pack(side="left")


    # ── AUTO-FIX ─────────────────────────────────
    def auto_fix_code(self):
        code = self.editor.get("1.0", "end-1c")
        if not code.strip():
            messagebox.showinfo("Editor vacío", "No hay código que corregir.")
            return

        fixes_applied = []

        # ── PASO 1: Eliminar caracteres fuera del alfabeto CyberCode PRIMERO ──
        # (debe ir antes de init/shutdown para que 'shutdown.' no falle la detección)
        valid_chars_pat = re.compile(r'[^a-zA-Z0-9_\s\+\-\*\/%=!<>:()\{\},;"\\]')
        invalid_found = valid_chars_pat.findall(code)
        if invalid_found:
            unique_bad = list(dict.fromkeys(invalid_found))
            code = valid_chars_pat.sub('', code)
            for ch in unique_bad:
                fixes_applied.append(f"• Carácter inválido eliminado: '{ch}'")

        # ── PASO 2: Comillas tipográficas → estándar ──
        for bad in ["\u2018", "\u2019", "\u201c", "\u201d"]:
            if bad in code:
                code = code.replace(bad, '"')
                fixes_applied.append("• Comilla tipográfica reemplazada por comilla estándar.")

        # ── PASO 3: Agregar 'init' si falta ──
        if not code.strip().startswith("init"):
            code = "init\n" + code
            fixes_applied.append("• Se agregó 'init' al inicio del programa.")

        # ── PASO 4: Agregar 'shutdown' si falta ──
        # Ahora que los chars inválidos ya se quitaron, la detección funciona bien
        last_line = code.strip().split("\n")[-1].strip()
        if last_line != "shutdown":
            code = code.rstrip() + "\nshutdown"
            fixes_applied.append("• Se agregó 'shutdown' al final del programa.")

        # ── PASO 5: Añadir ';' faltante en sentencias simples ──
        stmt_pat = re.compile(
            r'^(\s*)(jack|chrome|glitch|flatline)\s+\w+\s*:=.+[^;{}\s]$'
            r'|^(\s*)\w+\s*:=.+[^;{}\s]$'
            r'|^(\s*)(transmit|input)\s*\(.*\)\s*$'
            r'|^(\s*)return\s+.+[^;{}\s]$'
        )
        lines = code.split("\n")
        new_lines = []
        for ln in lines:
            s = ln.rstrip()
            if stmt_pat.match(s) and not s.endswith(";"):
                new_lines.append(s + ";")
                fixes_applied.append(f"• ';' añadido en: {s.strip()[:45]}")
            else:
                new_lines.append(ln)
        code = "\n".join(new_lines)

        if not fixes_applied:
            messagebox.showinfo("Sin cambios automáticos",
                "No se detectaron errores que se puedan corregir automáticamente.\n"
                "Usa '🔍 DETALLES DEL ERROR' para ver sugerencias manuales.")
            return

        resumen = "\n".join(dict.fromkeys(fixes_applied))
        if messagebox.askyesno("⚡ SOLUCIONADOR",
                               f"Correcciones detectadas:\n\n{resumen}\n\n"
                               "¿Aplicar correcciones y limpiar errores?"):
            # Aplicar código corregido al editor
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", code)

            # Limpiar resaltado y tabla de errores
            self.editor.tag_remove("error_line", "1.0", "end")
            self.err_tree.delete(*self.err_tree.get_children())

            # Recompilar
            self.status_lbl.config(text="⚡ SOLUCIONANDO...", fg=NEON_YELL)
            self.root.update()
            self.run_compiler()

            # Resultado final
            remaining = self.err_tree.get_children()
            if not remaining:
                self.status_lbl.config(text="✅ ERRORES CORREGIDOS", fg=NEON_GREEN)
                messagebox.showinfo("✅ Éxito",
                    "¡Todas las correcciones se aplicaron!\n"
                    "El código compiló sin errores.")
            else:
                n = len(remaining)
                messagebox.showwarning("Corrección parcial",
                    f"Se aplicaron las correcciones automáticas.\n"
                    f"Aún quedan {n} error(es) que requieren revisión manual.\n"
                    "Usa '🔍 DETALLES DEL ERROR' para más información.")

    def clear_results(self):
        self.token_tree.delete(*self.token_tree.get_children())
        self.sym_tree.delete(*self.sym_tree.get_children())
        self.err_tree.delete(*self.err_tree.get_children())
        self.editor.tag_remove("error_line", "1.0", "end")
        self.ast_text.config(state="normal")
        self.ast_text.delete("1.0", "end")
        self.ast_text.config(state="disabled")
        self.status_lbl.config(text="LISTO", fg=NEON_GREEN)

    def clear_all(self):
        self.editor.delete("1.0", "end")
        self.token_tree.delete(*self.token_tree.get_children())
        self.sym_tree.delete(*self.sym_tree.get_children())
        self.err_tree.delete(*self.err_tree.get_children())
        self.editor.tag_remove("error_line", "1.0", "end")
        self.ast_text.config(state="normal")
        self.ast_text.delete("1.0", "end")
        self.ast_text.config(state="disabled")
        self.status_lbl.config(text="LISTO", fg=NEON_GREEN)


#main
if __name__ == "__main__":
    root = tk.Tk()
    app = NetRunnerIDE(root)
    root.mainloop()