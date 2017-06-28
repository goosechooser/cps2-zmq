-- mame uses its own package path and so it doesn't find lzmq.threads for whatever reason??
-- package.path = '.\\?.lua;\\?\\init.lua;C:\\lua-5.3.3\\systree\\share\\lua\\5.3\\?\\init.lua;C:\\lua-5.3.3\\systree\\share\\lua\\5.3\\?.lua;C:\\Program Files (x86)\\LuaRocks\\lua\\'
local zmq = require("lzmq")
local mp = require("MessagePack")

-- RUN_LENGTH at 1024 manages to send all the data with no slow down
-- RUN_LENGTH of 2048 causes the machine to slow to 70%
-- not sure if multiple passes at different times or multiple processes at once is preferable (read: easier)
local SPRITE_START_ADDR = 0x708000

local RUN_LENGTH = 2000

local s = manager:machine().screens[":screen"]
local cpu = manager:machine().devices[":maincpu"]
local mem = cpu.spaces["program"]

context = zmq.context()
zassert = zmq.assert
mp.set_string('string')

-- Sprite RAM is two 8K SRAMs:
-- One mapped to 700000-707FFF and the other to 708000-70FFFF
-- we mask out this raw data into something more useful on the client (python) side
function read_sprite_ram(start_addr, num_of_entries)
	local sprite_ram = {}
	for i = 1, num_of_entries do
		offset = (i-1) * 0x8
        -- ideally would just do one read_u64(start_addr + offset) 
        -- but python throws a fit trying to convert it
        -- local byte0 = mem:read_u16(start_addr + offset)
		-- local byte1 = mem:read_u16(start_addr + offset + 0x2)
		-- local byte2 = mem:read_u16(start_addr + offset + 0x4)
		-- local byte3 = mem:read_u16(start_addr + offset + 0x6)
        local byte0 = mem:read_u32(start_addr + offset)
        local byte2 = mem:read_u32(start_addr + offset + 0x4)
        sprite_ram[i] = {byte0, byte2} 
	end
	return sprite_ram
end

-- TODO: write coroutine for this that sends frames of just difference
-- Palette starts at 0x90C000 ends 0x3FF
-- a collection of 32 palettes, each palette with 16 colors
function get_palettes(addr)
	palettes = {}
    local row_offset = 0x0
    
	for i = 0, 31 do
		palette = {}
        local color_offset = 0x0

		for j = 1, 16 do
            palette[j] = mem:read_u16(addr + row_offset + color_offset)
            color_offset =  color_offset + 0x2
		end
		palettes[i] = palette
        row_offset = row_offset + 0x20
	end
	return palettes
end

-- overall we're using a pub-sub model of messaging
-- the instance of MAME is a 'client' that just sends messages
-- doesnt care if the message gets received, drops messages if no subscribers (vaguely like UDP)
function setup_client()
    print("setting up publisher client")
    local publisher, err = context:socket{
        zmq.PUB,
        connect = "tcp://127.0.0.1:5556"
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

    local frame = {
        frame_number = frame_number,
        sprites = sprites_,
        palettes = palettes_
    }

    local message = mp.pack(frame)

-- not sure if any benefit could come from using a multi-part messaging scheme
    publisher:send(message)
end

-- set up
publisher = setup_client()

-- CALL BACKS
-- when we close MAME we want to clean up our sockets and zmq context
-- your terminal will also spew a bunch of garbage because register_frame seems to get called at the same time
-- tries to send messages out of a socket that doesnt exist and blows up
-- i'll file a bug report when they approve my forum accounts 
emu.register_stop(function()
    print("client closing")
    local last_msg = {
        frame_number = "closing"
    }
    
    message = mp.pack(last_msg)
    publisher:send(message)

    publisher:close()
    context:term()
end)

-- every frame
emu.register_frame(function()
    send_message()
end)