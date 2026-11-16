"""
cliente.py
----------
Clase Cliente con validaciones estrictas y datos personales encapsulados.
"""

import re

from entidad import Entidad
from excepciones import ClienteInvalidoError


class Cliente(Entidad):
    """Cliente de Software FJ."""

    _PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,60}$")
    _PATRON_DOCUMENTO = re.compile(r"^\d{6,10}$")
    _PATRON_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
    _PATRON_TELEFONO = re.compile(r"^\+?\d{7,13}$")

    def __init__(self, nombre, documento, email, telefono):
        super().__init__("CLI")
        # Se asigna a través de los setters para validar cada dato.
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono

    # ---------------- nombre ----------------
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ClienteInvalidoError("El nombre es obligatorio y debe ser texto.")
        valor = " ".join(valor.split())
        if not self._PATRON_NOMBRE.match(valor):
            raise ClienteInvalidoError(
                f"Nombre inválido '{valor}': solo letras y espacios (3 a 60 caracteres)."
            )
        self.__nombre = valor.title()

    # ---------------- documento ----------------
    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor):
        valor = str(valor).strip() if valor is not None else ""
        if not self._PATRON_DOCUMENTO.match(valor):
            raise ClienteInvalidoError(
                f"Documento inválido '{valor}': debe tener entre 6 y 10 dígitos."
            )
        self.__documento = valor

    # ---------------- email ----------------
    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor):
        if not isinstance(valor, str) or not self._PATRON_EMAIL.match(valor.strip()):
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self.__email = valor.strip().lower()

    # ---------------- teléfono ----------------
    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        limpio = re.sub(r"[\s-]", "", str(valor)) if valor is not None else ""
        if not self._PATRON_TELEFONO.match(limpio):
            raise ClienteInvalidoError(
                f"Teléfono inválido '{valor}': entre 7 y 13 dígitos."
            )
        self.__telefono = limpio

    # ---------------- privacidad ----------------
    @property
    def documento_protegido(self) -> str:
        """Documento enmascarado para mostrar en pantalla o logs."""
        return "*" * (len(self.__documento) - 4) + self.__documento[-4:]

    @property
    def email_protegido(self) -> str:
        usuario, dominio = self.__email.split("@")
        return f"{usuario[0]}***@{dominio}"

    # ---------------- contrato de Entidad ----------------
    def validar(self) -> bool:
        for campo in ("nombre", "documento", "email", "telefono"):
            if not getattr(self, campo, None):
                raise ClienteInvalidoError(f"El cliente no tiene '{campo}'.")
        return True

    def describir(self) -> str:
        return (f"Cliente {self.id}: {self.nombre} | Doc: {self.documento_protegido}"
                f" | Email: {self.email_protegido}")
