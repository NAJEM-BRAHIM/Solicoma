# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .damancom_utils import validate_num_affilie


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_ma_cnss_num_affilie = fields.Char(
        string="N° Affiliation CNSS",
        help="Numéro d'affiliation CNSS de l'entreprise (7 chiffres). "
             "La clé de contrôle est validée selon l'algorithme officiel CNSS.",
    )
    l10n_ma_cnss_code_agence = fields.Char(
        string="Code Agence CNSS",
        help="Code de l'agence CNSS (2 chiffres). "
             "Communiqué par la CNSS lors de l'affiliation.",
    )
    l10n_ma_cnss_activite = fields.Char(
        string="Activité CNSS",
        help="Libellé de l'activité de l'entreprise tel que déclaré à la CNSS.",
    )
    l10n_ma_cnss_code_postal = fields.Char(
        string="Code Postal CNSS",
    )

    @api.constrains('l10n_ma_cnss_num_affilie')
    def _check_num_affilie(self):
        for company in self:
            if company.l10n_ma_cnss_num_affilie:
                valid, msg = validate_num_affilie(company.l10n_ma_cnss_num_affilie)
                if not valid:
                    raise ValidationError(
                        _("N° d'affiliation CNSS invalide pour %s: %s") % (
                            company.name, msg
                        )
                    )
