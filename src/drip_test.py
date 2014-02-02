#!/usr/bin/env python3
"""Reads a wav file with drips and displays the time of each drip"""
import wave
import struct
import math
import pyaudio
from audio.drip_detector import DripDetector

pa = pyaudio.PyAudio()
stream = pa.open(
    rate=8000,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
)
detector = DripDetector(8000)
try:
    while True:
        frames = stream.read(1000)
        detector.add_frames(frames)
finally:
    stream.close()
    pa.terminate()
