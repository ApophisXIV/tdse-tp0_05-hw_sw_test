import re
import os.path

# ----------------------------- Color definitions ---------------------------- #
def prRed(skk): return f"\033[91m{skk}\033[00m"
def prGreen(skk): return f"\033[92m{skk}\033[00m"
def prYellow(skk): return f"\033[93m{skk}\033[00m"
def prLightPurple(skk): return f"\033[94m{skk}\033[00m"
def prPurple(skk): return f"\033[95m{skk}\033[00m"
def prCyan(skk): return f"\033[96m{skk}\033[00m"
def prLightGray(skk): return f"\033[97m{skk}\033[00m"
def prBlack(skk): return f"\033[98m{skk}\033[00m"
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
H_LINE = prCyan("# ---------------------------------------------------------------------------- #\n")

SCRIPT_TITLE = \
    H_LINE +\
    prCyan("#             FIUBA - Taller de sistemas embebidos - 1C 2025                   #\n") +\
    H_LINE

AUTHORS = prPurple("\
\n\
                    Guido Rodriguez - Karla Duque\n\
             guerodriguez@fi.uba.ar - kduque@fi.uba.ar\n\
\n")

SCRIPT_CAPTION = prLightGray(f"\
Este script se encarga de agregar las configuraciones necesarias para\n\
utilizar el printf en VSCode en un esquema semihosting mediante OpenOCD\n\
\n")

ADD_KEYWORD = prGreen("Agrega")
CONFIG_KEYWORD = prYellow("Configura")
OPTIONAL = prLightPurple("(Opcional)")

SCRIPT_DESCRIPTION = f"\
    - {ADD_KEYWORD} librerias como rdimon y sus configuraciones\n\
    - {ADD_KEYWORD} opciones de linking para utilizar en modo semihosting\n\
    - {ADD_KEYWORD} una task para en VSCode debug mediante OpenOCD\n\
    - {CONFIG_KEYWORD} el servidor OpenOCD en modo semihosting\n\
    - {OPTIONAL} {ADD_KEYWORD} una serie de botones en la status bar \n\
                para facilitar el desarrollo\n" +\
        H_LINE
# ---------------------------------------------------------------------------- #

# ----------------------------- Welcome messagge ----------------------------- #
def welcome_msg():
    print(SCRIPT_TITLE + AUTHORS + SCRIPT_CAPTION + SCRIPT_DESCRIPTION)
# ---------------------------------------------------------------------------- #

# -------------------------- Not first run messagge -------------------------- #
def not_first_run_msg():
    SCRIPT_CAPTION_WARNING = prRed(f"\
    Se detecto que este script fue ejecutado previamente y volver a hacerlo sin\n\
    revertir los cambios efectuados puede generar errores o conflictos en la\n\
    configuracion. Si realmente queres volver a ejecutarlo elimina el archivo \n\
    {prLightPurple(FIRST_RUN_FILE_PATH)}\n\n")+\
    prRed("    Y reverti los cambios efectuados el los sigientes archivos:\n") +\
    prLightPurple("\t./.vscode/launch.json\n") +\
    prLightPurple("\t./cmake/stm32cubemx/CMakeLists.txt\n") +\
    prLightPurple("\t./cmake/gcc-arm-none-eabi.cmake\n")

    print(SCRIPT_TITLE + AUTHORS + SCRIPT_CAPTION_WARNING + H_LINE)
# ---------------------------------------------------------------------------- #

# ------------------------------- Dry run check ------------------------------ #
FIRST_RUN_FILE_PATH = "add_printf_dry_run.bin"
def is_script_first_run():
    try:
        with open(FIRST_RUN_FILE_PATH,'rb') as f:
            if(f.read() == b'first_run_complete'):
                return False
    except FileNotFoundError:
        pass
    with open(FIRST_RUN_FILE_PATH,'wb') as f:
        f.write(b'first_run_complete')
        f.close()
    return True
# ---------------------------------------------------------------------------- #

