Como el archivo tiene cuatro c�digos distintos,es importante que est�n todos en la misma carpeta para funcionar.
Los c�digos utilizan Python 3, Gurobi, librer�a Pandas y librer�a Numpy.

El archivo que se quiera leer debe encontrarse en una carpeta llamada "Muestras" 
ya que, el c�digo "new_app" funciona de esa forma.

Los archivos .txt de parametros y de clusters deben estar en la misma carpeta
en la que se encuentran los c�digos. Se adjuntan archivos a modo de ejemplo

El c�digo que se debe correr es "new_app". 
Si se quiere realizar alg�n tipo de cambio en el modelo se debe revisar el c�digo "main".
Si se quiere cambiar el tiempo m�ximo para resolver o el Gap permitido se debe revisar el c�digo "custom".

Despu�s de correr el c�digo se arrojar� un archivo excel con las asignaciones y 
la informaci�n de cada alumno, este aparecer� en la misma carpeta en la que se encuentren los c�digos.
El archivo se sobreescribe cada vez que se corra el c�digo y encuentre soluci�n.

Los c�digos se encuentran comentados explicando la funci�n que cumplen. 
