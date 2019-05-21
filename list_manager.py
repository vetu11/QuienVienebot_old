# coding=utf-8
# Archivo: list_manager
# Autor: Ventura Pérez García - vetu@pm.me - github.com/vetu11
# Fecha última edición: 8/10
# Descripción: Describe la clase que se encargará de manejar las listas.

import json
from lista import Lista


class ListManager:

    def __init__(self):
        self.lists = {}

        with open("lists.json") as f:
            crude_lists = json.load(f)

        for list in crude_lists:
            self.lists[list["id"]] = Lista(**list)

    def guardar(self):
        # Guardar las listas
        # TODO: aún no ha sido probada

        crude_lists = []

        for lista in self.lists:
            crude_lists.append(vars(lista))

        with open("lists.json", "w") as f:
            json.dump(crude_lists, f, indent=2, ensure_ascii=False)