# -------------------------- Compiler linker options ------------------------- #
GCC_ARM_NONE_EABI_LINKER_OPTIONS = "\n\
# ---------------------------------------------------------------------------- #\n\
# Configuracion printf en semihosting\n\
# ---------------------------------------------------------------------------- #\n\
# Incluimos la biblioteca rdimon que le indica que podemos usar las systemcalls\n\
# pero estas son manejadas por el debugger controlado por el HOST\n\
set(CMAKE_C_LINK_FLAGS \"${CMAKE_C_LINK_FLAGS} -lrdimon\")\n\
set(CMAKE_C_LINK_FLAGS \"${CMAKE_C_LINK_FLAGS} -specs=rdimon.specs\")\n\
# Excluimos las llamadas del sistema (evitamos redefinir funciones basicas\n\
# como _write, _read, _open, _kill, _etc) y prevenimos posibles errores de \n\
# uso de las syscalls por parte del TARGET\n\
set(CMAKE_C_LINK_FLAGS \"${CMAKE_C_LINK_FLAGS} --specs=nosys.specs\")\n\
# ---------------------------------------------------------------------------- #\n\
"
PATH_GCC_ARM_COMPILER = "cmake/gcc-arm-none-eabi.cmake"
def add_linking_options(options):
    file_gcc_arm_compiler = open(PATH_GCC_ARM_COMPILER, 'a')
    file_gcc_arm_compiler.write(options)
    file_gcc_arm_compiler.close()
# ---------------------------------------------------------------------------- #

# --------------------------- Exclude syscalls file -------------------------- #
PATH_CMAKE_LIST_CUBEMX = "cmake/stm32cubemx/CMakeLists.txt"
def remove_syscall_link():
    file_cmake_list_cubemx = open(PATH_CMAKE_LIST_CUBEMX,'r')
    dump_cmake_list = file_cmake_list_cubemx.readlines()
    file_cmake_list_cubemx.close()
    
    file_cmake_list_cubemx = open(PATH_CMAKE_LIST_CUBEMX,"w")
    for line in dump_cmake_list:
        if(line.find("syscalls.c") != -1 and line.find('#') == -1):
            file_cmake_list_cubemx.write("#" + line)
        else:
            file_cmake_list_cubemx.write(line)
    file_cmake_list_cubemx.close()           
# ---------------------------------------------------------------------------- #

# ------------------------- Semihosting config server ------------------------ #
SEMIHOSTING_CONFIG = """\
        // --------------------------------------------------------------------------\n\
        // Configuracion semihosting - printf \n\
        // --------------------------------------------------------------------------\n\
        {{\n\
            \"name\": \"Debug con OpenOCD\",\n\
            \"cwd\": \"${{workspaceFolder}}\",\n\
            \"type\": \"cortex-debug\",\n\
            \"executable\": \"${{command:cmake.launchTargetPath}}\",\n\
            \"request\": \"launch\",\n\
            \"servertype\": \"openocd\",\n\
            \"serverpath\": "{_server_path}",\n\
            \"configFiles\": [\n\
                "{_debug_cfg_file}"\n\
            ],\n\
            \"serverArgs\": [\n\
                \"-s\",\n\
                "{_scripts}",\n\
                // \"-d3\"\n\
            ],\n\
            \"device\":"{_target}",\n\
            \"svdFile\": \"${{config:STM32VSCodeExtension.cubeCLT.path}}/STMicroelectronics_CMSIS_SVD/{_target_svd}\",\n\
            \"runToEntryPoint\": \"main\",\n\
            \"showDevDebugOutput\": \"raw\",\n\
            \"preLaunchCommands\": [\n\
                \"monitor arm semihosting enable\",\n\
                \"monitor sleep 100\",\n\
            ]\n\
        }},\n\
        // --------------------------------------------------------------------------\n\
        """
# ---------------------------------------------------------------------------- #

