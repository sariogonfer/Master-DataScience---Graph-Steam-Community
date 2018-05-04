Este entregable se compone de los siguientes elementos:

- feeder.py: Script de Python que descarga los datos de la API de Steam y los guarda, en diferentes ficheros dentro de un mismo directorio.
- data: Directorio que contiene los datos descargados por el script anterior. Apartir de los datos que contine este directorio, se generan los ficheros que se utilizan en el resto de módulos. Es importante mantener la estructura.
- graph.py: Script de Python que procesa los datos recogidos de la API (los almacenados en ./data/) y genera estadísticas y los ficheros que se generarán en la visualización.
- StaticPages: En este directorio encontramos dos ejemplos de grafos creados con d3js, junto con los datos que necesita cargar en formato JSON.
- InteractiveServer: En este directorio se encuentra un servidor realizado con el framework Flask, el cual publica una presentación hecha con Reveal.js y que contiene dos grafos interactivos.

# Procesamiento de los datos.

Junto con el entregable se adjuntan los datos necesarios para poder visualizar los grafos. Aún así, en caso de querer ejecutar el script para procesar los datos, el comando a ejecutar sería:

python graph.py

Este script mostrará por pantalla información sobre el grafo utilizado y además, generará los ficheros necesarios para la visualización dentro de los directorios StaticPages e InteractiveServer.

# Servidor interactivo.

Para arrancar este servidor, unicamente debemos ejecutar el siguiente comando dentro del directorio InteractiveServer:

python steam.py

Una vez arrancado, podremos acceder desde cualquier navegador (se recomienda Chrome) a través de la URL http://localhost:5000
