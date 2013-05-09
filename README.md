Recolor
=======

A command-line tool to recolor single-colored images.

Dependencies
------------
  
Due to the dependency to scikit-image, and consequentially to scipy and numpy,
a ridiculous number of dependencies is required:

  *  **Python 3.3** (older versions might work)
  *  **scipy**: From OS package manager, eg. port install py33-scipy
  *  **scikit-image**: pip install scikit-image

Usage
-----

### Example 1 

    recolor --color #FF0000 input1.png input2.png

  Creates input1.out.png and input2.out.png. If the files exists, creates
  input1.out.1.png and input2.out.1.png instead (or ones with the next
  available number.)

  The output files have their colors shifted so that the most saturated color
  of the image is now red.

### Example 2

    recolor --outdir=recolored --color #FF0000 input1.png input2.png

  Creates recolored/input1.png and recolored/input2.png. If the files exist,
  prompts for overwrite.

  The output files have their colors shifted so that the most saturated color
  of the image is now red.

