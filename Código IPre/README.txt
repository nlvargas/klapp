Como el archivo tiene cuatro códigos distintos,es importante que estén todos en la misma carpeta para funcionar.
Los códigos utilizan Python 3, Gurobi, librería Pandas y librería Numpy.

El archivo que se quiera leer debe encontrarse en una carpeta llamada "Muestras" 
ya que, el código "new_app" funciona de esa forma.

Los archivos .txt de parametros y de clusters deben estar en la misma carpeta
en la que se encuentran los códigos. Se adjuntan archivos a modo de ejemplo

El código que se debe correr es "new_app". 
Si se quiere realizar algún tipo de cambio en el modelo se debe revisar el código "main".
Si se quiere cambiar el tiempo máximo para resolver o el Gap permitido se debe revisar el código "custom".

Después de correr el código se arrojará un archivo excel con las asignaciones y 
la información de cada alumno, este aparecerá en la misma carpeta en la que se encuentren los códigos.
El archivo se sobreescribe cada vez que se corra el código y encuentre solución.

Los códigos se encuentran comentados explicando la función que cumplen. 
