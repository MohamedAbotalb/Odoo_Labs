from odoo import api, models, fields
    
    
class Patient(models.Model):
    _name = 'hms.patient'
    _rec_name = 'first_name'
    
    STATES = [
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious'),
    ]

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    birth_date = fields.Date(string='Birth Date')
    history = fields.Html(string='History')
    cr_ratio = fields.Float(string='CR Ratio')
    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ], string='Blood Type')
    pcr = fields.Boolean(string='PCR')
    image = fields.Binary(string='Image', help='image')
    address = fields.Text(string='Address')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    department_id = fields.Many2one('hms.department', string='Department', domain="[('is_opened', '=', False)]")
    department_capacity = fields.Integer(string='Department Capacity', related='department_id.capacity', readonly=True)
    doctor_ids = fields.Many2many(comodel_name='hms.doctor', string='Doctors', readonly=True)
    log_history = fields.Text(string='Log History')
    state = fields.Selection(STATES, string='State', default='undetermined')
    
    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = fields.Date.today()
                record.age = today.year - record.birth_date.year - ((today.month, today.day) < (record.birth_date.month, record.birth_date.day))
            else:
                record.age = 0
    
    @api.onchange('age')
    def warning_PCR(self):
        for record in self:
            if record.age < 30:
                record.pcr = True
                return { 
                    'warning': {'title': 'PCR Message', 'message': 'PCR field has been automatically checked '}
                }
            else:
                record.pcr = False
                
