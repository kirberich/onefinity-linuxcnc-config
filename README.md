# LinuxCNC configuration for a Onefinity Elite Foreman using a FlexiHAL card

⚠️ This is the actual specific configuration for my machine - it might be useful for adapting for other machines, but there is a lot of custom and highly specific stuff in here, don't expect anything here to be safe for use on your machine!

## Sources

- The configuration is adapted from the example configuration here: https://github.com/Expatria-Technologies/remora-flexi-hal
- The toolchange logic is heavily inspired by the code and information found here: http://www.linuxcnc.org/index.php/english/forum/10-advanced-configuration/5596-manual-tool-change--tool-lengh-touch-off?start=30#48235

## Features

- Z probing routine (using a probe block) for the current coordinate system
    - NOTE: As a safety measure, this routine doesn't start probing until the probe pin is triggered (see below)
- Tool length offset probing routine (run automatically after homing)
- Manual tool change routine, including probing tool lengths after every tool change
- Loaded tool is persisted on every tool change and loaded on startup
- Custom M-Code for applying saved coordinate systems to G59.3 to allow a large number of fixtures at known positions

## Custom M-Codes used in this config

Making tools persistent across restarts (see `python/remap.py`)

- `M910` - saves the tool currently in the spindle to a file
- `M911` - loads the persisted tool number from a file and sets it as the current tool

Z probing

- `M938` - Probe Z zero using a probing block (Set `_BlockThickness` variable in `subroutines/probe_z.ngc`)
- `M939` - Probe tool length offset (see `subroutines/tool_z_offset.ngc`) (Uses `M910` and `M911`)

Custom coordinate system

- `M959 P<i>` Activate custom coordinate system (see `python/remap.py` for list of coordinate systems)


## Z probing routine

The custom `M938` routine is just a standard G38.2 probing routine with a few tweaks to make it safer and compatible with tool length offsets

It needs one variable to be set, which is the thickness of the probing block.

### Safety check

The probe routine doesn't start until the probe pin is triggered once. This is to make sure that the magnet/clamp/etc is attached correctly to the spindle, and verify that touching the block to the tool in the spindle actually triggers the probe - without this, the probing will happily probe into the workpiece.

To use it:
- Position the tool above the location to be probed
- Connect the magnet/clamp for the probing block to the spindle
- Touch the block to the tool briefly and put the block back down on the workpiece
- At that point, the probe sequence starts. It will probe the block once fast, then again more slowly.

## Tool length offset probing

The loaded tool is automatically probed to set the offset after homing (`custom_postgui.hal`. This relies on the custom logic to persist loaded tools, which allows linuxcnc to know which tool was loaded across restarts.

⚠️ If you change the tool manually and then turn on and home the machine, LinuxCNC will wrongly assume that the old tool is loaded. The tool offsets should still be correct, but the correct procedure is to always use `M6 T<tool_number>` to change a tool.

## Manual tool change

The `M6` manual tool change command has been overwritten to run a custom sequence:

- First, `change_prolog` from `python/remap.py` is run. This does a few safety checks and saves state that is needed for the tool change
- Then, `subroutines/tool_change.ngc` is run. This does the following:
    - Remember the current position (to jog back to later)
    - If the requested tool is already loaded, only run the normal `M6` routine (essentially does nothing)
    - Move to a convenient location for changing the tool and wait for confirmation the tool has been changed
    - Probe the tool length offset
    - Save the loaded tool to a file to persist across restarts
    - Move back to the starting X/Y location

## Custom coordinate systems
This feature allows storing a large number of custom work offsets, mostly for fixtures in known locations

Calling `M959 P<i>` activates the G59.3 coordinate system, but then applies a custom x/y offset, depending on the index chosen.

The offsets are defined in `python/remap.py`.

Note that when using this, the program has to use G59.3 as its work offset!
Changing the G59.3 X/Y zero coordinates has no effect on programs using this feature, as the offset is always reset to the saved one.