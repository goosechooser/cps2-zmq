-- mame uses its own package path and so it doesn't find lzmq.threads for whatever reason??
-- package.path = '.\\?.lua;\\?\\init.lua;C:\\lua-5.3.3\\systree\\share\\lua\\5.3\\?\\init.lua;C:\\lua-5.3.3\\systree\\share\\lua\\5.3\\?.lua;C:\\Program Files (x86)\\LuaRocks\\lua\\'

local json = require("json")
local zmq = require("lzmq")

-- RUN_LENGTH at 1024 manages to send all the data with no slow down
-- RUN_LENGTH of 2048 causes the machine to slow to 70%
-- not sure if multiple passes at different times or multiple processes at once is preferable (read: easier)
local SPRITE_START_ADDR = 0x708000
local RUN_LENGTH = 1024

local s = manager:machine().screens[":screen"]
local cpu = manager:machine().devices[":maincpu"]
local mem = cpu.spaces["program"]

context = zmq.context()
zassert = zmq.assert

-- Sprite RAM is two 8K SRAMs:
-- One mapped to 700000-707FFF and the other to 708000-70FFFF
-- we mask out this raw data into something more useful on the client (python) side
function read_sprite_ram(start_addr, num_of_entries)
	local sprite_ram = {}
	for i = 1, num_of_entries do
		offset = (i-1) * 0x8
        -- ideally would just do one read_u64(start_addr + offset) 
        -- but python throws a fit trying to convert it
        local byte0 = mem:read_u16(start_addr + offset)
		local byte1 = mem:read_u16(start_addr + offset + 0x2)
		local byte2 = mem:read_u16(start_addr + offset + 0x4)
		local byte3 = mem:read_u16(start_addr + offset + 0x6)
        sprite_ram[i-1] = {byte0, byte1, byte2, byte3} 
	end
	return sprite_ram
end

-- Palette starts at 0x90C000 ends 0x3FF
-- a collection of 32 palettes, each palette with 16 colors
function get_palettes(addr)
	palettes = {}
    local row_offset = 0x0
    
	for i = 0, 31 do
		palette = {}
        local color_offset = 0x0

		for j = 0, 15 do
            palette[j] = mem:read_u16(addr + row_offset + color_offset)
            color_offset =  color_offset + 0x2
		end
		palettes[i] = palette
        row_offset = row_offset + 0x20
	end
	return palettes
end

-- threading DOESNT WORK (also the nature of threads in Lua is ... its own topic)
-- lzmq.threads doesn't seem to provide any benefit
-- thread.start() in MAME provided 'luaengine' doesn't work [for me/at all]
-- local thread_code = [[
--     local zmq = require "lzmq"
--     local zthreads = require "lzmq.threads"
--     zassert = zmq.assert

--     print('ye')
--     local context = zthreads.get_parent_ctx()
--     print("setting up subscriber")
--     local subscriber, err = context:socket{
--         zmq.SUB,
--         subscribe = '',
--         connect = "tcp://localhost:5557"
--     }
--     zassert(subscriber, err)

--     local i = 0
--     while i < 5 do
--         print('should block')
--         local message = subscriber:recv()
--         if message then
--             printf(message)
--             i = i + 1
--         end
--     end

--     subscriber:close()

-- ]]

-- overall we're using a pub-sub model of messaging
-- the instance of MAME acts like the 'server' and just sends data out
-- doesnt care if the message gets received, drops messages if no subscribers (vaguely like UDP)
function setup_server()
    print("setting up publisher")
    local publisher, err = context:socket{
        zmq.PUB,
        bind = "tcp://*:5556"
    }
    zassert(publisher, err)
    return publisher
end

-- right now it just reads the same area each frame and sends it out (dumb method)
-- a more detailed exploration of when addresses are written to would be fruitful
-- also figuring out how often the 32x16 palette structure changes and only sending the changes would be good
function send_message()
    local frame_number = s:frame_number()
	local sprites_ = read_sprite_ram(SPRITE_START_ADDR, RUN_LENGTH)
    local palettes_ = get_palettes(0x90C000)

    frame = {
        frame_number = frame_number,
        sprites = sprites_,
        palettes = palettes_
    }

-- serializing w/ json because im lazy
    local message = json.encode(frame)
-- not sure if any benefit could come from using a multi-part messaging scheme
-- im working on a machine with 16gb of ram so lmao you think im gonna make this leaner
    publisher:send(message)
end

-- MAME provided callback 'emu.register_start(callback)' doesnt get called when MAME starts??
-- set up
publisher = setup_server()

-- callbacks
-- when we close MAME we want to clean up our sockets and zmq context
-- your terminal will also spew a bunch of garbage because register_frame seems to get called at the same time
-- tries to send messages out of a socket that doesnt exist and blows up
-- i'll file a bug report when they approve my forum accounts 
emu.register_stop(function()
    print("server closing")
    last_msg = {
        frame_number = "closing",
        sprites = "ok",
        palette = "double ok"
    }

    message = json.encode(last_msg)
    print('msg encoded')
    publisher:send(message)
    print('msg sent')
    publisher:close()
    print('socket closed')
    context:term()
    print('context terminated')
end)

-- EVERY FRAME
emu.register_frame(function()
    send_message()
end)

-- there is also
-- emu.register_frame_done(function()
--     fun stuff here
--     wow maybe receive messages??
-- end)

-- not super sure of how the frame/frame_done callbacks interact
-- trying to send AND receive seems to drop machine speed to 70% which is 
-- not great