# --------------------------- Config OpenOCD server -------------------------- #
PATH_LAUNCH_JSON = ".vscode/launch.json"
def add_OpenOCD_server(open_ocd_server_path, target_mcu_reference, target_mcu_svd_path, open_ocd_debug_cfg_path, open_ocd_scripts_path):
    
    file_launch_json = open(PATH_LAUNCH_JSON,encoding='utf-8 ',mode='r')
    dump_json = file_launch_json.readlines()
    file_launch_json.close()
    
    was_added_configuration = False
    
    file_launch_json = open(PATH_LAUNCH_JSON,encoding='utf-8',mode='w')

    for line in dump_json:
        if(line.find("configurations") != -1 and not was_added_configuration):

            actual_line = line
            actual_index = dump_json.index(line)
            
            while(actual_line.find('[') == -1 or actual_line[0] == '\n'): 
                actual_line = dump_json[actual_index + 1]
                actual_index += 1
            
            actual_line += '\n' + SEMIHOSTING_CONFIG.format(\
                    _server_path=open_ocd_server_path,\
                    _target=target_mcu_reference,\
                    _debug_cfg_file = open_ocd_debug_cfg_path,\
                    _scripts = open_ocd_scripts_path,\
                    _target_svd = target_mcu_svd_path
                )

            line = actual_line
            was_added_configuration = True    
            
        file_launch_json.write(line)
        
    file_launch_json.close()
# ---------------------------------------------------------------------------- #

# ----------------------------- Parse config data ---------------------------- #
def parse_config_file(file_path):
    config = {}

    # Expresión regular para detectar claves y valores
    pattern = re.compile(r"^\s*([\w\-]+)\s*=\s*(.*?)\s*$") #TODO - REVISAR SI SIRVE PARA WIN

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = pattern.match(line)
            if match:
                key, value = match.groups()
                config[key] = value.strip() if value else None  # Si no hay valor, deja None

    return config
# ---------------------------------------------------------------------------- #

# ----------------------------- Wait until accept ---------------------------- #
def wait_until_accept():
    
    print(prYellow(">>> [INFO]  ") +" -\tCuando termines de configurar los datos presiona "+\
            f"[Y/y/Enter] sino [N/n] para cancelar")

    while True:
        respuesta = input(prCyan("<<< [INPUT]  ") +"-\t"+ "¿Terminaste la configuración? [Y/N]: ").strip().lower()

        if respuesta in ['y', ""]:
            print("")
            # print(prYellow(">>> [INFO]    ") + " - Continuando con el proceso...\n")
            break
        elif respuesta == 'n':
            print("")
            print(prRed(">>> [CANCEL]") + " - Operación cancelada por el usuario")
            print(prYellow(">>> [INFO]") + f" - Para correr de nuevo el script por favor eliminar el archivo {FIRST_RUN_FILE_PATH}")
            exit(1)
        else:
            print(prYellow(">>> [WARN]  ") +\
                " -\tEntrada no válida. Por favor, ingresa 'Y' para continuar o 'N' para cancelar")
# ---------------------------------------------------------------------------- #
def wait_for_custom_choice(options,cancel_option):
    # print(prYellow(">>> [INFO]  ") + " - Selecciona una opción:")
    
    for key, description in options.items():
        print(prGreen(f"\t\t({key})") + f" - {description}")

    while True:
        selected_option = input(prCyan("<<< [INPUT]  ") + "-\tSelecciona una opción: ").strip()

        if selected_option in options:
            print("")
            print(prYellow(">>> [INFO]  ") + f" - Elegiste: {options[selected_option]}\n")
            return selected_option
        elif selected_option == cancel_option:
            print("")
            print(prRed(">>> [CANCEL]") + " - Operación cancelada por el usuario.")
            print(prYellow(">>> [INFO]") + f" - Para correr de nuevo el script por favor eliminar el archivo {FIRST_RUN_FILE_PATH}")
            exit(1)
        else:
            print(prYellow(">>> [WARN]  ") + " -\tEntrada no válida. Ingresa una de las opciones disponibles\n")
