# Smart AT&T Global Network Client

This will create a seamless VPN connection between you and your enterprise by
adding a tray icon and keeping you connected whenever possible.

## Prerequisites

I'm assuming you already have the AT&T Global Network Client working so you'll
only need to compile C programs.

### In Ubuntu

    sudo apt-get install build-essential libc6-dev-x32

### In RedHat

    sudo yum install gcc-c++ glibc-devel.i686

## Installation

 1. Extract into any folder.
 2. Go to the extracted folder and compile with `make`.
 3. Execute `run.sh`.
 4. (optional) Add `run.sh` to the "Startup Applications" list.

## Hidden features

To make use of this features, you'll have to modify your configuration file
located in `~/.smart-agnc`. It is formatted like an `.ini` file with sections
and keys.

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

### Timeout for the connection process

You can define the maximum time the client has to get you connected. By adding
the key `timeout` inside the `vpn` section you set the number of seconds it
should wait until the process restarts by issuing a disconnect event.

## Disclaimer

I'm not a C programmer, so collaborations will be greatly appreciated.
