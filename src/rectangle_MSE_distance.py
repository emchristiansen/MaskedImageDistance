#!/usr/bin/env python

from util import *

def LinearMaskExtent(squashed):
  nonzero = where(squashed)[0]
  # Notice the plus 1.
  return (nonzero.min(), nonzero.max() + 1)

def NonzeroExtent(axis, mask):
  return LinearMaskExtent(mask.sum(axis).flatten())

def RectangularCropToMask(image, mask):
  (ymin, ymax) = NonzeroExtent(1, mask)
  (xmin, xmax) = NonzeroExtent(0, mask)

  cropped_image = image[ymin : ymax, xmin : xmax, :]
  cropped_mask = mask[ymin : ymax, xmin: xmax]

  return (cropped_image, cropped_mask)

def WarpArray(source, target_shape):
  (ty, tx) = target_shape
  return array(Image.fromarray(source).resize((tx, ty)))

def WarpImageAndMask(image, mask, target_shape):
  return (WarpArray(image, target_shape), WarpArray(mask, target_shape))

def CropAndWarp(image0, mask0, image1, mask1):
  (cimage0, cmask0) = RectangularCropToMask(image0, mask0)
  (cimage1, cmask1) = RectangularCropToMask(image1, mask1)

  (wimage1, wmask1) = WarpImageAndMask(cimage1, cmask1, shape(cmask0))

  assert(shape(cimage0) == shape(wimage1))
  assert(shape(cmask0) == shape(wmask1))
  assert(shape(cimage0)[0 : 2] == shape(cmask0)[0 : 2])

  return ((cimage0, cmask0), (wimage1, wmask1))

# Mask values are either 0 or 1.
def ANDMask(mask0, mask1):
  return mask0 * mask1

# Mask values are either 0 or 1.
def ORMask(mask0, mask1):
  return RoundMask(mask0 + mask1)

# Mask values are either 0 or 1.
def XORMask(mask0, mask1):
  return ORMask(mask0, mask1) - ANDMask(mask0, mask1)

def TextureError(image0, mask0, image1, mask1):
  and_mask = ANDMask(mask0, mask1)

  def Mask(image, mask):
    # TODO: figure out how to do this quickly using scipy.
    mask3 = zeros(shape(image))
    for y in range(shape(mask)[0]):
      for x in range(shape(mask)[1]):
        if (mask[y, x] == 1): mask3[y, x, :] = ones((1, 3))
            
    return (mask3 * image).astype(double)

  diff = Mask(image0, and_mask) - Mask(image1, and_mask)

  return (norm(diff.flatten(), 2) ** 2) / size(diff)

def ShapeError(mask0, mask1):
  # The error associated with mask mismatch.
  MASK_ERROR = 3 * (255 ** 2)

  xor_mask = XORMask(mask0, mask1)

  return xor_mask.sum() * MASK_ERROR / size(xor_mask)
  
def TotalError(image0, mask0, image1, mask1):
  texture = TextureError(image0, mask0, image1, mask1)
  shape = ShapeError(mask0, mask1)
  return texture + shape

def CropAndWarpAndGetError(image0, mask0, image1, mask1):
  ((image0, mask0), (image1, mask1)) = CropAndWarp(image0, mask0, image1, mask1)
  return TotalError(image0, mask0, image1, mask1)  

((image0, mask0), (image1, mask1)) = LoadImagesAndMasks()

print CropAndWarpAndGetError(image0, mask0, image1, mask1)


