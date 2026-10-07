# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SamplePlan(models.Model):
    _name = 'sample.plan'
    _description = 'Quality Sample Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(
        string="Document No.",
        readonly=True, )

    y_sample_document_origin_date = fields.Date(
        string="Origin Date",
        default=fields.Date.context_today
    )

    y_sample_document_name = fields.Char(
        string="Document Name",
        required=True
    )

    y_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('review', 'Review'),
            ('approved', 'Approved'),
            ('cancelled', 'Cancelled')
        ],
        string="Status",
        default='draft',tracking=True
    )


    y_dimensional_line_ids = fields.One2many(
        'sample.plan.dimensional.line',
        'y_sample_plan_id',
        string="Sample Plan Dimensional Lines"
    )

   

    @api.model
    def create(self, vals):
        # Create the record first
        record = super(SamplePlan, self).create(vals)
        # Set the sequence number after creation
        if not record.name:
            record.name = self.env['ir.sequence'].next_by_code('sample.plan')
        return record

    @api.constrains('y_dimensional_line_ids')
    def _check_qty_line_ranges(self):
        for plan in self:
            # Dictionary to hold ranges for each quality technique type
            technique_ranges = {}

            for line in plan.y_dimensional_line_ids:
                # Skip if the line is a section or note

                if line.y_display_type != 'line_note':
                    continue

                technique_type = line.y_quality_technique_type.id
                if technique_type not in technique_ranges:
                    technique_ranges[technique_type] = []
                # Check if 'Quantity From' is less than 'Quantity To'
                if line.y_qty_from >= line.y_qty_to:
                    raise ValidationError(
                        f"'Quantity From' should be less than 'Quantity To' for line '{line.name}' in quality technique type '{line.y_quality_technique_type.name}'."
                    )

                # Validate for overlapping ranges within the same quality technique type
                for qty_from, qty_to in technique_ranges[technique_type]:
                    if line.y_qty_from <= qty_to and line.y_qty_to >= qty_from:
                        raise ValidationError(
                            f"In quality technique type '{line.y_quality_technique_type.name}', the quantity range in line '{line.name}' overlaps with another line. "
                            "Ensure each line has a unique, non-overlapping range within the same quality technique type."
                        )

                # Add the current line's range for further checks
                technique_ranges[technique_type].append((line.y_qty_from, line.y_qty_to))


    def action_review(self):
        for data in self:
            data.y_state = 'review'

    def action_approve(self):
        for data in self:
            data.y_state = 'approved'

    def action_reset_draft(self):
        for data in self:
            data.y_state = 'draft'

    def action_cancel(self):
        for data in self:
            data.y_state = 'cancelled'


class SamplePlanDimensionalLine(models.Model):
    _name = 'sample.plan.dimensional.line'
    _description = 'Sample Plan Dimensional Line'

    y_sample_plan_id = fields.Many2one(
        'sample.plan',
        ondelete='cascade',
        string="Sample Plan",
    )

    name = fields.Char(string="Name", required=True)
    y_quality_technique_type = fields.Many2one(
        'quality.technique.type',
        string="Quality Technique Type",
        required=True)
    y_qty_from = fields.Integer(string="Quantity From", required=True)
    y_qty_to = fields.Integer(string="Quantity To", required=True)
    y_sample_size = fields.Integer(string="Sample Size", required=True)
    y_accepted_qty = fields.Integer(string="Accepted Quantity", required=True)
    y_reject_qty = fields.Integer(string="Reject Quantity", required=True)

    y_display_type = fields.Selection(
        [('line_section', 'Section'),
         ('line_note', 'Note'),
        ],
        string="Display Type",
        required=True,
        default='line_note',
    )


    
class QualityTechniqueType(models.Model):
    _name = 'quality.technique.type'
    _description = 'Quality Technique Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True,tracking=True)
    