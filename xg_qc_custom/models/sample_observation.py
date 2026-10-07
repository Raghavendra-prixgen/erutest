from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class SampleObservation(models.Model):
    _name = 'sample.observation'
    _description = 'Sample Observation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True,)
    active = fields.Boolean(string="Active", default=True)
    y_check_id = fields.Many2one('quality.check',ondelete='cascade',string="Quality Check",)
    y_product_id = fields.Many2one('product.product',ondelete='cascade',string="Product",)

    y_test_type_id = fields.Many2one('quality.point.test_type',ondelete='cascade',string="Type",)
    y_test_type = fields.Char(related='y_test_type_id.technical_name')

    y_sample_plan_id = fields.Many2one('sample.plan',ondelete='cascade',string="Sample Plan",)

    y_sample_observation_line_ids = fields.One2many('sample.observation.line','y_sample_observation_id',string="Sample Observation Line",)

    y_state = fields.Selection(
        [('draft', 'Draft'),('process', 'Processed'),('cancel', 'Cancelled'),],
        string="Status",default='draft',tracking=True)
    
    y_lot_id = fields.Many2one('stock.lot',string="Lot",)
    y_lot_qty  = fields.Float(string="Lot Quantity",)
    y_partner_id = fields.Many2one('res.partner',string="Partner",)
    y_po_ref = fields.Char(string="PO Reference",)
    y_grn_ref = fields.Char(string="GRN Reference",)
    y_instrument_used = fields.Char(string="Instrument Used",)
    y_inspection_approved_date = fields.Date(string="Inspection Date",)
    y_sample_size_dimensional = fields.Integer(string="Sample Size Dimensional",)
    y_sample_size_visual = fields.Integer(string="Sample Size Visual",)


    @api.model
    def create(self, vals):
        # Create the record first
        record = super(SampleObservation, self).create(vals)
        # Set the sequence number after creation
        if not record.name:
            record.name = self.env['ir.sequence'].next_by_code('sample.observation')
        return record
    
    def sample_observation_process(self):
        for observation in self:
            # Fetch the states of all lines
            states = observation.y_sample_observation_line_ids.mapped('y_state')
            # If there are failed or cancelled lines, set quality_state to 'fail'
            if 'fail' in states or 'cancelled' in states:
                
                # Get the first failed line and set its measure to the check_id.measure
                failed_line = observation.y_sample_observation_line_ids.filtered(
                    lambda line: line.y_state == 'fail' or line.y_state == 'cancelled')[:1]
                if failed_line and observation.y_test_type == 'measure':
                    observation.y_check_id.measure = failed_line.y_measure
                    observation.y_check_id.confirm_measure_btn()
                    observation.y_state = 'process'
                if failed_line and observation.y_test_type in ['passfail','picture']:
                    observation.y_check_id.fail_btn()
                    observation.y_state = 'process'
            # If all lines are passed, set quality_state to 'pass'
            elif all(state == 'pass' for state in states):
                pass_line = observation.y_sample_observation_line_ids.filtered(
                    lambda line: line.y_state == 'pass')[:1]
                if pass_line and observation.y_test_type == 'measure':
                    observation.y_check_id.measure = pass_line.y_measure
                    observation.y_check_id.confirm_measure_btn()
                    observation.y_state = 'process'
                if pass_line and observation.y_test_type in ['passfail','picture']:
                    observation.y_check_id.confirm_measure_btn()
                    observation.y_state = 'process'
                
            # Otherwise, raise an error for inconsistent states
            else:
                raise ValidationError(_("All observation lines must be either 'Passed', 'Failed', or 'Cancelled' to proceed."))