# ---------------------------------------------------------------------------- #

# -------------------------- Semihosting data input -------------------------- #
SEMIHOSTING_DATA_FILE_TEMPLATE = "\
# Agrega la ruta al servidor de OpenOCD de ST\n\
# Si realizaste una instalacion por defecto \n\
# este se encuentra habitualmente en:\n\
# [LINUX]: /home/TU_USUARIO/st/stm32cubeide_VERSION/plugins/com.st.stm32cube.ide.mcu.externaltools.openocd.linux64_NUMEROS_DE_VERSION/tools/bin/openocd\n\
# [LINUX_ALTERNATIVA]: /opt/st/stm32cubeide_VERSION/plugins/com.st.stm32cube.ide.mcu.externaltools.openocd.linux64_NUMEROS_DE_VERSION/tools/bin/openocd\n\
# [WIN]: C:\\st\\stm32cubeide_VERSION\\plugins\\com.st.stm32cube.ide.mcu.externaltools.openocd.linux64_NUMEROS_DE_VERSION\\tools\\bin\\openocd.exe\n\
path_to_OpenOCD = \n\
\n\
# Agrega la ruta a la carpeta de scripts de OpenOCD de ST\n\
# Si realizaste una instalacion por defecto \n\
# esta se encuentra habitualmente en:\n\
# [LINUX]: /home/TU_USUARIO/st/stm32cubeide_VERSION/plugins/com.st.stm32cube.ide.mcu.debug.openocd_NUMEROS_DE_VERSION/resources/openocd/st_scripts\n\
# [LINUX ALTERNATIVA]: /opt/st/stm32cubeide_VERSION/plugins/com.st.stm32cube.ide.mcu.debug.openocd_NUMEROS_DE_VERSION/resources/openocd/st_scripts\n\
# [WIN]: C:\\st\\stm32cubeide_VERSION\\plugins\\com.st.stm32cube.ide.mcu.debug.openocd_NUMEROS_DE_VERSION\\resources\\openocd\\st_scripts\n\
path_to_OpenOCD_scripts = \n\
\n\
# Agrega el nombre asociado a tu microcontrolador (EJ: STM32F103RBTx)\n\
# - Abri CubeMX con tu proyecto y en la pestaña 'Project Manager' busca 'MCU Reference'\n\
# - Copia y pega ese valor \n\
mcu_reference =\n\
\n\
# Agrega el nombre del archivo de descripcion SVD de tu Target (NO LA RUTA. EJ: STM32F103.svd)\n\
# Si realizaste una instalacion por defecto \n\
# esta se encuentra habitualmente en:\n\
# [LINUX]: /opt/st/stm32cubeclt_VERSION/STMicroelectronics_CMSIS_SVD/ACA_VA_EL_NOMBRE_DEL_DEVICE\n\
# [WIN]: C:\\st\\stm32cubeclt_VERSION/STMicroelectronics_CMSIS_SVD/ACA_VA_EL_NOMBRE_DEL_DEVICE\n\
mcu_target_svd =\n\
"
# ---------------------------------------------------------------------------- #

# ------------------------ OpenOCD debug file default ------------------------ #
OPEN_OCD_DEBUG_CONFIG_TEMPLATE = """
# This is an NUCLEO-F103RB board with a single STM32F103RBTx chip
#
# Generated by STM32CubeIDE
# Take care that such file, as generated, may be overridden without any early notice. Please have a look to debug launch configuration setup(s)
source [find interface/stlink-dap.cfg]

set WORKAREASIZE 0x5000

transport select "dapdirect_swd"

set CHIPNAME STM32F103RBTx
set BOARDNAME NUCLEO-F103RB

# Enable debug when in low power modes
set ENABLE_LOW_POWER 1

# Stop Watchdog counters when halt
set STOP_WATCHDOG 1

# STlink Debug clock frequency
set CLOCK_FREQ 8000

# Reset configuration
# use software system reset if reset done
reset_config none
set CONNECT_UNDER_RESET 0
set CORE_RESET 0

# ACCESS PORT NUMBER
set AP_NUM 0
# GDB PORT
set GDB_PORT 3333

# BCTM CPU variables
source [find target/stm32f1x.cfg]    
"""
# ---------------------------------------------------------------------------- #

