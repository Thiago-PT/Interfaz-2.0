# form_panel_datos.py

import customtkinter as ctk
from PIL import Image, ImageTk
import pymysql
from datetime import datetime
import csv
from typing import List, Tuple, Optional
import logging
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DatabaseConnection:
    def __init__(self):
        self.connection_params = {
            'host': 'b4qhbwwqys2nhher1vul-mysql.services.clever-cloud.com',
            'port': 3306,
            'db': 'b4qhbwwqys2nhher1vul',
            'user': 'upvge9afjesbmmgv',
            'password': 'BS2bxJNACO1XYEmWBqA0',
            'connect_timeout': 30  # Solo mantenemos este timeout
        }
    
    def get_connection(self) -> Optional[pymysql.Connection]:
        try:
            connection = pymysql.connect(**self.connection_params)
            logging.info("Conexión a base de datos establecida exitosamente")
            return connection
        except pymysql.Error as e:
            logging.error(f"Error de conexión a la base de datos: {e}")
            return None
                    
    def __enter__(self):
        self.connection = self.get_connection()
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
    
    def get_connection(self) -> Optional[pymysql.Connection]:
        try:
            return pymysql.connect(**self.connection_params)
        except Exception as e:
            logging.error(f"Error de conexión a la base de datos: {e}")
            return None

