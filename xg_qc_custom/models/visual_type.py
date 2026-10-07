from odoo import models, fields,api

class VisualType(models.Model):
    _name = 'visual.type'
    _description = 'Visual Type'
    _rec_name = 'y_code'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    y_code = fields.Char(string="Code", required=True,tracking=True,copy=False)
    y_description = fields.Char(string="Description",tracking=True)

class VisualGroup(models.Model):
    _name = 'visual.group'
    _description = 'Visual Group'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Name", required=True,tracking=True,copy=False)
    y_code = fields.Many2many('visual.type', string="Visual Type",tracking=True,copy=False)
    y_description = fields.Text(string="Description",tracking=True)

    @api.onchange('y_code')
    def _onchange_y_code(self):
        for record in self:
            # Clear existing description
            record.y_description = ""
            if record.y_code:
                descriptions = record.y_code.mapped('y_description')
                descriptions = [desc for desc in descriptions if desc]
                
                # Join descriptions with a newline, if any exist
                if descriptions:
                    record.y_description = ", ".join(descriptions)
    
