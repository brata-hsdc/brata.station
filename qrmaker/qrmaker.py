#!/usr/bin/python
#
#   File: qrmaker.py
# Author: Ellery Chan
#  Email: ellery@precisionlightworks.com
#   Date: 29 Mar 2016
#----------------------------------------------------------------------------
# Install notes:
#    > sudo apt-get install python-dev
#    > sudo pip install reportlab
#----------------------------------------------------------------------------
"""
Generate QR code image, composite into another image, then convert to a PDF document
"""
from __future__ import print_function, division

import sys
import argparse
from PIL import Image
import qrcode
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
import cStringIO

#----------------------------------------------------------------------------
class Rect(object):
    """ A rectangle object defined by (xmin, ymin), (xmax, ymax) using integer coords. """
    
    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        
        self.rearrange()
    
    def rearrange(self):
        """ Sort the mins and the maxes """
        if (self.xmin > self.xmax):
            self.xmin,self.xmax = self.xmax,self.xmin
        if (self.ymin > self.ymax):
            self.ymin,self.ymax = self.ymax,self.ymin
    
    def width(self):
        """ Return the rect x size """
        return self.xmax - self.xmin
    
    def height(self):
        """ Return the rect y size """
        return self.ymax - self.ymin
    
    def box(self):
        return (self.xmin, self.ymin, self.xmax, self.ymax)

#----------------------------------------------------------------------------
class QrMakerApp(object):
    QR_BORDER_PIXELS = 4
    
    def __init__(self):
        self.bgImage = None
        self.qrBox = Rect(727, 1326, 1033, 1020)
        self.smallTextBox = Rect(29, 1543-1513, 284, 1543-1461)
        self.bigTextBox = Rect(435, 1543-1459, 1033, 1543-1367)

    def parseCmdLine(self):
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-i", "--image", required=True, help="Background image")
        parser.add_argument("-s", "--smallText", default="", help="Text to be displayed in the small text box")
        parser.add_argument("-b", "--bigText", default="", help="Text to be displayed in the large text box")
        parser.add_argument("-q", "--qrCode", help="URL or text for QR code")
        self.args = parser.parse_args()
                
    def makeQrCode(self, qrText):
        """ Generate a QR code image, and return it as a pygame image object """
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=self.QR_BORDER_PIXELS,
        )
        qr.add_data(qrText)
        qr.make(fit=True)
         
        # Return a PIL image object
        img = qr.make_image().convert("RGB")
        return img

    def makeTextImage(self, text):
        pass
    
    def addImage(self, image, loc):
        pass
    
    def addSmallText(self, canvas, text, x, y):
        stylesheet=getSampleStyleSheet()
        para = Paragraph(text, stylesheet["Normal"])
        frame = Frame(x + self.smallTextBox.xmin * inch/154, y + self.smallTextBox.ymin * inch/154,
                      self.smallTextBox.width()/154.0 * inch, self.smallTextBox.height()/154.0 * inch,
                      showBoundary=0)
        w,h = para.wrap(self.smallTextBox.width(), self.smallTextBox.height())
        frame.addFromList([para], canvas)
#         para.drawOn(canvas, self.smallTextBox.xmin, self.smallTextBox.ymin)
    
    def addBigText(self, canvas, text, x, y):
        stylesheet=getSampleStyleSheet()
        para = Paragraph(text, stylesheet["Normal"])
        frame = Frame(x + self.bigTextBox.xmin * inch/154, y + self.bigTextBox.ymin * inch/154,
                      self.bigTextBox.width()/154.0 * inch, self.bigTextBox.height()/154.0 * inch,
                      showBoundary=0)
        w,h = para.wrap(self.bigTextBox.width(), self.bigTextBox.height())
        frame.addFromList([para], canvas)
#         para.drawOn(canvas, self.bigTextBox.xmin, self.bigTextBox.ymin)
    
    def loadBgImage(self, path):
        self.bgImage = Image.open(path)
    
    def makePdfDoc(self, path, smText, bigText):
        pdf = Canvas(path, pagesize=letter)
        pgWidth,pgHeight = letter
        
        # Put stuff into the PDF document
#         imgName = self.args.image
        imgdata = cStringIO.StringIO()
        self.bgImage.save(imgdata, format='png')
        imgdata.seek(0)  # rewind the data
        imWidth = 7 * inch
        imHeight = 10 * inch
        layoutW,layoutH = pdf.drawImage(ImageReader(imgdata), (pgWidth-imWidth)/2, inch/2, width=imWidth, height=imHeight, preserveAspectRatio=True)
        print("Layout:", layoutW, layoutH)
        
        self.addSmallText(pdf, self.args.smallText, (pgWidth-imWidth)/2, inch/2)
        self.addBigText(pdf, self.args.bigText, (pgWidth-imWidth)/2, inch/2)
        
        pdf.showPage() # Create a page break
        pdf.save() # save to file and close
        
    def run(self):
        self.parseCmdLine()
        
        # Load the background image
        print("Loading bg image")
        self.loadBgImage(self.args.image)
        
        # Make the QR code
        if self.args.qrCode:
            print("Making qr code")
            qr = self.makeQrCode(self.args.qrCode)
            qr = qr.resize((self.qrBox.width(), self.qrBox.height()))
            print("pasting qr code")
            self.bgImage.paste(qr, self.qrBox.box())
        
        print("making pdf")
        self.makePdfDoc("img/doc.pdf", self.args.smallText, self.args.bigText)
        print("done making pdf")

if __name__ == '__main__':
    app = QrMakerApp()
    app.run()
    sys.exit(0)
