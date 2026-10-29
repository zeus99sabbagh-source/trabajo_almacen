***Guía Paso a Paso para el Usuario Final***   

Estimado cliente, esta guía detallada le enseñará a operar de forma sencilla, eficiente y totalmente segura nuestro sistema de control logístico, diseñado específicamente para optimizar el almacenamiento de mercancía y el despacho de transporte de su empresa.   

*¿Cómo iniciar el programa?*
Asegúrese de tener Python correctamente instalado en su computadora. Abra su ventana de ejecución y ejecute el archivo del sistema escribiendo la instrucción correspondiente. Al iniciar la ejecución correctamente, verá aparecer de forma inmediata en su pantalla el menú principal que despliega todas las opciones disponibles para la gestión operativa.  

***Descripción detallada de las Opciones del Menú***  

1. Apilar caja
Para qué sirve: Permite registrar de manera formal el ingreso de una nueva caja de mercancía al almacén interno, el cual se encuentra estructurado bajo el estricto método LIFO (Last In, First Out — el último elemento en entrar es obligatoriamente el primero en salir).
Cómo usarlo: Seleccione la opción. A continuación, el sistema le solicitará que escriba el nombre, código o identificador único de la caja. Tras esto, el sistema procesará la solicitud y le confirmará en pantalla que la caja ha sido colocada de manera exitosa en la cima de la pila.

2. Retirar caja de la cima
Para qué sirve: Extrae y saca del sistema operativo la última caja que fue colocada o apilada en el almacén, respetando la lógica de la estructura LIFO.
Cómo usarlo: Seleccione la opción. El sistema procesará la instrucción y le mostrará en pantalla el nombre exacto de la caja que ha sido extraída, informándole además cuál pasa a ser la nueva cima resultante del inventario.
Nota de seguridad y control: En caso de que intente retirar un elemento cuando el almacén se encuentre completamente vacío, el sistema no se cerrará ni generará fallos técnicos; en su lugar, le mostrará de forma inmediata un aviso claro y descriptivo indicando que no hay elementos disponibles para retirar.

3. Llegada de camión
Para qué sirve: Registra de manera formal la llegada de un nuevo vehículo de transporte a la bahía de carga y espera. Esta sección opera bajo el método FIFO (First In, First Out — el primero en llegar es estrictamente el primero en ser atendido y despachado).
Cómo usarlo: Seleccione la opción. El sistema le pedirá que ingrese la placa, matrícula o identificador oficial del camión. El sistema le confirmará con un mensaje en pantalla que el vehículo se encuentra debidamente formado y en espera dentro de la fila de la bahía.

4. Despachar primer camión
Para qué sirve: Atiende, procesa y despacha de manera definitiva al camión que lleva más tiempo esperando en la cola de la bahía de transporte.
Cómo usarlo: Seleccione la opción. El sistema le indicará con precisión cuál camión ha sido despachado con éxito y cuál vehículo pasa a ocupar el siguiente turno al frente de la cola.
Nota de seguridad y control: Si la fila de la bahía se encuentra vacía al momento de solicitar un despacho, el programa le notificará amablemente que no hay camiones en espera, protegiendo la estabilidad operativa del software contra interrupciones inesperadas.

5. Ver estado almacén y camiones
Para qué sirve: Funciona como una radiografía esquemática completa en tiempo real que le permite visualizar gráficamente cuántas cajas hay apiladas y qué camiones continúan formados en la fila. Esta vista se complementa con estadísticas detalladas de transacciones acumuladas y el registro de la bitácora reciente.
Cómo usarlo: Seleccione la opción. Visualice de forma clara en la pantalla el listado actualizado de su inventario físico y del transporte logístico.

6. Salir
Para qué sirve: Permite cerrar de manera ordenada y totalmente segura la aplicación informática.
Cómo usarlo: Seleccione la opción para finalizar la ejecución. *(Importante: si al momento de intentar cerrar la aplicación aún existen elementos activos dentro del almacén o la fila, el sistema le solicitará una confirmación adicional antes de apagarse, previniendo así cualquier pérdida accidental de información operativa)*.

***Recomendaciones adicionales de Uso y Manejo Integral de Errores***

Protección avanzada contra errores humanos: El programa ha sido diseñado y configurado con múltiples capas de validación para garantizar que bajo ninguna circunstancia se cierre de manera abrupta por fallos de introducción de datos. Si por equivocación ingresa un valor incorrecto, deja el espacio completamente en 
blanco o selecciona una opción numérica que se encuentre fuera del rango válido permitido, el sistema le mostrará un mensaje descriptivo detallando el error y volverá a desplegar el menú principal de manera automática para permitirle continuar trabajando sin contratiempos.   

Garantía de integridad de los datos: Es fundamental recordar siempre que las cajas dentro de la bodega siguen estrictamente el orden LIFO, lo que significa que por seguridad física del almacenamiento no es posible retirar elementos intermedios sin antes haber extraído los que se encuentran posicionados exactamente encima; 
de igual forma, los camiones operan bajo un estricto orden secuencial FIFO.  

Modos de ejecución alternativos avanzados: Si su equipo cuenta con un entorno gráfico compatible y desea una experiencia visual mucho más atractiva, moderna y fluida, puede ejecutar el sistema en modo gráfico utilizando el parámetro visual correspondiente;
asimismo, si prefiere probar el comportamiento del software de manera inmediata sin necesidad de ingresar datos de forma manual, puede iniciar la aplicación con un conjunto de datos de prueba precargados agregando el parámetro opcional de demostración.   
