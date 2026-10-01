Materials and equipment
=======================

Rentman calls every inventory item a material, and the API exposes each one
as an equipment resource. One page of materials:

.. code-block:: python

   async with RentmanClient(token=token) as client:
       page = await client.async_list_equipment()
       mixer = page.items[0]
       print(mixer.code, mixer.name, mixer.price)

Filtering, sorting, field selection, and expansion go through the query
object:

.. code-block:: python

   from aiorentman import Query, Sort, eq, lt

   query = Query(
       fields=("name", "code", "price"),
       sort=(Sort("name"),),
       filters=(eq("type", "0"), lt("price", 200)),
       limit=100,
   )
   page = await client.async_list_equipment(query)

Field names are the schema property names of the resource, including
``custom_<number>`` names for custom fields. The library validates them
against the pinned OpenAPI document in its contract test, not at runtime.

Linked fields such as ``folder`` hold a :class:`aiorentman.RentmanLink`
with the API path of the linked resource. Pass the field to ``expand`` and
the parser returns the full typed model instead:

.. code-block:: python

   from aiorentman import Query, RentmanLink

   page = await client.async_list_equipment(Query(expand=("folder",)))
   folder = page.items[0].folder
   if not isinstance(folder, RentmanLink):
       print(folder.name)

Combination materials carry their definition in
``async_list_equipment_set_content`` and the physical reality of a
serialized case is recorded in actual content, available per serial number
through ``async_list_actual_content_of_serial_number``.
