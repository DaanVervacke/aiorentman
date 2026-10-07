Quickstart
==========

Install with uv:

.. code-block:: bash

   uv add aiorentman

List one page of materials, or walk every material with the cursor handled
for you:

.. code-block:: python

   import asyncio

   from aiorentman import RentmanClient


   async def main() -> None:
       async with RentmanClient(token="your-api-token") as client:
           page = await client.async_list_equipment()
           print(page.item_count, "materials on this page")

           async for equipment in client.async_iter_equipment():
               print(equipment.code, equipment.name)


   asyncio.run(main())

Every list method returns a :class:`aiorentman.RentmanPage` with the parsed
items and the paging metadata. Every iter method is an async generator that
follows ``next_page_url`` until it is exhausted.

Requests are paced against the documented limits of 10 requests per second
and 20 concurrent requests, set through ``requests_per_second`` and
``max_concurrent``. Pass ``requests_per_second=None`` to disable pacing when
another part of your application already throttles.
