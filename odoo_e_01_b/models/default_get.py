from odoo import api, fields, models, tools, _
from odoo.models import BaseModel
from collections import defaultdict, OrderedDict, deque


class InheritBaseModel():

    @api.model
    def default_get(self, fields_list):
        """ default_get(fields_list) -> default_values

        Return default values for the fields in ``fields_list``. Default
        values are determined by the context, user defaults, and the model
        itself.

        :param list fields_list: names of field whose default is requested
        :return: a dictionary mapping field names to their corresponding default values,
            if they have a default value.
        :rtype: dict

        .. note::

            Unrequested defaults won't be considered, there is no need to return a
            value for fields whose names are not in `fields_list`.
        """
        defaults = {}
        parent_fields = defaultdict(list)
        ir_defaults = self.env['ir.default']._get_model_defaults(self._name)

        for name in fields_list:
            # 1. look up context
            key = 'default_' + name
            if key in self._context:
                defaults[name] = self._context[key]
                continue

            # 2. look up ir.default
            if name in ir_defaults:
                defaults[name] = ir_defaults[name]
                continue

            field = self._fields.get(name)

            # 3. look up field.default
            if field and field.default:
                defaults[name] = field.default(self)
                continue

            # 4. delegate to parent model
            if field and field.inherited:
                field = field.related_field
                parent_fields[field.model_name].append(field.name)

        # convert default values to the right format
        #
        # we explicitly avoid using _convert_to_write() for x2many fields,
        # because the latter leaves values like [(Command.LINK, 2),
        # (Command.LINK, 3)], which are not supported by the web client as
        # default values; stepping through the cache allows to normalize
        # such a list to [(Command.SET, 0, [2, 3])], which is properly
        # supported by the web client
        for fname, value in defaults.items():
            if fname in self._fields:
                field = self._fields[fname]
                value = field.convert_to_cache(value, self, validate=False)
                defaults[fname] = field.convert_to_write(value, self)

        # add default values for inherited fields
        for model, names in parent_fields.items():
            defaults.update(self.env[model].default_get(names))

        default_company_model_names = ['res.config.settings','res.company']
        if self._name not in default_company_model_names:
            if len(defaults):
                if defaults.get('company_id'):
                    parent_company_id = self.env['res.company'].search([('id','=',defaults.get('company_id'))]).filtered(lambda x:not x.child_ids or x.parent_id).ids
                    if not parent_company_id:                    
                        # default_company_model_names += self.env['default.company.access'].search([],limit=1).y_model_ids.mapped('model')
                        if self._context.get('params'):
                            if self._context.get('params').get('model') not in default_company_model_names:
                                defaults.update({'company_id':False})
                        else:
                            defaults.update({'company_id':False})

        
        return defaults


BaseModel.default_get = InheritBaseModel.default_get