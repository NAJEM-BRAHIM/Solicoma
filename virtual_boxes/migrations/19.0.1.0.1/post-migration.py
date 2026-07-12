# -*- coding: utf-8 -*-
"""
Post-migración para virtual_boxes 19.0.1.0.1
Elimina las columnas huérfanas del sistema viejo `virtual_box`
DESPUÉS de que los datos hayan sido copiados a `num_boxes` en pre-migration.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info("virtual_boxes: eliminando columnas obsoletas virtual_box")

    columns_to_drop = [
        ('stock_quant', 'virtual_box'),
        ('stock_move', 'virtual_box'),
        ('stock_move_line', 'virtual_box'),
        ('sale_order_line', 'virtual_box'),
        ('account_move_line', 'virtual_box'),
        ('account_move', 'total_virtual_box'),
    ]

    for table, column in columns_to_drop:
        cr.execute("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, (table, column))
        if cr.fetchone():
            try:
                cr.execute('ALTER TABLE "%s" DROP COLUMN "%s" CASCADE' % (table, column))
                _logger.info("  - DROP %s.%s OK", table, column)
            except Exception as e:
                _logger.warning("  - DROP %s.%s falló: %s", table, column, e)

    # Limpiar entradas en ir_model_fields que apunten a campos virtual_box
    cr.execute("""
        DELETE FROM ir_model_fields
        WHERE name IN ('virtual_box', 'total_virtual_box')
          AND model IN (
              'stock.quant', 'stock.move', 'stock.move.line',
              'sale.order.line', 'account.move.line', 'account.move'
          )
    """)
    _logger.info("  - %s registros ir_model_fields limpiados", cr.rowcount)

    _logger.info("virtual_boxes: post-migración completada")
