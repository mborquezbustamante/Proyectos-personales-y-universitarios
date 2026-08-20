import tkinter as tk
import sys
import io
from tkinter import messagebox
from graphviz import Digraph
from PIL import Image, ImageTk

# ====== LÓGICA ======
try:
    # ER / AFND
    from ER_AFND import ( convertir_ER_a_AFND, mostrar_afnd_formato_proyecto)
    # AFND → AFD + reporte + simulación
    from AFND_AFD import (afnd_a_afd,  mostrar_afd_formato_proyecto, buscar_ocurrencias as _reporte_ocurrencias, simular_afd_generador,)
    # Validador ER
    from Introducir_ER import introducir_er
    
except ImportError as e:
    print("-" * 50)
    print("FATAL ERROR: No se pudieron importar los módulos de lógica.")
    print(f"Detalle del error: {e}")
    print("-" * 50)
    sys.exit(1)

# ====== RENDER (Graphviz) ======
class AutomataApp:
    def __init__(self, master):
        self.master = master
        master.title("Proyecto Teoría de la Computación")

        # Estado de app
        self.afnd = None
        self.afd = None
        self.er_actual = ""

        # Estado interno de simulación
        self._sim_gen = None
        self._sim_running = False
        self._sim_after_id = None
        self._sim_last_edge = None  # (from,to)
        self._sim_curr_state = None

        # --- Layout base ---
        self.panel_control = tk.Frame(master, padx=10, pady=10, relief=tk.RAISED, bd=2)
        self.panel_control.pack(side=tk.TOP, fill=tk.X)

        self.panel_principal = tk.Frame(master, padx=10, pady=5)
        self.panel_principal.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.panel_entrada_salida = tk.Frame(self.panel_principal)
        self.panel_entrada_salida.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.panel_visual = tk.Frame(self.panel_principal, bg='#e0e0e0', relief=tk.SUNKEN)
        self.panel_visual.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Controles ---
        tk.Label(self.panel_control, text="ER:").grid(row=0, column=0, sticky="w")
        self.er_entry = tk.Entry(self.panel_control, width=20)
        self.er_entry.grid(row=0, column=1, padx=5)
        self.er_entry.insert(0, "a.b|c*")  # demo

        self.btn_er_afnd = tk.Button(self.panel_control, text="ER → AFND", command=self.convertir_a_afnd)
        self.btn_er_afnd.grid(row=0, column=2, padx=5)

        self.btn_afnd_afd = tk.Button(self.panel_control, text="AFND → AFD", command=self.convertir_a_afd, state=tk.DISABLED)
        self.btn_afnd_afd.grid(row=0, column=3, padx=5)

        self.btn_buscar = tk.Button(self.panel_control, text="Buscar Ocurrencias", command=self.buscar_ocurrencias, state=tk.DISABLED)
        self.btn_buscar.grid(row=0, column=4, padx=5)

        # Botones de simulación
        self.btn_simular = tk.Button(self.panel_control, text="Simular ▶", command=self.simular_play, state=tk.DISABLED)
        self.btn_simular.grid(row=0, column=5, padx=5)

        self.btn_pausa = tk.Button(self.panel_control, text="Pausa ⏸", command=self.simular_pause, state=tk.DISABLED)
        self.btn_pausa.grid(row=0, column=6, padx=5)

        self.btn_paso = tk.Button(self.panel_control, text="Paso ▷", command=self.simular_step, state=tk.DISABLED)
        self.btn_paso.grid(row=0, column=7, padx=5)

        # Entrada de texto
        tk.Label(self.panel_entrada_salida, text="Introducir el texto donde buscar las ocurrencias:")
        tk.Label(self.panel_entrada_salida, text="Introducir el texto donde buscar las ocurrencias:").pack(side=tk.TOP, anchor="w", pady=(0, 3))
        self.texto_input = tk.Text(self.panel_entrada_salida, height=8, width=55)
        self.texto_input.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        self.texto_input.insert(tk.END, "aaabababbbbb-\nbbbcba-\nbabc")

        # Salida del programa
        tk.Label(self.panel_entrada_salida, text="Salida del Programa (Historial de pasos):").pack(side=tk.TOP, anchor="w", pady=(0, 3))
        self.salida_texto = tk.Text(self.panel_entrada_salida, height=15, width=55, state=tk.DISABLED, bg="#f8f8f8")
        self.salida_texto.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Área de visualización: Canvas
        tk.Label(self.panel_visual, text="Área de Visualización", bg='#d3d3d3', height=2, font=("Arial", 12)).pack(side=tk.TOP, fill=tk.X, ipady=10)
        self.canvas = tk.Canvas(self.panel_visual, bg='white', height=520)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Redibujo responsivo
        self._last_auto = None
        self._last_title = ""
        self.canvas.bind("<Configure>", lambda e: self._redibujar())

    # =========================
    # Helpers de salida texto
    # =========================
    def _actualizar_salida(self, contenido, append=False):
        self.salida_texto.config(state=tk.NORMAL)
        if not append:
            self.salida_texto.delete(1.0, tk.END)
        else:
            self.salida_texto.insert(tk.END, "\n")
        self.salida_texto.insert(tk.END, contenido)
        self.salida_texto.config(state=tk.DISABLED)

    def _capturar_output(self, func, *args):
        sys_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        try:
            func(*args)
            return buffer.getvalue()
        finally:
            sys.stdout = sys_stdout

    # =========================
    # Acciones
    # =========================
    def convertir_a_afnd(self):
        er_bruta = self.er_entry.get()
        self.afnd = None
        self.afd = None
        try:
            # validar
            self.er_actual = introducir_er(er_bruta)
            # ER → AFND y rizo de búsqueda flotante
            afnd_base = convertir_ER_a_AFND(self.er_actual)
            self.afnd = afnd_base

            # limpiar simulación
            self._sim_reset()

            # limpiar salida y escribir solo AFND
            self._actualizar_salida("", append=False)
            output_afnd = self._capturar_output(mostrar_afnd_formato_proyecto, self.afnd)
            self._actualizar_salida(f"--- 1. ER Válida: {self.er_actual} ---\n--- AFND CONSTRUIDO ---\n", append=False)
            self._actualizar_salida(output_afnd, append=True)

            # habilitar siguiente paso
            self.btn_afnd_afd.config(state=tk.NORMAL)
            self.btn_buscar.config(state=tk.DISABLED)
            self.btn_simular.config(state=tk.DISABLED)
            self.btn_pausa.config(state=tk.DISABLED)
            self.btn_paso.config(state=tk.DISABLED)

            # dibujar AFND
            self._dibujar_automata(self.afnd, f"AFND de '{self.er_actual}'")

        except ValueError as e:
            msg = f"Error de Validación/Conversión:\n{e}"
            self._actualizar_salida(msg, append=False)
            messagebox.showerror("Error", str(e))
        except Exception as e:
            msg = f"Error inesperado en ER → AFND: {type(e).__name__}: {e}"
            self._actualizar_salida(msg, append=False)
            messagebox.showerror("Error Inesperado", msg)

    def convertir_a_afd(self):
        if self.afnd is None:
            messagebox.showwarning("Advertencia", "Primero debe generar el AFND.")
            return
        try:
            self.afd = afnd_a_afd(self.afnd)

            # reset simulación
            self._sim_reset()

            # limpiar salida y escribir solo AFD
            self._actualizar_salida("", append=False)
            output_afd = self._capturar_output(mostrar_afd_formato_proyecto, self.afd)
            self._actualizar_salida("--- 2. AFND → AFD COMPLETADO ---\n", append=False)
            self._actualizar_salida(output_afd, append=True)

            self.btn_buscar.config(state=tk.NORMAL)
            # habilitar simulación
            self.btn_simular.config(state=tk.NORMAL)
            self.btn_pausa.config(state=tk.NORMAL)
            self.btn_paso.config(state=tk.NORMAL)

            # dibujar AFD
            self._dibujar_automata(self.afd, f"AFD de '{self.er_actual}'")

        except Exception as e:
            msg = f"Error en la conversión AFND → AFD: {type(e).__name__}: {e}"
            self._actualizar_salida(msg, append=False)
            messagebox.showerror("Error de Conversión", msg)
            self.afd = None

    def buscar_ocurrencias(self):
        if self.afd is None:
            messagebox.showwarning("Advertencia", "Primero debe generar el AFD.")
            return
        texto = self.texto_input.get(1.0, tk.END)
        try:
            # limpiar y mostrar solo el reporte
            self._actualizar_salida("", append=False)
            output_rep = self._capturar_output(_reporte_ocurrencias, self.afd, texto)
            self._actualizar_salida("--- 3. REPORTE DE OCURRENCIAS ---\n", append=False)
            self._actualizar_salida(output_rep, append=True)

            # opcional: mantener dibujo del AFD activo
            self._dibujar_automata(self.afd, "AFD activo para búsqueda")

        except Exception as e:
            msg = f"Error durante la búsqueda de ocurrencias: {type(e).__name__}: {e}"
            self._actualizar_salida(msg, append=False)
            messagebox.showerror("Error de Búsqueda", msg)

    # =========================
    # Render estilo Graphviz con resaltado
    # =========================
    def _es_sumidero(self, estado):
        if hasattr(estado, "es_sumidero") and getattr(estado, "es_sumidero"):
            return True
        if not estado.transiciones:
            return False
        for _, dests in estado.transiciones.items():
            if len(dests) != 1:
                return False
            if next(iter(dests)) is not estado:
                return False
        return True

    def _clear_canvas(self, titulo=""):
        self.canvas.delete("all")
        if titulo:
            self.canvas.create_text(16, 16, anchor="nw", text=titulo, font=("Arial", 12, "bold"))

    def _build_graphviz(self, automata, titulo, highlight_state=None, highlight_edge=None):
        dot = Digraph(comment=titulo)
        dot.graph_attr.update({
            "rankdir": "LR",
            "splines": "true",
            "concentrate": "false",
            "nodesep": "0.55",
            "ranksep": "0.7",
            "dpi": "180"
        })
        dot.node_attr.update({
            "shape": "circle",
            "fontsize": "12",
            "fontname": "Arial",
            "width": "0.7",
            "height": "0.7",
            "fixedsize": "true"
        })
        dot.edge_attr.update({
            "fontname": "Arial",
            "fontsize": "11",
            "arrowsize": "0.9",
            "penwidth": "1.6"
        })

        # nodo de inicio
        start_id = "__start__"
        dot.node(start_id, shape="point", width="0.06", label="", color="black")

        # nodos
        for e in automata.estados:
            attrs = {}
            if e in automata.estados_aceptacion:
                attrs["shape"] = "doublecircle"
            if self._es_sumidero(e):
                attrs["style"] = "filled"
                attrs["fillcolor"] = "lightgray"
            if highlight_state and e.nombre == highlight_state:
                attrs["style"] = "filled"
                attrs["fillcolor"] = "khaki"
            dot.node(e.nombre, **attrs)

        # flecha de inicio
        if automata.estado_inicial:
            dot.edge(start_id, automata.estado_inicial.nombre)

        # transiciones
        for e in automata.estados:
            for simb, dests in e.transiciones.items():
                label = "ε" if simb == "" else str(simb)
                for d in dests:
                    eattrs = {}
                    if highlight_edge and (e.nombre, d.nombre) == highlight_edge:
                        eattrs["penwidth"] = "3.0"
                        eattrs["color"] = "red"
                    dot.edge(e.nombre, d.nombre, label=label, **eattrs)

        return dot

    def _render_to_canvas(self, dot, titulo):
        png_bytes = dot.pipe(format="png")  # render en memoria
        img = Image.open(io.BytesIO(png_bytes))
        # fit al canvas
        cw = max(self.canvas.winfo_width(), 200)
        ch = max(self.canvas.winfo_height(), 200)
        img.thumbnail((cw - 20, ch - 50), Image.LANCZOS)
        self._imgtk = ImageTk.PhotoImage(img)  # mantener referencia
        self._clear_canvas(titulo)
        self.canvas.create_image(10, 36, anchor="nw", image=self._imgtk)

    def _dibujar_automata(self, automata, titulo="", highlight_state=None, highlight_edge=None):
        if automata is None or automata.estado_inicial is None:
            self._clear_canvas("Sin autómata para visualizar")
            self._last_auto, self._last_title = None, ""
            return
        self._last_auto, self._last_title = automata, titulo
        dot = self._build_graphviz(automata, titulo, highlight_state, highlight_edge)
        self._render_to_canvas(dot, titulo)

    def _redibujar(self):
        if self._last_auto is None:
            return
        dot = self._build_graphviz(self._last_auto, self._last_title, self._sim_curr_state, self._sim_last_edge)
        self._render_to_canvas(dot, self._last_title)

    # =========================
    # Controlador de simulación
    # =========================
    def _sim_reset(self):
        self._sim_gen = None
        self._sim_running = False
        self._sim_last_edge = None
        self._sim_curr_state = None
        if self._sim_after_id:
            self.master.after_cancel(self._sim_after_id)
            self._sim_after_id = None

    def _sim_next_event(self):
        if self._sim_gen is None:
            texto = self.texto_input.get(1.0, tk.END)
            self._sim_gen = simular_afd_generador(self.afd, texto)
        try:
            ev = next(self._sim_gen)
        except StopIteration:
            self._actualizar_salida("Simulación completada.", append=True)
            self._sim_running = False
            return None
        return ev

    def _sim_apply_event(self, ev):
        et = ev["evento"]
        if et == "nueva_linea":
            self._actualizar_salida(f"[Línea {ev['linea']}] \"{ev['texto']}\"", append=True)
            self._sim_curr_state = self.afd.estado_inicial.nombre if self.afd and self.afd.estado_inicial else None
            self._sim_last_edge = None
            self._dibujar_automata(self.afd, f"AFD – Línea {ev['linea']}", self._sim_curr_state, self._sim_last_edge)
        elif et == "nuevo_inicio":
            self._actualizar_salida(f"↳ Inicio en posición {ev['i']}", append=True)
            self._sim_curr_state = self.afd.estado_inicial.nombre
            self._sim_last_edge = None
            self._dibujar_automata(self.afd, f"AFD – inicio {ev['i']}", self._sim_curr_state, None)
        elif et == "transicion":
            q_from = ev["q_from"]
            q_to = ev["q_to"]
            simb = ev["simbolo"]
            if q_to is None:
                self._actualizar_salida(f"  ({q_from}, '{simb}') → ∅  [corte]", append=True)
                self._sim_last_edge = None
            else:
                self._actualizar_salida(f"  ({q_from}, '{simb}') → {q_to}", append=True)
                self._sim_curr_state = q_to
                self._sim_last_edge = (q_from, q_to)
            self._dibujar_automata(self.afd, f"AFD – '{simb}'", self._sim_curr_state, self._sim_last_edge)
        elif et == "aceptacion":
            self._actualizar_salida(f"  ✓ ACEPTA hasta pos {ev['j']}", append=True)
        elif et == "fin_inicio":
            self._actualizar_salida(f"  Fin inicio → {ev['resultado']}", append=True)
        elif et == "fin_linea":
            self._actualizar_salida(f"[Fin línea {ev['linea']}]", append=True)

    def simular_play(self):
        if self.afd is None:
            messagebox.showwarning("Advertencia", "Primero genere el AFD.")
            return
        if not self._sim_running:
            self._sim_running = True
            self._sim_loop()

    def _sim_loop(self):
        if not self._sim_running:
            return
        ev = self._sim_next_event()
        if ev is not None:
            self._sim_apply_event(ev)
            # Velocidad: 250 ms por paso
            self._sim_after_id = self.master.after(250, self._sim_loop)
        else:
            self._sim_running = False

    def simular_pause(self):
        self._sim_running = False
        if self._sim_after_id:
            self.master.after_cancel(self._sim_after_id)
            self._sim_after_id = None

    def simular_step(self):
        if self.afd is None:
            messagebox.showwarning("Advertencia", "Primero genere el AFD.")
            return
        if self._sim_running:
            return
        if self._sim_gen is None:
            texto = self.texto_input.get(1.0, tk.END)
            self._sim_gen = simular_afd_generador(self.afd, texto)
        ev = self._sim_next_event()
        if ev is not None:
            self._sim_apply_event(ev)
        else:
            self._sim_reset()


if __name__ == '__main__':
    root = tk.Tk()
    app = AutomataApp(root)
    root.mainloop()
