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

## Disclaimer

I'm no C programmer, so collaborations will be greatly appreciated.
