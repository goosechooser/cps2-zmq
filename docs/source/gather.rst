The gather Package
==================

:mod:`gather` is responsible for setting up a connection between a MAME instance (acting as a server)
and a client (:mod:`MameClient` in this implementation). This is handled by the ZeroMQ library using the PyZMQ bindings.

Previous iterations of this project accomplished this through manual creation and connecting of Pipes, 
Queues, and Threads, but this became unweldy.

Currently only :mod:`MameWorker` is provided for processing messages, but other classes could be written as needed.

.. toctree::
   :maxdepth: 1

   MameClient
   MameSink
   MameWorker
