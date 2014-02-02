How to Print with the Peachy Printer
====================================

Theory of Operation
-------------------

Like other 3D printers, the Peachy Printer builds an object from the ground up using layers. Each layer is built,
bottom to top, one at a time, with the next layer adhering to the layer below it, forming a solid object. For proper
adhesion, it's essential that each layer be drawn at the right time, at the right speed, with just the right amount of
resin sitting on top of the existing layers.

The ability to make solid objects from a liquid resin is called photopolymerization. When the resin is exposed to light
of the correct frequency, it begins to form polymer chains, which bond and create a solid. The longer the resin is
exposed, the more this occurs, and the harder it becomes. However, there is such a thing as *too hard*. We've found
that the print comes out clear and smooth when the previous layer isn't fully cured. Too soft and the part won't stay
together; too hard and it will have ridges and gaps between layers. For this reason, it's important to carefully
control the amount of light exposure at all times. At the same time, the spot of the laser light is not completely
uniform: it is brighter in the center and becomes fainter as you move out radially. As a result, the center of the
spot will be exposed more than the outer portion, creating a smaller spot than may initially be expected. Overexposure
will cause the spot size to become larger, causing some parts of the layer to be drawn thicker than others. In summary,
it's important to control the exposure time to within a reasonable margin to get consistent results.

When printing, the printer will draw a single layer at predetermined speeds. It will then wait until the appropriate
time to draw the next layer. It does this by listening to the drips, counting the number that have passed to determine
the current height of the liquid in the container. When the height reaches that of the next layer, it begins drawing
the next layer. In order for this to work properly, the printer must have sufficient time to draw the current layer
before the liquid level rises to the height of the next layer.

Toolchain Usage
---------------

Printing an object with the Peachy Printer currently consists of four stages:
1. Convert your STL or other 3D model into GCODE using a slicer
2. Calibrate the printer using the *calibrate* tool
3. Convert the GCODE into a WAV and CUE file using the *gcode_to_wav* tool
4. Play the WAV/CUE files to the printer using the *wav_player* tool

We start by using an existing slicer to create GCODE instructions. GCODE is basically a language for defining movements
in 3D space. It describes a *toolpath* which our printer will follow to create the structure of the object. There are
many slicers available and any of them should work with the appropriate settings.

When setting up the slicer, there are a few important things to consider. First is that, because the Z level is
controlled by slowly dripping water into the container, there is no way to go back down during the print. You'll have
to make sure the slicer doesn't attempt to move up and then back down during the print. There usually isn't a need for
this, but options such as retracting or moving to a clearance height can cause this, so disable any such options.

The next thing to consider is your *feed rate*, which is the speed at which the printer follows the paths. Due to the
need for a specific exposure time, this feed rate will need to be adjusted based on the the laser power and the spot
size of the laser beam to meet your desired exposure. You'll likely have to determine this experimentally, by printing
small, simple objects and adjusting based on the quality of the print.

Next you'll have to calibrate the printer. See later in this document for details on how to perform calibration.

Now you can use the *gcode_to_wav* tool to make the audio data for the printer. Run it from the command line using the
following options:

    gcode_wav_converter.py <tuning_file> <gcode_file> <wav_file> <cue_file>

Where <gcode_file> is the path to the gcode file that came from the slicer, <wav_file> and <cue_file> are the paths
where the audio data and a file containing information about where each layer is stored in that file, and <tuning_file>
is the file you saved from *calibrate*.

Once you have the WAV and CUE files, you are ready to print! With the salt water and resin in your container, the valve
closed, and the resin just starting to touch the base you are printing to, run the *wav_player* tool like so:

    wav_player.py <tuning_file> <wav_file> <cue_file>

At the start of the program, it will move the laser to the waiting position and wait for the drips to begin. Open the
valve and watch the messages on the screen as it starts to measure the drip speed. After it sees enough drips, it will
start drawing the first layer. You will find that it will actually draw the layer several times over, curing just a
little bit of resin each time. This helps to get a clearer print. It will also warn you if the drip rate is too high
and it didn't get time to finish drawing the layer. If this happens, simply close the valve a bit to slow down the drip
rate.

When it is finished printing, remove your print carefully, as it may still be soft. If desired, you can now cure it
further by exposing it to strong UV light or leaving it the sun for a few hours. Clean it afterwards with soap and
water to remove any remaining resin.

First-Time Setup and Calibration
--------------------------------

In order for the software to properly position the laser to draw the layers of the print, it needs to know several
parameters that determine the mapping of the laser position to the physical location in your build area. These can all
be set through the *calibrate* program.

Before we begin, let us quickly explain how units work in our software. The units used within the toolchain should match
the units that your slicer outputs in its GCODE. This is typically millimeters, but may be inches or some other unit.
Please check your slicer's configuration before measuring and calibrating to ensure the units match the slicer.

First, measure the size of your build area. This is the physical area in which you will be building prints within the
printer.

Next, measure the number of drips per unit of height in your container. Start by measuring the height of the water in
your build container when it's near the bottom of where you would print. Then run the *drip_test.py* program and open
the valve a little ways until it starts to measure drips. Make sure not to open it too much to the point where it can't
measure drips reliably. If you open the valve further and the measured drip rate suddenly drops, the water is starting
to flow rather than drip and it won't measure the drips accurately. Once the water level has risen to the top of where
you want to print, measure the height of the liquid again and check how many drips were counted. Divide the number of
drips by the difference in height to get the number of drips per unit height.

