#!/usr/bin/env python3
"""
Simple HTTPS reverse proxy for Cortex RAG server.
Wraps the HTTP RAG server with self-signed HTTPS.
"""
import ssl
import asyncio
from pathlib import Path
import subprocess

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Forward requests from HTTPS client to HTTP backend."""
    backend_reader, backend_writer = await asyncio.open_connection('localhost', 8100)

    async def forward(src, dst):
        try:
            while True:
                data = await src.read(8192)
                if not data:
                    break
                dst.write(data)
                await dst.drain()
        except Exception:
            pass
        finally:
            dst.close()

    await asyncio.gather(
        forward(reader, backend_writer),
        forward(backend_reader, writer),
        return_exceptions=True
    )


async def main():
    cert_file = Path('/tmp/cortex-cert.pem')
    key_file = Path('/tmp/cortex-key.pem')

    # Generate self-signed certificate if not exists
    if not cert_file.exists() or not key_file.exists():
        print("Generating self-signed certificate...")
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', str(key_file),
            '-out', str(cert_file),
            '-days', '365', '-nodes',
            '-subj', '/CN=100.97.25.117'
        ], check=True)
        print(f"Certificate created: {cert_file}")

    # Create SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(cert_file, key_file)

    # Start HTTPS server
    server = await asyncio.start_server(
        handle_client,
        '0.0.0.0',
        8443,
        ssl=ssl_context
    )

    addr = server.sockets[0].getsockname()
    print(f'HTTPS proxy running on https://100.97.25.117:8443')
    print(f'Proxying to http://localhost:8100')
    print('Press Ctrl+C to stop')

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nStopped')
