
from odoo import models, fields, api,_
import json
from odoo.exceptions import AccessError, UserError, ValidationError

import requests
from markupsafe import Markup
import string
import random
import html 



class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self,vals):
        if not vals.get('author_id') and vals.get('model') == 'claim.request':
            value = self.env['ir.config_parameter'].sudo().get_param('odoo_pondlogs_intergation.user_id') or False
            user_obj = self.env['res.users'].browse(int(value))
            vals['author_id'] = user_obj.partner_id.id
        return super().create(vals)





class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    user_id = fields.Many2one('res.users', string="User", readonly=False,)

    def set_values(self):
        super(ResConfigSettings,self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('odoo_pondlogs_intergation.user_id',self.user_id.id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            user_id = int(params.get_param('odoo_pondlogs_intergation.user_id')) or False,
        )
        return res


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    eruvaka_access_token = fields.Char(string="Access Token")
    user_name = fields.Char(string="User Name",store=True,related="user_id.name")
    password = fields.Char(string="Password")
    
    
    

    def set_values(self):
        super(ResConfigSettingsInherit,self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('odoo_pondlogs_intergation.eruvaka_access_token',self.eruvaka_access_token)
        param.set_param('odoo_pondlogs_intergation.user_name',self.user_name)
        param.set_param('odoo_pondlogs_intergation.password',self.password)

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        res.update(eruvaka_access_token = param.get_param('odoo_pondlogs_intergation.eruvaka_access_token'))
        res.update(user_name = param.get_param('odoo_pondlogs_intergation.user_name'))
        res.update(password = param.get_param('odoo_pondlogs_intergation.password'))
        
        
        return res

    def generate_token(self):
        N = 20
        accessToken = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=N))
        self.env['ir.config_parameter'].sudo().set_param('odoo_pondlogs_intergation.eruvaka_access_token',
                                                                 accessToken)



class ApiLogs(models.Model):
    _name = "api.logs"
    _description = "API Logs"

    api_name = fields.Char(string="Api Name" ,readonly="1")
    payload = fields.Char(string="Payload",readonly="1")
    response = fields.Char(string="Response" ,readonly="1")
    odoo_ref = fields.Char(string="OdooRef" ,readonly="1")
    call_status = fields.Char(string="Call Status" ,readonly="1")
    created_by = fields.Char(string="Created By" ,readonly="1")
    created_on = fields.Datetime(string="Created On" ,readonly="1")

class DeviceMotor(models.Model):
    _name = "device.type"

    name = fields.Char(string="Device Type")
    device_primary_id = fields.Char(string="Device Primary Id")


class ProductTemplateNew(models.Model):
    _inherit = "product.template"

    device_type_ids = fields.Many2many('device.type',string="Device Type")

class ProductProductNew(models.Model):
    _inherit = "product.product"

    device_type_ids = fields.Many2many('device.type',string="Device Type")





class ApiConnection(models.Model):
    _name = "api.connection"
    _description = "API Connection"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    eruvaka_database_url = fields.Char(string= "Eruvaka Database URL")
    eruvaka_username=fields.Char(string="User Name")
    eruvaka_password=fields.Char(string="Password")
    eruvaka_access_token=fields.Char(string="Access Token",readonly="1")
    y_eruvaka_device_id = fields.Char(string="URL Device ID",tracking=True)
    # y_eruvaka_close_claim = fields.Char(string="URL Update Claim",tracking=True)
    y_eruvaka_approve_claim = fields.Char(string="URL  Warranty Claim",tracking=True)
    
    


    def get_connection(self):
        url = self.eruvaka_database_url
        accesstoken_url = url+'warranty/authenticate'
        username = self.eruvaka_username
        password = self.eruvaka_password
        the_data = {"username": username, "password": password}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # Execute the post
        accesstoken = requests.post(accesstoken_url, data=the_data, headers=headers)
        response = accesstoken.json()
        
        # username = self.eruvaka_username
        # password=self.eruvaka_password
        # url = self.eruvaka_database_url + '/authenticate'
        # payload = {
        # "username":username,
        # "password":password,
        #     }
        # data_order=json.dumps(payload)
        # r = requests.post(url,payload)
        # response = r.json()
        self.eruvaka_access_token=response.get('access_token')
        if response.get('success')== True:
            self.sudo().message_post(body="Connection Success")
            print("Connection Success")
        else:
            self.sudo().message_post(body="Connection Fail")
            print("Connection Fail")

        return self.eruvaka_access_token    




