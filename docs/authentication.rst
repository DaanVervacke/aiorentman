Authentication
==============

Rentman authenticates every request with a JSON Web Token that is personal
to one Rentman user. Generate it in the Rentman application under
Configuration, Integrations. Only the most recently generated token works:
regenerating invalidates the previous one immediately.

The client takes the token explicitly or falls back to the
``RENTMAN_TOKEN`` environment variable:

.. code-block:: python

   from aiorentman import RentmanClient


   async def main() -> None:
       async with RentmanClient(token="your-api-token") as client:
           page = await client.async_list_equipment()

Construct the client inside a coroutine. Without an injected session it
creates an ``aiohttp.ClientSession``, which needs a running event loop.

Constructing a client without a ``token`` argument or ``RENTMAN_TOKEN`` raises
:class:`aiorentman.RentmanAuthenticationError`. There is no refresh flow. A rejected token surfaces as
:class:`aiorentman.RentmanAuthenticationError` with status 401, and the only
remedy is configuring a new token in Rentman and constructing a new client.

A token can read and write everything its Rentman user can. Treat them like
passwords and never commit them.
