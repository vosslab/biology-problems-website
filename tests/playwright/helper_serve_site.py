#!/usr/bin/env python3
"""Serve the built MkDocs site for the managed Playwright test server."""

# Standard Library
import pathlib
import argparse
import functools
import subprocess
import http.server


class PlaywrightHTTPServer(http.server.ThreadingHTTPServer):
	"""Accept concurrent browser asset requests without dropping connections."""

	# Browser workers fetch many assets concurrently; keep enough queued connections.
	# Set the listen queue before ThreadingHTTPServer activates its socket.
	request_queue_size = 128


#============================================
def parse_args() -> argparse.Namespace:
	"""Read the port chosen once by the Playwright runner."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-p', '--port', dest='port', type=int, required=True)
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Serve only the repository's built site on loopback."""
	args = parse_args()
	root_result = subprocess.run(
		['git', 'rev-parse', '--show-toplevel'],
		cwd=pathlib.Path(__file__).resolve().parent,
		check=True, capture_output=True, text=True,
	)
	site_directory = pathlib.Path(root_result.stdout.strip()) / 'site'
	# ASVS 4.1.1: retain the standard static handler's file-type response headers.
	handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=site_directory)
	with PlaywrightHTTPServer(('127.0.0.1', args.port), handler) as server:
		server.serve_forever()


if __name__ == '__main__':
	main()
