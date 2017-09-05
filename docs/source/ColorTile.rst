.. py:module:: cps2zmq.process.ColorTile
.. py:currentmodule:: cps2zmq.process.ColorTile

:py:mod:`ColorTile` Module
===========================

The :py:mod:`~cps2zmq.process.ColorTile` module provides a class with the same name which is
used to represent a CPS2 Tile with color added. This module has a few factory functions and provides
functions for converting the :py:mod:`~cps2zmq.process.ColorTile` to a variety of formats for further processing.

Examples
--------

The ColorTile Class
-------------------

.. autoclass:: cps2zmq.process.ColorTile.ColorTile

The :py:class:`~cps2zmq.process.ColorTile.ColorTile` class has the following methods

.. automethod:: cps2zmq.process.ColorTile.ColorTile.to_array
.. automethod:: cps2zmq.process.ColorTile.ColorTile.to_bmp
.. automethod:: cps2zmq.process.ColorTile.ColorTile.to_png
.. automethod:: cps2zmq.process.ColorTile.ColorTile.to_tile

Factories
---------
.. autofunction:: cps2zmq.process.ColorTile.from_tile
.. autofunction:: cps2zmq.process.ColorTile.from_image

