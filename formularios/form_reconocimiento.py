# form_reconocimiento.py

import customtkinter as ctk
from PIL import Image, ImageTk

def mostrar_ventana_reconocimiento(frame_principal, callback_return):
    # Limpiar el frame principal
    for widget in frame_principal.winfo_children():
        widget.destroy()
    
    # Crear un frame contenedor
    frame_reconocimiento = ctk.CTkFrame(frame_principal, fg_color="transparent")
    frame_reconocimiento.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Título
    label_titulo = ctk.CTkLabel(
        frame_reconocimiento,
        text="Reconocimiento Facial",
        font=("Roboto", 24, "bold")
    )
    label_titulo.pack(pady=20)
    
    # Frame para la cámara (placeholder)
    frame_camera = ctk.CTkFrame(frame_reconocimiento, width=640, height=480)
    frame_camera.pack(pady=20)
    
    # Label placeholder para la cámara
    label_camera = ctk.CTkLabel(
        frame_camera,
        text="Área de la Cámara",
        font=("Roboto", 16)
    )
    label_camera.place(relx=0.5, rely=0.5, anchor="center")
    
    # Botones de control
    frame_botones = ctk.CTkFrame(frame_reconocimiento, fg_color="transparent")
    frame_botones.pack(pady=20)
    
    btn_iniciar = ctk.CTkButton(
        frame_botones,
        text="Iniciar Reconocimiento",
        font=("Roboto", 14),
        command=lambda: print("Iniciando reconocimiento..."),
        width=200
    )
    btn_iniciar.pack(side="left", padx=10)
    
    btn_detener = ctk.CTkButton(
        frame_botones,
        text="Detener",
        font=("Roboto", 14),
        command=lambda: print("Deteniendo reconocimiento..."),
        width=200
    )
    btn_detener.pack(side="left", padx=10)
    
    # Botón para volver
    btn_volver = ctk.CTkButton(
        frame_reconocimiento,
        text="Volver al Menú Principal",
        font=("Roboto", 14),
        command=lambda: callback_return(frame_principal),
        width=200
    )
    btn_volver.pack(pady=20)