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

Todas la peticiones ``POST`` y ``PATCH`` deben ser codificadas con JSON
y deben contener la definicion del tipo ``application/json``, caso contrario la
API devolverá un ``415 Unsupported Media Type`` status_messages

Verbos HTTP
~~~~~~~~~~~

Utilizamos los verbos estandares de HTTP para indicar la intención de una
petición.

* ``GET`` - solicita acceso a uno o más recursos y devuelve el resultado en
            formato JSON.

* ``POST`` - utilizada para crear nuevos recursos.

* ``PATCH`` - se utiliza para modificar un recuso especifico.

* ``DELETE`` - con este verbo se elimina un determinado recurso.

Códigos de Estado
~~~~~~~~~~~~~~~~~

Los códigos de estado se establecen de acuerdo al contexto y la acción
solicitada. De esta forma si una petición es erronea el que realizó la petición
tiene la posibilidad de investigar que es lo que estubo mal con la petición.
Los códigos de estado devueltos por cada uno de los verbos HTTP se enumeran a
continuación:

* ``200 Ok`` - Las solicitudes ``GET``, ``POST`` y ``DELETE`` han sido
  exitosas y el/los recursos son devueltos en el cuerpo del mensaje.

* ``201 Created`` - Es la respuesta a una petición ``POST`` exitosa y el
  recurso es devuelto en el cuerpo del mensaje.

* ``400 Bad Request`` - Falta un atributo requeredo por la solicitud API.

* ``401 Unauthorized`` - El usuario no ha sido autenticado, se requiere un
  *token* válido de usuario.

* ``403 Forbidden`` - La solicitud no está permitida.

* ``404 Not Found`` - El recurso no puede ser accedido porque no se encuentra.

* ``405 Method Not Allowed`` - La solicitud no es soportada para el método
  dado.

* ``409 Conflict`` - Existe un recurso que genera conflicto debido a las
  restricciones planteadas por el sistema.

* ``500 Server Error`` - Se produjo un error en el servidor mientras se
  procesaba la solicitud.

Respuestas
~~~~~~~~~~

Todas las respuestas contienen la definición del tipo ``application/json`` y su
cuerpo de mensaje esta codificado en JSON.

La representación JSON de un recurso simple es::

TODO: Write json representation
