# Home Assistant Integration - Bouygues Bbox Router

This an override of an official [Home Assistant](https://www.home-assistant.io/) integration.\
The `bbox` integration allows you to observe and control [Bbox router](http://www.bouygues.fr/).

There is currently support for the following device types within Home Assistant:

- Device tracker for connected devices (via subentries configuration)

## Usage

### Initial setup

You must have set a password for your Bbox router web administration page.

The first time Home Assistant will connect to your Bbox, you will need to specify the password of Bbox.

### Supported routers

Only the routers with Bbox OS are supported:

- Bbox (all versions)

### Notes

Note that the Bbox waits for some time before marking a device as inactive, meaning that there will be a small delay (1 or 2 minutes) between the time you disconnect a device and the time it will appear as "away" in Home Assistant.

You should take this into account when specifying the `consider_home` parameter.
On the contrary, the Bbox immediately reports devices newly connected, so they should appear as "home" almost instantly, as soon as Home Assistant refreshes the devices states.

## Projects Scripts

### Start

Use `docker-compose up` command to start a Home Assistant locally.

### Release

This script allow to release a version of the project (Bump project version, update manifest version and create a git tag).\
Use following command : `uv run ./scripts/release.py <version>` where `version` is the version number with semantic versioning.

