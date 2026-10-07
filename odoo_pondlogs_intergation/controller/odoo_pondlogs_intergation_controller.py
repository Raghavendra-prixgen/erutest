
from odoo import fields, http, _
from odoo.http import request,Response
from datetime import datetime
import json
import logging
import os
from pprint import pprint
from odoo import api, models
from odoo.http import request
from . import validations
import requests
import string
import random

class ClaimRequest(http.Controller):
    @http.route('/web/api/claimrequest',type="json",auth="none",methods=['POST'])
    def CreateClaimRequest(self,**received_payload):
        claim_access = request.env['ir.config_parameter'].sudo().get_param('odoo_pondlogs_intergation.eruvaka_access_token')

        headers = request.httprequest.headers
        
        split_token = headers.get('Authorization').split()
        bearer_token = split_token[1]
        # claim_obj = request.env['claim.request'].sudo().search([('api_bearer_token','=',bearer_token)])

        # if not claim_obj:
        if bearer_token == claim_access:

   
            device_type_ids = []
            # if received_payload.get('device_type_ids'):
            #     for device_type in received_payload.get('device_type_ids'):
            #         device_type_obj = request.env['device.type'].sudo().search([('device_primary_id','=',device_type)])
            #         device_type_ids.append(device_type_obj.id)

            device_type = received_payload.get('device_type')
            failure_part_no = received_payload.get('failure_part_no')
            internal_ref = request.env['product.template'].sudo().search([('default_code','=',failure_part_no)])
            device_type_obj = request.env['device.type'].sudo().search([('device_primary_id','=',device_type)])
            
            
            if device_type_obj not in internal_ref.device_type_ids:
                return {'success':False,'message':'Device Types Is Not Mapped For This Product','status':"error",}
                
            else:
                received_payload['device_type'] = device_type_obj.id
                claim_obj = validations.API.claimidvalidation(received_payload.get('claim_id'))
                if claim_obj:
                    return {'success':False,'response':{
                        'message':'Claim Request already exist','status':200}} 
                
                claim_request_fields = request.env['claim.request'].sudo().fields_get()
                mandatory_fields = []
                #remove unwanted keys
                processed_dict = validations.API.RemoveUnwantedKeys(received_payload)
                # processed_dict['api_bearer_token'] = bearer_token
                response = validations.API.FieldValidation(claim_request_fields,processed_dict,mandatory_fields)
                if response:
                    return response
                else:
                    claim_obj = request.env['claim.request'].sudo().create(processed_dict)
                    return {'success':True,'response':{'claim_id':claim_obj.id},'message':'Claim request created','status':200}
        else:
            return {'success':False,'message':'Access Token not matched','status':"error",}

        # else:
        #     return {'success':False,'message':'Access Token is already used','status':"error",}
                

    @http.route('/odoo/productwarranty/authenticate',type="json",auth="none",methods=['POST'])
    def OdooAuthenticate(self,**received_payload):
        claim_obj = request.env['ir.config_parameter'].sudo().get_param('odoo_pondlogs_intergation.eruvaka_access_token')
        claim_user = request.env['ir.config_parameter'].sudo().get_param('odoo_pondlogs_intergation.user_name')
        claim_password = request.env['ir.config_parameter'].sudo().get_param('odoo_pondlogs_intergation.password')
        # if claim_obj == received_payload.get('access_token'):
        if claim_user == received_payload.get('username') and claim_password == received_payload.get('password'):
            N = 20
            accessToken = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=N))
            request.env['ir.config_parameter'].sudo().set_param('odoo_pondlogs_intergation.eruvaka_access_token',
                                                                 accessToken)
            return {'success':True,'response':{'Access-Token':accessToken},'message':'Access Token Generated','status':200}
        else:
            return {'success':False,'message':'Access Failed','status':200}

    

    @http.route('/web/api/claimrequestupdate',type="json",auth="none",methods=['POST'])
    def UpdateEmployeeMaster(self,**received_payload):
        update_claim_req_fields = request.env['claim.request'].sudo().fields_get()
        claim_access = request.env['ir.config_parameter'].sudo().get_param('odoo_pondlogs_intergation.eruvaka_access_token')
        headers = request.httprequest.headers
        split_token = headers.get('Authorization').split()
        bearer_token = split_token[1]






        
        # device_type = received_payload.get('device_type')
        # failure_part_no = received_payload.get('failure_part_no')
        
        # internal_ref = request.env['product.template'].sudo().search([('default_code','=',failure_part_no)])
        # device_type_obj = request.env['device.type'].sudo().search([('device_primary_id','=',device_type)])
                
        # claim_obj = request.env['claim.request'].sudo().search([('api_bearer_token','=',bearer_token)])

        # if not claim_obj:

        
        if claim_access == bearer_token:
            # if device_type_obj not in internal_ref.device_type_ids:
                
            #     return {'success':False,'message':'device types is not mapped for this product','status':"error",}
            # else:
            #     received_payload['device_type'] = device_type_obj.id
                
            mandatory_fields = []
            processed_dict = validations.API.RemoveUnwantedKeys(received_payload)
            response = validations.API.FieldValidation(update_claim_req_fields,processed_dict,mandatory_fields)
            if response:
                # Response.status = response.get('status')
                return response
            else:
                if not validations.API.claimidvalidation(processed_dict.get('claim_id')):
                    return {'success':False,'response':{},'message':'Claim Request {} Not Exist'.format(processed_dict.get('claim_id')),'status':403}
            claim_obj = request.env['claim.request'].sudo().search([('claim_id','=',processed_dict.get('claim_id'))])
            if claim_obj.claim_status != 'approved':
                return {'success':False,'message':'Claim status not in Approved state','status':"error",}


            claim_obj.write(processed_dict)
            # Response.status = "200"
            return {'success':True,'response':{'claim_id':claim_obj.id},'message':'Claim Updated','status':200}
            
        else:
            return {'success':False,'message':'Access Token is Not Matched','status':"error",}

        # else:
        #     return {'success':False,'message':'Access Token is already used','status':"error",}
                
        
        