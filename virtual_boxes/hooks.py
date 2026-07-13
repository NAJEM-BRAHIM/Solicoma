# -*- coding: utf-8 -*-
"""
Hooks de instalación/actualización para virtual_boxes.

post_init_hook: se ejecuta tanto en instalación nueva como en actualización,
a diferencia de los scripts de migración (que solo corren en upgrade cuando
había una versión previa en la base de datos).

Limpia los registros obsoletos del campo 'virtual_box' que pueden haber quedado
de los módulos anteriores sis_cajavirtual o de la versión vieja de virtual_boxes.
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


def post_init_hook(env):
    """Limpia vistas y campos obsoletos del campo 'virtual_box'."""
    cr = env.cr
    _logger.info("virtual_boxes: post_init_hook — limpiando registros obsoletos de 'virtual_box'")

    stale_ids = set()

    # 1. Vistas cuyo arch contiene <field name="virtual_box" (sin 'use_')
    cr.execute("""
        SELECT id, name, model
        FROM ir_ui_view
        WHERE arch_db::text LIKE %s
    """, ('%name="virtual_box"%',))
    for view_id, name, model in cr.fetchall():
        _logger.info("  - Vista obsoleta (arch): id=%s name=%r model=%s", view_id, name, model)
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

    # 5. Limpiar ir_model_data de sis_cajavirtual (vistas y campos)
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

    _logger.info("virtual_boxes: post_init_hook completado")
