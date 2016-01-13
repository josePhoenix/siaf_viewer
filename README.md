# SIAF Viewer

*Note: This is probably mostly useful internally at STScI.*

This viewer provides an interactive wrapper around functionality available in the `jwxml` submodule of [WebbPSF](https://github.com/mperrin/webbpsf) to manipulate the Science Instrument Aperture File (SIAF). Currently it lets the user plot a selectable subset of apertures in the `Tel` frame (V2, V3 coordinates).

On startup, the viewer loads the five instrument SIAFs from the WebbPSF data package based on the value of `$WEBBPSF_PATH` (falling back to the Central Store copy if that variable is unset). There is currently no facility for substituting in a new file for a particular instrument. (Instead, copy the WebbPSF data and try out your edits there with `$WEBBPSF_PATH` set appropriately.)

There's still plenty of functionality in the `SIAF` manipulation class that isn't exposed in this interface. (For example, plotting apertures in other frames, showing detector and science origin indicators, etc.)

The script does not take any command line arguments. Invoke with `python siaf_viewer.py`.
