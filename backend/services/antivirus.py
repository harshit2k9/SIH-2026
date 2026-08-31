"""
Async ClamAV scanning via the clamd daemon's INSTREAM protocol, implemented
directly over asyncio streams (avoids pulling in a blocking clamd client
library that would stall the event loop).

Protocol: send 'zINSTREAM\\0', then length-prefixed chunks (4-byte big-endian
size + chunk bytes), then a zero-length chunk to signal EOF. Response line
tells us OK / FOUND <signature>.
"""
import asyncio
import struct

from app.config import settings


class ScanResult:
    def __init__(self, infected: bool, signature: str | None = None):
        self.infected = infected
        self.signature = signature


async def scan_file(file_path: str) -> ScanResult:
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(settings.CLAMAV_HOST, settings.CLAMAV_PORT),
        timeout=settings.CLAMAV_TIMEOUT,
    )
    try:
        writer.write(b"zINSTREAM\0")
        await writer.drain()

        with open(file_path, "rb") as f:
            while chunk := f.read(settings.UPLOAD_CHUNK_SIZE):
                writer.write(struct.pack("!L", len(chunk)) + chunk)
                await writer.drain()

        writer.write(struct.pack("!L", 0))   # zero-length chunk = EOF marker
        await writer.drain()

        response = await asyncio.wait_for(reader.readline(), timeout=settings.CLAMAV_TIMEOUT)
        response_text = response.decode(errors="ignore").strip("\0\n ")

        if "FOUND" in response_text:
            signature = response_text.split(":")[-1].replace("FOUND", "").strip()
            return ScanResult(infected=True, signature=signature)
        return ScanResult(infected=False)
    finally:
        writer.close()
        await writer.wait_closed()
