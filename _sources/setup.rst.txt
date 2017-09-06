Project Setup
*************

Before using the `gather` package, some setup is required.

* Download and install PyZMQ (and python if not already)
* Download and install Lua5.X - I'm using 5.3 but 5.1 or 5.2 should work.
* Download and install LZMQ
* Download and install MAME (version > 1.7.6)

Running the Project
===================

* Launch the 'Client' - `python [path to MameServer.py]`
* Launch the 'Server' - from the command line `mame64 [rom_name] -autoboot_script zmq_server.lua`
* Close the MAME window when you've captured enough data
