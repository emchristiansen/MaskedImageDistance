import argparse
import Image
from scipy import *
from scipy.linalg import *

def RoundMask(mask): return mask.astype(bool).astype(uint8)

def LoadImagesAndMasks():
  parser = argparse.ArgumentParser(description='Returns L2 distance between two masked images of the same size.')
  parser.add_argument('image0', type=str, nargs=1)
  parser.add_argument('mask0', type=str, nargs=1)
  parser.add_argument('image1', type=str, nargs=1)
  parser.add_argument('mask1', type=str, nargs=1)

  args = parser.parse_args()

  def Load(color, image): 
    return array(Image.open(image).convert(color))

  images = map(lambda i: Load("RGB", i), [args.image0[0], args.image1[0]])
  (mask0, mask1) = map(lambda i: Load("L", i), [args.mask0[0], args.mask1[0]])

  mask0 = RoundMask(mask0)
  mask1 = RoundMask(mask1)

  return ((images[0], mask0), (images[1], mask1))
