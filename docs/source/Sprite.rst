.. py:module:: cps2_zmq.process.Sprite
.. py:currentmodule:: cps2_zmq.process.Sprite

:py:mod:`Sprite` Module
=======================

The :py:mod:`~cps2_zmq.process.Sprite` module provides a class with the same name which is
used to represent a CPS2 Sprite. This module has a few factory functions and provides
functions for converting the :py:mod:`~cps2_zmq.process.Sprite` to a variety of formats for further processing.

Examples
--------

A few sprites acquired by using :py:mod:`~cps2_zmq.gather` and then printed with :py:meth:`~cps2_zmq.process.Sprite.Sprite.topng`: 
    .. image:: ../../../cps2-zmq-docs/images/sprite_ex_1.png
        :width: 32 px
        :height: 48 px
    .. image:: ../../../cps2-zmq-docs/images/sprite_ex_2.png
        :width: 112 px
        :height: 48 px
    .. image:: ../../../cps2-zmq-docs/images/sprite_ex_3.png
        :width: 96 px
        :height: 16 px

The Sprite Class
----------------

.. autoclass:: cps2_zmq.process.Sprite.Sprite

The :py:class:`~cps2_zmq.process.Sprite.Sprite` class has the following methods

.. automethod:: cps2_zmq.process.Sprite.Sprite.color_tiles
.. automethod:: cps2_zmq.process.Sprite.Sprite.toarray
.. automethod:: cps2_zmq.process.Sprite.Sprite.tobmp
.. automethod:: cps2_zmq.process.Sprite.Sprite.topng
.. automethod:: cps2_zmq.process.Sprite.Sprite.totile

Factories
---------

.. autofunction:: cps2_zmq.process.Sprite.fromdict
.. autofunction:: cps2_zmq.process.Sprite.from_image

Functions
---------

.. autofunction:: cps2_zmq.process.Sprite.list2d

Processing Sprites further
--------------------------
