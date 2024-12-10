import laspy
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import numpy as np


def add_noise_to_las(input_path, output_path, noise_percentage, fixed_error):
    """
    Lee una nube de puntos LAS, agrega ruido a las coordenadas XYZ basado en un porcentaje del rango de datos
    y un error fijo, respetando las clases del archivo LAS.

    Parámetros:
    - input_path: Ruta del archivo LAS de entrada.
    - output_path: Ruta del archivo LAS de salida.
    - noise_percentage: Nivel de ruido como porcentaje del rango de coordenadas.
    - fixed_error: Error fijo a sumar en cada coordenada XYZ.
    """
    try:
        # Abrir archivo LAS de entrada
        with laspy.open(input_path) as las_file:
            las = las_file.read()

        # Calcular el rango de las coordenadas
        range_x = las.x.max() - las.x.min()
        range_y = las.y.max() - las.y.min()
        range_z = las.z.max() - las.z.min()

        # Calcular el nivel de ruido (en función del porcentaje)
        noise_std_x = range_x * noise_percentage / 100
        noise_std_y = range_y * noise_percentage / 100
        noise_std_z = range_z * noise_percentage / 100

        # Generar ruido aleatorio y agregar el error fijo
        noise_x = np.random.normal(0, noise_std_x, len(las.x)) + fixed_error
        noise_y = np.random.normal(0, noise_std_y, len(las.y)) + fixed_error
        noise_z = np.random.normal(0, noise_std_z, len(las.z)) + fixed_error

        las.x += noise_x
        las.y += noise_y
        las.z += noise_z

        # Guardar archivo modificado
        with laspy.open(output_path, mode="w", header=las.header) as out_file:
            out_file.write_points(las.points)

        messagebox.showinfo("Éxito", f"Archivo guardado en:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo procesar el archivo:\n{e}")


def select_input_file():
    """
    Permite al usuario seleccionar un archivo LAS de entrada y actualiza la ruta mostrada.
    """
    input_path = filedialog.askopenfilename(
        title="Selecciona el archivo LAS de entrada",
        filetypes=[("Archivos LAS", "*.las")]
    )
    if input_path:
        input_path_var.set(input_path)
        # Generar una ruta de salida predeterminada
        base_name = os.path.basename(input_path)
        dir_name = os.path.dirname(input_path)
        name, ext = os.path.splitext(base_name)
        default_output = os.path.join(dir_name, f"{name}_noised{ext}")
        output_path_var.set(default_output)


def select_output_file():
    """
    Permite al usuario seleccionar un archivo LAS de salida y actualiza la ruta mostrada.
    """
    output_path = filedialog.asksaveasfilename(
        title="Selecciona la ruta del archivo LAS de salida",
        defaultextension=".las",
        filetypes=[("Archivos LAS", "*.las")]
    )
    if output_path:
        output_path_var.set(output_path)


def process_files():
    """
    Inicia el procesamiento del archivo LAS con ruido añadido.
    """
    input_path = input_path_var.get()
    output_path = output_path_var.get()
    noise_percentage = noise_percentage_var.get()
    fixed_error = fixed_error_var.get()

    if not input_path or not output_path:
        messagebox.showwarning("Advertencia", "Por favor selecciona ambas rutas de archivo.")
        return

    try:
        noise_percentage = float(noise_percentage)
        fixed_error = float(fixed_error)
        if noise_percentage < 0 or fixed_error < 0:
            raise ValueError("Los valores deben ser números positivos.")
    except ValueError as e:
        messagebox.showerror("Error", f"Por favor introduce valores válidos.\n{e}")
        return

    add_noise_to_las(input_path, output_path, noise_percentage, fixed_error)


# Configuración de la ventana principal
root = tk.Tk()
root.title("Agregar Ruido a LAS")
root.geometry("500x400")

# Variables para almacenar las rutas de los archivos y los niveles de ruido
input_path_var = tk.StringVar()
output_path_var = tk.StringVar()
noise_percentage_var = tk.StringVar(value="1.0")  # Valor predeterminado de ruido como porcentaje
fixed_error_var = tk.StringVar(value="0.0")  # Valor predeterminado de error fijo

# Etiqueta y botón para el archivo de entrada
tk.Label(root, text="Archivo LAS de entrada:").pack(anchor="w", padx=10, pady=5)
tk.Entry(root, textvariable=input_path_var, width=60, state="readonly").pack(padx=10, pady=5)
tk.Button(root, text="Seleccionar archivo de entrada", command=select_input_file).pack(padx=10, pady=5)

# Etiqueta y botón para el archivo de salida
tk.Label(root, text="Archivo LAS de salida:").pack(anchor="w", padx=10, pady=5)
tk.Entry(root, textvariable=output_path_var, width=60, state="readonly").pack(padx=10, pady=5)
tk.Button(root, text="Seleccionar archivo de salida", command=select_output_file).pack(padx=10, pady=5)

# Campo para especificar ruido como porcentaje
tk.Label(root, text="Ruido como porcentaje del rango (X, Y, Z):").pack(anchor="w", padx=10, pady=5)
tk.Entry(root, textvariable=noise_percentage_var, width=20).pack(padx=10, pady=5)

# Campo para especificar error fijo
tk.Label(root, text="Error fijo a añadir (en unidades):").pack(anchor="w", padx=10, pady=5)
tk.Entry(root, textvariable=fixed_error_var, width=20).pack(padx=10, pady=5)

# Botón para iniciar el procesamiento
tk.Button(root, text="Procesar archivo", command=process_files, padx=10, pady=5).pack(pady=20)

# Iniciar el loop principal de Tkinter
root.mainloop()
