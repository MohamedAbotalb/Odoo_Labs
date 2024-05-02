from odoo import models, fields

class Doctor(models.Model):
    _name = 'hms.doctor'
    _rec_name = 'first_name'
    

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    image = fields.Binary(string='Image', help='image')
    department_id = fields.Many2one(comodel_name='hms.department', string='Department')
