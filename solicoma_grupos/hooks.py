# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

# Modelos que no admiten ir.rule (Odoo lo prohíbe explícitamente)
MODELS_SIN_REGLA = {'ir.rule'}


def post_init_hook(env):
    """
    Al instalar el módulo genera para TODOS los modelos no transitorios:
      - ir.model.access : perm_read=True, write/create/unlink=False
      - ir.rule         : bloquea write/create/unlink con dominio [('id','<',0)]
                          (ningún registro tiene ID negativo → bloqueo total)

    El usuario debe estar también en 'base.group_user' (Usuario Interno)
    para acceder al backend. Las ir.rule de este grupo se combinan con AND
    con las de otros grupos, anulando cualquier permiso de escritura heredado.
    """
    group = env.ref('solicoma_grupos.group_solo_lectura')
    all_models = env['ir.model'].search([('transient', '=', False)])

    # ir.model.access: sin sudo() porque el modelo tiene _allow_sudo_commands=False
    AccessModel = env['ir.model.access']
    # ir.rule: con sudo() para saltar restricciones de escritura en meta-modelos
    RuleModel = env['ir.rule'].sudo()

    # --- ir.model.access: batch (sin validaciones complejas, es seguro) ---
    access_vals = []
    for model in all_models:
        name_safe = model.model.replace('.', '_')
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

    if access_vals:
        AccessModel.create(access_vals)
        _logger.info('Solo Lectura: %d registros ir.model.access creados.', len(access_vals))

    # --- ir.rule: uno a uno para aislar errores por modelo ---
    rule_ok = 0
    rule_skip = 0
    for model in all_models:
        if model.model in MODELS_SIN_REGLA:
            continue
        name_safe = model.model.replace('.', '_')
        if RuleModel.search([
            ('model_id', '=', model.id),
            ('groups', 'in', [group.id]),
        ], limit=1):
            continue
        try:
            RuleModel.create({
                'name': f'rule_solo_lectura_{name_safe}',
                'model_id': model.id,
                'groups': [(4, group.id)],
                'domain_force': "[('id', '<', 0)]",
                'perm_read': False,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            })
            rule_ok += 1
        except Exception as e:
            _logger.warning(
                'Solo Lectura: no se pudo crear regla para %s: %s',
                model.model, e,
            )
            rule_skip += 1

    _logger.info(
        'Solo Lectura: %d reglas ir.rule creadas, %d omitidas.',
        rule_ok, rule_skip,
    )