Now we'll use *calibrate* to configure all of the parameters. First enter the min and max X and Y values for your build
area. These need to match the values that your slicer produces. Typically, if you tell the slicer that your build area's
size is 'x' by 'y', then it will use 0 as the min X and Y and 'x' and 'y' as the max X and Y values. The total width
and length of these axes should match the physical width and length of your build area.

Next, enter the dwell location. This is where the laser will be pointed while waiting for the next layer. If you are
using the included Peachy circuit, the laser will be disabled during this time, so the location just has to be somewhere
within the build area, but if you are unable to disable the laser, place this in a location where it won't interfere
with your print, since any resin in this location will be cured. You can avoid wasting resin and possibly interfering
with the print by placing a non-reflective, water-proof object in this location. If you do add an object within the
build area, be sure to remeasure your drips per unit height, since there is now less volume in your build area.

The next option, maximum velocity, needs to be determined experimentally. We'll do this once we have the rest of the
printer calibrated. For now, a value of about 100 millimeters/second (or the equivalent in your slicer's units) should
be acceptable.

For drips per height, enter the number you measured previously using *drip-test.py*. You will need to update this value
in the future if you use a different container or add or remove any items within the container. Also, be aware that the
container should have as consistent of a cross-sectional area as possible to ensure that the number of drips per height
doesn't change considerably at different heights.

Sublayer height determines how thin of a layer the printer will cure on each pass, irrespective of the layer height
used when slicing. We have found that curing a thin layer at a time produces smoother prints with fewer surface defects.
Our experiments show that a value of about 0.01 millimeters works well. You want want to use a larger height if you want
to be able to print faster, but note that too thick of a layer may cause bubbles and ridges in the print. Also note that
this interacts with the feed rate and the laser power, so you will have to determine new feed rates if you change this.
For now, use the default value of 0.01 millimeters, or the equivalent in your slicer's units.

Modulation is used to drive the Peachy circuit. If you are using the Peachy circuit, we recommend setting both the
circuit and the software to use AM. If you are unable to use the circuit, use DC, but note that your sound card's output
must be DC coupled to work properly. Most sound cards are not DC coupled.

We will now calibrate the positioning of the laser within your build area. The X and Y location is mapped to mirror
movements using the tuning parameters on the right side. These include offset (shifting left/right/up/down), rotation,
scale (larger/smaller), shear (one axis is shifted as you move along the other axis), and trapezoid (one axis is shrunk
or expanded as you move along the other axis). Calibration consists of playing a test pattern and adjusting these until
the pattern is drawn in the correct location in the build area. We will calibrate this at different heights to determine
how the mapping changes as the height changes, so it's important to calibrate to the same location each time.

Start by placing the calibration grid inside your build container. To ensure we can get it in the same horizontal
position each time, try to line it up with a corner of the container that will be the same at any height (such as a
vertical edge). Using a ruler, determine where the center of the grid is in relation to the build area you defined
previously. In *calibrate*, enter these values as the center for the test pattern. Now choose a size for the pattern to
be drawn. This should cover as much of the calibration grid as possible while still fitting comfortably within the
build area. You should also use a size which will line up perfectly on the grid lines of the calibration grid when we
have it calibrated correctly. Enter this size in for the test pattern. You should see the test pattern being drawn.

At this point, it's likely that the test pattern being drawn does not line up correctly with the calibration grid. We
will now calibrate it by adjusting the tuning parameters. Start by adjusting the offset until the center of the pattern
lines up with the center of the grid. You may find it easier to do this by making the test pattern very small so that it
effectively makes a dot in the center. Next, using the full size for the test pattern, adjust the scale until the drawn
pattern is the correct size. If you find that the pattern doesn't line up because it is rotated or skewed, you'll want
to fix that and adjust the scale again. If it is rotated, change the rotation until the sides of the pattern line up
with the grid lines. If the pattern is skewed or distorted, adjust the shear and/or trapezoid parameters until the
pattern is square. Continue adjusting all of these until the pattern is square, centered properly, and is the correct
size. To complete this stage of the calibration, measure the height of your calibration grid from the bottom of the
build container and enter that in the height field just above the tuning parameters.

Now we will calibrate it at another height. Place an object inside the build container and rest the calibration grid
on top of it such that the grid is sitting at the maximum height you want to build to. Make sure the grid is level
and is horizontally in the same position it was when on the bottom (lined up against the same corner). Meausre the
height from the bottom of the container to the calibration grid. In *calibrate*, press the "Add new calibration" button
and enter the height of the grid. You should now see that the test pattern is being drawn much smaller than before and
may also have shifted. Adjust the tuning parameters until the pattern is once again centered, square, and the proper
size.

Next, we will place the calibration grid at an intermediate height and test that the calibration is working correctly.
Place the grid on an object so that it sits about half way up to the maximum build height. Measure the height of the
grid from the bottom of the container. In *calibrate*, switch to the Test tab and enter the height here. The pattern
should now adjust and be drawn appropriately on the grid. If it's close but not quite right, we can add an additional
calibration here by pressing "Calibrate here". This will take you back to the calibrate tab with a new calibration
point added so you can adjust the tuning parameters again. We suggest testing the calibration between each pair of
calibration points to ensure you get a reasonably good fit at every height.

When you are done calibrating, press the Save button and enter a filename where it should save the tuning. This is the
tuning file that you will use with the *gcode_wav_converter* and *wav_player* in the rest of the toolchain.