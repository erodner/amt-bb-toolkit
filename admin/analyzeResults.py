import re
import string
import sys
import matplotlib.pyplot as plt
from pprint import pprint
import os
import json
import argparse

"read ascii table with a header specification"
def readASCIITableWithHeader (fn):
  i = 0
  d = []
  with open(fn,'r') as f:
    for line in f:
      fields = string.split(line.rstrip(), '\t')

      # remove "..." in the beginning and the end of the fields
      for k in range(len(fields)):
        m = re.match ( '^"?(.*?)"?$', fields[k] )
        fields[k] = m.group(1)
      
      #print fields
      #print len(fields)

      if i==0:
        # read header
        header = fields
      else:
        # read content fields
        if len(fields)!=len(header):
          print "# Ignoring a line because of field count mismatch"
          #raise InvalidArgumentException("Header fields mismatch with content fields")
        else:
          h = dict((header[k],fields[k]) for k in range(len(fields)))
          d.append(h)

      i += 1
  return d

" measuring the area of a given rectangle given as coordinates for left-top and bottom-right corner "
def bbarea(bb):
  if bb[0] > bb[2] or bb[1] > bb[3]:
    area = 0
  else:
    area = ( bb[2] - bb[0] + 1 ) * ( bb[3] - bb[1] + 1 )
  return area

" measuring the overlap score of two bounding boxes "
def bboverlap(a,b):
  clipbb = [ max( a[0], b[0] ), max( a[1], b[1] ), min( a[2], b[2] ), min( a[3], b[3] ) ]
  area_intersect = bbarea(clipbb)
  area_union = bbarea(a) + bbarea(b) - area_intersect
  return area_intersect / float(area_union)

" adding a bounding box to the current figure in a given color (matplotlib) "
def showbb(box,color):
  lx = box[0]
  ly = box[1]
  width = box[2] - box[0] + 1
  height = box[3] - box[1] + 1    
  plt.gca().add_patch(plt.Rectangle((lx,ly),width,height,fill=False,edgecolor=color,linewidth=3))


##################### MAIN
# main program

parser = argparse.ArgumentParser(description='Analyze/view/merge bounding box annotations')
parser.add_argument('--amtresults',
                    help='AMT result file',
                    required=True)
parser.add_argument('--imgdir',
                    help='Image directory',
                    default='images')
parser.add_argument('--output', 
                    help='Output file for final bounding boxes',
                    default='bb.txt')
parser.add_argument('--display',
                    help='Display images [always,never] or when a rejection occurs [reject]',
                    default='reject',
                    choices=['always','never','reject'])
parser.add_argument('--mergerule',
                    help='Merge rule for the best pair of bounding boxes',
                    default='smallest',
                    choices=['smallest','avg'])
parser.add_argument('--rejectionthresh', 
                    help='Rejection threshold applied to a bounding box and the merged box',
                    default=0.2,
                    type=float)
parser.add_argument('--imgfnmapping',
                    help='Maps image filenames using two given columns in a file, e.g. img00001.jpg -> my-picture.jpg',
                    default='')

args = parser.parse_args()

imgfnmap = {}
if len(args.imgfnmapping)>0:
  m = re.match('^(.+?):(\d+):(\d+)$',args.imgfnmapping)
  if not m:
    raise InvalidArgumentException("Image filename mappings have to be of the form <imgfn>:colindex1:colindex2");
  with open(m.group(1),'r') as mapf:
    for l in mapf:
      a = re.split('\s+',l.rstrip())
      imgfnmap[a[int(m.group(2))]] = a[int(m.group(3))]

# read the ascii results
d = readASCIITableWithHeader (args.amtresults)

# collect bounding boxes sorted according to images
boxes = {}
for amtres in d:
  workerid = amtres['workerid']
  resstr = amtres['Answer.results']
  annos = string.split(resstr, ',')
  i = 0
  while i<len(annos):
    imgfn = annos[i]
    i+=1
    x1 = int(annos[i])
    i+=1
    y1 = int(annos[i])
    i+=1
    x2 = int(annos[i])
    i+=1
    y2 = int(annos[i])
    i+=1
    
    if not imgfn in boxes:
      boxes[imgfn] = {}
    
    if x1>x2:
      (x1,x2) = (x2,x1)
    if y1>y2:
      (y1,y2) = (y2,y1)

    boxes[imgfn][workerid] = [ x1, y1, x2, y2 ]


ci = 0
available_colors = "bgcmykw"
workercolors = {}

finalbb = {}

for imgfn,bb in boxes.items():
  display = (args.display == 'always')

  print "Number of boxes given for", imgfn, ":", len(bb)

  workerids = bb.keys()

  if len(bb) > 1:
    # select the pair of bounding boxes with the largest overlap score
    bestov = -1.0
    for k1 in range(len(bb)):
      for k2 in range(k1+1,len(bb)):
        a = bb[workerids[k1]]
        b = bb[workerids[k2]]
        ov = bboverlap(a,b)
        if ov > bestov:
          if args.mergerule == 'avg':
            # rule 1: take the average bounding box 
            avbb = [ (a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2, (a[3]+b[3])/2 ]
          elif args.mergerule == 'smallest':
            # rule 2: take the smallest bounding box
            if bbarea(a)>bbarea(b):
              avbb = b
            else:
              avbb = a
          bestov = ov

    for workerid,box in bb.items():
      ov = bboverlap(avbb,box)
      print workerid, ov
      if ov < args.rejectionthresh:
        display = (args.display != 'never')

  else:
    avbb = bb[ bb.keys()[0] ]

  if imgfn in imgfnmap:
    finalbb[imgfnmap[imgfn]] = avbb
  else: 
    finalbb[imgfn] = avbb

  if display:
    rfn = args.imgdir + os.path.sep + imgfn
    img = plt.imread( rfn )
    plt.imshow(img)
    #plt.axis('off')

    for workerid,box in bb.items():
      if not workerid in workercolors:
        workercolors[workerid] = available_colors[ci]
        ci = (ci + 1) % len(available_colors)

      showbb(box,workercolors[workerid])
      showbb(avbb,'r')

    plt.show()

with open(args.output,'w') as mergef:
  json.dump(finalbb,mergef,sort_keys=True,indent=4)
