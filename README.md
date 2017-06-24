# documentation (in progress)
<https://goosechooser.github.io/cps2-zmq/>

# how to setup
* download/install python + pyzmq
* download/install lua5.X + lzmq (good luck)
* clone repo 
* make a new virtualenv or whatever
* `pip install -e .`
* `launch MameServer.py`
* `launch mame64 with -autoboot_script zmq_client.lua`

# what do
* MAME 'client' sends sprite + palette data out
* python 'server' collects it and pushes it to threads for processing
* worker threads do their work and write the contents of a Frame to disk in JSON format
* these serialized Frame objects can be used for whatever
* see <https://github.com/goosechooser/cps2-gfx-editor> for ideas [This is out of date]

