from aiohttp import web
import socketio

socket_io = socketio.AsyncServer()
app = web.Application()
socket_io.attach(app)

@socket_io.on('message')          # from textbook
async def print_message(socket_id, data):
    print(f"Socket ID: {socket_id}")
    print(f"Data: {data}")

web.run_app(app, port=8080)
