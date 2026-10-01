API reference
=============

Client
------

.. autoclass:: aiorentman.client.RentmanClient
   :members:

Query
-----

.. automodule:: aiorentman.query
   :members: Query, Sort, Filter, FilterOperator, eq, neq, lt, lte, gt, gte, is_null

Models
------

.. autoclass:: aiorentman.RentmanPage
   :members:
.. autoclass:: aiorentman.RentmanLink
   :members:
.. autoclass:: aiorentman.Equipment
   :members:
.. autoclass:: aiorentman.SerialNumber
   :members:
.. autoclass:: aiorentman.EquipmentAssignedSerial
   :members:
.. autoclass:: aiorentman.ActualContent
   :members:
.. autoclass:: aiorentman.EquipmentSetContent
   :members:
.. autoclass:: aiorentman.Folder
   :members:
.. autoclass:: aiorentman.StockLocation
   :members:
.. autoclass:: aiorentman.WarehouseStatus
   :members:
.. autoclass:: aiorentman.Status
   :members:
.. autoclass:: aiorentman.StockMovement
   :members:
.. autoclass:: aiorentman.Repair
   :members:
.. autoclass:: aiorentman.Project
   :members:
.. autoclass:: aiorentman.Subproject
   :members:
.. autoclass:: aiorentman.ProjectEquipment
   :members:
.. autoclass:: aiorentman.Accessory
   :members:
.. autoclass:: aiorentman.Alternative
   :members:
.. autoclass:: aiorentman.Supplier
   :members:
.. autoclass:: aiorentman.Vehicle
   :members:
.. autoclass:: aiorentman.ExtraInputField
   :members:
.. autoclass:: aiorentman.ProjectStatus
   :members:
.. autoclass:: aiorentman.ProjectType
   :members:
.. autoclass:: aiorentman.ProjectFunctionGroup
   :members:
.. autoclass:: aiorentman.ProjectFunction
   :members:
.. autoclass:: aiorentman.ProjectCrew
   :members:
.. autoclass:: aiorentman.ProjectVehicle
   :members:
.. autoclass:: aiorentman.ProjectEquipmentGroup
   :members:
.. autoclass:: aiorentman.ProjectCost
   :members:
.. autoclass:: aiorentman.ProjectRequest
   :members:
.. autoclass:: aiorentman.ProjectRequestEquipment
   :members:
.. autoclass:: aiorentman.Quote
   :members:
.. autoclass:: aiorentman.Contract
   :members:
.. autoclass:: aiorentman.Invoice
   :members:
.. autoclass:: aiorentman.InvoiceLine
   :members:
.. autoclass:: aiorentman.Payment
   :members:
.. autoclass:: aiorentman.LedgerCode
   :members:
.. autoclass:: aiorentman.TaxClass
   :members:
.. autoclass:: aiorentman.Subrental
   :members:
.. autoclass:: aiorentman.SubrentalEquipmentGroup
   :members:
.. autoclass:: aiorentman.SubrentalEquipment
   :members:
.. autoclass:: aiorentman.PurchaseOrder
   :members:
.. autoclass:: aiorentman.PurchaseOrderCost
   :members:
.. autoclass:: aiorentman.PurchaseOrderGlobalCost
   :members:
.. autoclass:: aiorentman.Crew
   :members:
.. autoclass:: aiorentman.CrewAvailability
   :members:
.. autoclass:: aiorentman.CrewRate
   :members:
.. autoclass:: aiorentman.Appointment
   :members:
.. autoclass:: aiorentman.AppointmentCrew
   :members:
.. autoclass:: aiorentman.Invitation
   :members:
.. autoclass:: aiorentman.TimeRegistration
   :members:
.. autoclass:: aiorentman.TimeRegistrationActivity
   :members:
.. autoclass:: aiorentman.LeaveRequest
   :members:
.. autoclass:: aiorentman.LeaveMutation
   :members:
.. autoclass:: aiorentman.LeaveType
   :members:
.. autoclass:: aiorentman.Contact
   :members:
.. autoclass:: aiorentman.ContactPerson
   :members:

Exceptions
----------

.. autoclass:: aiorentman.RentmanError
.. autoclass:: aiorentman.RentmanCommunicationError
.. autoclass:: aiorentman.RentmanTimeoutError
.. autoclass:: aiorentman.RentmanInvalidResponseError
.. autoclass:: aiorentman.RentmanNotFoundError
.. autoclass:: aiorentman.RentmanAuthenticationError
.. autoclass:: aiorentman.RentmanAuthorizationError
.. autoclass:: aiorentman.RentmanRateLimitError
.. autoclass:: aiorentman.RentmanClientClosedError
