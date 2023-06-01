import numpy as np
import urllib.request
import cv2


img_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/1_command_line/source/icon/"

cl_icon_img = "cl_icon.png"

def url_to_image(url):
  resp = urllib.request.urlopen(url)
  image = np.asarray(bytearray(resp.read()), dtype='uint8')
  image = cv2.imdecode(image, cv2.IMREAD_COLOR)

  return image

tiger_image = url_to_image('https://bananabearbooks.com/wp-content/uploads/2018/04/tiger-illustration-bananabeabooks.jpg')