import os
from struct import Struct
import sqlite3
import pytest
from cps2_zmq import mame_db
from cps2_zmq.process import Tile

db_name = "test_db.db"

@pytest.fixture(scope="session")
def db_conn(request):
    print("setting db up")
    with sqlite3.connect(db_name) as conn:
        # cursor = conn.cursor()
        conn.execute("""CREATE TABLE tiles
                    (memory_address text, tile_data int, dimensions int)
        """)
        yield conn
        conn.execute("DROP TABLE tiles")
        print("tearing db down")

def test_create_database():
    test_db = "some_db.db"
    mame_db.create_database(test_db)

    assert os.path.exists(test_db)
    os.remove(test_db)

def test_create_entry(db_conn):
    mame_db.create_entry(db_conn, '0x69', 69, 16)

    for row in db_conn.execute('select * from tiles'):
        assert tuple(row) == ('0x69', 69, 16)

def test_update_tile_data(db_conn):
    mame_db.update_tile_data(db_conn, '0x69', 420)

    for row in db_conn.execute('select * from tiles'):
        assert tuple(row) == ('0x69', 420, 16)

def test_read_entry(db_conn):
    result = mame_db.read_entry(db_conn, '0x69')
    assert result == ('0x69', 420, 16)

def test_create_tile_entry(db_conn):
    ROW_FMT = Struct(8 * 'c')
    tile_data = 'F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4F1F2F3F4'
    tile = Tile.new(1000, bytearray.fromhex(tile_data), 8)
    mame_db.create_tile_entry(db_conn, tile)

    result = mame_db.read_entry(db_conn, hex(tile.address))
    assert result[0] == hex(tile.address)
    assert bytearray(result[1]).hex() == '0f0f0f0f00080605' * 8
    assert result[2] == 8