class DataManager:
    @staticmethod
    def fetch_asistencia(limit: int = 100) -> List[Tuple]:
        with DatabaseConnection() as conn:
            if not conn:
                return []
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT i.id_ingreso, 
                               CONCAT(e.nombres, ' ', e.apellidos) as nombre,
                               e.grupo,
                               e.jornada,
                               i.fecha,
                               i.codigo_est
                        FROM ingreso i
                        JOIN estudiante e ON i.codigo_est = e.codigo_est
                        ORDER BY i.fecha DESC 
                        LIMIT %s
                    """, (limit,))
                    return cursor.fetchall()
            except Exception as e:
                logging.error(f"Error al obtener datos de ingreso: {e}")
                return []

    @staticmethod
    def fetch_estudiantes() -> List[Tuple]:
        with DatabaseConnection() as conn:
            if not conn:
                return []
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT codigo_est, nombres, apellidos, grupo, jornada 
                        FROM estudiante
                    """)
                    return cursor.fetchall()
            except Exception as e:
                logging.error(f"Error al obtener estudiantes: {e}")
                return []

    @staticmethod
    def fetch_usuarios_hoy() -> int:
        with DatabaseConnection() as conn:
            if not conn:
                return 0
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT codigo_est) 
                        FROM ingreso 
                        WHERE DATE(fecha) = CURDATE()
                    """)
                    result = cursor.fetchone()
                    return result[0] if result else 0
            except Exception as e:
                logging.error(f"Error al obtener usuarios de hoy: {e}")
                return 0

    @staticmethod
    def export_to_csv(datos: List[Tuple], filename: Optional[str] = None) -> str:
        if not filename:
            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exportacion_ingreso_{fecha_actual}.csv"
        
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Nombre", "Grupo", "Jornada", "Fecha", "Código Estudiante"])
                writer.writerows(datos)
            logging.info(f"Datos exportados exitosamente a {filename}")
            return filename
        except Exception as e:
            logging.error(f"Error al exportar datos: {e}")
            raise

class DashboardPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Sección de Estadísticas
        self.create_stats_section()
        
        # Sección de Tabla de Asistencia
        self.create_attendance_table()
        
        # Sección de Gráficos de Asistencia
        self.create_attendance_charts()
        
        # Botones de Control
        self.create_control_buttons()
        
    def create_stats_section(self):
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Obtener datos para estadísticas
        estudiantes = DataManager.fetch_estudiantes()
        usuarios_hoy = DataManager.fetch_usuarios_hoy()
        asistencia = DataManager.fetch_asistencia()
        
        # Crear tarjetas de estadísticas
        self.create_stat_card(stats_frame, "Total Estudiantes", len(estudiantes), 0)
        self.create_stat_card(stats_frame, "Asistencia Hoy", usuarios_hoy, 1)
        self.create_stat_card(stats_frame, "Total Registros", len(asistencia), 2)
        
    def create_stat_card(self, parent, title: str, value: int, column: int):
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=column, padx=10, pady=5, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=("Roboto", 12)).pack(pady=5)
        ctk.CTkLabel(card, text=str(value), font=("Roboto", 20, "bold")).pack(pady=5)
        
    def create_attendance_table(self):
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Encabezados
        columns = ["ID", "Nombre", "Grupo", "Jornada", "Fecha", "Código"]
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                self.table_frame,
                text=col,
                font=("Roboto", 12, "bold")
            ).grid(row=0, column=i, padx=5, pady=5, sticky="w")
            
        self.actualizar_tabla()
        
    def actualizar_tabla(self):
        # Limpiar tabla existente (excepto encabezados)
        for widget in self.table_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()
                
        # Obtener datos frescos
        datos = DataManager.fetch_asistencia()
        
        # Llenar tabla
        for i, row in enumerate(datos, start=1):
            for j, value in enumerate(row):
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M")
                    
                ctk.CTkLabel(
                    self.table_frame,
                    text=str(value),
                    font=("Roboto", 12)
                ).grid(row=i, column=j, padx=5, pady=2, sticky="w")
                
    def create_attendance_charts(self):
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Obtener datos para gráficos
        self.data = DataManager.fetch_asistencia()
        
        # Crear gráficos
        self.create_attendance_by_group_chart()
        self.create_attendance_by_jornada_chart()
        self.create_daily_attendance_chart()
        
    def create_attendance_by_group_chart(self):
        # Agrupar datos por grupo
        grupo_data = {}
        for row in self.data:
            grupo = row[2]  # índice del grupo
            grupo_data[grupo] = grupo_data.get(grupo, 0) + 1
            
        self.figura_grupos = Figure(figsize=(6, 4), facecolor="#3E3E3E")
        ax = self.figura_grupos.add_subplot(111)
        ax.bar(grupo_data.keys(), grupo_data.values(), color='cyan')
        ax.set_xlabel('Grupo', color='white')
        ax.set_ylabel('Cantidad de Ingresos', color='white')
        ax.set_title('Asistencia por Grupo', color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        
        canvas = FigureCanvasTkAgg(self.figura_grupos, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="left", padx=10, pady=10)
        
    def create_attendance_by_jornada_chart(self):
        # Agrupar datos por jornada
        jornada_data = {}
        for row in self.data:
            jornada = row[3]  # índice de la jornada
            jornada_data[jornada] = jornada_data.get(jornada, 0) + 1
            
        self.figura_jornada = Figure(figsize=(6, 4), facecolor="#3E3E3E")
        ax = self.figura_jornada.add_subplot(111)
        ax.pie(
            jornada_data.values(),
            labels=jornada_data.keys(),
            autopct='%1.1f%%',
            colors=['#FF9999', '#66B2FF']
        )
        ax.set_title('Distribución por Jornada', color='white')
        
        canvas = FigureCanvasTkAgg(self.figura_jornada, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="left", padx=10, pady=10)
        
    def create_daily_attendance_chart(self):
        # Agrupar datos por fecha
        fecha_data = {}
        for row in self.data:
            fecha = row[4].date()  # índice de la fecha
            fecha_data[fecha] = fecha_data.get(fecha, 0) + 1
            
        self.figura_diaria = Figure(figsize=(6, 4), facecolor="#3E3E3E")
        ax = self.figura_diaria.add_subplot(111)
        ax.plot(list(fecha_data.keys()), list(fecha_data.values()), color='orange', marker='o')
        ax.set_xlabel('Fecha', color='white')
        ax.set_ylabel('Cantidad de Ingresos', color='white')
        ax.set_title('Asistencia Diaria', color='white')
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        
        canvas = FigureCanvasTkAgg(self.figura_diaria, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="left", padx=10, pady=10)
        
    def create_control_buttons(self):
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Actualizar Datos",
            command=self.actualizar_datos,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Exportar a CSV",
            command=self.exportar_datos,
            width=150
        ).pack(side="left", padx=5)
        
    def actualizar_datos(self):
        self.actualizar_tabla()
        # Limpiar y recrear gráficos
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self.create_attendance_charts()
        self.show_message("Datos actualizados correctamente")
        
    def exportar_datos(self):
        datos = DataManager.fetch_asistencia()
        if datos:
            try:
                filename = DataManager.export_to_csv(datos)
                self.show_message(f"Datos exportados a {filename}")
            except Exception as e:
                self.show_message(f"Error al exportar: {str(e)}", "error")
                
    def show_message(self, message: str, msg_type: str = "info"):
        color = "red" if msg_type == "error" else "green"
        label = ctk.CTkLabel(
            self,
            text=message,
            text_color=color,
            font=("Roboto", 12)
        )
        label.pack(pady=5)
        self.after(3000, label.destroy)

def mostrar_panel_datos(frame_principal: ctk.CTkFrame, callback_return):
    # Limpiar frame principal
    for widget in frame_principal.winfo_children():
        widget.destroy()
        
    # Crear y mostrar el dashboard
    dashboard = DashboardPanel(frame_principal)
    dashboard.pack(fill="both", expand=True)
    
    # Botón para volver
    ctk.CTkButton(
        frame_principal,
        text="Volver al Menú Principal",
        command=lambda: callback_return(frame_principal),
        width=200
    ).pack(pady=10)

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Panel de Asistencia Escolar")
    app.configure(bg="#2E2E2E")
    mostrar_panel_datos(app, lambda x: x.destroy())
    app.mainloop()