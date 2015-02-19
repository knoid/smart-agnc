## v0.1.4

## v0.1.3 (2015-02-18)

 * Added help and close buttons to about window
 * Added alert messages translations
 * Multi-threading for AGNC communications
 * Multi-threading for checking updates
 * Using iniparse library to preserve comments in configuration file
 * Added pt_BR translation

## v0.1.2 (2015-01-28)

 * Restarting AGNC daemon when DAEMON_DEAD state is received
 * Restarting AGNC daemon in background process
 * Windows start centered
 * Logs now rotate depending on their file size

## v0.1.1 (2015-01-26)

 * Restarting AGNC daemon when necessary improves stability
 * Connection information window redesign
 * Added an About dialog
 * Notify OS when finished loading
 * Checks for new versions

## v0.1.0 (2015-01-22)

 * All main features implemented, so bumping version to 0.1.0
 * Added proxy settings
 * Added logs to improve feedback quality

## v0.0.8 (2015-01-20)

 * Packages for everybody!
 * fixed python 2.4 module compatibility
 * improved agnc subprocess' stability

## v0.0.7 (2015-01-17)

 * Turned the project into a python module
 * Alert messages with better syntax
 * Automatic AGNC services restart when they misbehave
 * Optional exit button

## v0.0.6 (2015-01-12)

 * External scripts configuration supports `~` in the path
 * Automatic and manual change password dialog
 * AgnBinder events don't overlap (fixes IP: None bug)

## v0.0.5 (2015-01-10)

 * Makefile is now compatible with RedHat and Ubuntu's libraries
 * External script's output now shows up through notify
 * Timeout for the connecting process, defined in config (default: 40 secs)
 * Multiple icons sets!

## v0.0.4 (2015-01-08)

 * Different icons for different color schemes
 * Using python's own logging class
 * Translation into es_AR now available
 * Encoding password in configuration file

## v0.0.3 (2015-01-07)

 * Formatted values inside the "VPN Connection Information" window
 * Shows VPN's assigned IP inside popup menu
 * Configuration file supports external edits
 * Ability to execute external scripts on certain conditions

## v0.0.2 (2015-01-06)

 * Added a tray icon!
 * Improved installation instructions
 * Improved agnc python interface stability
 * Using GNU GPL v2 License

## v0.0.1 (2015-01-05)

 * Window to configure your VPN credentials
 * Connect and disconnect from VPN
 * Automatic VPN reconnection
 * Tray icon supports Ubuntu's appindicator and GTK's StatusIcon
