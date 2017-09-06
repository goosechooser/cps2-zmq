.. py:module:: cps2zmq.gather.MameServer
.. py:currentmodule:: cps2zmq.gather.MameServer

:py:mod:`MameServer` Module
===========================
The :py:mod:`~cps2zmq.gather.MameServer` module contains a class of the same name.
It is the first stop in a message processing chain. It receives messages from the 'server' running in a MAME instance
and pushes them to a queue for workers to pull from.

Examples
--------

The MameServer Class
---------------------

.. autoclass:: cps2zmq.gather.MameServer.MameServer
