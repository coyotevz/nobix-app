.. _api:

Nobix Application Server API
============================

Todas las peticiones a la API requieren autenticación, más información en ...

Nuestra API utiliza URLs orientada a recursos que aprovechan las
caracteristicas de HTTP, como autenticación, verbos y códigos de respuesta.
Todos los cuerpos de petición y respuesta se codifican/decodifican con JSON,
incluyendo las respuestas de error.

Petición
--------

La URL base de esta API es ``http://<server>/api/v1`` donde ``<server>`` debe ser
reeplazado por el nombre de servidor que corre Nobix Application Server.

Cuerpo
~~~~~~

Todas la peticiones ``POST``, ``PUT``, ``PATCH`` deben ser codificadas con JSON
y deben contener la definicion del tipo ``application/json``, caso contrario la
API devolverá un ``415 Unsupported Media Type`` status_messages

Verbos HTTP
~~~~~~~~~~~

Utilizamos los verbos estandares de HTTP para indicar la intención de una
petición.

* ``GET`` - solicita acceso a uno o más recursos y devuelve como resultado en
            formato JSON.

* ``POST`` - utilizada para crear recursos nuevos.

* ``GET``, ``PUT`` - FIXME:continuar aqui...
