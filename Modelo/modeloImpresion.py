import time
import win32api
from pathlib import Path

class ModeloImpresion:
    def __init__(self):
        pass
    def imprimir_pdf(self, ruta_archivo: Path, nombre_impresora: str):
        try:
            time.sleep(1)
            if not ruta_archivo.exists():
                return False, f"El archivo ya no existe: {ruta_archivo.name}"
            if not nombre_impresora:
                return False, "Error de configuración: No se ha especificado una impresora."
            win32api.ShellExecute(
                0, "printto", str(ruta_archivo), f'"{nombre_impresora}"', ".", 0
            )
            return True, f"Enviado a '{nombre_impresora}': {ruta_archivo.name}"
        except Exception as e:
            error_msg = str(e)
            if "No application is associated" in error_msg:
                return False, (f"Error: {e}. (Asegúrese de tener un lector "
                               f"de PDF como Adobe Reader instalado)")
            return False, f"Error al imprimir {ruta_archivo.name}: {e}"