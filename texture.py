import cv2
import numpy as np

class Texture:
    def __init__(self, heads, tails=None, edge=None):
      self.heads = heads.copy()
      self.edge = edge.copy() if edge is not None else np.zeros((heads.shape[0], heads.shape[1], 4), np.uint8)
      if tails is None:
        self.tails = cv2.GaussianBlur(self.heads, (101, 101), 0)

    def export(self, path):
      r = self.heads.shape[0] // 2
      assert(2*r == self.heads.shape[1])
      assert(2*r == self.tails.shape[0])
      assert(2*r == self.tails.shape[1])

      texture = np.zeros((r*4, r*4, 4), np.uint8)
      
      texture[r*2:, :r*2] = self.heads
      texture[r*2:, r*2:] = self.tails
      texture[:r*2, :r*4] = cv2.resize(self.edge, (r*4, r*2), interpolation=cv2.INTER_AREA)

      # Save the texture
      cv2.imwrite(path, texture)