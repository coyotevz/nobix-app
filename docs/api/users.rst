.. _api/users:

Usuarios
========

.. http:get:: /users

    Solicita una lista de usuarios.

    **Respuesta:**

    .. sourcecode:: http+json

        HTTP/1.1 200 OK

        {"objects":
          [{
            "id": 1,
            "username": "augusto",
            "email": "augusto@roccasalva.com.ar",
            "name": "Augusto Roccasalva",
            "state": "active",
            "created_at": "2012-05-23T08:00:58Z",
            "bio": null
          }]
        }
