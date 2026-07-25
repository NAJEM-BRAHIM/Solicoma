# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Al instalar el módulo genera para TODOS los modelos no transitorios:
      - ir.model.access : perm_read=True, write/create/unlink=False
      - ir.rule         : bloquea write/create/unlink con dominio siempre falso
                          [('id', '<', 0)] — ningún registro tiene ID negativo.

    El usuario debe estar también en 'base.group_user' (Usuario Interno)
    para poder acceder al backend. Las reglas de este grupo anulan los
    permisos de escritura que otros grupos pudieran conceder (las reglas
    entre grupos se combinan con AND en Odoo).
    """
    # Modelos excluidos de ir.rule (Odoo no permite reglas sobre sí mismo)
    MODELS_SIN_REGLA = {'ir.rule'}

    group = env.ref('solicoma_grupos.group_solo_lectura')
    all_models = env['ir.model'].search([('transient', '=', False)])

    AccessModel = env['ir.model.access'].sudo()
    RuleModel = env['ir.rule'].sudo()

    access_vals = []
    rule_vals = []

    for model in all_models:
        name_safe = model.model.replace('.', '_')

        # --- ir.model.access: solo lectura ---
        if not AccessModel.search([
            ('model_id', '=', model.id),
            ('group_id', '=', group.id),
        ], limit=1):
            access_vals.append({
                'name': f'access_solo_lectura_{name_safe}',
                'model_id': model.id,
                'group_id': group.id,
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            })

        # --- ir.rule: dominio imposible → bloquea write/create/unlink ---
        if model.model not in MODELS_SIN_REGLA and not RuleModel.search([
            ('model_id', '=', model.id),
            ('groups', 'in', [group.id]),
        ], limit=1):
            rule_vals.append({
                'name': f'rule_solo_lectura_{name_safe}',
                'model_id': model.id,
                'groups': [(4, group.id)],
                'domain_force': "[('id', '<', 0)]",
                'perm_read': False,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            })

    # Crear en batch para mayor rendimiento
    if access_vals:
        AccessModel.create(access_vals)
        _logger.info('Solo Lectura: %d registros ir.model.access creados.', len(access_vals))

    if rule_vals:
        RuleModel.create(rule_vals)
        _logger.info('Solo Lectura: %d reglas ir.rule creadas.', len(rule_vals))
