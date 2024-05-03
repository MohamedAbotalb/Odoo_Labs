from odoo import models, fields

    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one('hms.patient', string='Related Patient', unique=True, required=True)
    vat = fields.Char(string='Tax ID', required=True)

    _sql_constraints = [
        ('unique_related_patient_id', 'UNIQUE (related_patient_id)', 'The related patient must be unique.'),
        ('check_related_patient_id', 'CHECK (related_patient_id IS NOT NULL)', 'The related patient must be specified.'),
    ]