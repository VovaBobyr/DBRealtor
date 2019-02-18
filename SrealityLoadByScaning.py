import os
import shutil
import requests
import sys

def get_images(infile):
  """ Find - ImageNames """
  imagelist = []
  myfile = open(infile, mode="r", encoding="latin_1")
  what_to_look = '/image/th/'
  element_number = 1
  for line_image in myfile:
      if what_to_look in line_image:
          exist_image = 0
          while exist_image != -1:
              image_pos_start = line_image.rfind('/image/th/')
              image_pos_end = line_image.rfind('.jpg')
              image_name = line_image[image_pos_start+10:image_pos_end+4]
              print(image_name)
              imagelist.append(image_name)
              line_image = line_image[0:image_pos_start]
              exist_image = line_image.rfind('/image/th/')
  return imagelist
  myfile.close()


def get_authorname(link):
   """ Define author and seria and album names based on link"""
   author_name = ''
   seria_name = ''
   album_name = ''

   # Find Album
   symbol_pos = link.rfind('/')
   album_name = link[symbol_pos+1:link.__len__()]

   # Find Seria
   link = link[0:symbol_pos]
   symbol_pos = link.rfind('/')
   seria_name = link[symbol_pos+1:link.__len__()]

   # Find Seria
   link = link[0:symbol_pos]
   symbol_pos = link.rfind('/')
   author_name = link[symbol_pos+1:link.__len__()]

   return (author_name, seria_name, album_name)


def update_progress(progress):
   # update_progress() : Displays or updates a console progress bar
   ## Accepts a float between 0 and 1. Any int will be converted to a float.
   ## A value under 0 represents a 'halt'.
   ## A value at 1 or bigger represents 100%
   barLength = 10 # Modify this to change the length of the progress bar
   status = ""
   if isinstance(progress, int):
       progress = float(progress)
   if not isinstance(progress, float):
       progress = 0
       status = "error: progress var must be float\r\n"
   if progress < 0:
       progress = 0
       status = "Halt...\r\n"
   if progress >= 1:
       progress = 1
       status = "Done...\r\n"
   block = int(round(barLength*progress))
   text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
   sys.stdout.write(text)
   sys.stdout.flush()


# ========================== MAIN ==============================#


url_start = 'https://www.sreality.cz/hledani/prodej/byty'

page = requests.get(url_start)

inputfile = "script_sreality.txt"
myfile = open(inputfile, mode="w", encoding="latin_1")
myfile.write(page.text)
myfile.close()

'''

print("Count of image: " + str(images_list.__len__()))


#================= Part for saving Images locally =======================#
folder = 'D:/Windows.old/$Recycle.Bin/Comix/8muses/'
# folder = 'C:/Inst/01/'

folder = folder + author + '/' + seria + '/' + album

if not os.path.exists(folder):
  os.makedirs(folder)

count = 1
image_count = images_list.__len__()

print("Saving Images:")
print("progress : 0->" + str(image_count))

saved_count=0
for idx, image_name in enumerate(images_list):
  path = folder + '/' + image_name
  if os.path.exists(path):
      print('Canceled, already exist: ' + path)
      continue

  url = 'https://www.8muses.com/image/fl/' + image_name
  print(url)

  r = get_request_over_proxy(url, http_proxy)
  # Uncomment in case want file load

  update_progress(round(idx/images_list.__len__(),2))

  with open(path, 'wb') as f:
      print(path)
      r.raw.decode_content = True
      shutil.copyfileobj(r.raw, f)
      saved_count = saved_count + 1

print("\nSaved imagges: " + str(saved_count))
'''

