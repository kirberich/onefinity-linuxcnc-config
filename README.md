# LinuxCNC configuration for a Onefinity Elite Foreman using a FlexiHAL card

⚠️ This is the actual specific configuration for my machine - it might be useful for adapting for other machines, but there is a lot of custom and highly specific stuff in here, don't expect anything here to be safe for use on your machine!

## Sources

- The configuration is adapted from the example configuration here: https://github.com/Expatria-Technologies/remora-flexi-hal
- The toolchange logic is heavily inspired by the code and information found here: http://www.linuxcnc.org/index.php/english/forum/10-advanced-configuration/5596-manual-tool-change--tool-lengh-touch-off?start=30#48235

## Features

- Z probing routine for the current coordinate system
- Tool length offset probing routine (run automatically after homing)
- Manual tool change routine, including probing tool lengths after every tool change
- Loaded tool is persisted on every tool change and loaded on startup
- Custom M-Code for applying saved coordinate systems to G59.3 to allow a large number of fixtures at known positions
