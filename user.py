# coding=utf-8
# Archivo: user
# Autor: vetu11
# Fecha última edición: 1/10/2018
# Descripción: Se define la clase User, que contiene las descripciónes minimas por parte de Telegram, y los datos
# adicionales generados por el bot.


class User:
    # Usuario de Telegram.

    def __init__(self, **kwargs):

        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.username = kwargs.get("username")
        self.id = kwargs.get("id")
        self.language_code = kwargs.get("language_code", "ES-es")
        self.full_name = kwargs.get("full_name")
        self.full_name_simple = kwargs.get("full_name_simple")

        assert self.first_name is not None, "Error al crear el usuario: first_name es None"
        assert self.id is not None, "Error al crear el usuario: id es None"

        # Check types
        if not isinstance(self.first_name, str) and isinstance(id, int):
            raise TypeError

        if self.full_name is None:
            self.create_full_name()

    def create_full_name(self):
        # crea las variables self.full_name y self.full_name_simple

        assert self.first_name is not None, "self.first_name es None"

        if self.last_name is None:
            self.full_name_simple = self.first_name
        else:
            self.full_name_simple = self.first_name + " " + self.last_name

        if self.username is None:
            self.full_name = self.full_name_simple
        else:
            self.full_name = "[%s](%s)" % (self.full_name_simple, self.username)

    def guardar(self):
        # Escribe los datos del usuario en un archivo.

        pass
