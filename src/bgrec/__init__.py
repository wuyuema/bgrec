import cv2 as cv
import numpy as np

import bgrec.grabcut
import bgrec.canny
import bgrec.shrink

gc = bgrec.grabcut.grab_cut
can = bgrec.canny.canny
clps = bgrec.canny.canny_clps
shrk = bgrec.shrink.shrink