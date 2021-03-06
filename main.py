import glob
import json
import re
import socket
import time
from enum import Enum
from pathlib import Path
from threading import Event

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)


class State(Enum):
    CONNECT = 1
    MESSAGE = 2
    DONE = 3


def poll(robot_root_path: str, zone_id: int, stop_event: Event=Event()) -> None:
    message = json.dumps({
        'zone': zone_id,
        'mode': 'competition',
    }).encode('utf-8')

    state = State.CONNECT
    while not stop_event.is_set():
        try:
            if state is State.CONNECT:
                sock.connect(robot_root_path + "game/state")
                state = State.MESSAGE

            if state is State.MESSAGE:
                sock.sendall(message)
                response_data = sock.recv(2048).decode('utf-8')
                response_message = json.loads(response_data)

                if response_message.get('zone') == zone_id:
                    print("done")
                    state = State.DONE
                else:
                    state = State.MESSAGE

            if state is State.DONE:
                time.sleep(1)
                state = State.MESSAGE

        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
            print("cant connect")
            state = State.CONNECT


def main() -> None:
    my_dir = Path(__file__).parent

    # Get all files named zone-1, zone-2, etc..
    id_files = glob.glob(str(my_dir / "zone-*"))
    if not id_files:
        print("Could not find any zone ids (files like zone-1 or zone-0)")
        exit(0)

    id_file = id_files[0]
    if len(id_files) > 1:
        print("Warning, found more than 1 zone file!")

    # Get the first number in the filename
    zone_number_match = re.search(r'\d', id_file)
    if zone_number_match is None:
        exit("No zone id number found in filename {!r}".format(id_file))

    zone_id = int(zone_number_match.group(0))
    print("ID:", zone_id)

    poll("/var/robotd/", zone_id)


if __name__ == "__main__":
    main()
