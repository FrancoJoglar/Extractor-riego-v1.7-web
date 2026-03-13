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

        # --- Run Button ---
        self.btn_run_extract = tk.Button(self.tab_extract, text="NUBE ☁️ -> SUBIR DATOS A SUPABASE", 
                                        command=self.start_extraction_thread, 
                                        font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", height=2)
        self.btn_run_extract.pack(pady=15, padx=20, fill="x")

        # Load defaults
        self.load_defaults()

    def setup_program_tab(self):
        # Description
        desc_label = tk.Label(self.tab_program, text="Genera la planilla para programar los riegos de mañana.\nLos datos se obtienen directamente de Supabase.", 
                              justify="left", font=("Arial", 10), bg=self.bg_color)
        desc_label.pack(pady=15, padx=10)

        # --- Date Filter ---
        frame_pg_date = tk.LabelFrame(self.tab_program, text="Fecha de Programación", bg=self.bg_color, font=("Arial", 9, "bold"))
        frame_pg_date.pack(pady=10, padx=10, fill="x")

        tk.Label(frame_pg_date, text="Seleccionar Fecha (DD-MM-YYYY):", font=self.font_label, bg=self.bg_color).pack(side="left", padx=5, pady=10)
        self.entry_pg_date = tk.Entry(frame_pg_date, font=self.font_entry, width=15)
        self.entry_pg_date.pack(side="left", padx=5, pady=10)
        
        # Por defecto mañana
        manana = (datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y')
        self.entry_pg_date.insert(0, manana)

        # --- Output Path for Programmed Schedule ---
        frame_output = tk.LabelFrame(self.tab_program, text="Ruta de Exportación (Programación con Horarios)", bg=self.bg_color, font=("Arial", 9, "bold"))
        frame_output.pack(pady=10, padx=10, fill="x")
        
        self.entry_output_horarios = tk.Entry(frame_output, font=self.font_entry)
        self.entry_output_horarios.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.entry_output_horarios.insert(0, os.path.join(os.getcwd(), "Planilla_Programacion_Horarios.xlsx"))
        
        btn_browse_output_horarios = tk.Button(frame_output, text="...", command=self.browse_output_horarios, font=self.font_btn, width=5)
        btn_browse_output_horarios.pack(side="right", padx=5, pady=5)

        # --- Run Buttons ---
        self.btn_run_program = tk.Button(self.tab_program, text="GENERAR PLANILLA DE PROGRAMACIÓN (EXCEL)", 
                                         command=self.start_program_thread, 
                                         font=("Arial", 11, "bold"), bg="#2196F3", fg="white", height=2)
        self.btn_run_program.pack(pady=15, padx=20, fill="x")

        self.btn_program_horarios = tk.Button(self.tab_program, text="📅 PROGRAMAR HORARIOS DE INICIO", 
                                         command=self.start_program_horarios_thread, 
                                         font=("Arial", 11, "bold"), bg="#FF9800", fg="white", height=2)
        self.btn_program_horarios.pack(pady=15, padx=20, fill="x")


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

    def browse_output_horarios(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], 
                                              initialfile="Planilla_Programacion_Horarios.xlsx")
        if filename:
            self.entry_output_horarios.delete(0, tk.END)
            self.entry_output_horarios.insert(0, filename)

    def log(self, msg):
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    # --- Threading Extracts ---
    def start_extraction_thread(self):
        input_path = self.entry_input.get()
        start = self.entry_date_start.get().strip()
        end = self.entry_date_end.get().strip()
        output_path = self.entry_output.get()

        if not input_path or not start or not output_path:
            messagebox.showwarning("Faltan Datos", "Completa la ruta de entrada, salida y fecha.")
            return

        date_str = f"{start}:{end}" if end else start
        
        self.btn_run_extract.config(state="disabled", text="Procesando...")
        self.log_area.delete(1.0, tk.END)
        self.log(f"Iniciando extracción para: {date_str}")
        
        threading.Thread(target=self.run_extraction, args=(input_path, date_str, output_path), daemon=True).start()

    def run_extraction(self, input_path, date_str, output_path):
        try:
            def callback(msg): self.root.after(0, self.log, msg)
            extract_riego.process_extraction(input_path, date_str, output_path, callback)
            self.root.after(0, lambda: messagebox.showinfo("Éxito", "Extracción y subida completada."))
        except Exception as e:
            self.root.after(0, self.log, f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_run_extract.config(state="normal", text="NUBE ☁️ -> SUBIR DATOS A SUPABASE"))

    # --- Threading Programming ---
    def start_program_thread(self):
        fecha = self.entry_pg_date.get().strip()
        if not fecha:
            messagebox.showwarning("Aviso", "Ingresa una fecha válida.")
            return

        # Redirigir print a la log_area
        self.btn_run_program.config(state="disabled", text="Exportando...")
        self.log(f"Generando reporte de programación para: {fecha}")
        
        threading.Thread(target=self.run_program_export, args=(fecha,), daemon=True).start()

    def run_program_export(self, fecha):
        try:
            # Sobrescribir el print temporalmente o capturar salida si fuera necesario
            # Pero exportar_para_programacion tiene prints directos.
            # Para este caso, simplificamos asumiendo que el usuario verá el Excel abrirse.
            export_programacion.exportar_para_programacion(fecha)
            self.root.after(0, self.log, "Reporte generado con éxito.")
        except Exception as e:
            self.root.after(0, self.log, f"ERROR EXPORT: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_run_program.config(state="normal", text="GENERAR PLANILLA DE PROGRAMACIÓN (EXCEL)"))

    # --- Threading Programar Horarios ---
    def start_program_horarios_thread(self):
        fecha = self.entry_pg_date.get().strip()
        output_path = self.entry_output_horarios.get().strip()
        
        if not fecha:
            messagebox.showwarning("Aviso", "Ingresa una fecha válida.")
            return

        self.btn_program_horarios.config(state="disabled", text="Programando...")
        self.log(f"Programando horarios para: {fecha}")
        
        threading.Thread(target=self.run_program_horarios, args=(fecha, output_path), daemon=True).start()

    def run_program_horarios(self, fecha, output_path):
        try:
            programar_horarios.programar_horarios_a_excel(fecha, output_path)
            self.root.after(0, self.log, "Programación con horarios generada con éxito.")
        except Exception as e:
            self.root.after(0, self.log, f"ERROR PROGRAMAR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_program_horarios.config(state="normal", text="📅 PROGRAMAR HORARIOS DE INICIO"))

if __name__ == "__main__":
    root = tk.Tk()
    # Estilo para tabs
    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[10, 5])
    
    app = RiegoApp(root)
    root.mainloop()
