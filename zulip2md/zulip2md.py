import os
import time
import json
import argparse
from datetime import datetime
from collections import OrderedDict


def get_topic(jason, topic):
    timestream = {}
    for message in jason:
        if message["subject"] == topic:
            timestream[message["timestamp"]] = message

    data = OrderedDict(sorted(timestream.items()))
    return data


def get_scribed_block(first_message, data):
    content = first_message["content"].split("** says")
    if len(content) > 1:  # TODO: fixed when the regex is in
        text = content[1].strip()
        author = content[0].replace("@**", "")

        return text, author
    else:
        return None, None


def sort_data(data):
    markdown = ""
    attributed = OrderedDict()

    attendees = []
    topics = []
    proposals = []
    resolutions = []
    scribes = []
    for message in data.values():
        # Get attendees
        if "present+" in message["content"]:
            attendees.append(message["sender_full_name"])
        # Get topics
        if "TOPIC:" in message["content"]:
            topic = message["content"].replace(
                "-", "").replace("*", "").replace("TOPIC:", "").strip()
            topics.append((message["timestamp"], topic))
        # Get proposals
        if "PROPOSAL:" in message["content"] or "PROPOSED:" in message["content"]:
            proposals.append(message["content"])
        # Get resolutions
        if "RESOLUTION:" in message["content"] or "RESOLVED:" in message["content"]:
            resolutions.append(message["content"])

        # Find the scribe(s)
        if "scribe: " in message["content"].lower():
            scribe = message["content"].lower().split("scribe: ")[1]
            if "\n" in scribe:
                scribe = scribe.split("\n")[0]
            scribe = scribe.replace("@", "")
            scribe = scribe.replace("*", "")
            scribe = scribe.strip()
            scribes.append(scribe)

        # Scribe messages
        # TODO replace this with regex /@\*\*([^*]*)\*\*/ says
        if message["content"].startswith("@**"):
            text, author = get_scribed_block(message, data)
            if text is not None:
                attributed[message["timestamp"]] = {
                    "time": message["timestamp"],
                    "author": author,
                    "content": text,
                    "scribed": True
                }

        elif message["content"].startswith(".."):
            attributed[message["timestamp"]] = {
                "time": message["timestamp"],
                "author": None,
                "content": message["content"],
                "scribed": True
            }
        else:
            # Inline interjections
            attributed[message["timestamp"]] = {
                "time": message["timestamp"],
                "author": message["sender_full_name"],
                "content": message["content"],
                "scribed": False
            }

        # TODO: Capture emoji reactions to messages

        os.environ["TZ"] = "Europe/Paris"
        time.tzset()
        date = datetime.fromtimestamp(int(next(iter(attributed))))
        meta = {
            "date": date,
            "attendees": attendees,
            "topics": topics,
            "resolutions": resolutions,
            "proposals": proposals,
            "scribes": scribes
        }

    return attributed, meta


def to_markdown(messages, meta):

    markdown = ""
    topics = ""

    template = """
## Minutes: Credible Web CG (%s)

* [Agenda](https://credweb.org/agenda/%s.html)
* Attendees: %s
* Scribe(s): %s

### Topics
%s


    """

    topics_template = "1. [%s](#%s)"

    author_template = "[#](#%s) **%s**: %s\n"
    line_template = "[#](#%s) %s\n"
    text_template = "> %s: %s\n"

    date = datetime.strftime(meta["date"], "%d %B %Y")
    datelink = datetime.strftime(meta["date"], "%Y%m%d")

    for time, topic in meta["topics"]:
        topics = "%s%s" % (topics, topics_template % (topic, time))

    markdown = template % (date, datelink, (',').join(
        meta["attendees"]), (',').join(meta["scribes"]), topics)

    print(markdown)

    for time, msg in messages.items():
        if msg["author"] is not None:
            if not msg["scribed"]:
                formatted = text_template % (msg["author"], msg["content"])
            else:
                formatted = author_template % (
                    msg["time"], msg["author"], msg["content"])
        else:
            formatted = line_template % (msg["time"], msg["content"])

        markdown = "%s%s" % (markdown, formatted)

    return markdown


def write(markdown, outfile):
    with open(outfile) as file:
        pass


def convert(args):

    infile = args.inf
    outfile = args.out
    topic = args.topic

    with open(infile) as f:
        jason = json.load(f)

    data = get_topic(jason, topic)
    messages, meta = sort_data(data)
    markdown = to_markdown(messages, meta)
    # write(markdown, outfile)


def cli():

    parser = argparse.ArgumentParser()
    parser.add_argument("--inf", help="JSON file to parse")
    parser.add_argument("--out", help="Markdown file to write out to")
    parser.add_argument("--topic", help="Topic to extract from stream")

    args = parser.parse_args()

    convert(args)


if __name__ == '__main__':
    cli()
