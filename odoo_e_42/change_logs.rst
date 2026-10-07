V17.0.0.1 (16-03-2024) ***Preksha M***
========================================================
app renamed to odooe42

V17.0.0.1 -------> V17.0.0.2 (19-03-2024) **Preksha M**
========================================================
added functionality for set to quotation.

17.0.0.2 --------->17.0.0.3 (30-03-2024)  **Preksha M**
===============================================================
Added request to approve for sale


17.0.0.3 --------------->17.0.0.4(3-06-2024)  **Prakruthi**
===============================================================
changes made login from in request for approval need to fetch from salesperson.
added object.name in mail.template subject.

17.0.0.4 --------------->17.0.0.5(18-06-2024)  **Preksha M**
===============================================================
1.Added constraint in sale approval for cretion of approval lines
2.Added exchange rate and added warning meesage based on exchange rate.
3.Added Error message if the approval lines not present.
4.Changes in get-data function for fetching the approval lines



17.0.0.5 --------------->17.0.0.6(23-10-2024)  **$@g@r**
===============================================================
1.removed all usererror and validation error

17.0.0.6 --------------->17.0.0.7(10-02-2025)  **$@g@r**
===============================================================
resolved psycopg2.errors.InvalidTextRepresentation: invalid input syntax for type boolean: "The SO total amount '1.13' exceeds the approved limit '0.0'"

17.0.0.7 ----> 17.0.0.8(05-Aug-2026)  **Anke**
========================================================
Added _validate_analytic_distribution() request approval