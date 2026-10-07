# -*- coding: utf-8 -*-

from odoo import models, fields, api


class QualityPoint(models.Model):
    _inherit = "quality.point"

    measure_frequency_type = fields.Selection([
        ('all', 'All'),
        ('random', 'Randomly'),
        ('periodical', 'Periodically'),
        ('sample','Sample')], string="Control Frequency",
        default='all', required=True)

    y_sample_id = fields.Many2one(
        'sample.plan',
        ondelete='cascade',
        string='Sample Plan',
        domain="[('y_state', '=', 'approved')]", tracking=True,
    )

    y_instrument_id = fields.Many2one(
        'quality.instrument',
        string='Instrument', tracking=True,
    )

    y_visual_group_id = fields.Many2one(
        'visual.group',
        string='Visual Group', tracking=True,
    )

class QualityInstrument(models.Model):
    _name = "quality.instrument"
    _description = "Quality Instrument"

    name = fields.Char(string='Instrument Name', required=True, tracking=True)
