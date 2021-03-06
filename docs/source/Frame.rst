.. py:module:: cps2zmq.process.Frame
.. py:currentmodule:: cps2zmq.process.Frame

:py:mod:`Frame` Module
=======================

The :py:mod:`~cps2zmq.process.Frame` module provides a class with the same name which is
used to represent a CPS2 Frame. This module has a few factory functions and provides
functions for converting the :py:mod:`~cps2zmq.process.Frame` to a variety of formats for further processing.

Example
--------

A Frame acquired by using :py:mod:`~cps2zmq.gather` and then printed with :py:meth:`~cps2zmq.process.Frame.Frame.to_png`:

    .. image:: _images/Frame_ex.png
        :width: 400 px
        :height: 400 px


The Frame Class
----------------

.. autoclass:: cps2zmq.process.Frame.Frame

The :py:class:`~cps2zmq.process.Frame.Frame` class has the following methods

.. automethod:: cps2zmq.process.Frame.Frame.add_sprites
.. automethod:: cps2zmq.process.Frame.Frame.to_png
.. automethod:: cps2zmq.process.Frame.Frame.to_file
.. automethod:: cps2zmq.process.Frame.from_file

Processing Frames further
--------------------------
