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