# ------------------------------ Get config data ----------------------------- #
FILE_IS_EMPTY = 0
PATH_OPENOCD_DEBUG_FILE = './OpenOCD_Debug.cfg'

def wait_until_data_is_valid(file_path,err_msg, callback = None, validate_fields=False):
    
    file_is_not_valid = True
    while file_is_not_valid:
        
        wait_until_accept()
        
        with open(file_path,'r') as f:
            if len(f.read()) == FILE_IS_EMPTY:
                print(prRed(">>> [ERROR] ") + " - \t" + err_msg)
            else: file_is_not_valid = False
            f.close()
        
        if validate_fields:
            if callback(file_path):            
                file_is_not_valid = True
                print(prRed(">>> [ERROR] ") + " - \t" + err_msg)
            else:
                file_is_not_valid = False

def semihosting_parser(file_path):
    semihosting_dict = parse_config_file(file_path)
    return None in semihosting_dict.values()

def print_help_openocd_debug_cfg():
    print(f"""\
    {prLightPurple("Pasos para generar un archivo de configuración de OpenOCD:")}

    1. Crea un proyecto en STM32CubeIDE para el mismo dispositivo o placa.
    2. Abre la configuración de debug. Run => Debug Configurations => STM32 C/C++ Application => Debugger
    3. Cambia la opción de "Debug Probe" de [ST-Link GDB-Server] a [ST-Link OpenOCD].
    4. Configuration Script => Show Generator Options => Mode Setup => Reset Mode => [Software System Reset]
    4. Una vez cambiado y luego de tocar "Apply", STM32CubeIDE generará automáticamente un nuevo archivo en el explorador de proyectos.
    5. Busca el archivo generado en la carpeta de depuración. Su nombre suele ser "<NOMBRE_DEL_PROYECTO> Debug.cfg".
    6. Copia el contenido de este archivo y pégalo en un nuevo archivo de configuración.

    Este archivo se utilizará para configurar OpenOCD correctamente con el dispositivo.
    """)

def generate_openocd_debug_file(use_default_content = False):
    with open(PATH_OPENOCD_DEBUG_FILE,'w') as f:
        if use_default_content: f.write(OPEN_OCD_DEBUG_CONFIG_TEMPLATE)
        f.close()
    print(prGreen(">>> [ADD]   ") + f" - Se genero el archivo de configuracion del servidor OpenOCD " +\
          prPurple("(Ahora completalo)") if not use_default_content else "")
    
    
    
def set_custom_debug_config_file():
    print(prYellow(">>> [INFO]  ") + " - Para continuar" + prPurple(" ES NECESARIO ") +\
        f"que configures el archivo de debug del servidor \n\
               de OpenOCD el archivo que vas a encontrar en {PATH_OPENOCD_DEBUG_FILE}")
    
    generate_openocd_debug_file()
    print_help_openocd_debug_cfg()
       
    ERR_MSG_DEBUB_FILE = "El archivo de configuracion de OpenOCD esta vacio y es necesario que sea completado por el usuario"
    wait_until_data_is_valid(PATH_OPENOCD_DEBUG_FILE,ERR_MSG_DEBUB_FILE,ERR_MSG_DEBUB_FILE)

