#!/usr/bin/python

import argparse
import os
import re
import colorsys

import skimage.io
import skimage.color
import numpy

from pprint import pprint

### Parse args

cliParser = argparse.ArgumentParser(
  description="Recolor - recolor single-colored graphic elements")

cliParser.add_argument('-f', 
                       '--force', 
                      help="Overwrite without prompting.", 
                      action='store_true')
cliParser.add_argument('-c', '--color', 
  help="Color in #RRGGBB, #RGB, rgb(100%, 0%, 0%), rgb(255,0,0),"
       " hsl(359,0%,100%) or hsl(359,255,255) format. Color names are also"
       " supported.")
cliParser.add_argument('--outdir', 
  help="Directory to write the recolored files to. If not specified, "
       "the output is written to original_filename.out.original_extension.",
  required=False)
cliParser.add_argument('--valuefactor', 
  help="Factor by which change in value should be accounted for.",
  required=False)
cliParser.add_argument('--outfile', 
  help="Name of the output file.",
  required=False)
cliParser.add_argument('infile', help="Input file names", nargs='+')




def process(inFile, outFile, color, valueFactor):
  image = skimage.io.imread(inFile)
  colorHSV = colorsys.rgb_to_hsv(*color)
  colorHSV = [colorHSV[0], colorHSV[1], colorHSV[2]]
  pprint(colorHSV)
  imageHSV = skimage.color.rgb2hsv(image)
  originalHSV = findMostSaturatedColor(imageHSV)

  diffH = colorHSV[0] - originalHSV[0]
  diffS = colorHSV[1] - originalHSV[1]
  if originalHSV[1]:
    factorS = colorHSV[1] / originalHSV[1]
  else:
    factorS = 1.0

  if originalHSV[2]:
    factorV = colorHSV[2] / originalHSV[2]
  else:
    factorV = 1.0

  imageMask = getSaturationMask(imageHSV, originalHSV)
  invMask = 1.0 - imageMask

  outputH = imageHSV.compress([True, False, False], axis=2)
  outputS = imageHSV.compress([False, True, False], axis=2)
  outputV = imageHSV.compress([False, False, True], axis=2)

  outputH = (outputH + imageMask * diffH) % 1
  outputS = (outputS + imageMask * diffS).clip(0.0, 1.0)
  #outputS = (outputS * imageMask * factorS + outputS * invMask).clip(0.0, 1.0)
  outputV = (valueFactor * (outputV * imageMask * factorV + outputV * invMask)
    + (1.0 - valueFactor) * outputV).clip(0.0, 1.0)

  imageProcessedHSV = numpy.dstack((outputH, outputS, outputV))

  imageAddedRGB = skimage.color.hsv2rgb(imageProcessedHSV)
  skimage.io.imsave(outFile, imageAddedRGB)

def findMostSaturatedColor(imageHSV):
  """
  Searches for the most saturated color.
  """
  imageS = imageHSV.compress([False, True, False], axis=2)
  index = imageS.argmax() 
  index = numpy.unravel_index(index, imageS.shape)
  return imageHSV[index[0], index[1]]

def getSaturationMask(imageHSV, color):
  imageS = imageHSV.compress([False, True, False], axis=2)
  imageS = imageS.astype('float')
  imageS /= color[1]
  return (imageS * 32.0).clip(0.0, 1.0)
  
def parseColor(color):
  matches = re.match(r"#([a-f0-9]{2})([a-f0-9]{2})([a-f0-9]{2})", 
                     color, 
                     re.IGNORECASE)
  if matches:
    return (int(matches.group(1), 16) / 255.0,
            int(matches.group(2), 16) / 255.0,
            int(matches.group(3), 16) / 255.0)
  
  return None



args = cliParser.parse_args()
color = parseColor(args.color)
outdir = args.outdir
outFile = args.outfile
valueFactor = args.valuefactor
if not valueFactor:
  valueFactor = 0.0
else:
  valueFactor = float(valueFactor)
force = args.force

### Process
for inFile in args.infile:
  if outdir:
    outFile = os.path.join(outdir, inFile)
    if os.path.exists(outFile) and not force:
      print ('File ' + outFile + ' already exists.')
      input = input('Overwrite? [y/N]: ')
      if input.strip() != 'y':
        print ('Nothing done. Continuing.')
        continue
      else:
        print ('Overwriting.')
  elif outFile:
    if os.path.exists(outFile) and not force:
      print ('File ' + outFile + ' already exists.')
      input = input('Overwrite? [y/N]: ')
      if input.strip() != 'y':
        print ('Nothing done. Continuing.')
        continue
      else:
        print ('Overwriting.')
  else:
    pathParts = os.path.splitext(inFile)
    outFile = pathParts[0] + '.out' + pathParts[1]
    index = 1
    while os.path.exists(outFile):
      outFile = pathParts[0] + '.out.' + str(index) + pathParts[1]
  process(inFile, outFile, color, valueFactor)
