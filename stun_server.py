#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import socket
import struct

_HEADER = struct.Struct("!HHI12s")
_ATTRIBUTE_HEADER = struct.Struct("!HH")
_MAGIC_COOKIE = 0x2112A442
_BINDING_REQUEST = 0x0001
_BINDING_SUCCESS = 0x0101
_USERNAME = 0x0006
_XOR_MAPPED_ADDRESS = 0x0020
_MAX_DATAGRAM_BYTES = 65_535

log = logging.getLogger("stun")


def _username(request: bytes) -> str | None:
    offset = _HEADER.size
    while offset + _ATTRIBUTE_HEADER.size <= len(request):
        attribute_type, length = _ATTRIBUTE_HEADER.unpack_from(request, offset)
        value_start = offset + _ATTRIBUTE_HEADER.size
        value_end = value_start + length
        if value_end > len(request):
            return None
        if attribute_type == _USERNAME:
            return request[value_start:value_end].decode("utf-8", errors="replace")
        offset = value_start + ((length + 3) & ~3)
    return None


def _binding_success(request: bytes, peer: tuple[str, int]) -> bytes | None:
    if len(request) < _HEADER.size:
        return None

    message_type, length, cookie, transaction_id = _HEADER.unpack_from(request)
    if message_type != _BINDING_REQUEST or cookie != _MAGIC_COOKIE:
        return None
    if length % 4 or len(request) != _HEADER.size + length:
        return None

    address = struct.unpack("!I", socket.inet_aton(peer[0]))[0] ^ cookie
    port = peer[1] ^ (cookie >> 16)
    attribute = struct.pack(
        "!HHBBHI", _XOR_MAPPED_ADDRESS, 8, 0, 1, port, address
    )
    header = _HEADER.pack(_BINDING_SUCCESS, len(attribute), cookie, transaction_id)
    return header + attribute


def _serve(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((host, port))
        log.info("Listening on udp://%s:%d", *server.getsockname())
        while True:
            request, peer = server.recvfrom(_MAX_DATAGRAM_BYTES)
            response = _binding_success(request, peer)
            if response is None:
                continue

            log.info(
                "Binding request peer=%s:%d transaction=%s username=%s",
                peer[0],
                peer[1],
                request[8:20].hex(),
                _username(request) or "-",
            )
            try:
                server.sendto(response, peer)
            except OSError as exc:
                log.warning("Could not respond to %s:%d: %s", peer[0], peer[1], exc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Log WebRTC STUN binding requests and return XOR-MAPPED-ADDRESS."
    )
    parser.add_argument("--host", default="0.0.0.0", help="IPv4 address to bind")
    parser.add_argument("--port", type=int, default=3478, help="UDP port to bind")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    try:
        _serve(args.host, args.port)
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
