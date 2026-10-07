from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
import math


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"
   
   
    def get_kit_product_quantity(self, kit_product):
        kit_product_name = self._extract_product_name(kit_product)
        
        kit_lines = self.y_sale_kit_line_ids.filtered(lambda l: l.y_sale_kit_id.display_name == kit_product_name)
        return kit_lines.y_kit_quantity if kit_lines else 0.0 

    def _extract_product_name(self, product_string):
        # Split based on the first occurrence of colon and space
        if ': ' in product_string:
            product_string = product_string.split(': ', 1)[1].strip()

        return product_string.split('-')[0].strip()
    def calculate_group_weights(self):
        group_weights = {}
        
        for line in self.y_packaging_line_ids:
            group = line.y_group
            qty_in_package = line.y_qty_in_package
            net_weight = line.y_net_weight
            gross_weight = line.y_gross_weight
            volumetric_weight_option = float(self.y_volumetric_weight)  # Convert string to float
            # Calculate volumetric weight based on the selected volumetric weight option
            Volumetric_weight = 0.0
            if volumetric_weight_option != 0.0:
                Volumetric_weight = (((line.y_length * line.y_width * line.y_height) / volumetric_weight_option)* line.y_total_package)
            if group in group_weights:
                group_weights[group]['qty_in_package'] += qty_in_package
                group_weights[group]['Volumetric_weight'] = Volumetric_weight
                group_weights[group]['net_weight'] += net_weight
                group_weights[group]['gross_weight'] += gross_weight
            else:
                group_weights[group] = {'net_weight': net_weight, 'gross_weight': gross_weight, 'qty_in_package': qty_in_package, 'Volumetric_weight': Volumetric_weight}
        
        return group_weights
    
    
    def get_total_quantity(self):
        total_quantity = 0.0
        for line in self.y_packaging_line_ids:
            total_quantity += line.y_total_qty
        return total_quantity

    
    def get_total_net_weight(self):
        total_net_weight = 0.0
        for line in self.y_packaging_line_ids:
            total_net_weight += line.y_net_weight
        return total_net_weight
    
    def get_total_gross_weight(self):
        total_gross_weight = 0.0
        for line in self.y_packaging_line_ids:
            total_gross_weight += line.y_gross_weight
        return total_gross_weight

    def get_total_y_total_package(self):
        seen_groups = set()
        total_y_total_package = 0
        
        for line in self.y_packaging_line_ids:
            group = line.y_group
            if group not in seen_groups:
                seen_groups.add(group)
                total_y_total_package += line.y_total_package
                
        return total_y_total_package

    def get_total_Volumetric_weight(self):
        seen_groups = set()
        total_y_total_package = 0
        
        for line in self.y_packaging_line_ids:
            group = line.y_group
            if group not in seen_groups:
                seen_groups.add(group)
                volumetric_weight_option = float(self.y_volumetric_weight)  # Convert string to float
                if volumetric_weight_option != 0.0:
                    Volumetric_weight = (((line.y_length * line.y_width * line.y_height)/volumetric_weight_option) * line.y_total_package)
                    total_y_total_package += Volumetric_weight

        return total_y_total_package



               
    




















