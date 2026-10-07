aiorentman
===========

Unofficial asynchronous Python library to interact with the `Rentman API
<https://api.rentman.net/>`_. It covers every documented read path, from
equipment, serial numbers, stock, and repairs to projects, crew, invoices,
tasks, and files, with create, update, and delete methods for every
documented write path.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   quickstart
   authentication
   equipment
   serial-numbers
   api

Rentman runs one rolling API version and migrates integrations
automatically. This library pins its contract to OpenAPI 1.16.0 and its
test suite checks every endpoint and model against that document.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