class ClaimRequest(models.Model):
    _name = "claim.request"
    _description = "Claim Request"
    _rec_name = 'claim_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    claim_id = fields.Char(string="Claim Id")
    customer_name = fields.Char(string="Customer name")
    device_type = fields.Char(string="Device type")
    device_id = fields.Char(string="Device Id")
    motor_id = fields.Char(string="Motor Id")
    issue = fields.Char(string="Issue")
    failure_part_no = fields.Char(string="Failure part no")
    failure_part_name = fields.Char(string="Failure part name")
    failure_date = fields.Date(string="Failure date")
    approved_date = fields.Date(string="Approve date")
    approved_by = fields.Char(string="Approved by")
    claim_status = fields.Selection([('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),

        ('closed', 'Closed'),
        ],copy=False,tracking=True,string="Claim status",default='draft')
    claim_date = fields.Date(string="Claim date")
    warrenty_exists = fields.Boolean(string="Warrenty_exists")
    device_type_ids = fields.Many2many('device.type',string="Device Type")
    device_types_id = fields.Many2one('device.type',string="Device Type")
    api_bearer_token = fields.Char(string="Bearer Token")
    device_type = fields.Many2one('device.type',string="Device Type")

    def action_reject(self):
        for rec in self:
            if rec.claim_status == 'draft':
                # rec.write({'claim_status':'approved'})
                api_connection = self.env['api.connection'].search([],limit=1)
                url = api_connection.eruvaka_database_url
                approve_url = api_connection.y_eruvaka_approve_claim
               
                if approve_url and url :
                    extension_url =  approve_url
                    rec.write({'claim_status':'rejected'})
                    
                    # extension_url = url+'warranty/update-claim-status'
                    accesstoken_url = url+'warranty/authenticate'
                    the_data = {"username": api_connection.eruvaka_username, "password": api_connection.eruvaka_password}

                    # the_data = {"username": 'eruvakaOddoUser', "password": 'YfG%h5!PHt5zEWD9'}
                    authheaders = {'Content-Type': 'application/x-www-form-urlencoded'}
                    # Execute the post
                    accesstoken = requests.post(accesstoken_url, data=the_data, headers=authheaders)
                    response = accesstoken.json()
                    authtoken = response.get('access_token')



                    headers = {'Content-Type': 'application/json','Authorization':authtoken}

                    
                   

                    pondlogs_payload = {
                            'claim_id': rec.claim_id,
                            'claim_status': "REJECTED",
                            'date':str(rec.claim_date)
                        }
                    
                    
                    pondlogs_payload=json.dumps(pondlogs_payload)
                   
                    r = requests.post(extension_url, data=pondlogs_payload, headers=headers)
                    response = r.json()
                    api_payload = {
                    'api_name':'updated-claims-reject',
                    'payload':pondlogs_payload,
                    'response':response,
                    'odoo_ref':rec.claim_id,
                    'created_by':self.env.user.name,
                    'created_on':fields.Datetime.now(),
                    }
                    api_logs = self.env['api.logs'].create(api_payload)
                else:
                    if not approve_url:
                        raise ValidationError(_("Warranty Claim Is NOt Mapped,Please Provide Warranty Claim URL"))


            


    def action_approve(self):
        for rec in self:
            if rec.claim_status == 'draft':
                # rec.write({'claim_status':'approved'})
                api_connection = self.env['api.connection'].search([],limit=1)
                url = api_connection.eruvaka_database_url
                approve_url = api_connection.y_eruvaka_approve_claim
               
                if approve_url and url :
                    extension_url = approve_url
                    rec.write({'claim_status':'approved'})
                    
                    # extension_url = url+'warranty/update-claim-status'
                    accesstoken_url = url+'warranty/authenticate'
                    the_data = {"username": api_connection.eruvaka_username, "password": api_connection.eruvaka_password}

                    # the_data = {"username": 'eruvakaOddoUser', "password": 'YfG%h5!PHt5zEWD9'}
                    authheaders = {'Content-Type': 'application/x-www-form-urlencoded'}
                    # Execute the post
                    accesstoken = requests.post(accesstoken_url, data=the_data, headers=authheaders)
                    response = accesstoken.json()
                    authtoken = response.get('access_token')

                    headers = {'Content-Type': 'application/json','Authorization':authtoken}

                    pondlogs_payload = {
                            'claim_id': rec.claim_id,
                            'claim_status': "APPROVED",
                            'date':str(rec.claim_date)
                        }
                    
                    pondlogs_payload=json.dumps(pondlogs_payload)
                   
                    r = requests.post(extension_url, data=pondlogs_payload, headers=headers)
                    response = r.json()
                    api_payload = {
                    'api_name':'updated-claims-approve',
                    'payload':pondlogs_payload,
                    'response':response,
                    'odoo_ref':rec.claim_id,
                    'created_by':self.env.user.name,
                    'created_on':fields.Datetime.now(),
                    }
                    api_logs = self.env['api.logs'].create(api_payload)
                else:
                    if not approve_url:
                        raise ValidationError(_("Warranty Claim Is NOt Mapped,Please Provide Warranty Claim URL"))







    # def action_closed(self):
    #     for rec in self:
    #         if rec.claim_status == 'approved':
    #             api_connection = self.env['api.connection'].search([],limit=1)
    #             url = api_connection.eruvaka_database_url
    #             cancel_url = api_connection.y_eruvaka_close_claim
                
    #             # extension_url = url+'/updated-claims'
                
    #             if cancel_url and url:
    #                 extension_url = url + cancel_url
    #                 payload = {
    #                 "claim_id":rec.claim_id,
    #                 "claim_Status":'Closed',
    #                 "date":rec.claim_date,
    #                     }
    #                 data_order=json.dumps(payload)
    #                 r = requests.post(extension_url,data_order)
    #                 response = r.json()
    #                 api_payload = {
    #                     'api_name':'updated-claims',
    #                     'payload':data_order,
    #                     'response':response,
    #                     'odoo_ref':rec.claim_id,
    #                     'created_by':self.env.user.name,
    #                     'created_on':fields.Datetime.now(),
    #                     }
    #                 api_logs = self.env['api.logs'].create(api_payload)
    #                 if r.status_code== 200:
    #                     self.sudo().message_post(body="Success")
    #                     print("Connection Success")
    #                 else:
    #                     self.sudo().message_post(body="Fail")
    #                     print("Connection Fail")
    #             else:
    #                 if not cancel_url:
    #                     raise ValidationError(_("Update Claim Is Not Mapped,Please Provide Update Claim URL"))
    #         else:
    #             raise ValidationError(_("Claim request not in approved state"))





class StockPicking(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):
        res = super().button_validate()

        for rec in self:
            if rec.sale_id:
                api_connection = self.env['api.connection'].search([],limit=1)
                url = api_connection.eruvaka_database_url
                device_id = api_connection.y_eruvaka_device_id
                # extension_url = url+'warranty/device-details'
                if device_id and url:
                    extension_url =  device_id
                    if extension_url:
                        accesstoken_url = url+'warranty/authenticate'
                        # the_data = {"username": api_connection.eruvaka_username, "password": api_connection.eruvaka_password}

                        the_data = {"username": 'eruvakaOddoUser', "password": 'YfG%h5!PHt5zEWD9'}
                        authheaders = {'Content-Type': 'application/x-www-form-urlencoded'}
                        # Execute the post
                        accesstoken = requests.post(accesstoken_url, data=the_data, headers=authheaders)
                        response = accesstoken.json()
                        authtoken = response.get('access_token')



                        headers = {'Content-Type': 'application/json','Authorization':authtoken}

                        lots = rec.move_line_ids_without_package.filtered(lambda x:x.product_id.y_product_warranty == True).mapped('lot_id').filtered(lambda x:x.y_motor_id).mapped('y_motor_id')
                        product_list = []
                        for stock_move in rec.move_ids_without_package.filtered(lambda x:x.product_id.y_product_warranty == True):
                            for device_type in stock_move.product_id.device_type_ids.mapped('device_primary_id'):

                                value = {
                                "part_no": stock_move.product_id.default_code,
                                "part_name": stock_move.product_id.name,
                                "device_type": device_type
                                }
                                product_list.append(value)


                        pondlogs_payload = {
                        "motor_ids":lots,
                        
                        "parts":product_list
                        }


                        
                        pondlogs_payload=json.dumps(pondlogs_payload)


                        r = requests.post(extension_url, data=pondlogs_payload, headers=headers)
                        response = r.json()
                        api_payload = {
                        'api_name':'warranty/device-details',
                        'payload':pondlogs_payload,
                        'response':response,
                        'odoo_ref':rec.name,
                        'created_by':self.env.user.name,
                        'created_on':fields.Datetime.now(),
                        }
                        api_logs = self.env['api.logs'].create(api_payload)
                        # if r.status_code== 200:
                        #     rec.sudo().message_post(body="Success")
                        #     print("Connection Success")
                        # else:
                        #     rec.sudo().message_post(body="Fail")
                        #     print("Connection Fail")

                else:
                    if not device_id:
                        raise ValidationError(_("Device Id Is NOt Mapped,Please Provide Device Id"))




        return res


        




    