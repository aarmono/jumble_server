#!/usr/bin/env python3
from os import path
from collections import defaultdict
import argparse

from bottle import route, run, request, static_file, response
from multiprocessing import Pool

JUMBLE_DICTIONARY = None

def gen_key(letters):
    return "".join(sorted(letters.lower()))

def load_file(filepath):
    ret = defaultdict(list)
    with open(filepath, "r") as f:
        with Pool() as p:
            words = f.read().splitlines()
            keys = p.map(gen_key, words)
            for (key, word) in zip(keys, words):
                ret[key].append(word)

    return ret

def find_words(jumble_dict, letters):
    key = gen_key(letters)

    return jumble_dict.get(key)

@route('/')
def index():
    this_file_path = path.abspath(__file__)
    this_dir = path.dirname(this_file_path)
    return static_file('index.html', root=this_dir)

@route('/lookup')
def get_token():
    response.content_type = "text/plain"
    words = find_words(JUMBLE_DICTIONARY, request.query.letters)

    return '\n'.join(words) if words is not None else ""

def main():
    parser = argparse.ArgumentParser(description='Jumble server')
    parser.add_argument('--bind', dest='host', type=str, default='127.0.0.1',
                        help='bind to specified ip address')
    parser.add_argument('--port', dest='port', type=int, default=8090,
                        help='bind to specified port')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Enable debug mode in HTTP server')
    parser.add_argument('--dict', dest='dict', type=str, default='words_alpha.txt',
                        help='path to dictionary file, one word per line')

    args = parser.parse_args()

    global JUMBLE_DICTIONARY
    JUMBLE_DICTIONARY = load_file(args.dict)

    run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
