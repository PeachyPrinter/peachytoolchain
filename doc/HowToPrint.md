How to Print with the Peachy Printer
====================================

Theory of Operation
-------------------

Like other 3D printers, the Peachy Printer builds an object from the ground up using layers. Each layer is built, bottom to top, one at a time, with the next layer adhering to the layer below it, forming a solid object. For proper adhesion, it's essential that each layer be drawn at the right time, at the right speed, with just the right amount of resin sitting on top of the existing layers.

The ability to make solid objects from a liquid resin is called photopolymerization. When the resin is exposed to light of the correct frequency, it begins to form polymer chains, which bond and create a solid. The longer the resin is exposed, the more this occurs, and the harder it becomes. However, there is such a thing as *too hard*. We've found that the print comes out clear and smooth when the previous layer isn't fully cured. Too soft and the part won't stay together; too hard and it will have ridges and gaps between layers. For this reason, it's important to carefully control the amount of light exposure at all times. At the same time, the spot of the laser light is not completely uniform: it is brighter in the center and becomes fainter as you move out radially. As a result, the center of the spot will be exposed more than the outer portion, creating a smaller spot than may initially be expected. Overexposure will cause the spot size to become larger, causing some parts of the layer to be drawn thicker than others. In summary, it's important to control the exposure time to within a reasonable margin to get consistent results.

When printing, the printer will draw a single layer at predetermined speeds. It will then wait until the appropriate time to draw the next layer. It does this by listening to the drips, counting the number that have passed to determine the current height of the liquid in the container. When the height reaches that of the next layer, it begins drawing the next layer. In order for this to work properly, the printer must have sufficient time to draw the current layer before the liquid level rises to the height of the next layer.

Toolchain Usage
---------------

Printing an object with the Peachy Printer currently consists of four stages:
1. Convert your STL or other 3D model into GCODE using a slicer
2. Calibrate the printer using the *calibrate* tool
3. Convert the GCODE into a WAV and CUE file using the *gcode_to_wav* tool
4. Play the WAV/CUE files to the printer using the *wav_player* tool

We start by using an existing slicer to create GCODE instructions. GCODE is basically a language for defining movements in 3D space. It describes a *toolpath* which our printer will follow to create the structure of the object. There are many slicers available and any of them should work with the appropriate settings.

When setting up the slicer, there are a few important things to consider. First is that, because the Z level is controlled by slowly dripping water into the container, there is no way to go back down during the print. You'll have to make sure the slicer doesn't attempt to move up and then back down during the print. There usually isn't a need for this, but options such as retracting or moving to a clearance height can cause this, so disable any such options.

The next thing to consider is your *feed rate*, which is the speed at which the printer follows the paths. Due to the need for a specific exposure time, this feed rate will need to be adjusted based on the the laser power and the spot size of the laser beam to meet your desired exposure. You'll likely have to determine this experimentally, by printing small, simple objects and adjusting based on the quality of the print.

Next you'll have to calibrate the printer. Run the *calibrate-main.py* script and you will be presented with a small window with several adjustments. It will continually draw a test pattern over and over. You can switch between patterns using the "Pattern" dropdown box. You can use the "Speed" to control how quickly the pattern is drawn. Drawing it faster will make it easier to see the whole pattern at once, but too fast and the printer may round off the corners and not be able to keep up. This can also be used to determine the maximum speed of your printer. With it drawing a pattern, adjust the other controls to adjust the size, shape, and location of the pattern on a test grid, until it comes out properly. The size of the pattern will also be the maximum size of your print area. Once you have adjusted it to get the proper shape, use the "Save" button to save the settings to a file. If you need to adjust the calibration again later, you can use the "Load" button to load your previous settings as a starting point.

Now you can use the *gcode_to_wav* tool to make the audio data for the printer. Run it from the command line using the following options:

    gcode_to_wav.py <gcode_file> <wav_file> <cue_file> <tuning_file>

Where <gcode_file> is the path to the gcode file that came from the slicer, <wav_file> and <cue_file> are the paths where the audio data and a file containing information about where each layer is stored in that file, and <tuning_file> is the file you saved from *calibrate*.

Once you have the WAV and CUE files, you are ready to print! With the salt water and resin in your container, the valve closed, and the resin just starting to touch the base you are printing to, run the *wav_player* tool like so:

    wav_player.py <wav_file> <cue_file>

At the start of the program, it will move the laser to the waiting position and wait for the drips to begin. Open the valve and watch the messages on the screen as it starts to measure the drip speed. After it sees enough drips, it will start drawing the first layer. You will find that it will actually draw the layer several times over, curing just a little bit of resin each time. This helps to get a clearer print. It will also warn you if the drip rate is too high and it didn't get time to finish drawing the layer. If this happens, simply close the valve a bit to slow down the drip rate.

When it is finished printing, remove your part carefully, as it may still be soft. If desired, you can now cure it further by exposing it to strong UV light or leaving it the sun for a few hours. Clean it afterwards with soap and water to remove any remaining resin.

First-Time Setup
----------------

There are a few parameters you will need to adjust in the program before the first time you print. These are necessary because everybody's printer will be different. In the future, we will have a tool to help with this, rather than having to edit the code yourself.

First, measure the size of your print area. This should match the size of the square you get when running the *calibrate* tool with your tuning values loaded.

Next, measure the number of drips per millimeter of height in your container. Start by measuring the height of the water in your build container when it's near the bottom of where you would print. Then run the *drip_test.py* program and open the valve a little ways until it starts to measure drips. Make sure not to open it too much to the point where it can't measure drips reliably. If you open the valve further and the measured drip rate suddenly drops, the water is starting to flow rather than drip and it won't measure the drips accurately. Once the water level has risen to the top of where you want to print, measure the height of the liquid again and check how many drips were counted. Divide the number of drips by the difference in height to get the number of drips per millimeter.

Now we'll configure the software to use these values. Edit *gcode_to_wav.py* and change the values in the *PrinterParameters* class. Set the X and Y Axis Min and Max Pos. The total length of the X and Y axes should match the size of square that you made while tuning with *calibrate*. The actual min and max values should reflect the dimensions you give to your slicer. This way you could have min 0 and max "width of square", or you could have min and max be -/+ "half width of square" or any other combination that adds up to the total size. Also set the DwellPos to be a part of the print area where you know you will not be printing. The laser will dwell here between layers to avoid curing parts of the print itself. In the future, this dwell will be removed and replaced with blanking the laser. Finally, set the Min and Max Velocity and Acceleration based on the physical speeds your mirrors can handle. The "Speed" setting in *calibrate* can be used to experiment with this. In the future, there will be a more robust mechanism for deriving these values.


