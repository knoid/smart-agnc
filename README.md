# Smart AT&T Global Network Client

Smart AT&T Global Network Client improves upon the AT&T Global Network Client by
 * showing the status of the VPN connection with just a glance at the tray icon
 * reconnecting the VPN connection when it drops
 * providing quick connection through the tray icon
 * customized scripts to extend it your way.

## Prerequisites

Have the AT&T Global Network Client installed.

## Installation

Just download the package you need from the
[releases](/knoid/smart-agnc/releases) page.

## Hidden features

Some of this features require modifying the configuration file in
`~/.smart-agnc`. File uses `.ini` format with section and keys.

### Execute a script when a certain connection state is met

Add new section called `scripts` and set there any numeric status code as the
key and a file path as the value. For example, to execute `my_script.sh` when
the connection is established you would need:

    [vpn]
    ...

    [scripts]
    400 = /home/my_user/my_script.sh

You may also need to use `350 - STATE_VPN_RECONNECTED` depending on your purpose.
You can find every connection state in [agn_binder.py](src/py-interface/agn_binder.py).

### Customize maximum timeout for connection attempt

The maximum time out for establishing a VPN connection by the client can be
defined in the configuration file. Add `timeout` key followed by timeout, in
seconds, in the `vpn` section.

If a connection is not established within the max number of seconds timeout,
a disconnect event is issued to restart the connection process.

### Exit button

Adding the option `--exit-button` when starting the app will add an exit button
to the context menu.

## Disclaimer

I'm not a C programmer, so collaborations will be greatly appreciated.
