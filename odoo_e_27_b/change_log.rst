
.. 16.0.4.4_beta(V16-Functional9) ------> 17.0.0.1(02-11-2023) **lavanya mg**
.. ========================================================
.. 1. App converted from V16 functional9 repo odoo 16 to odoo 17
.. 2. Added Purchase Request Functionalities from Mas project(16.0.0.3) --->
.. ("Use this module to have notification of requirements of materials and/or external services and keep track of such requirements")
.. 3. Added Merge Po Functionalities from Elsteel project(16.0.0.3) ---> #commented(manufacturing_base need added in depends because we are using y_so_origin fields it is in manufacturing base
.. )
.. 4. Added Purchase Order Routing Functionalities from V16 functional9 repo (16.0.0.2) --->(Routing option given in Purchase order lines)
.. 5. Removed Purchase discount Functionalities
.. 6. Removed Landed Cost Functionalities
.. 7. Added Purchase Adavance Payment Functionalities from V16 functional9 repo (16.0.3.7_Beta)
.. 8. Added Purchase Short Close Functionalities from V16 functional9 repo (16.0.0.5_Beta)----->(1.Given the short close option in action button form view 2. Added short close boolean coloum in Purchase order screen)
.. 9. Removed Serial Number from (Purchase.Order.line) model
.. 10. Merge Po Functionalities manufacturing_base ----->(Removed in depends because we are using y_so_origin fields it is in Purchase base)
.. 11. Added Functionalities Purchase Orders to Bill

.. 17.0.0.1 -------------------> 17.0.0.2(15-11-2023) **lavanya mg**
.. ========================================================================
.. 1. Error resolved (ValueError: Invalid field 'y_so_origin' on model 'stock.picking')
.. 2. Removed  y_so_origin field because we are using y_so_origin fields it is in Manufacturing base
.. 3. Purchase Tolerance added validation for %
.. 4. Merge PO added validation if different document type,Partner,branch
.. 5. Rename order to bill to ---> receipt to bill
.. 6. Document Type readonly when state == 'purchase'
.. 7. Resloved Merge PO Error 
.. 8. Resloved Add PO Charges Issue


.. 17.0.0.2 -------------------> 17.0.0.3(1-12-2023) **Navyashree R**
.. ========================================================================
.. 1. added split po Functionalities


.. 17.0.0.3 -------------------> 17.0.0.4(14-12-2023) **lavanya mg**
.. ========================================================================
.. 1. Updated Purchase Short Close Functionalities

.. V17.0.0.4 -----> V17.0.0.5(**30/Dec/2023**)***Anke***
.. =====================================================
.. Update Setting Values

.. V17.0.0.5 -----> V17.0.0.6(**03/Jan/2024**)***lavanya mg***
.. =====================================================
.. 1. Updated Purchase Request Functionalities
.. 2. Commented code  Purchase Short Close Functionalities (If all moves in a picking are frozen and qty of any move is > 0 )

.. V17.0.0.6 -----> V17.0.0.7(**12/Jan/2024**)***lavanya mg***
.. =====================================================
.. raise UserError ("Select at least one product to short close.") on confirm button in Short Close Wizard

.. V17.0.0.7 -----> V17.0.0.8(**25/Jan/2024**)***Athul***
.. =====================================================
.. removed revision functionality


.. V17.0.0.8 -----> V17.0.0.9(**30/Jan/2024**)***Anke***
.. =====================================================
.. removed revision functionality


.. V17.0.0.9 -----> V17.0.1.0(**30/Jan/2024**)***anke***
.. =====================================================
.. added Product group


.. V17.0.1.0 -----> V17.0.1.1(**08/Feb/2024**)***lavanya mg***
.. =====================================================
.. String name added to fields (y_advace_request_count,y_parent_rfq_ref,y_split_ids)


.. V17.0.1.1 -----> V17.0.1.2(**22/Feb/2024**)***lavanya mg***
.. =====================================================
.. Product group String changed to Purchase Group


.. V17.0.1.2 -----> V17.0.1.3(**23/Feb/2024**)***lavanya mg***
.. =====================================================
.. Updated Product Sourcing functionality


17.0.0.1 (13-03-2024) **Prakruthi C
==================================================
app converted from purchase_base_17-17.0.1.3 to odoo_e_27_b.

17.0.0.1 ---------> 17.0.0.2(22-04-2024) **Sushmitha Patel
==========================================================
PO number mapped GRN Source Document

17.0.0.2 ---------> 17.0.0.3(09-05-2024) **lavanya mg
==========================================================
Updated code from base app purchase_base_17 to odoo_e_27_b

17.0.0.3 ---------> 17.0.0.4(24-05-2024) **lavanya mg
==========================================================
Updated code from base app purchase_base_17 to odoo_e_27_b

17.0.0.4 ---------> 17.0.0.5(19-06-2024) **$@g@r
==========================================================
added approved by and created by for downpayment tree view

17.0.0.5 ---------> 17.0.0.6(01-06-2024) **lavanya mg
==========================================================
Updated code from base app purchase_base_17 to odoo_e_27_b

17.0.0.6 ---------> 17.0.0.7(2-07-2024) **Spurthi
==========================================================
Changed the string name of field (date_required)

17.0.0.7 ---------> 17.0.0.8(18-07-2024) **lavanya mg
==========================================================
Removed _get_overprocessed_stock_moves function and added condition for product sourcing _onchange_product_ids

17.0.0.8 ---------> 17.0.0.9(11-11-2024) **$@g@r
==========================================================
resolved payment term error

17.0.0.9 ---------> 17.0.1.0(22-11-2024) **$@g@r
==========================================================
changed vendor pricelist functionality

17.0.1.1 ---------> 17.0.1.2(02-12-2024) **$@g@r
==========================================================
added analytic distribution validation


17.0.1.2 ---------> 17.0.1.3(23-01-2025) **$@g@r
==========================================================
changed purchase request functionality

17.0.1.3 ---------> 17.0.1.4(04-02-2025) **$@g@r
==========================================================
changed purchase request functionality

17.0.1.4 ---------> 17.0.1.5(04-02-2025) **@meen**
==========================================================
1. Through Purchase request lines if ww create RFQ for partial qty for the remaining qty info will be missing

17.0.1.5 ---------> 17.0.1.6(06-03-2025) **@meen**
==========================================================
Fix the issue confirming the po without purchase request

17.0.1.6 ---------> 17.0.1.7(10-03-2025) **$@g@r**
==========================================================
added domain for rfq window action


17.0.1.7 ---------> 17.0.1.8(13-03-2025) **@meen**
==========================================================
Fix the issue for loading the price unit

17.0.1.8 ---------> 17.0.1.9(13-03-2025) **@meen**
==========================================================
1- Order Line unmerging issue fixed
2- issue fixed create rfq after cancel the po

17.0.1.9 ---------> 17.0.2.0(10-09-2026) **akshatha**
==========================================================
added a validation before purchase approval


17.0.2.0 ---------> 17.0.2.1(15-09-2026) **Pooja**
==========================================================
added mandatory reason wizard on PR cancel/reject


17.0.2.1 ---------> 17.0.2.2(05-10-2026) **Pooja**
==================================================================
Changed Purchase Orders window action domain to purchase, done, cancel
