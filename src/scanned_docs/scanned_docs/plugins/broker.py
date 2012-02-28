# -*- coding: utf-8 -*-

import argparse
import zmq


def main():
    """ main method """
    parser = argparse.ArgumentParser()

    parser.add_argument("--in")
    parser.add_argument("--out")
    args = parser.parse_args()

    context = zmq.Context()

    frontend = context.socket(zmq.PULL)
    frontend.bind(getattr(args, "in"))

    backend = context.socket(zmq.PUSH)
    backend.bind(args.out)

    while True:
        msg = frontend.recv()
        backend.send(msg)


if __name__ == "__main__":
    main()
