import argparse
import json


def get_topic(json, topic):
    pass


def to_markdown(json):
    pass


def write(markdown):
    pass


def convert(json, topic):
    pass


def cli():

    parser = argparse.ArgumentParser()
    parser.add_argument("--inf", help="JSON file to parse")
    parser.add_argument("--out", help="Markdown file to write out to")
    parser.add_argument("--topic", help="Topic to extract from stream")

    args = parser.parse_args()
    infile = args.inf
    outfile = args.out
    topic = args.topic

    print infile
    print outfile
    print topic


if __name__ == '__main__':
    cli()
