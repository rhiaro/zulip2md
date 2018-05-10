import os
import time
import json
import argparse
from datetime import datetime
from collections import OrderedDict


def is_in(term, string):
    terms = {
        "prop": ["proposal:", "proposed:"],
        "reso": ["resolved:", "resolution:"],
        "topi": ["topic:"],
        "pres": ["present+"],
        "scri": ["scribe:"]
    }
    for t in terms[term]:
        if t in string.lower():
            return True

    return False


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


def strip_quotes(text):
    parts = text.split("```")
    if len(parts) > 1:
        stripped = "Re: \"%s\" -- %s" % (parts[0], parts[1])
        return stripped
    else:
        return text


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
        if is_in("pres", message["content"]):
            attendees.append(message["sender_full_name"])
            continue
        # Get topics
        if is_in("topi", message["content"]):
            topic = message["content"].replace(
                "-", "").replace("*", "").replace("TOPIC:", "").replace("topic:", "").replace("Topic:", "").strip()
            topics.append((message["timestamp"], topic))
            attributed[message["timestamp"]] = {
                "time": message["timestamp"],
                "author": None,
                "content": topic,
                "scribed": False
            }
            continue
        # Get proposals
        if is_in("prop", message["content"]):
            proposals.append(message["content"])
        # Get resolutions
        if is_in("reso", message["content"]):
            resolutions.append(message["content"])

        # Find the scribe(s)
        if is_in("scri", message["content"]):
            scribe = message["content"].lower().split("scribe: ")[1]
            if "\n" in scribe:
                scribe = scribe.split("\n")[0]
            scribe = scribe.replace("@", "")
            scribe = scribe.replace("*", "")
            scribe = scribe.strip()
            scribes.append(scribe)
            continue

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
                "content": strip_quotes(message["content"]),
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

### Minutes

"""

    topics_template = "1. [%s](#%s)\n"

    author_template = """<a id="%s" href="#%s">#</a> **%s** says: %s\n\n"""
    line_template = """<a id="%s" href="#%s">#</a> %s\n\n"""
    text_template = """<a id="%s" href="#%s">#</a> [%s] *%s*\n\n"""
    topic_template = """### %s\n\n"""

    date = datetime.strftime(meta["date"], "%d %B %Y")
    datelink = datetime.strftime(meta["date"], "%Y%m%d")

    for time, topic in meta["topics"]:
        topics = "%s%s" % (topics, topics_template % (topic, time))

    markdown = template % (date, datelink, (', ').join(
        meta["attendees"]), (', ').join(meta["scribes"]), topics)

    for time, msg in messages.items():

        if msg["author"] is not None:

            if not msg["scribed"]:  # inline interjections
                formatted = text_template % (
                    msg["time"], msg["time"], msg["author"], msg["content"])
            else:  # First statement
                formatted = author_template % (msg["time"], msg["time"], msg[
                                               "author"], msg["content"])
        else:
            if not msg["scribed"]:  # topics
                formatted = topic_template % msg["content"]
            else:  # subsequent statements
                formatted = line_template % (
                    msg["time"], msg["time"], msg["content"])

        markdown = "%s%s" % (markdown, formatted)

    return markdown


def write(markdown, outfile):
    with open(outfile, 'w') as file:
        file.write(markdown)


def convert(args):

    infile = args.inf
    outfile = args.out
    topic = args.topic

    with open(infile) as f:
        jason = json.load(f)

    data = get_topic(jason, topic)
    messages, meta = sort_data(data)
    markdown = to_markdown(messages, meta)
    # print(markdown)
    write(markdown, outfile)


def cli():

    parser = argparse.ArgumentParser()
    parser.add_argument("--inf", help="JSON file to parse")
    parser.add_argument("--out", help="Markdown file to write out to")
    parser.add_argument("--topic", help="Topic to extract from stream")

    args = parser.parse_args()

    convert(args)


if __name__ == '__main__':
    cli()
