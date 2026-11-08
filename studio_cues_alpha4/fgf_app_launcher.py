#!/usr/bin/env python3
"""Detached local FGF editor application entrypoint. Starts once, opens browser.
No terminal needs to remain open and no privileged filesystem routes exist.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import urllib.request

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
STATE=Path.home()/'.cache'/'fgf'/'studio_alpha4.json'
LOG=Path.home()/'.cache'/'fgf'/'studio_alpha4.log'

def alive():
    try:
        data=json.loads(STATE.read_text(encoding='utf-8'))
        port=int(data['port']);pid=int(data['pid'])
        if not(1024<=port<=65535 and pid>0):return None
        request=urllib.request.Request(f'http://127.0.0.1:{port}/__fgf/health',headers={'Host':f'127.0.0.1:{port}'})
        with urllib.request.urlopen(request,timeout=.45) as response:
            if json.loads(response.read()).get('version')=='alpha.4':return (port,pid)
    except (OSError,ValueError,KeyError,TypeError,urllib.error.URLError):pass
    return None

def open_browser(url):
    custom=os.environ.get('FGF_BROWSER','').strip()
    cmd=custom if custom and shutil.which(custom) else next((p for p in ('librewolf','firefox','chromium') if shutil.which(p)),None)
    if cmd:subprocess.Popen([cmd,url],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    elif shutil.which('xdg-open'):subprocess.Popen(['xdg-open',url],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    else:print(url)

def main():
    parser=argparse.ArgumentParser(description='FGF SBC application launcher (no terminal wait)')
    parser.add_argument('--stop',action='store_true',help='Stop the local FGF metadata service')
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    if args.stop:
        current=alive()
        if current:
            os.kill(current[1],signal.SIGTERM)
            print('Stopping local FGF helper')
        else:print('No FGF helper running')
        return 0
    if not (ROOT/'index.html').is_file():
        print('FGF editor missing:',ROOT/'index.html',file=sys.stderr);return 1
    current=alive()
    if not current:
        STATE.parent.mkdir(parents=True,exist_ok=True)
        with LOG.open('ab') as log:
            subprocess.Popen([sys.executable,str(HERE/'launch_fgf.py'),'--no-browser','--state-file',str(STATE)],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
        for _ in range(35):
            current=alive()
            if current:break
            time.sleep(.07)
    if not current:
        print('FGF launcher could not start; see',LOG,file=sys.stderr);return 2
    url=f'http://127.0.0.1:{current[0]}/'
    if not args.no_browser:open_browser(url)
    print('FGF editor launched:',url)
    return 0
if __name__=='__main__':raise SystemExit(main())
