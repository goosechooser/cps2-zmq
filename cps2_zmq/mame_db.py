import sqlite3
from cps2_zmq.process import Tile

def create_database(db_name):
    """
    Make the database.
    """
    conn = sqlite3.connect(db_name)
    with conn:
        conn.execute("""CREATE TABLE tiles
                    (memory_address text, tile_data int, dimensions int)
        """)

def create_entry(conn, memory_address, tile_data, dimensions):
    """
    Create a new tile entry.
    """
    with conn:
        sql = "INSERT INTO tiles VALUES (?,?,?)"
        conn.execute(sql, (memory_address, tile_data, dimensions))

def read_entry(conn, memory_address):
    """
    Returns the entry for the given memory address.
    """
    with conn:
        sql = "SELECT * FROM tiles WHERE memory_address = ?"
        result = [row for row in conn.execute(sql, (memory_address,))]
    return result[0]

def update_tile_data(conn, memory_address, tile_data):
    """
    Update existing tile entry.
    """
    with conn:
        # cursor = conn.cursor()
        sql = """
        UPDATE tiles
        SET tile_data = ? 
        WHERE memory_address = ?
        """
        conn.execute(sql, (tile_data, memory_address))

def create_tile_entry(conn, tile):
    create_entry(conn, hex(tile.address), tile.data, tile.dimensions)

if __name__ == "__main__":
    pass
