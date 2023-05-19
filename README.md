# Professional Firmware for the Voxelab Aquila and Creality Ender 3 Printers

![GitHub contributors](https://img.shields.io/github/contributors/classicrocker883/MriscocProUI.svg)
![GitHub Release Date](https://img.shields.io/github/release-date/classicrocker883/MriscocProUI.svg)
[![Build Status](https://github.com/classicrocker883/MriscocProUI/workflows/CI/badge.svg)](https://github.com/classicrocker883/MriscocProUI/actions)
[![Build Configs](https://github.com/classicrocker883/MriscocProUI/actions/workflows/compile-configs.yml/badge.svg?event=release)](https://github.com/classicrocker883/MriscocProUI/releases)

## Universal RET6/RCT6 chips: G32, N32, (working on H32), Creality 4.2.7 and 4.2.2 boards

### - Please read this: -
When you first turn on the printer and on the Main Menu, go to `Level / Mesh Settings / Mesh Inset`. You will see `Mesh X Maximum`,
set this to the value that is `Mesh Y Maximum` (or another value as to not hit the bed clips).

This next part may be optional, but its recommended to do anyway...
Go back to the `Level` menu, look for `Load Bed Mesh` and select it. A status message should then confirm it's loaded. 
(Before that, select which Mesh to load from the `Memory Slot`).

***Mesh Inset doesnt actually save after restart, so it must be done after the printer is turned on every time (until the issue is fixed)*.***

So when you start printing and it says Advance Pause with Runout enabled, you may have to change the pull-up to HIGH, or LOW (depending on what is already selected). This is found in the Prepare menu/ Filament Management/ Filament Settings. 
If you encounter any issues please feel free to post it on the issues tab, or if anything is going well please leavd a comment. 


I will be working on more upgrades and features and tweaks along the way. Enjoy using this fork of Marlin as I intend it to be the best. It is easy to use and convenient. So far I really enjoy the new settings and toolbar for the main menu. There is a variety of parameters and options that can be changed without having to reflash the firmware. 

[Linear Advance Information](https://github.com/MarlinFirmware/MarlinDocumentation/blob/master/_features/lin_advance.md)

The Precompiled binary files of this firmware can work with STM32 (STM32F103RET6/RCT6) and it's clones G32 (GD32F103RET6), N32 (Nation), and possibly H32. They can be downloaded from:
[Latest Release](https://github.com/classicrocker883/MriscocProUI/releases/latest)

<img height=260 src="https://enfss.voxelab3dp.com/10001/picture/2021/09/b849845bd0ffa889f00a782aae76ccf3.jpg" align="left" />
<img height=260 src="https://enfss.voxelab3dp.com/10001/picture/2021/09/677b721574efca3daa5c0d39e438fee6.jpg" align="middle" /> 
<img height=260 src="buildroot/share/pixmaps/Ender-3V2.jpg" align="left" />
<img height=300 src="buildroot/share/pixmaps/Ender-3S1.jpg" align="middle"  />
<BR/>

## Donations
Please consider making a donation, as large or as small and as often as you'd like.
Thank you for your support, I receive donations through [Paypal](https://www.paypal.com/paypalme/andrewleduc)   

[<img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif">](https://www.paypal.com/donate/?business=PFNSKQX9WQQ8W&no_recurring=0&currency_code=USD)   

## Wiki
 - [How to install the firmware](https://github.com/mriscoc/Ender3V2S1/wiki/How-to-install-the-firmware)
 - [Installing a 3D/BLTouch](https://github.com/mriscoc/Ender3V2S1/wiki/3D-BLTouch)
 - [Color themes](https://github.com/mriscoc/Ender3V2S1/wiki/Color-Themes)
 - [How to use with Octoprint](https://github.com/mriscoc/Ender3V2S1/wiki/Octoprint)
  
## Community links
* [Voxelab Aquila Facebook Group](https://www.facebook.com/groups/voxelabaquila/?ref=share&mibextid=NSMWBT) 
* [Telegram](https://t.me/ender3v2s1firmware)
* [r/VoxelabAquila on Reddit](https://www.reddit.com/r/VoxelabAquila)
* [r/ender3V2 on Reddit](https://www.reddit.com/r/ender3v2) 
* [r/Ender3v2Firmware on Reddit](https://www.reddit.com/r/Ender3v2Firmware) 
* [E3V2 Facebook](https://www.facebook.com/groups/ender3v2firmware)
* [E3S1 Facebook](https://www.facebook.com/groups/ender3s1printer)

<!--[](https://raw.githubusercontent.com/mriscoc/Ender3V2S1/Ender3V2S1-Released/screenshots/main.jpg)-->

## Marlin Support

The Issue Queue is reserved for Bug Reports and Feature Requests. To get help with configuration and troubleshooting, please use the following resources:

- [Marlin Documentation](https://marlinfw.org) - Official Marlin documentation
- [Marlin Discord](https://discord.gg/n5NJ59y) - Discuss issues with Marlin users and developers
- Facebook Group ["Marlin Firmware"](https://www.facebook.com/groups/1049718498464482/)
- RepRap.org [Marlin Forum](https://forums.reprap.org/list.php?415)
- Facebook Group ["Marlin Firmware for 3D Printers"](https://www.facebook.com/groups/3Dtechtalk/)
- [Marlin Configuration](https://www.youtube.com/results?search_query=marlin+configuration) on YouTube

## Credits

Thanks to Reddit u/schuh8 for donating his board to help test the firmware.
<br>
and I*_U*1
</br>



Find me on [Facebook](https://www.facebook.com/yoboyyy) 

Join the Voxelab Aquila [Facebook Group](https://www.facebook.com/groups/voxelabaquila/)

This fork of Mriscoc's ProUI firmware is maintained by [@classicrocker883](https://github.com/classicrocker883) (yours truly)

ProUI is a Marlin based firmware maintained by [@mriscoc](https://github.com/mriscoc)

Marlin is maintained mainly by [@thinkyhead](https://github.com/thinkyhead) 

This work would not be possible without me spending time working on it for free.

I would greatly appreate supporters, helpers and betatesters whenever possible.

Please consider making a donation or show your support or input if you end up using this firmware.

It wasn't easy getting it to this point. I am just a basic programmer and the work is mostly trial and error. Thank goodness for VS Code's compiler which shows me what changes need to be made as I make them.

Marlin firmware is an Open Source project hosted on Github, [Marlin](https://marlinfw.org/) is owned and maintained by the maker community.  

VS Code is an IDE program owned and maintained by Microsoft.

## Disclaimer  

THIS FIRMWARE AND ALL OTHER FILES IN THE DOWNLOAD ARE PROVIDED FREE OF CHARGE WITH NO WARRANTY OR GUARANTEE. SUPPORT IS NOT INCLUDED JUST BECAUSE YOU DOWNLOADED THE FIRMWARE. WE ARE NOT LIABLE FOR ANY DAMAGE TO YOUR PRINTER, PERSON, OR ANY OTHER PROPERTY DUE TO USE OF THIS FIRMWARE. IF YOU DO NOT AGREE TO THESE TERMS THEN DO NOT USE THE FIRMWARE.

## LICENSE
For the license, check the header of each file, if the license is not specified there, the project license will be used. Marlin is licensed under the GPL.
