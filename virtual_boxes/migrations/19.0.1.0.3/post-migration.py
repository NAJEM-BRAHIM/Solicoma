# -*- coding: utf-8 -*-
"""
Post-migración para virtual_boxes 19.0.1.0.3

Misma limpieza que la post_init_hook pero ejecutada en el camino de upgrade,
garantizando que se ejecuta aunque la BD ya estuviera en 19.0.1.0.2.

En Odoo 19, ir_ui_view NO tiene columna 'module'; la referencia del módulo
está en ir_model_data (module, model='ir.ui.view', res_id=view_id).
"""
import logging

_logger = logging.getLogger(__name__)

AFFECTED_MODELS = [
    'stock.move',
    'stock.move.line',
    'stock.picking',
    'stock.quant',
    'sale.order.line',
    'account.move',
    'account.move.line',
]


def migrate(cr, version):
    _logger.info(
        "virtual_boxes 19.0.1.0.3: limpiando registros obsoletos del campo 'virtual_box'"
    )

    stale_ids = set()

    # 1. Vistas con arch que referencian el campo obsoleto 'virtual_box'
    cr.execute("""
        SELECT id, name, model
        FROM ir_ui_view
        WHERE arch_db::text LIKE %s
    """, ('%name="virtual_box"%',))
    for view_id, name, model in cr.fetchall():
        _logger.info(
            "  - Vista obsoleta (arch): id=%s name=%r model=%s", view_id, name, model
        )
        stale_ids.add(view_id)

    # 2. Vistas registradas bajo el módulo 'sis_cajavirtual'
    cr.execute("""
        SELECT imd.res_id, v.name, v.model
        FROM ir_model_data imd
        JOIN ir_ui_view v ON v.id = imd.res_id
        WHERE imd.module = 'sis_cajavirtual'
          AND imd.model = 'ir.ui.view'
    """)
    for view_id, name, model in cr.fetchall():
        if view_id not in stale_ids:
            _logger.info(
                "  - Vista obsoleta (sis_cajavirtual): id=%s name=%r model=%s",
                view_id, name, model,
            )
            stale_ids.add(view_id)

    # 3. Eliminar las vistas obsoletas
    if stale_ids:
        ids_list = list(stale_ids)
        cr.execute(
            "UPDATE ir_ui_view SET inherit_id = NULL WHERE inherit_id = ANY(%s)",
            (ids_list,),
        )
        cr.execute("DELETE FROM ir_ui_view WHERE id = ANY(%s)", (ids_list,))
        _logger.info("  - %s vista(s) obsoleta(s) eliminada(s)", len(ids_list))
    else:
        _logger.info("  - No se encontraron vistas obsoletas con campo 'virtual_box'")

    # 4. Limpiar ir_model_fields huérfanos del campo 'virtual_box'
    cr.execute("""
        DELETE FROM ir_model_fields
        WHERE name = 'virtual_box'
          AND model = ANY(%s)
    """, (AFFECTED_MODELS,))
    if cr.rowcount:
        _logger.info("  - %s registro(s) ir_model_fields eliminado(s)", cr.rowcount)

    # 5. Limpiar ir_model_data de sis_cajavirtual
    cr.execute("""
        DELETE FROM ir_model_data
        WHERE module = 'sis_cajavirtual'
          AND model IN ('ir.ui.view', 'ir.model.fields')
    """)
    if cr.rowcount:
        _logger.info("  - %s registro(s) ir_model_data de sis_cajavirtual eliminado(s)", cr.rowcount)

    # 6. Marcar sis_cajavirtual como desinstalado
    cr.execute("""
        UPDATE ir_module_module
        SET state = 'uninstalled'
        WHERE name = 'sis_cajavirtual'
          AND state IN ('installed', 'to upgrade', 'to remove')
    """)
    if cr.rowcount:
        _logger.info("  - Módulo 'sis_cajavirtual' marcado como 'uninstalled'")

    _logger.info("virtual_boxes 19.0.1.0.3: post-migración completada")
