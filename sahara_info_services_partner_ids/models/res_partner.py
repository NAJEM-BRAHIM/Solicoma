# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_ma_ice = fields.Char(
        string="ICE",
        help="Identifiant Commun de l'Entreprise (15 chiffres)",
    )
    l10n_ma_nif = fields.Char(
        string="NIF",
        help="Numéro d'Identification Fiscale",
    )
    l10n_ma_rc = fields.Char(
        string="RC",
        help="Registre de Commerce",
    )

    # Odoo 19: models.Constraint reemplaza a _sql_constraints (deprecado)
    _unique_l10n_ma_ice = models.Constraint(
        'UNIQUE(l10n_ma_ice)',
        'El ICE ya existe en otro partner. Debe ser único.',
    )
    _unique_l10n_ma_nif = models.Constraint(
        'UNIQUE(l10n_ma_nif)',
        'El NIF ya existe en otro partner. Debe ser único.',
    )
    _unique_l10n_ma_rc = models.Constraint(
        'UNIQUE(l10n_ma_rc)',
        'El RC ya existe en otro partner. Debe ser único.',
    )

    @api.constrains('l10n_ma_ice')
    def _check_l10n_ma_ice_uniqueness(self):
        for partner in self:
            if partner.l10n_ma_ice:
                duplicate = self.search([
                    ('l10n_ma_ice', '=', partner.l10n_ma_ice),
                    ('id', '!=', partner.id),
                ], limit=1)
                if duplicate:
                    raise ValidationError(_(
                        'El ICE "%s" ya está asignado al partner "%s". '
                        'Debe ser único.'
                    ) % (partner.l10n_ma_ice, duplicate.display_name))

    @api.constrains('l10n_ma_nif')
    def _check_l10n_ma_nif_uniqueness(self):
        for partner in self:
            if partner.l10n_ma_nif:
                duplicate = self.search([
                    ('l10n_ma_nif', '=', partner.l10n_ma_nif),
                    ('id', '!=', partner.id),
                ], limit=1)
                if duplicate:
                    raise ValidationError(_(
                        'El NIF "%s" ya está asignado al partner "%s". '
                        'Debe ser único.'
                    ) % (partner.l10n_ma_nif, duplicate.display_name))

    @api.constrains('l10n_ma_rc')
    def _check_l10n_ma_rc_uniqueness(self):
        for partner in self:
            if partner.l10n_ma_rc:
                duplicate = self.search([
                    ('l10n_ma_rc', '=', partner.l10n_ma_rc),
                    ('id', '!=', partner.id),
                ], limit=1)
                if duplicate:
                    raise ValidationError(_(
                        'El RC "%s" ya está asignado al partner "%s". '
                        'Debe ser único.'
                    ) % (partner.l10n_ma_rc, duplicate.display_name))