def get_input_data():
    
    # Parsear semihosting_data.cfg
    # - No validamos rutas 
    # - Si validamos campos vacios -> ERROR
    PATH_SEMIHOSTING_DATA_FILE_TEMPLATE = "semihosting_data.cfg"
    print(prYellow(">>> [INFO]  ") + " -\tPara continuar" + prPurple(" ES NECESARIO ") +\
       f"que configures una serie de parametros\n\t\ten el archivo que vas a encontrar en {PATH_SEMIHOSTING_DATA_FILE_TEMPLATE}")
    
    with open(PATH_SEMIHOSTING_DATA_FILE_TEMPLATE,'w') as f:
        f.write(SEMIHOSTING_DATA_FILE_TEMPLATE)
        f.close()
    print(prGreen(">>> [ADD]   ") + " -\tSe genero el archivo de configuracion de variables para semihosting")

    wait_until_data_is_valid(PATH_SEMIHOSTING_DATA_FILE_TEMPLATE,
                             "No dejes campos vacios en el archivo de configuracion",
                             semihosting_parser,validate_fields=True)

    print(H_LINE)
    print(prYellow(">>> [INFO]  ") + " -\tPara continuar" + prPurple(" ES NECESARIO ") +\
        f"que elijas si queres configurar un archivo\n"+\
        "\t\tde debug del servidor de OpenOCD o utilizar una configuracion por defecto\n"+\
        "\t\tbasada en la "+ prLightPurple("Nucleo-F103") +" (que no funcionaria si usas otra placa)")
    
    OPTION_DEBUG_CFG_DEFAULT = "1" 
    OPTION_DEBUG_CFG_CUSTOM = "2" 
    OPTION_DEBUG_CFG_ABORT = "3" 
    
    options_debug_cfg = {
        OPTION_DEBUG_CFG_DEFAULT: "Utilizar configuración predeterminada",
        OPTION_DEBUG_CFG_CUSTOM: "Utilizar configuración personalizada",
    }
    option = wait_for_custom_choice(options_debug_cfg,OPTION_DEBUG_CFG_CUSTOM)
    
    if option == OPTION_DEBUG_CFG_DEFAULT:
        generate_openocd_debug_file(use_default_content=True)
    
    # Parsear OpenOCD_debug.cfg
    # - Si validamos si el archivo esta vacio -> ERROR
    elif option == OPTION_DEBUG_CFG_CUSTOM:
        set_custom_debug_config_file()
    
    return (parse_config_file(PATH_SEMIHOSTING_DATA_FILE_TEMPLATE), PATH_OPENOCD_DEBUG_FILE)     
# ---------------------------------------------------------------------------- #

def normalize_path(path):
    normalized_path = os.path.normpath(path)
    if os.name == 'nt': 
        return normalized_path.replace('\\','\\\\')
    else:
        return normalized_path.replace('\\','/')

if __name__ == "__main__":
     
    if(not is_script_first_run()):
        not_first_run_msg()
        exit(0)
        
    welcome_msg()    
    
    semihosting_data, path_to_OpenOCD_debug_cfg = get_input_data()
    
    remove_syscall_link()
    print(prRed(">>> [REMOVE]") + " - Se elimina de la lista de compilacion y linking syscalls.c")
    
    add_linking_options(GCC_ARM_NONE_EABI_LINKER_OPTIONS)
    print(prGreen(">>> [ADD]   ") + " - Se agregan flags de linking para rdimon")
    print(prGreen(">>> [ADD]   ") + " - Se agregan flags de linking para evitar syscalls manejadas por el target")
    
    add_OpenOCD_server(
        open_ocd_server_path=normalize_path(semihosting_data['path_to_OpenOCD']),
        open_ocd_scripts_path=normalize_path(semihosting_data['path_to_OpenOCD_scripts']),
        open_ocd_debug_cfg_path=normalize_path(path_to_OpenOCD_debug_cfg),
        target_mcu_reference=semihosting_data['mcu_reference'],
        target_mcu_svd_path=semihosting_data['mcu_target_svd'],
    )
    print(prGreen(">>> [ADD]   ") + " - Se configura el servidor de OpenOCD")
    print(prGreen(">>> [ADD]   ") + " - Se configura monitor en modo semihosting")



# PATH_SETTINGS_JSON = ".vscode/settings.json"  # Opcional si tiene instalada la extension "Task Buttons"