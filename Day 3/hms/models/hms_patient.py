import re
from odoo import api, models, fields
from odoo.exceptions import ValidationError
    
    
class PatientLogHistory(models.Model):
    _name = 'hms.patient.log.history'
    
    description = fields.Text(string='Description')
    patient_id = fields.Many2one('hms.patient', string='Patient')

    
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
    log_history_ids = fields.One2many('hms.patient.log.history', 'patient_id', string='Log History')
    state = fields.Selection(STATES, string='State', default='undetermined')
    email = fields.Char(string='Email', required=True, unique=True)
    
    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'The email address must be unique.'),
    ]
    
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
                
    @api.onchange('history')
    def change_history_log(self):
        vals = {
            'description': 'History field updated for patient %s'%(self.first_name),
            'patient_id': self.id,
        }
        self.env['hms.patient.log.history'].create(vals)
        
    @api.constrains('email')
    def _check_email_format(self):
        for record in self:
            if record.email and not self._is_valid_email(record.email):
                raise ValidationError("Invalid email format for %s" % record.email)

    def _is_valid_email(self, email):
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+(\.[\w]+)+$', email))
    
    def _check_unique_email(self, email):
        existing_patient = self.env['hms.patient'].search([('email', '=', email)])
        return bool(existing_patient)
    
    @api.constrains('email')
    def _check_unique_email_constraint(self):
        for patient in self:
            if patient.email and self._check_unique_email(patient.email):
                raise ValidationError('Email address already exists.')
                
    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = fields.Date.today()
                record.age = today.year - record.birth_date.year - ((today.month, today.day) < (record.birth_date.month, record.birth_date.day))
            else:
                record.age = 1
