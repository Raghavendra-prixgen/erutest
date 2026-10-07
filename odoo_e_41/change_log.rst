17.0.0.1 (15-03-2024)  **Chandanashree S**
===============================================================
App Converted from UV purchase_approval_17

17.0.0.1 --------------->17.0.0.2(30-03-2024)  **Preksha M**
===============================================================
Added request to approve purchase

17.0.0.2 --------------->17.0.0.3(06-05-2024)  **Chandanashree**
===============================================================
Added Log for request to approv e and approve button

17.0.0.3 --------------->17.0.0.4(07-05-2024)  **Prakruthi**
===============================================================
On click of confirm button validation error is not getting before approvals only.

17.0.0.4 --------------->17.0.0.5(07-05-2024)  **Vishnu**
===============================================================
add purchase approvals email triggering

17.0.0.5 --------------->17.0.0.6(15-05-2024)  **Vishnu**
===============================================================
Revert the purchase approvals email triggering functionality

17.0.0.6 --------------->17.0.0.7(22-05-2024)  **Preksha M**
===============================================================
added currency field in purchase approval and document type.
changed the function to call the function get_data in write method
added conditions for approval grid and added conditions for creating approval configuration
added log for doctype

17.0.0.7 --------------->17.0.0.8(22-05-2024)  **Preksha M**
===============================================================
changes in function  upgrade bug fix

17.0.0.8 --------------->17.0.0.9(27-05-2024)  **Preksha M**
===============================================================
Added summary in manifest

17.0.0.9 --------------->17.0.1.0(29-05-2024)  **Preksha M**
===============================================================
Changed the purchase approval functionality removed the currency 
and added email trigger functionality.


17.0.1.0 --------------->17.0.1.1(3-06-2024)  **Prakruthi**
===============================================================
changes made login from in request for approval need to fetch from buyes.
added object.name in mail.template subject.

17.0.1.1 --------------->17.0.1.2(13-06-2024)  **Spurthi**
===============================================================
1: Bug-----> Fixed issue (2nd level approval were able to approve , without 1st level approval)

17.0.1.2 --------------->17.0.1.3(25-06-2024)  **Preksha M**
===============================================================
Server action to update the currency rate and 

17.0.1.3 --------------->17.0.1.4(2-07-2024)  **Spurthi**
===============================================================
Added group access for unlock button in po

17.0.1.4 --------------->17.0.1.5(21-08-2024)  **Vishnu M**
===============================================================
bug fix 

17.0.1.5 --------------->17.0.1.6(27-08-2024)  **Navya Shree R**
===============================================================
reject state added in purchase order and after click on request for approval the state changed to to approve in purchase order 
and while mail triggering issue is there that is resolved when po is rejected

17.0.1.6 --------------->17.0.1.7(30-10-2024)  **$@g@r
===============================================================
remove usererror and validation error for purchase approval

17.0.1.7 --------------->17.0.1.8(28-11-2024)  **$@g@r
===============================================================
invisible get_approval button

17.0.1.7 --------------->17.0.1.9(06-04-2025)  **Navya shree R**
===============================================================
1. approve button visible for respective users [changes done as in eruvaka repo app odoo_e_41]
2. when po is cancelled then recipt also need to cancelled
3. when RFQ is created through purchase request if the created RFQ is cancelled then purchase request should alow to create other RFQ


17.0.1.9 --------------->17.0.2.0(08-04-2025)  **$@g@r**
===============================================================
button approve added groups and hide get approval button 



17.0.2.0 --------------->17.0.2.1(30-04-2025)  **$@g@r**
===============================================================
removed po warning 

17.0.2.1 --------------->17.0.2.2(11-07-2025)  **Navya shree**
===============================================================
commented the ir.rules of [rule_purchase_order_own_documents,rule_purchase_order_1st_lvl_approval,rule_purchase_order_2nd_lvl_approval,rule_purchase_order_3rd_lvl_approval,rule_purchase_order_4th_lvl_approval and rule_purchase_order_5th_lvl_approval]

17.0.2.2 --------------->17.0.2.3(14-01-2026)  **Navya shree**
===============================================================
1. added validation in request_for_approve button if purchase.order amount is greater than maximum_approval_limit amount set in global.model