import time
import configparser
import datetime
from pathlib import Path
from Modelo.modeloImpresion import ModeloImpresion
from Controlador.controladorServicio import ControladorServicio


RUTA_CONFIG = Path(__file__).parent / "config.ini"


def log_en_cmd(tipo: str, mensaje: str):
    ahora = datetime.datetime.now().strftime("%H:%M:%S")
    if tipo == "info":
        print(f"[{ahora} INFO]   {mensaje}")
    elif tipo == "exito":
        print(f"[{ahora} ÉXITO]  {mensaje}")
    elif tipo == "error":
        print(f"[{ahora} ERROR]  {mensaje}")
    else:
        print(f"[{ahora}] {mensaje}")


def cargar_configuracion(manejador_log):
    configurador = configparser.ConfigParser()
    if not RUTA_CONFIG.exists():
        manejador_log("error", f"No se encontró el archivo '{RUTA_CONFIG}'.")
        return None
    try:
        configurador.read(RUTA_CONFIG)
        config = configurador['Configuracion']
        ruta_carpeta = Path(config['CarpetaVigilar'])
        nombre_impresora = config['NombreImpresora']
        if not ruta_carpeta.is_absolute():
            manejador_log("error", f"La ruta '{ruta_carpeta}' no es absoluta. Use C:\\...")
            return None
        if not nombre_impresora:
            raise ValueError("NombreImpresora está vacío en config.ini")
        return ruta_carpeta, nombre_impresora
    except Exception as e:
        manejador_log("error", f"Error leyendo el archivo config.ini: {e}")
        return None


def ejecutar_aplicacion():
    log_en_cmd("info", "==================================================")
    log_en_cmd("info", "   PRUEBA DE FUNCIONALIDAD (MODELO Y CONTROLADOR) ")
    log_en_cmd("info", "==================================================")

    configuracion = cargar_configuracion(log_en_cmd)
    if configuracion is None:
        input("Presione Enter para salir.")
        return
    ruta_carpeta_config, nombre_impresora_config = configuracion

    try:
        modelo = ModeloImpresion()
    except Exception as e:
        log_en_cmd("error", f"ERROR FATAL al cargar el Modelo: {e}")
        input("Presione Enter para salir.")
        return

    controlador = ControladorServicio(
        modelo=modelo,
        manejador_log=log_en_cmd
    )
    controlador.configurar(
        ruta_carpeta=ruta_carpeta_config,
        nombre_impresora=nombre_impresora_config
    )
    if not controlador.iniciar_vigilancia():
        input("Presione Enter para salir.")
        return

    log_en_cmd("info", "(Presione CTRL+C para detener la prueba)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo servicio...")
        controlador.detener_vigilancia()
        log_en_cmd("info", "Backend detenido limpiamente.")


if __name__ == "__main__":
    ejecutar_aplicacion()