class SampleObservationLine(models.Model):
    _name = 'sample.observation.line'
    _description = 'Sample Observation Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name",)
    active = fields.Boolean(string="Active", default=True)
    y_sample_observation_id = fields.Many2one(
        'sample.observation',
        ondelete='cascade',
        string="Sample Observation",
    )
    y_title = fields.Char(string="Title", required=True)

    y_measure = fields.Float(string="Measure", required=True)
    y_norm = fields.Float(string="Norm",)
    y_norm_unit = fields.Char(string="Norm Unit",)
    y_tolerance_min = fields.Float(string="Min Tolerance",)
    y_tolerance_max = fields.Float(string="Max Tolerance",)
    y_remarks = fields.Char(string="Remarks",size=150)
    y_pass_or_fail_boolean = fields.Boolean(string="Pass or Fail",copy=False,default=False)

    y_state = fields.Selection(
        [
            ('to_do', 'To Do'),
            ('pass', 'Passed'),
            ('fail', 'Failed'),
            ('cancelled', 'Cancelled')
        ],
        string="Status",
        default='to_do'
    )

    y_check_id = fields.Many2one('quality.check',ondelete='cascade',string="Quality Check",)
    y_product_id = fields.Many2one('product.product',ondelete='cascade',string="Product",)

    y_test_type_id = fields.Many2one('quality.point.test_type',ondelete='cascade',string="Type",)
    y_test_type = fields.Char(related='y_test_type_id.technical_name')
    y_sample_plan_id = fields.Many2one('sample.plan',ondelete='cascade',string="Sample Plan",)


    y_lot_id = fields.Many2one('stock.lot',string="Lot",)
    y_lot_qty  = fields.Float(string="Lot Quantity",)
    y_partner_id = fields.Many2one('res.partner',string="Partner",)
    y_po_ref = fields.Char(string="PO Reference",)
    y_grn_ref = fields.Char(string="GRN Reference",)
    y_instrument_used = fields.Char(string="Instrument Used",)
    y_inspection_approved_date = fields.Date(string="Inspection Date",)
    y_sample_size_dimensional = fields.Integer(string="Sample Size Dimensional",)
    y_sample_size_visual = fields.Integer(string="Sample Size Visual",)

    @api.model
    def create(self, vals):
        record = super(SampleObservationLine, self).create(vals)
        # Trigger recomputation for all records with same observation
        if record.y_sample_observation_id:
            self.search([
                ('y_sample_observation_id', '=', record.y_sample_observation_id.id),
                ('id', '>=', record.id)
            ])._compute_display_name()
        return record

    def _compute_display_name(self):
        for rec in self:
            observation = rec.y_sample_observation_id
            if observation:
                # Count number of records for this observation
                sequence = self.search_count([
                    ('y_sample_observation_id', '=', observation.id),
                    ('id', '<=', rec.id)  # Only count records created before or equal to current
                ])
                rec.display_name = f"{observation.name}-{sequence:07d}"
                rec.name = f"{observation.name}-{sequence:07d}"

            else:
                rec.display_name = f"New-{rec.id:07d}"
                rec.name = f"New-{sequence:07d}"


    @api.depends('y_measure')
    def _compute_y_state(self):
        for rec in self:
            if rec.y_sample_observation_id.y_check_id.test_type == 'measure':
                if rec.y_measure < rec.y_tolerance_min or rec.y_measure > rec.y_tolerance_max:
                    rec.y_state = 'fail'
                else:
                    rec.y_state = 'pass'

    def pass_btn(self):
        self.y_pass_or_fail_boolean = True
        self.y_state = 'pass'

    def fail_btn(self):
        self.y_pass_or_fail_boolean = True
        self.y_state = 'fail'
            

    @api.model
    def write(self, vals):
        super(SampleObservationLine, self).write(vals)
        if 'y_measure' in vals:
            self._compute_y_state()
        else:
            pass



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def generate_inspection_sheets(self, check_ids, move_line_id):
        # Call the super method to ensure any inherited functionality is executed
        super(StockPicking, self).generate_inspection_sheets(check_ids, move_line_id)
        
        # Flag to track if observations were created
        observations_created = False
        
        sheet = self.env['inspection.sheet']

        # Loop through each check to create individual sample observations
        if move_line_id.quantity > 1:
            for check in check_ids:
                # Create Sample Observation for each check
                sample_observation_vals = {
                    'name': '',
                    'y_check_id': check.id,
                    'y_product_id': check.product_id.id,
                    'y_partner_id': self.partner_id.id,
                    'y_test_type_id': check.point_id.test_type_id.id,
                    'y_lot_id': check.lot_id.id if check.lot_id else False,
                    'y_po_ref': self.origin if self.origin else False,
                    'y_grn_ref': self.name if self.name else False,
                    'y_instrument_used': check.point_id.y_instrument_id.name if check.point_id.y_instrument_id.name else False,
                    'y_lot_qty': check.qty_line if check.qty_line else 0.0,
                    'y_sample_plan_id': check.point_id.y_sample_id.id if check.point_id.y_sample_id else False,
                }
                sample_observation = self.env['sample.observation'].create(sample_observation_vals)

                # Function to create observation lines
                def create_observation_lines(count, technique_type):
                    if count > 0:
                        # Update the sample size fields based on technique type
                        if technique_type.lower() == 'dimensional':
                            sample_observation.write({'y_sample_size_dimensional': count})
                        elif technique_type.lower() in ['visual']:
                            sample_observation.write({'y_sample_size_visual': count})
                            
                        for _ in range(count):
                            sample_observation_line_vals = {
                                'y_sample_observation_id': sample_observation.id,
                                'y_title': check.point_id.title,
                                'y_check_id': check.id,
                                'y_product_id': check.product_id.id,
                                'y_partner_id': self.partner_id.id,
                                'y_test_type_id': check.point_id.test_type_id.id,
                                'y_lot_id': check.lot_id.id if check.lot_id else False,
                                'y_po_ref': self.origin if self.origin else False,
                                'y_grn_ref': self.name if self.name else False,
                                'y_instrument_used': check.point_id.y_instrument_id.name if check.point_id.y_instrument_id.name else False,
                                'y_lot_qty': check.qty_line if check.qty_line else 0.0,
                                'y_sample_plan_id': check.point_id.y_sample_id.id if check.point_id.y_sample_id else False,
                                'y_measure': 0.0,
                                'y_norm': check.point_id.norm if check.point_id.test_type == 'measure' else 0.0,
                                'y_norm_unit': check.point_id.norm_unit if check.point_id.test_type == 'measure' else 0.0,
                                'y_tolerance_min': check.point_id.tolerance_min if check.point_id.test_type == 'measure' else 0.0,
                                'y_tolerance_max': check.point_id.tolerance_max if check.point_id.test_type == 'measure' else 0.0,
                                'y_sample_size_dimensional': sample_observation.y_sample_size_dimensional if sample_observation.y_sample_size_dimensional else 0.0,
                                'y_sample_size_visual': sample_observation.y_sample_size_visual if sample_observation.y_sample_size_visual else 0.0,
                                'y_state': 'to_do'
                            }
                            self.env['sample.observation.line'].create(sample_observation_line_vals)
                        return True
                    return False

                # If no sample plan is selected, use total quantity (1 in this case)
                if not check.point_id.y_sample_id:
                    # Default to 'dimensional' if test_type is measure, otherwise 'visual'
                    default_technique = 'dimensional' if check.point_id.test_type == 'measure' else 'visual'
                    if create_observation_lines(int(move_line_id.quantity), default_technique):
                        observations_created = True
                    continue

                # Handle cases with sample plan
                technique_type = '' 
                if check.point_id.test_type == 'measure':
                    technique_type = 'Dimensional'
                elif check.point_id.test_type in ['passfail', 'picture']:
                    technique_type = 'Visual'
                
                sample_plan_lines = self.env['sample.plan.dimensional.line'].search([
                    ('y_sample_plan_id', '=', sample_observation.y_sample_plan_id.id),
                    ('y_quality_technique_type.name', '=', technique_type)
                ])

                # Validate sample plan lines and move line product
                if move_line_id.product_id == sample_observation.y_product_id:
                    for sample_plan_line in sample_plan_lines:
                        if sample_plan_line.y_qty_from <= move_line_id.quantity <= sample_plan_line.y_qty_to:
                            plan_line_count = int(sample_plan_line.y_sample_size)
                            
                            if create_observation_lines(plan_line_count, technique_type):
                                observations_created = True
                            break  # Use first matching sample plan line
        
        # Update the y_observation_create field for the quality check
        if check_ids:
            for check in check_ids:
                check.y_observation_create = observations_created
                check.y_visual_group_description = check.point_id.y_visual_group_id.y_description if check.point_id.y_visual_group_id else False

        return observations_created

class QualityCheck(models.Model):
    _inherit = 'quality.check'

    y_observation_create = fields.Boolean(string='Create Sample Observation', default=False)
    y_visual_group_description = fields.Text(string='Visual Group Description',)

    @api.model
    def unlink(self):
        for check in self:
            sample_observations = self.env['sample.observation'].search([('y_check_id', '=', check.id)])
            for observation in sample_observations:
                observation.y_sample_observation_line_ids.unlink()
                observation.unlink()
        return super(QualityCheck, self).unlink()
    

    def button_sample_observation_view(self):
        action = {
            'name': _("Sample Observations"),
            'type': 'ir.actions.act_window',
            'res_model': 'sample.observation',
            'view_mode': 'tree,form',
            'context': {'default_y_check_id': self.id},
            'domain': [('y_check_id', '=', self.id)],
        }
        return action
    
   

        