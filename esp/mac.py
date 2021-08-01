import machine
import ujson as json

node_id = machine.unique_id()
node_id = '{:02x}{:02x}{:02x}{:02x}'.format(node_id[0], node_id[1], node_id[2], node_id[3])
print('Node ' + node_id)

_MAC_ACK_PING = json.dumps({
    'cmd': 'ack_ping',
    'id': node_id
}).encode('ascii')

_MAC_ACK_SYNC = json.dumps({
    'cmd': 'ack_sync',
    'id': node_id
}).encode('ascii')

_MAC_ACK_CONF = json.dumps({
    'cmd': 'ack_conf',
    'id': node_id
}).encode('ascii')


def nak(reason=None):
    return json.dumps({
        'cmd': 'nak',
        'reason': '' if reason is None else reason
    }).encode('ascii')


def process_command(data, client):
    packet = None
    try:
        packet = data.decode('ascii')
        packet = json.loads(packet)
        command = packet['cmd']
        if command == 'ping':
            return _MAC_ACK_PING
        elif command == 'sync':
            client.mac_sync()
            return _MAC_ACK_SYNC
        elif command == 'conf':
            new_conf = packet['new']
            client.update_conf(new_conf)
            return _MAC_ACK_CONF
        else:
            return nak('Command handler not found for command: ' + command)
    except UnicodeError:
        # Ascii decode error
        print('[ERROR] Cannot decode incoming packet')
        return None
    except ValueError:
        # Json decode error
        print('[ERROR] Cannot parse json')
        return None
    except KeyError:
        # Invalid command
        print('[ERROR] No \'cmd\' field found in packet - ' + repr(packet))
        return None
