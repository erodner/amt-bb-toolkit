import sys
import re
import subprocess

def output_hid(hid):
  if len(hid)>0:
    spec = ";".join(hid) 
    if len(spec) > 255:
      print "Maximum length of task specification reached (length = %d) !" % (len(spec))
      sys.exit(-1)
    print spec



if len(sys.argv) != 4:
  print "usage:", sys.argv[0], "<list> <num-images-per-hid> <category-regexp>"
  sys.exit(-1)

imagelistfn = sys.argv[1]
numimages = int(sys.argv[2])
creg = sys.argv[3]

print "images"
index = 0

hid = []

shout = open ("cp-files.sh", 'w')

with open(imagelistfn) as f:
  for imagefn in f:
    # obtain image dimensions using identify
    imagefn = imagefn.rstrip()
    #print "processing", imagefn

    try:
      # get image size using ImageMagick
      output = subprocess.check_output(["identify", "-format",  "%w %h", imagefn])
      size = output.rstrip().split(' ')
      # get the category name
      m = re.search( creg, imagefn )
      category = m.group(1)
      nimagefn = "%06d.jpg" % (index)
      shout.write( "cp " + imagefn + " " + nimagefn + "\n" )
      #print "category:", category
      imageinfo = category + "," + nimagefn + "," + size[0] + "," + size[1]


      hid.append(imageinfo)
      index = index + 1

      if len(hid) == numimages:
        output_hid(hid)
        hid = []

    except OSError as detail:
      print "Unable to run identify:", detail

output_hid(hid)

shout.close()
