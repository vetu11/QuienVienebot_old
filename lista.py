# coding=utf-8
# Archivo: lista
# Descipción: describe la clase Lista, que es una lista de amigos.

from uuid import uuid4
from time import time


class Lista:
    # Lista de amigos con distintos métodos para cambiar su voto.
    def __init__(self, **kwargs):

        self.text = kwargs.get("text")
        self.id = kwargs.get("id", str(uuid4()))
        self.from_user_id = kwargs.get("from_user_id")
        self.date = kwargs.get("date", time())
        self.list = []
