# Taller de Sistemas Embebidos - 1C2025 - FIUBA
Trabajo Práctico N°: 0 - Proyecto N°: 01

## Problemas encontrados durante la práctica y algunos comentarios

_Activación del modo semihosting para debug_  
- Para utilizar el logger se debe emplear el debugger con printf y para hacerlo hay que configurar un par de cosas.
- **Recomiendo fuertemente** utilizar el script que desarrollé para configurar el semihosting y OpenOCD para utilizar printf https://github.com/ApophisXIV/FIUBA-TSE/blob/main/add_printf.py

_Inclusión de directorios dentro de los archivos app y linking_
- Al utilizar VSCode para el desarrollo mediante CMake activamente uno debe agregar la ruta de la carpeta app junto con sus archivos fuente (src)
- De otro modo los archivos que se encuentran dentro de App no serán compilados ni linkeados

Esto se hace de la siguiente manera: 
- Ir al archivo CMakelists.txt que está en el directorio raíz/root del proyecto
- **Opcional y recomendación**: `set(CMAKE_C_STANDARD 11)` cambiarlo a `set(CMAKE_C_STANDARD 99)` para utilizar el Standard C99
- Buscar la siguiente sección
  ```
  # Link directories setup
  target_link_directories(${CMAKE_PROJECT_NAME} PRIVATE
    ...
  )
  ```
- Agregar `app/` antes del paréntesis de cierre
- Buscar la siguiente sección
  ```
  target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ...
  )
  ```
- Agregar `file(GLOB APP_SOURCES "app/src/*.c")` antes de la inmediatamente antes de la sección. Esto permite obtener todos los paths de los archivos que matchean con la ruta pedida y sean .c (mirar wildcards)
- Agregar `${APP_SOURCES}` antes del paréntesis de cierre. Invocamos la variable que creamos llamada APP_SOURCES que contiene todas las rutas de los archivos .c de app/src
- Buscar la siguiente sección 
  ```
  # Add include paths
  target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
      ...
  )
  ```
- Agregar `app/inc` antes del paréntesis de cierre. Esto permite que podamos incluir los .h (archivos de cabecera / header files) sin necesidad de depender de una ruta absoluta o relativa simplente incluimos el archivo

