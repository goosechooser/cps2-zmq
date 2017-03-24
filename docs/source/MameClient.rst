.. py:module:: cps2_zmq.gather.MameClient
.. py:currentmodule:: cps2_zmq.gather.MameClient

:py:mod:`MameClient` Module
===========================
The :py:mod:`~cps2_zmq.gather.MameClient` module contains a class of the same name.
It is the first stop in a message processing chain. It receives messages from the 'server' running in a MAME instance
and pushes them to a queue for workers to pull from.

Examples
--------

The MameClient Class
---------------------

.. autoclass:: cps2_zmq.gather.MameClient.MameClient
