# app.py
# --- IMPORTS ---
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# --- CLASE PARA LA BASE DE DATOS ---
class Database:
    """Gestiona la conexión y las operaciones con la base de datos MySQL."""
    def __init__(self, host, user, password, database):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                self.create_table()
        except Error as e:
            messagebox.showerror("❌ Error de Conexión", f"No se pudo conectar a la base de datos:\n{e}")
            self.connection = None

    def create_table(self):
        """Crea la tabla de empleados si no existe."""
        if not self.connection:
            return
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS empleados (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    sexo VARCHAR(50) NOT NULL,
                    correo VARCHAR(255) UNIQUE NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
        except Error as e:
            messagebox.showerror("⚠️ Error de Tabla", f"No se pudo crear la tabla:\n{e}")

    def add_employee(self, nombre, sexo, correo):
        """Añade un nuevo empleado."""
        if not self.connection:
            return False
        try:
            query = "INSERT INTO empleados (nombre, sexo, correo) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (nombre, sexo, correo))
            self.connection.commit()
            return True
        except Error as e:
            messagebox.showerror("🚫 Error al Añadir", f"No se pudo agregar el empleado:\n{e}")
            return False

    def get_employees(self):
        """Obtiene todos los empleados."""
        if not self.connection:
            return []
        try:
            self.cursor.execute("SELECT id, nombre, sexo, correo FROM empleados ORDER BY id")
            return self.cursor.fetchall()
        except Error as e:
            messagebox.showerror("⚠️ Error de Lectura", f"No se pudieron obtener los empleados:\n{e}")
            return []

    def delete_employee(self, employee_id):
        """Elimina un empleado."""
        if not self.connection:
            return False
        try:
            query = "DELETE FROM empleados WHERE id = %s"
            self.cursor.execute(query, (employee_id,))
            self.connection.commit()
            return True
        except Error as e:
            messagebox.showerror("⚠️ Error al Eliminar", f"No se pudo eliminar el empleado:\n{e}")
            return False

    def close(self):
        """Cierra la conexión."""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

# --- CLASE PARA LA INTERFAZ GRÁFICA ---
class EmployeeApp(tk.Tk):
    """Interfaz gráfica del sistema de registro de empleados."""
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        if not self.db.connection:
            self.destroy()
            return

        self.title("🌟 Sistema de Registro de Empleados 🌟")
        self.geometry("850x550")
        self.configure(bg="#f7f9fc")

        # --- Estilo personalizado ---
        style = ttk.Style(self)
        style.theme_use("clam")

        # Colores personalizados
        style.configure("TFrame", background="#f7f9fc")
        style.configure("TLabel", background="#f7f9fc", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("TButton", background=[("active", "#4A90E2")])
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#4A90E2", foreground="white")
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", font=("Segoe UI", 9))

        # --- Crear interfaz ---
        self._create_widgets()
        self.refresh_employee_list()

    def _create_widgets(self):
        """Crea todos los widgets."""
        header_label = ttk.Label(
            self, 
            text="👥 Registro de Empleados", 
            font=("Segoe UI", 18, "bold"), 
            background="#f7f9fc",
            foreground="#333"
        )
        header_label.pack(pady=10)

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Formulario ---
        form_frame = ttk.LabelFrame(main_frame, text="📝 Añadir Nuevo Empleado", padding="15")
        form_frame.pack(fill=tk.X, pady=10)

        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Sexo:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.sex_combobox = ttk.Combobox(
            form_frame, 
            values=["Masculino", "Femenino", "Otro"], 
            state="readonly", 
            width=37
        )
        self.sex_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.sex_combobox.set("Masculino")

        ttk.Label(form_frame, text="Correo:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.email_entry = ttk.Entry(form_frame, width=40)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)

        add_button = ttk.Button(form_frame, text="➕ Añadir Empleado", command=self.add_employee)
        add_button.grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)

        # --- Tabla ---
        list_frame = ttk.LabelFrame(main_frame, text="📋 Lista de Empleados", padding="15")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("id", "nombre", "sexo", "correo")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("sexo", text="Sexo")
        self.tree.heading("correo", text="Correo")

        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("nombre", width=200)
        self.tree.column("sexo", width=120, anchor=tk.CENTER)
        self.tree.column("correo", width=250)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Botones inferiores ---
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=15)

        delete_button = ttk.Button(
            action_frame, 
            text="🗑️ Eliminar Empleado Seleccionado", 
            command=self.delete_employee
        )
        delete_button.pack(side=tk.LEFT, padx=5)

        refresh_button = ttk.Button(
            action_frame, 
            text="🔄 Actualizar Lista", 
            command=self.refresh_employee_list
        )
        refresh_button.pack(side=tk.LEFT, padx=5)

    def add_employee(self):
        """Añade empleado."""
        nombre = self.name_entry.get().strip()
        sexo = self.sex_combobox.get()
        correo = self.email_entry.get().strip()

        if not nombre or not correo:
            messagebox.showwarning("⚠️ Campos Vacíos", "El nombre y el correo son obligatorios.")
            return

        if self.db.add_employee(nombre, sexo, correo):
            messagebox.showinfo("✅ Éxito", "Empleado añadido correctamente.")
            self.clear_form()
            self.refresh_employee_list()

    def delete_employee(self):
        """Elimina empleado seleccionado."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("⚠️ Sin Selección", "Selecciona un empleado para eliminar.")
            return

        item_data = self.tree.item(selected_item)
        employee_id = item_data['values'][0]

        if messagebox.askyesno("🗑️ Confirmar", f"¿Seguro que deseas eliminar al empleado con ID {employee_id}?"):
            if self.db.delete_employee(employee_id):
                messagebox.showinfo("✅ Éxito", "Empleado eliminado correctamente.")
                self.refresh_employee_list()

    def refresh_employee_list(self):
        """Actualiza la lista."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for emp in self.db.get_employees():
            self.tree.insert("", tk.END, values=emp)

    def clear_form(self):
        """Limpia los campos."""
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.sex_combobox.set("Masculino")
        self.name_entry.focus()

# --- MAIN ---
def main():
    """Punto de entrada."""
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = "toor"
    DB_NAME = "empresa_db"

    db = Database(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

    if db.connection:
        app = EmployeeApp(db)

        def on_closing():
            if messagebox.askokcancel("Salir", "¿Deseas cerrar la aplicación?"):
                db.close()
                app.destroy()

        app.protocol("WM_DELETE_WINDOW", on_closing)
        app.mainloop()

if __name__ == "__main__":
    main()
