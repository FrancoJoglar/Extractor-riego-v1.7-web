import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import sys
import os
import threading
from datetime import datetime, timedelta

# Import logic
try:
    import extract_riego
    import export_programacion
    import programar_horarios
except ImportError:
    # Handle case where script is run from wrong directory or frozen
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import extract_riego
    import export_programacion
    import programar_horarios

class RiegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Riego Extractor & Programación")
        self.root.geometry("650x600")
        
        # --- Styles ---
        self.bg_color = "#f5f5f5"
        self.root.configure(bg=self.bg_color)
        self.font_label = ("Arial", 10)
        self.font_entry = ("Arial", 10)
        self.font_btn = ("Arial", 10, "bold")

        # --- Tab Control ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Tabs
        self.tab_extract = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_program = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_maintenance = tk.Frame(self.notebook, bg=self.bg_color) # NUEVO: Tab mantenimiento
        
        self.notebook.add(self.tab_extract, text=" 1. Extractor de Excel ")
        self.notebook.add(self.tab_program, text=" 2. Exportar Programación ")
        self.notebook.add(self.tab_maintenance, text=" 3. Mantenimiento Supabase ") # NUEVO: Tab mantenimiento

        self.setup_extract_tab()
        self.setup_program_tab()
        self.setup_maintenance_tab() # NUEVO: Setup tab mantenimiento


        # --- Common Log Area ---
        tk.Label(root, text="Consola de Salida:", font=self.font_label, bg=self.bg_color).pack(anchor="w", padx=10)
        self.log_area = scrolledtext.ScrolledText(root, height=10, font=("Consolas", 9))
        self.log_area.pack(pady=5, padx=10, fill="both", expand=True)

    def setup_extract_tab(self):
        # --- Input File ---
        frame_input = tk.LabelFrame(self.tab_extract, text="Archivo de Entrada", bg=self.bg_color, font=("Arial", 9, "bold"))
        frame_input.pack(pady=10, padx=10, fill="x")
        
        self.entry_input = tk.Entry(frame_input, font=self.font_entry)
        self.entry_input.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        btn_browse_input = tk.Button(frame_input, text="Seleccionar", command=self.browse_input, font=self.font_btn)
        btn_browse_input.pack(side="right", padx=5, pady=5)

        # --- Date Input ---
        frame_date = tk.LabelFrame(self.tab_extract, text="Rango de Fechas (YYYY-MM-DD)", bg=self.bg_color, font=("Arial", 9, "bold"))
        frame_date.pack(pady=10, padx=10, fill="x")
        
        tk.Label(frame_date, text="Inicio:", font=self.font_label, bg=self.bg_color).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_date_start = tk.Entry(frame_date, font=self.font_entry, width=15)
        self.entry_date_start.grid(row=0, column=1, padx=5, pady=5)
        self.entry_date_start.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(frame_date, text="Fin (Opc):", font=self.font_label, bg=self.bg_color).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_date_end = tk.Entry(frame_date, font=self.font_entry, width=15)
        self.entry_date_end.grid(row=0, column=3, padx=5, pady=5)

        # --- Output File ---
        frame_output = tk.LabelFrame(self.tab_extract, text="Archivo de Salida", bg=self.bg_color, font=("Arial", 9, "bold"))
        frame_output.pack(pady=10, padx=10, fill="x")
        
        self.entry_output = tk.Entry(frame_output, font=self.font_entry)
        self.entry_output.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        btn_browse_output = tk.Button(frame_output, text="Guardar Como...", command=self.browse_output, font=self.font_btn)
        btn_browse_output.pack(side="right", padx=5, pady=5)

        # --- Run Buttons ---
        btn_frame = tk.Frame(self.tab_extract, bg=self.bg_color)
        btn_frame.pack(pady=15, padx=20, fill="x")

        self.btn_crear_planilla = tk.Button(btn_frame, text="📋 CREAR PLANILLA\n(Desde Planilla Maestra M3)", 
                                         command=self.start_crear_planilla_thread, 
                                         font=("Arial", 10, "bold"), bg="#2196F3", fg="white", height=3)
        self.btn_crear_planilla.pack(side="left", padx=5, fill="x", expand=True)

        self.btn_sincronizar = tk.Button(btn_frame, text="☁️ SINCRONIZAR\n(Subir a Supabase)", 
                                         command=self.start_sincronizar_thread, 
                                         font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", height=3)
        self.btn_sincronizar.pack(side="left", padx=5, fill="x", expand=True)

        # Load defaults
        self.load_defaults()

    def setup_program_tab(self):
        desc_label = tk.Label(self.tab_program, text="Extrae datos de Supabase para programar los riegos.\nSelecciona una fecha y genera/actualiza la planilla.", 
                              justify="left", font=("Arial", 10), bg=self.bg_color)
        desc_label.pack(pady=15, padx=10)

        frame_pg_date = tk.LabelFrame(self.tab_program, text="Fecha de Programación", bg=self.bg_color, font=("Arial", 9, "bold"))
        frame_pg_date.pack(pady=10, padx=10, fill="x")

        tk.Label(frame_pg_date, text="Seleccionar Fecha (DD-MM-YYYY):", font=self.font_label, bg=self.bg_color).pack(side="left", padx=5, pady=10)
        self.entry_pg_date = tk.Entry(frame_pg_date, font=self.font_entry, width=15)
        self.entry_pg_date.pack(side="left", padx=5, pady=10)
        
        manana = (datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y')
        self.entry_pg_date.insert(0, manana)

        frame_output = tk.LabelFrame(self.tab_program, text="Ruta de Exportación", bg=self.bg_color, font=("Arial", 9, "bold"))
        frame_output.pack(pady=10, padx=10, fill="x")
        
        self.entry_output_prog = tk.Entry(frame_output, font=self.font_entry)
        self.entry_output_prog.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.entry_output_prog.insert(0, os.path.join(os.getcwd(), "Planilla_Programacion.xlsx"))
        
        btn_browse_output_prog = tk.Button(frame_output, text="...", command=self.browse_output_prog, font=self.font_btn, width=5)
        btn_browse_output_prog.pack(side="right", padx=5, pady=5)

        btn_frame = tk.Frame(self.tab_program, bg=self.bg_color)
        btn_frame.pack(pady=20, padx=20, fill="x")

        self.btn_extraer_supabase = tk.Button(btn_frame, text="📥 EXTRAER DE SUPABASE\n(Para fecha seleccionada)", 
                                         command=self.start_extraer_supabase_thread, 
                                         font=("Arial", 10, "bold"), bg="#2196F3", fg="white", height=3)
        self.btn_extraer_supabase.pack(side="left", padx=5, fill="x", expand=True)

        self.btn_program_horarios = tk.Button(btn_frame, text="📅 PROGRAMAR HORARIOS\n(Con hora de inicio)", 
                                         command=self.start_program_horarios_thread, 
                                         font=("Arial", 10, "bold"), bg="#FF9800", fg="white", height=3)
        self.btn_program_horarios.pack(side="left", padx=5, fill="x", expand=True)


    def setup_maintenance_tab(self):
        # Description
        desc_label = tk.Label(self.tab_maintenance, text="⚠️ Herramientas de Limpieza de Datos ⚠️\nUse con precaución. Estas acciones son irreversibles.", 
                               justify="center", font=("Arial", 10, "bold"), fg="#d32f2f", bg=self.bg_color)
        desc_label.pack(pady=40, padx=10)

        # --- Clear Table Button ---
        btn_clear_table = tk.Button(self.tab_maintenance, text="🗑️ LIMPIAR TABLA 'RIEGOS SOLICITADOS' POR COMPLETO", 
                                         command=self.confirm_clear_supabase, 
                                         font=("Arial", 11, "bold"), bg="#f44336", fg="white", height=3)
        btn_clear_table.pack(pady=20, padx=50, fill="x")
        
        # Info text
        info_label = tk.Label(self.tab_maintenance, text="Esto borrará todos los registros que se han subido a la nube\nen la tabla de Riegos Solicitados.", 
                               justify="center", font=("Arial", 9, "italic"), bg=self.bg_color)
        info_label.pack(pady=10)

    def confirm_clear_supabase(self):
        # Doble confirmación
        resp = messagebox.askyesno("Confirmar Acción Crítica", 
                                   "¿ESTÁ SEGURO de que desea borrar TODOS los registros de 'Riegos Solicitados'?\n\nEsta acción NO se puede deshacer.")
        if resp:
            # Segunda confirmación
            resp2 = messagebox.askokcancel("Última Advertencia", 
                                           "Se procederá a vaciar la tabla en Supabase.\n¿Continuar?")
            if resp2:
                self.start_clear_thread()

    def start_clear_thread(self):
        self.log("Solicitando limpieza de tabla en Supabase...")
        threading.Thread(target=self.run_clear, daemon=True).start()

    def run_clear(self):
        try:
            def callback(msg): self.root.after(0, self.log, msg)
            extract_riego.clear_riegos_solicitados(callback)
            self.root.after(0, lambda: messagebox.showinfo("Limpieza Completada", "La tabla ha sido vaciada correctamente."))
        except Exception as e:
            self.root.after(0, self.log, f"ERROR EN LIMPIEZA: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error de Limpieza", str(e)))


    def load_defaults(self):
        base_dir = os.getcwd()
        input_dir = os.path.join(base_dir, "input")
        if os.path.exists(input_dir):
             for f in os.listdir(input_dir):
                 if f.endswith(".xlsx") and "M3 reales" in f:
                     self.entry_input.insert(0, os.path.join(input_dir, f))
                     break

    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if filename:
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, filename)
            if not self.entry_output.get():
                self.entry_output.insert(0, "riego_extracted.xlsx")

    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if filename:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, filename)

    def browse_output_prog(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], 
                                              initialfile="Planilla_Programacion.xlsx")
        if filename:
            self.entry_output_prog.delete(0, tk.END)
            self.entry_output_prog.insert(0, filename)

    def log(self, msg):
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    # --- Threading Extracts ---
    def start_crear_planilla_thread(self):
        input_path = self.entry_input.get()
        start = self.entry_date_start.get().strip()
        end = self.entry_date_end.get().strip()
        output_path = self.entry_output.get()

        if not input_path or not start or not output_path:
            messagebox.showwarning("Faltan Datos", "Completa la ruta de entrada, salida y fecha.")
            return

        date_str = f"{start}:{end}" if end else start
        
        self.btn_crear_planilla.config(state="disabled", text="Procesando...")
        self.log_area.delete(1.0, tk.END)
        self.log(f"Iniciando procesamiento para: {date_str}")
        
        threading.Thread(target=self.run_crear_planilla, args=(input_path, date_str, output_path), daemon=True).start()

    def run_crear_planilla(self, input_path, date_str, output_path):
        try:
            def callback(msg): self.root.after(0, self.log, msg)
            extract_riego.process_extraction(input_path, date_str, output_path, callback)
            self.root.after(0, lambda: messagebox.showinfo("Éxito", "Planilla procesada correctamente."))
        except Exception as e:
            self.root.after(0, self.log, f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_crear_planilla.config(state="normal", text="📋 CREAR PLANILLA\n(Desde Planilla Maestra M3)"))

    # --- Threading Extraer de Supabase (Pestaña 2) ---
    def start_extraer_supabase_thread(self):
        fecha = self.entry_pg_date.get().strip()
        if not fecha:
            messagebox.showwarning("Aviso", "Ingresa una fecha válida.")
            return

        self.btn_extraer_supabase.config(state="disabled", text="Extrayendo...")
        self.log(f"Extrayendo datos de Supabase para: {fecha}")
        
        threading.Thread(target=self.run_extraer_supabase, args=(fecha,), daemon=True).start()

    def run_extraer_supabase(self, fecha):
        try:
            output_path = self.entry_output_prog.get().strip()
            export_programacion.exportar_para_programacion(fecha, output_path)
            self.root.after(0, self.log, "Datos extraídos con éxito.")
        except Exception as e:
            self.root.after(0, self.log, f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_extraer_supabase.config(state="normal", text="📥 EXTRAER DE SUPABASE\n(Para fecha seleccionada)"))

    # --- Threading Programar Horarios ---
    def start_program_horarios_thread(self):
        fecha = self.entry_pg_date.get().strip()
        output_path = self.entry_output_prog.get().strip()
        
        if not fecha:
            messagebox.showwarning("Aviso", "Ingresa una fecha válida.")
            return

        self.btn_program_horarios.config(state="disabled", text="Programando...")
        self.log(f"Programando horarios para: {fecha}")
        
        threading.Thread(target=self.run_program_horarios, args=(fecha, output_path), daemon=True).start()

    def run_program_horarios(self, fecha, output_path):
        try:
            programar_horarios.programar_horarios(fecha, output_path)
            self.root.after(0, self.log, "Programación con horarios generada con éxito.")
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self.log, f"ERROR PROGRAMAR: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.root.after(0, lambda: self.btn_program_horarios.config(state="normal", text="📅 PROGRAMAR HORARIOS DE INICIO"))

    # --- Threading Sincronizar ---
    def start_sincronizar_thread(self):
        fecha = self.entry_pg_date.get().strip()
        if not fecha:
            messagebox.showwarning("Aviso", "Ingresa una fecha válida.")
            return

        self.btn_sincronizar.config(state="disabled", text="Sincronizando...")
        self.log(f"Sincronizando datos con Supabase para: {fecha}")
        
        threading.Thread(target=self.run_sincronizar, args=(fecha,), daemon=True).start()

    def run_sincronizar(self, fecha):
        try:
            export_programacion.sincronizar_a_supabase(fecha)
            self.root.after(0, self.log, "Sincronización completada con éxito.")
        except Exception as e:
            self.root.after(0, self.log, f"ERROR SINCRONIZAR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_sincronizar.config(state="normal", text="☁️ SINCRONIZAR\n(Subir a Supabase)"))

if __name__ == "__main__":
    root = tk.Tk()
    # Estilo para tabs
    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[10, 5])
    
    app = RiegoApp(root)
    root.mainloop()
