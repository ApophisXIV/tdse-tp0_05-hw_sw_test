# Taller de Sistemas Embebidos - 1C2025 - FIUBA
Trabajo Práctico N°: 0 - Proyecto N°: 01

## Problemas encontrados durante la práctica y algunos comentarios

### _Activación del modo semihosting para debug_  
- Para utilizar el logger se debe emplear el debugger con printf y para hacerlo hay que configurar un par de cosas.
- **Recomiendo fuertemente** utilizar el script que desarrollé para configurar el semihosting y OpenOCD para utilizar printf https://github.com/ApophisXIV/FIUBA-TSE/blob/main/add_printf.py

### _Inclusión de directorios dentro de los archivos app y linking_
- Al utilizar VSCode para el desarrollo mediante CMake activamente uno debe agregar la ruta de la carpeta app junto con sus archivos fuente (src)
- De otro modo los archivos que se encuentran dentro de App no serán compilados ni linkeados

Esto se hace de la siguiente manera: 
- Ir al archivo CMakelists.txt que está en el directorio raíz/root del proyecto
- **Opcional y recomendación**: `set(CMAKE_C_STANDARD 11)` cambiarlo a `set(CMAKE_C_STANDARD 99)` para utilizar el Standard C99
- **Opcional:** Buscar la siguiente sección para agregar `libs` (bibliotecas propias y/o externas)

  Agregar `app/lib` antes del paréntesis de cierre
  ```cmake
  # Link directories setup
  target_link_directories(${CMAKE_PROJECT_NAME} PRIVATE
    ...
  )
  ```
- Buscar la siguiente sección para agregar los archivos fuente de la aplicación
  
  Agregar `file(GLOB APP_SOURCES "app/src/*.c")` inmediatamente antes de la sección. Esto permite obtener y guardar en la variable `APP_SOURCES` todos los paths de los archivos que matchean con la ruta pedida y sean .c (mirar wildcards)
  
  Agregar `${APP_SOURCES}` antes del paréntesis de cierre. Invocamos la variable que creamos llamada APP_SOURCES que contiene todas las rutas de los archivos .c de app/src
  ```cmake
  target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ...
  )
  ```
- Buscar la siguiente sección para agregar los `headers` (archivos de cabecera) 

  Agregar `app/inc` antes del paréntesis de cierre. Esto permite que podamos incluir los .h (archivos de cabecera / header files) sin necesidad de depender de una ruta absoluta o relativa simplente incluimos el archivo
  ```cmake
  # Add include paths
  target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
      ...
  )
  ```

  Finalmente los cambios resultan en:

  ```cmake
  # Link directories setup
  target_link_directories(${CMAKE_PROJECT_NAME} PRIVATE
      # Add user defined library search paths
      app/lib
  )

  # Add sources to executable (all C files in app/src)
  file(GLOB APP_SOURCES "app/src/*.c")
  target_sources(${CMAKE_PROJECT_NAME} PRIVATE 
      ${APP_SOURCES}
  )

  # Add include paths
  target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
      app/inc
  )

  ```

### _Problemas con intellisense_

- Es habitual que intellisense tenga problemas con algunas definiciones internas de la HAL pues en el IDE se encuentra definido de forma automática el `define` correspondiente al microcontrolador utilizado. De este modo, debemos hacerlo de forma manual (por ahora no encontré la forma oficial de hacerlo). En el archivo `c_cpp_properties.json` en la carpeta `.vscode` debemos agregar:  
  ```json
  "includePath": [
      "${workspaceFolder}/**"
  ],
  "defines": [
      "STM32F103xB" // En el caso de usar la NUCLEO103
  ],
  ```
