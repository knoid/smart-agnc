# Smart AT&T Global Network Client

This will create a seamless VPN connection between you and your enterprise by
adding a tray icon and keeping you connected whenever possible.

## Prerequisites

I'm assuming you already have the AT&T Global Network Client working so you'll
only need to compile C programs.

### In Ubuntu

    sudo apt-get install build-essential

### In RedHat

    sudo yum install gcc-c++ glibc-devel.i686

## Installation

 1. Extract into any folder.
 2. Go to `src` folder and compile with `make`.
 3. Execute `run.sh`.
 4. (optional) Add `run.sh` to the "Startup Applications" list.

## Hidden feature

### Execute a script when a certain connection state is met

Inside your configuration file located in `~/.smart-agnc` you can add a section
called `scripts` and add there any numeric status code as the key and a file
path as the value. For example, to execute `my_script.sh` when the connection is
established you would need:

    [vpn]
    account = ...
    username = ...
    password = ...

    [scripts]
    400 = /home/my_user/my_script.sh

You may also need to use `350 - STATE_VPN_RECONNECTED` depending on your purpose.
You can find every connection state in [agn_binder.py](src/py-interface/agn_binder.py).

## Disclaimer

I'm no C programmer, so collaborations will be greatly appreciated.
