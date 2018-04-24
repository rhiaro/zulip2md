from collections import OrderedDict
import argparse
import json


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

        # Sniff subsequent messages from the same speaker
        # afters = []
        # for message in data.values():
        #     if message["content"].startswith("@**"):
        #         continue
        #     if message["timestamp"] > first_message["timestamp"] and message["content"].startswith(".."):
        #         text = "%s\n%s" % (text, message["content"])

        return text, author
    else:
        return None, None


def to_markdown(data):
    markdown = ""
    attributed = OrderedDict()

    attendees = []
    proposals = []
    resolutions = []
    scribes = []
    for message in data.values():
        # Get attendees
        if "present+" in message["content"]:
            attendees.append(message["sender_full_name"])
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

        # Format scribe messages
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
            # TODO: format these differently

        # TODO: Capture emoji reactions to messages

    # Time sort
    for k, v in attributed.items():
        if v["author"] is not None:
            print(v["time"])
            print(v["author"])
        if not v["scribed"]:
            print(">>>> %s", v["content"])
        else:
            print(v["content"])

    # Glue together

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
    markdown = to_markdown(data)
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
