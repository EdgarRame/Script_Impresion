import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from Modelo.modeloImpresion import ModeloImpresion

class ControladorServicio:
    def __init__(self, modelo: ModeloImpresion, manejador_log):
        self.modelo = modelo
        self.log = manejador_log
        self.observador = Observer()
        self.ruta_a_vigilar = None
        self.nombre_impresora = None
        self._hilos_impresion = []

    def configurar(self, ruta_carpeta: Path, nombre_impresora: str):
        self.ruta_a_vigilar = ruta_carpeta
        self.nombre_impresora = nombre_impresora
        self.log("info", f"Servicio configurado.")
        self.log("info", f"Carpeta: {self.ruta_a_vigilar}")
        self.log("info", f"Impresora: {self.nombre_impresora}")

    def iniciar_vigilancia(self):
        if not self.ruta_a_vigilar or not self.nombre_impresora:
            self.log("error", "El servicio no está configurado. Llame a .configurar() primero.")
            return False
        if not self.ruta_a_vigilar.exists():
            self.log("error", f"La carpeta especificada no existe: '{self.ruta_a_vigilar}'")
            self.log("error", "Por favor, cree la carpeta manualmente e intente de nuevo.")
            return False
        manejador_eventos = self._ManejadorEventos(self)
        self.observador = Observer()
        self.observador.schedule(manejador_eventos, str(self.ruta_a_vigilar), recursive=False)
        try:
            self.observador.start()
            self.log("exito", f"Vigilancia iniciada en: {self.ruta_a_vigilar}")
            return True
        except Exception as e:
            self.log("error", f"No se pudo iniciar la vigilancia: {e}")
            return False

    def detener_vigilancia(self):
        if self.observador.is_alive():
            self.observador.stop()
            self.observador.join()
        self.log("info", "Vigilancia detenida.")

    def _procesar_archivo_detectado(self, ruta_archivo_str: str):
        ruta_archivo = Path(ruta_archivo_str)
        self.log("info", f"Archivo detectado: {ruta_archivo.name}")
        exito, mensaje = self.modelo.imprimir_pdf(ruta_archivo, self.nombre_impresora)
        if exito:
            self.log("exito", mensaje)
        else:
            self.log("error", mensaje)

    class _ManejadorEventos(FileSystemEventHandler):
        def __init__(self, controlador_principal):
            self.controlador = controlador_principal
        def on_created(self, event):
            if not event.is_directory and event.src_path.lower().endswith('.pdf'):
                hilo_impresion = threading.Thread(
                    target=self.controlador._procesar_archivo_detectado,
                    args=(event.src_path,),
                    daemon=True
                )
                hilo_impresion.start()
                self.controlador._hilos_impresion.append(hilo_impresion)