#!/usr/bin/env python3
"""Local-only FGF editor launcher and read-only SBC buttstore catalog.
No arbitrary file access routes, no credentials in the editor HTML.
"""
from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import urlsplit
import webbrowser

HERE = Path(__file__).resolve().parent
EDITOR = HERE.parent / 'index.html'
DEFAULT_STORES = Path.home() / 'SBC_Streamer_Apps' / 'user_data' / 'buttstores'
MAX_BYTES = 2 * 1024 * 1024


def catalog(store_dir=None):
    store_dir = Path(store_dir) if store_dir is not None else DEFAULT_STORES
    stores = []
    try:
        files = sorted(store_dir.iterdir(), key=lambda x: x.name.casefold()) if store_dir.is_dir() else []
    except OSError:
        files = []
    for path in files:
        if len(stores) >= 24:
            break
        try:
            if path.is_symlink() or not path.is_file() or path.suffix.lower() != '.buttstore' or path.stat().st_size > MAX_BYTES:
                continue
            raw = json.loads(path.read_text(encoding='utf-8'))
            if raw.get('buttstore_format') != '3DCP-BUTTSTORE' or not isinstance(raw.get('body'), dict):
                continue
            cards = raw['body'].get('cards', [])
            if not isinstance(cards, list):
                continue
            safe_cards = []
            for item in cards[:250]:
                if not isinstance(item, dict) or not item.get('id'):
                    continue
                ident = str(item['id'])[:120]
                label = str(item.get('label') or ident)[:120]
                # Publish only a recognized non-sensitive classification, never raw card fields.
                tags = {'sponsor':'sponsor','partner':'partner','deets':'normal','fan':'fan','special':'special','uni':'uni','obs':'obs',
                        'title':'title','opener':'opener','curtain cue':'curtain cue','ending sponsor':'ending sponsor',
                        'ending talk':'ending talk','after talk':'after talk','thank you':'thank you','last card':'last card',
                        'go away segment':'go away segment','credits':'credits','chat thank you':'chat thank you'}
                types=[str(item.get(k,'')).strip().lower() for k in ('group','section','category','segment','border_type','border_tag','border')]
                group=next((tags[x] for x in types if x in tags),'')
                safe_cards.append({'id': ident, 'label': label, 'group': group})
            if safe_cards:
                stores.append({'file': path.name[:180], 'cards': safe_cards})
        except (OSError, ValueError, TypeError, UnicodeError, AttributeError):
            continue
    return {'schema': 'FGF/local-buttstore-catalog/1', 'stores': stores}


class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if os.environ.get('FGF_VERBOSE') == '1':
            super().log_message(fmt, *args)

    def do_GET(self):
        host = self.headers.get('Host', '')
        if host not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'):
            self.send_error(403, 'Invalid host')
            return
        # A foreign website must never read the local catalog, even if a browser is misconfigured.
        if self.headers.get('Sec-Fetch-Site', 'none') not in ('none', 'same-origin'):
            self.send_error(403, 'Cross-site access prohibited')
            return
        if self.headers.get('Origin', '') not in ('', f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'):
            self.send_error(403, 'Cross-origin access prohibited')
            return
        path = urlsplit(self.path).path
        if path in ('/', '/index.html', '/fgf/FGF_alpha27_Studio_Cues_Editor.html'):
            try:
                content = EDITOR.read_bytes()
            except OSError:
                self.send_error(404)
                return
            self.send_payload(content, 'text/html; charset=utf-8')
        elif path == '/__fgf/catalog':
            content = json.dumps(catalog(getattr(self.server, 'store_dir', DEFAULT_STORES)), ensure_ascii=False).encode('utf8')
            self.send_payload(content, 'application/json; charset=utf-8')
        elif path == '/__fgf/health':
            self.send_payload(b'{"ok":true,"version":"alpha.4"}', 'application/json; charset=utf-8')
        elif path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
        else:
            self.send_error(404, 'FGF does not expose arbitrary files')

    def send_payload(self, body, mime):
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Cross-Origin-Resource-Policy', 'same-origin')
        self.send_header('Content-Security-Policy', "frame-ancestors 'none'")
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def open_in_browser(url):
    choice = os.environ.get('FGF_BROWSER', '').strip()
    browser = choice if choice and shutil.which(choice) else (shutil.which('librewolf') or shutil.which('firefox'))
    if browser:
        subprocess.Popen([browser, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        webbrowser.open(url)


def main():
    parser = argparse.ArgumentParser(description='FGF Studio Cues editor (local buttstore discovery)')
    parser.add_argument('--no-browser', action='store_true', help='Print URL without opening a browser')
    parser.add_argument('--buttstores-dir', type=Path, default=DEFAULT_STORES, help='read-only source for .buttstore metadata')
    parser.add_argument('--state-file',type=Path,default=None)
    args = parser.parse_args()
    if not EDITOR.is_file():
        parser.error('FGF editor HTML missing at '+str(EDITOR))
    with ThreadingHTTPServer(('127.0.0.1', 0), AppHandler) as server:
        server.store_dir = args.buttstores_dir.expanduser().resolve()
        address = f'http://127.0.0.1:{server.server_port}/'
        print('FGF Studio Cues alpha.4 — local editor')
        print('Editor:', address)
        print('Default buttstores:', server.store_dir)
        print('Deck Card file discovery:', len(catalog(server.store_dir)['stores']), 'collection(s)')
        print('Launcher runs in detached app mode by default. DMS runs separately.')
        if args.state_file:
            args.state_file.parent.mkdir(parents=True,exist_ok=True)
            args.state_file.write_text(json.dumps({'port':server.server_port,'pid':os.getpid()}),encoding='utf-8')
        if not args.no_browser:
            open_in_browser(address)
        try:
            server.serve_forever(poll_interval=0.2)
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
            if args.state_file:
                try:
                    old=json.loads(args.state_file.read_text(encoding='utf-8'))
                    if old.get('pid')==os.getpid():args.state_file.unlink(missing_ok=True)
                except (OSError,ValueError):pass


if __name__ == '__main__':
    main()
