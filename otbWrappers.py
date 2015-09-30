# -*- coding: utf-8 -*-#
#!/usr/bin/python
# Filename: otbWrappers.py

import subprocess

def HaralickTextureExtraction(inImage, outImage, texture):   
    otb = "otbcli_HaralickTextureExtraction -progress true "
    block = " -ram 500 -channel 1 -parameters.xrad 2 -parameters.yrad 2  -parameters.min 0 -parameters.max 255"
    cmd = otb + "-in " + inImage + block + " -texture " +  texture + " -out "+ outImage
    subprocess.call(cmd, shell = True)
