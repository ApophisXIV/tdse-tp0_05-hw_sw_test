# Archivo startup_stm32f103xb.s

En este archivo se definen la secuencia de inicialiazcion del microcontrolador.

- Define el vector de interrupciones disponibles 
- Define la función de reset
- Define la función de inicio del programa

Descripción de las secciones:
- `.text`: Contiene el código ejecutable del programa.
- `.data`: Contiene las variables inicializadas.
- `.bss`: Contiene las variables no inicializadas.
- `.isr_vector`: Contiene el vector de interrupciones.
- `.stack`: Define el tamaño de la pila del microcontrolador.

