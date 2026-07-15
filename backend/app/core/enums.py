"""Enumeraciones compartidas de dominio."""

from enum import IntEnum


class EstadoTransaccion(IntEnum):
    """Estados de transacción usados en la lógica de negocio.

    Deuda semántica conocida: el seed SQL (``dbflash.sql``) inserta id=1 como
    ``Pendiente`` en ``tbestado``, pero ``payments_worker`` y ``saldo_pendiente``
    usan id_estado=1 para transacciones fallidas por saldo insuficiente.
    """

    FALLIDO = 1
    EN_ESPERA = 2
    COMPLETADA = 3
