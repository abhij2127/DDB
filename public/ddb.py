import sqlite3
import threading

# Define the host and port number to be used
HOST = 'localhost'
PORT = 5000

# Create a database connection and cursor
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Create a table for storing key-value pairs
cursor.execute("CREATE TABLE IF NOT EXISTS key_value (key TEXT PRIMARY KEY, value TEXT)")

# List to hold all the peer connections
peer_connections = []

# Function to handle incoming messages from peers
def handle_peer_messages(peer_conn):
    while True:
        try:
            message = peer_conn.recv(1024)
            if message:
                message_parts = message.decode().split(' ')
                command = message_parts[0]
                key = message_parts[1]
                if command == 'PUT':
                    value = message_parts[2]
                    cursor.execute("INSERT OR REPLACE INTO key_value (key, value) VALUES (?, ?)", (key, value))
                    conn.commit()
                    print(f"PUT {key}={value}")
                elif command == 'GET':
                    cursor.execute("SELECT value FROM key_value WHERE key=?", (key,))
                    result = cursor.fetchone()
                    if result:
                        value = result[0]
                        peer_conn.send(value.encode())
                    else:
                        peer_conn.send(b'')
        except:
            index = peer_connections.index(peer_conn)
            peer_connections.remove(peer_conn)
            peer_conn.close()
            break

# Function to start the server and accept incoming connections
def start_server():
    print(f"Server started on port {PORT}")
    while True:
        # Accept incoming connections
        peer_conn, peer_address = server_socket.accept()

        # Add the new peer connection to the list
        peer_connections.append(peer_conn)

        # Start a new thread to handle incoming messages from the peer
        peer_thread = threading.Thread(target=handle_peer_messages, args=(peer_conn,))
        peer_thread.start()

# Function to send a message to all connected peers
def broadcast_message(message):
    for peer_conn in peer_connections:
        peer_conn.send(message.encode())

# Function to start the client and connect to other peers
def start_client():
    # Continuously send messages to other peers
    while True:
        message = input()
        message_parts = message.split(' ')
        command = message_parts[0]
        key = message_parts[1]
        if command == 'PUT':
            value = message_parts[2]
            cursor.execute("INSERT OR REPLACE INTO key_value (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            broadcast_message(message)
            print(f"PUT {key}={value}")
        elif command == 'GET':
            cursor.execute("SELECT value FROM key_value WHERE key=?", (key,))
            result = cursor.fetchone()
            if result:
                value = result[0]
                print(f"GET {key}={value}")
            else:
                value = ''
            broadcast_message(f"GET {key}={value}")
        else:
            print("Invalid command")

if __name__ == '__main__':
    choice = input("Start as server (s) or client (c): ")

    if choice == 's':
        # Create a socket object for the server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to a specific address and port
        server_socket.bind((HOST, PORT))

        # Listen for incoming connections
        server_socket.listen()

        start
