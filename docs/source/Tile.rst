.. py:module:: cps2_zmq.process.Tile
.. py:currentmodule:: cps2_zmq.process.Tile

:py:mod:`Tile` Module
===========================

The :py:mod:`~cps2_zmq.process.Tile` module provides a class with the same name which is
used to represent a single CPS2 graphical tile. This module has a few factory functions and provides
functions for converting the :py:mod:`~cps2_zmq.process.Tile` to a variety of formats for further processing.

Examples
--------

The Tile Class
-------------------

.. autoclass:: cps2_zmq.process.Tile.Tile

The :py:class:`~cps2_zmq.process.Tile.Tile` class has the following methods

.. automethod:: cps2_zmq.process.Tile.Tile.unpack
.. automethod:: cps2_zmq.process.Tile.Tile.pack
.. automethod:: cps2_zmq.process.Tile.Tile.to_array
.. automethod:: cps2_zmq.process.Tile.Tile.to_bmp
.. automethod:: cps2_zmq.process.Tile.Tile.to_png

Factories
---------
.. autofunction:: cps2_zmq.process.Tile.new
.. autofunction:: cps2_zmq.process.Tile.from_image

