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
       filters=(eq("type", "item"), lt("price", 200)),
       limit=100,
   )
   page = await client.async_list_equipment(query)

Field names are the schema property names of the resource, including
``custom_<number>`` names for custom fields. The library passes them through
unchecked, except that filters reject the reserved parameter names
``fields``, ``sort``, ``expand``, ``limit``, and ``offset``, and filters and
sorts reject the generated fields ``qrcodes``, ``tags``, and
``qrcodes_of_serial_numbers`` with a ``ValueError``. Other fields the schema
marks as generated, such as ``displayname``, pass through unchecked, and the
API rejects them as filters and as sorts while a limit is set. A ``limit`` outside 1
to 1500, a negative ``offset``, and an id below 1 raise ``ValueError`` too.

Linked fields such as ``folder`` hold a :class:`aiorentman.RentmanLink`
with the API path of the linked resource. Pass the field to ``expand`` and
the parser returns the full typed model instead, when the field annotation
names one. A field annotated as ``RentmanLink`` only parses an expanded
object to ``None`` on an optional link and to an empty link on a required
one, and the object stays available in ``raw``:

.. code-block:: python

   from aiorentman import Folder, Query

   page = await client.async_list_equipment(Query(expand=("folder",)))
   folder = page.items[0].folder
   if isinstance(folder, Folder):
       print(folder.name)

Combination materials carry their definition in
``async_list_equipment_set_content`` and the physical reality of a
serialized case is recorded in actual content, available per serial number
through ``async_list_actual_content_of_serial_number``.
