from odoo import models

class StockPicking(models.Model):
    _inherit = 'packaging.list'

    def get_total_quantity(self):
        total_quantity = 0.0
        for line in self.y_packaging_list_ids:
            total_quantity += line.y_quantity
        return total_quantity

    
    def get_total_net_weight(self):
        total_net_weight = 0.0
        for line in self.y_packaging_list_ids:
            total_net_weight += line.y_net_weight
        return total_net_weight
    
    def get_total_gross_weight(self):
        total_gross_weight = 0.0
        for line in self.y_packaging_list_ids:
            total_gross_weight += line.y_gross_weight
        return total_gross_weight


    def get_report_values(self):
        kit_list = []

        for record in self.y_packaging_list_ids:
            kit_name_parts = record.y_kit_product.split('-')[:-1]
            kit_name = '-'.join(kit_name_parts).strip()

            if kit_name not in kit_list:
                kit_list.append(kit_name)

        kit_details = []
        for kit_name in kit_list:
            kit_lines = self.y_packaging_list_ids.filtered(lambda r: r.y_kit_product.split('-')[0].strip() == kit_name)
            merged_package_info_by_code_desc = {}
            total_length, total_width, total_height = 0, 0, 0  # Initialize total dimensions for each kit
            processed_package_types = set()
            for line in kit_lines:
                key = (line.y_default_code, line.y_product_description)
                if key in merged_package_info_by_code_desc:
                    merged_package_info_by_code_desc[key]['total_quantity'] += line.y_quantity
                    merged_package_info_by_code_desc[key]['total_net_weight'] += line.y_net_weight
                    merged_package_info_by_code_desc[key]['total_gross_weight'] += line.y_gross_weight
                    merged_package_info_by_code_desc[key]['package_names'].add(line.y_packing_stock_id.name)
                else:
                    merged_package_info_by_code_desc[key] = {
                        'total_quantity': line.y_quantity,
                        'total_net_weight': line.y_net_weight,
                        'total_gross_weight': line.y_gross_weight,
                        'package_names': {line.y_packing_stock_id.name}
                    }

                # Calculate total dimensions for each package group if the package_type_id is unique
                if line.package_type_id.id not in processed_package_types:
                    total_length += line.package_type_id.packaging_length
                    total_width += line.package_type_id.width
                    total_height += line.package_type_id.height
                    processed_package_types.add(line.package_type_id.id)
            
            
            
            merged_info_list = []
            processed_packages = set()  # To keep track of processed package names
            
            max_qty_per_package = {}  # Initialize dictionary to store max quantity per package group

            for key, info in merged_package_info_by_code_desc.items():
                # Check if package names have been processed before
                package_names_key = tuple(sorted(info['package_names']))
                if package_names_key in processed_packages:
                    continue  # Skip processing if package names have already been processed

                # Aggregate codes and descriptions within the same package names group
                merged_codes = set()
                merged_descriptions = set()
                total_quantity = 0
                total_net_weight = 0
                total_gross_weight = 0

                for code_desc, package_info in merged_package_info_by_code_desc.items():
                    if package_info['package_names'] == info['package_names']:
                        merged_codes.add(code_desc[0])
                        merged_descriptions.add(code_desc[1])
                        total_quantity += package_info['total_quantity']
                        total_net_weight += package_info['total_net_weight']
                        total_gross_weight += package_info['total_gross_weight']
                
                merged_info_list.append({
                    'codes': ', \n'.join(merged_codes),
                    'description': ' , \n'.join(merged_descriptions),
                    'total_quantity': total_quantity,
                    'total_net_weight': total_net_weight,
                    'total_gross_weight': total_gross_weight,
                    'package_names': info['package_names']
                })


                # Calculate and store max quantity for the group of codes and descriptions
                code_description_key = ', '.join(merged_codes) + ', ' + ', '.join(merged_descriptions)
                product_template = self.env['product.template'].search([
                    ('default_code', 'in', list(merged_codes)),
                    ('name', 'in', list(merged_descriptions))
                ])
                max_qty = max(product_template.packaging_ids.filtered(
                    lambda p: any(qty in p.name for qty in info['package_names'])).mapped('qty'), default=0)
                max_qty_per_package[code_description_key] = max_qty
                # print(info['package_names'],'111111111111111111111111111111111111111111111111111',list(merged_codes),list(merged_descriptions),max_qty_per_package[code_description_key],max_qty)
                # Add processed package names to the set
                processed_packages.add(package_names_key)

            kit_details.append({
                'kit_name': kit_name,
                'merged_info_list': merged_info_list,
                'total_length': total_length,
                'total_width': total_width,
                'total_height': total_height,
                'max_qty_per_package': max_qty_per_package[code_description_key]
            })
            # print(kit_details,'222222222222222222222222222222222222222222222')

        return kit_details
  
      

    



    











































