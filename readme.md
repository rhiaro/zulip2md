# Zulip to Markdown

[Zulip](https://zulipchat.com) is an open source chat solution which uses streams (like channels) and topics (for organising content within a stream).

The Zulip API lets you export a stream with all messages to JSON. This script takes that export, extracts the topic of your choice, and returns it formatted as markdown. You could convert this markdown to HTML or MediaWiki syntax or whatever else you like, to create a static copy of your Zulip chat logs.

## Usage

```
$ git clone git@github.com:rhiaro/zulip2md.git
$ python zulip2md --in=zulip-meeting.json --out=/path/to/out.md --topic=yyyy-mm-dd
```

If no topic is passed, it exports the whole stream.

## Getting the export JSON

You could use [zulip-export](https://github.com/zulip/zulip/blob/master/tools/zulip-export/zulip-export) to export your stream. See that repo for more usage examples, but for reference you wanna do something like:

```
$ pip install zulip
$ git clone git@github.com:zulip/zulip.git
$ cd zulip/tools/zulip-export
$ python zulip-export --user=<your email address> --api-key=<your api key> --stream=<stream-name>
```

And the `zulip-stream-name.json` file lands in the `zulip-export` directory.