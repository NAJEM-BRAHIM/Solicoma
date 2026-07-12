# -*- coding: utf-8 -*-
"""
Pre-migración para virtual_boxes 19.0.1.0.1
Copia los datos del campo viejo `virtual_box` al campo nuevo `num_boxes`
ANTES de que Odoo cargue el nuevo modelo (donde virtual_box ya no existe).
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info("virtual_boxes: migrando datos virtual_box -> num_boxes")

    # Lista de (tabla, columna_vieja, columna_nueva)
    migrations = [
        ('stock_quant', 'virtual_box', 'num_boxes'),
        ('stock_move', 'virtual_box', 'num_boxes'),
        ('stock_move_line', 'virtual_box', 'num_boxes'),
        ('sale_order_line', 'virtual_box', 'num_boxes'),
        ('account_move_line', 'virtual_box', 'num_boxes'),
    ]

    for table, old_col, new_col in migrations:
        # Verificar que la columna vieja exista
        cr.execute("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, (table, old_col))
        if not cr.fetchone():
            _logger.info("  - %s.%s no existe, salto", table, old_col)
            continue

        # Verificar que la columna nueva exista (debería, viene del módulo nuevo)
        cr.execute("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, (table, new_col))
        if not cr.fetchone():
            # Si no existe la columna nueva todavía, créala
            cr.execute(
                'ALTER TABLE "%s" ADD COLUMN "%s" INTEGER DEFAULT 0' % (table, new_col)
            )

        # Copiar valores donde num_boxes sea 0 o NULL y virtual_box tenga valor
        cr.execute(
            'UPDATE "%s" SET "%s" = COALESCE("%s", 0) WHERE COALESCE("%s", 0) = 0 AND COALESCE("%s", 0) <> 0'
            % (table, new_col, old_col, new_col, old_col)
        )
        _logger.info("  - %s: %s filas migradas", table, cr.rowcount)

    # Migrar total_virtual_box -> total_boxes en account_move
    cr.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'account_move' AND column_name = 'total_virtual_box'
    """)
    if cr.fetchone():
        # total_boxes en el nuevo código es compute store=False, así que no migramos,
        # sólo limpiamos el campo viejo al final.
        _logger.info("  - account_move.total_virtual_box detectado (se borrará en post)")

    _logger.info("virtual_boxes: pre-migración completada")
