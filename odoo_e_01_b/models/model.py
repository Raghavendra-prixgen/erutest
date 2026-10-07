# -*- coding: utf-8 -*-
import json
from itertools import chain

from lxml import etree
import odoo
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, AccessError, UserError

from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import UserError





class ResCompany(models.Model):
    _inherit = 'res.company'

    def create(self,vals):
        res = super(ResCompany,self).create(vals)
        if res.parent_id and res.parent_id.child_ids:
            self.env.cr.execute("""UPDATE stock_warehouse SET active=False WHERE company_id = {}""".format(res.parent_id.id))
            self.env.cr.execute("""UPDATE stock_location SET active=False WHERE company_id = {}""".format(res.parent_id.id))
            self.env.cr.execute("""UPDATE stock_picking_type SET active=False WHERE company_id = {}""".format(res.parent_id.id))
            self.env.cr.execute("""UPDATE stock_route SET active=False WHERE company_id = {}""".format(res.parent_id.id))
            # self.env.cr.execute("""select id from res_users WHERE company_id = {}""".format(res.parent_id.id))
            # user_ids = [user['id'] for user in self.env.cr.dictfetchall()]
            # if len(user_ids) == 1:
            #     self.env.cr.execute("""UPDATE res_users SET company_id={} WHERE id = {}""".format(res.id,user_ids))
            # if len(user_ids) > 1:
            #     self.env.cr.execute("""UPDATE res_users SET company_id={} WHERE id IN {}""".format(res.id,tuple(user_ids)))


        return res



class ParentCompanyAccess(models.Model):
    _name = 'parent.company.access'
    _description = 'Access Record Rule'


    y_model_ids = fields.Many2many('ir.model')


# class DefaultCompanyAccess(models.Model):
#     _name = 'default.company.access'
#     _description = 'Default Company Access Rule'


#     y_model_ids = fields.Many2many('ir.model')

class Model(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        """ Returns the fields_views of given views, along with the fields of
        the current model, and optionally its filters for the given action.

        :param views: list of [view_id, view_type]
        :param dict options: a dict optional boolean flags, set to enable:

            ``toolbar``
                includes contextual actions when loading fields_views
            ``load_filters``
                returns the model's filters
            ``action_id``
                id of the action to get the filters, otherwise loads the global
                filters or the model

        :return: dictionary with fields_views, fields and optionally filters
        """

        options = options or {}
        result = {}

        result['views'] = {
            v_type: self.get_view(
                v_id, v_type if v_type != 'list' else 'tree',
                **options
            )
            for [v_id, v_type] in views
        }

        models = {}
        for view in result['views'].values():
            for model, model_fields in view.pop('models').items():
                models.setdefault(model, set()).update(model_fields)

        result['models'] = {}

        for model, model_fields in models.items():
            result['models'][model] = self.env[model].fields_get(
                allfields=model_fields, attributes=self._get_view_field_attributes()
            )

        # Add related action information if asked
        if options.get('toolbar'):
            for view in result['views'].values():
                view['toolbar'] = {}

            bindings = self.env['ir.actions.actions'].get_bindings(self._name)
            for action_type, key in (('report', 'print'), ('action', 'action')):
                for action in bindings.get(action_type, []):
                    view_types = (
                        action['binding_view_types'].split(',')
                        if action.get('binding_view_types')
                        else result['views'].keys()
                    )
                    for view_type in view_types:
                        view_type = view_type if view_type != 'tree' else 'list'
                        if view_type in result['views']:
                            result['views'][view_type]['toolbar'].setdefault(key, []).append(action)

        if options.get('load_filters') and 'search' in result['views']:
            result['views']['search']['filters'] = self.env['ir.filters'].get_filters(
                self._name, options.get('action_id')
            )



        # Added Domain company filed for to remove parent company have branch

        models_name_list = self.env['parent.company.access'].search([],limit=1)
        if self._name not in models_name_list.y_model_ids.mapped('model'):
            company_ids = self.env['ir.model']._get(self._name).field_id.filtered(lambda x:x.relation == 'res.company')
            for company_id in company_ids:
                branch_company_ids = self.env['res.company'].search([]).filtered(lambda x:not x.child_ids or x.parent_id).ids
                if branch_company_ids:
                    list_views = [view[-1] for view in views]
                    if len(branch_company_ids) == 1:
                        domain = str([('id','=',branch_company_ids[:1])])
                    else:
                        domain = str([('id','in',branch_company_ids)])
                    if 'list' in list_views:
                        doc = etree.XML(result['views']['list']['arch'])
                        for node in doc.xpath("//field[@name='%s']"%(company_id.name)):
                            node.set('domain',domain)
                        result['views']['list']['arch'] = etree.tostring(doc)

                    if 'form' in list_views:
                        doc = etree.XML(result['views']['form']['arch'])
                        for node in doc.xpath("//field[@name='%s']"%(company_id.name)):
                            node.set('domain',domain)
                        result['views']['form']['arch'] = etree.tostring(doc)

        return result