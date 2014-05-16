## Video to sound

This is a set of python using OpenCV to extract color information from live input video.
Color, position and blobsise are tracked, and this information is passed onto a supercollider
client communicating with SuperCollider via `OSC`.

### How'd it work?

Color (hue) information is determined by calculating the most prevalent hue value within a
detected blob. This number ( 0 to 180 ) is converted into a midi note.

Webcams don't provide very accurate color information. Therefore, the image as a whole is
analyzed and the color spectrum per image is spread over buckets. This way we can at least
reliable name about six color ranges: red, orange, yellow, green, blue, violet.

![Gratuitous image from the visual output of the color tracker](https://raw.githubusercontent.com/mvhenten/video-to-sound/master/vts_dump_1400265146.jpg)

### Supercollider

Supercollider is a realtime synthesizer environment. I've created one synth, called color.
It's a very simple sound intended for DEMO purposes. There once was a more elaborate synthesizer
that could process many more paramters, but people just didn't "get" it. This is better.

The basics of the synth is a simple sine wave, with an added vibrato and small reverb, making
a simple and pure sound (much like Brian Eno's "bloom").

### Setting this up

__N.B.__ This is a note to self

1. Get python running with opencv. Try running `python/run.py` and see if it crashes. http://opencv.willowgarage.com/documentation/python/index.html
1. Install SuperCollider together with supercollider plugin for "gedit". Checkout `color.sc`, if super collider is there, should be able to play around with the debug commands. Supercollider PPA: https://launchpad.net/~supercollider/+archive/ppa
1. Install supercollider python packages: http://pypi.python.org/pypi/SC/0.2

#### Calibrate the webcam

Webcams and video grabbers used to be difficult to get working, but no more. Just plug it in.

*Always* calibrate the webcam. Use `guvcview -d /dev/video1`, and save the calibrated settings
to "default.gpfl" in the `python/suport` directory. The script will load the settings.

Run guvcview without video to calibrate while running the actual script, put a number of colored
items and try to tweak until all colors are detected. __NOTE__ This needs a lot of LIGHT! Good
Lighting conditions are important.

#### Running SuperCollider

Jackd may need some configurin:

    dpkg-reconfigure -p high jackd
    sudo adduser <uname> audio

Check for messages complaining about memory and realtime priority when in trouble.
Most convenient way to start supercollider under ubuntu is by running it trough the `gedit`
plugin. Start `gedit`, enable the plugin and supercollider mode, boot the server.

If all went well, the following line of code shold produce output:

    { SinOsc.ar(440) }.play;

_(press ctrl-e to execute by line, press ESC to kill the sound)_

Open up `sc/color.sc`, select the SynthDef (until the line `send(s)`) to load the synth into
the server.

#### Running the python script

cd into the `python` dir. run:

    python run.py -d 1

Put some colored objects under the camera. Do additional calibration using

    guvcview -d /dev/video1 -o

Be sure to save the result to `default.gpfl`. run.py will read this file to setup the cam.


