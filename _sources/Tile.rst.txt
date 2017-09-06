.. py:module:: cps2zmq.process.Tile
.. py:currentmodule:: cps2zmq.process.Tile

:py:mod:`Tile` Module
===========================

The :py:mod:`~cps2zmq.process.Tile` module provides a class with the same name which is
used to represent a single CPS2 graphical tile. This module has a few factory functions and provides
functions for converting the :py:mod:`~cps2zmq.process.Tile` to a variety of formats for further processing.

Examples
--------

The Tile Class
-------------------

.. autoclass:: cps2zmq.process.Tile.Tile

The :py:class:`~cps2zmq.process.Tile.Tile` class has the following methods

.. automethod:: cps2zmq.process.Tile.Tile.from_packed_bytes
.. automethod:: cps2zmq.process.Tile.Tile.pack
.. automethod:: cps2zmq.process.Tile.Tile.to_array
.. automethod:: cps2zmq.process.Tile.Tile.to_bmp
.. automethod:: cps2zmq.process.Tile.Tile.to_png
.. automethod:: cps2zmq.process.Tile.from_image
