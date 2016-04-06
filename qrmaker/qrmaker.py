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
# Usage: qrmaker.py [-h] -i IMAGE [-s SMALLTEXT] [-b BIGTEXT] [-q QRCODE]
#                   [-f CSVFILE]
#                   outFile
# 
# positional arguments:
#   outFile               Name of the PDF output file
# 
# optional arguments:
#   -h, --help            show this help message and exit
#   -i IMAGE, --image IMAGE
#                         Background image
# 
# Args for single page PDF document:
#   -s SMALLTEXT, --smallText SMALLTEXT
#                         Text to be displayed in the small text box
#   -b BIGTEXT, --bigText BIGTEXT
#                         Text to be displayed in the large text box
#   -q QRCODE, --qrCode QRCODE
#                         URL or text for QR code
# 
# Args for multiple page PDF document:
#   -f CSVFILE, --csvFile CSVFILE
#                         A CSV file containing lines of
#                         qrText,bigText,smallText
#----------------------------------------------------------------------------
"""
Generate QR code image, composite into another image, then convert to a PDF document.
Use either the -f option, or the -q/-b/-s options.  If you use -f, -q/-b/-s are ignored.

The format of the lines in the CSV input file is:

    qrText,bigText,smallText
    
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
import csv

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
    
    def scale(self, factor):
        """ Scale all coordinate values by multiplying by factor """
        self.xmin *= factor
        self.ymin *= factor
        self.xmax *= factor
        self.ymax *= factor

#----------------------------------------------------------------------------
class QrMakerApp(object):
    QR_BORDER_PIXELS = 4
    
    def __init__(self):
        self.bgImage = None
        self.qrBox = Rect(727, 1326, 1033, 1020)
        self.smallTextBox = Rect(29, 1543-1513, 284, 1543-1461)
        self.bigTextBox = Rect(435, 1543-1459, 1033, 1543-1367)
        self.pdf = None
        self.pageData = []

    def parseCmdLine(self):
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-i", "--image", required=True, help="Background image")
        
        group1 = parser.add_argument_group("Args for single page PDF document")
        group1.add_argument("-s", "--smallText", default="", help="Text to be displayed in the small text box")
        group1.add_argument("-b", "--bigText", default="", help="Text to be displayed in the large text box")
        group1.add_argument("-q", "--qrCode", help="URL or text for QR code")
        
        group2 = parser.add_argument_group("Args for multiple page PDF document")
        group2.add_argument("-f", "--csvFile", help="A CSV file containing lines of qrText,bigText,smallText")
        
        parser.add_argument("outFile", help="Name of the PDF output file")
        self.args = parser.parse_args()
                
    def readCsvFile(self, csvFileName):
        """ Read a CSV file containing lines with 3 fields each.
            The fields are:  qrText,bigText,smallText
            Blank lines are ignored.
            Lines with proper content are added to the pageData list.
        """
        with open(csvFileName, "rb") as f:
            rdr = csv.reader(f)
            lineNum = 0
            for line in rdr:
                lineNum += 1
                if len(line): # not blank
                    if len(line) != 3:
                        print("Error in line {}:  Wrong number of fields".format(lineNum), file=sys.stderr)
                    else:
                        self.pageData.append(line)
    
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

    def addSmallText(self, canvas, text, x, y):
        text = "<para align=CENTER><b>{}</b></para>".format(text)
        stylesheet=getSampleStyleSheet()
        para = Paragraph(text, stylesheet["Normal"])
        frame = Frame(x + self.smallTextBox.xmin * inch/154, y + self.smallTextBox.ymin * inch/154,
                      self.smallTextBox.width()/154.0 * inch, self.smallTextBox.height()/154.0 * inch,
                      showBoundary=0)
        w,h = para.wrap(self.smallTextBox.width(), self.smallTextBox.height())
        frame.addFromList([para], canvas)
    
    def addBigText(self, canvas, text, x, y):
        text = '<para align="center" spaceBefore="-100"><font size=32><b>{}</b></font></para>'.format(text)
        stylesheet=getSampleStyleSheet()
        para = Paragraph(text, stylesheet["Normal"])
        frame = Frame(x + self.bigTextBox.xmin * inch/154, y + self.bigTextBox.ymin * inch/154,
                      self.bigTextBox.width()/154.0 * inch, self.bigTextBox.height()/154.0 * inch,
                      showBoundary=0)
        w,h = para.wrap(self.bigTextBox.width(), self.bigTextBox.height())
        frame.addFromList([para], canvas)
    
    def loadBgImage(self, path):
        """ Load bgImage from a file """
        self.bgImage = Image.open(path)
    
    def addQrCode(self, qrText):
        """ Create a qrcode image and composite it into the bgImage """
        qr = self.makeQrCode(qrText)
        qr = qr.resize((self.qrBox.width(), self.qrBox.height()))
        self.bgImage.paste(qr, self.qrBox.box())
    
    def makePdfPage(self, bgImgFile, qrText, smText, bigText):
        # Load the background image from a file
        self.loadBgImage(bgImgFile)
        
        # Write the qrcode into the background image
        self.addQrCode(qrText)
        
        # Copy the background image to a memory buffer
        # that can be read as an in-memory file
        imgdata = cStringIO.StringIO()
        self.bgImage.save(imgdata, format='png')
        imgdata.seek(0)  # rewind the data
        
        # Define the image size on the page
        imWidth = 7 * inch
        imHeight = 10 * inch
        
        # Put the background image into the PDF page
        pgWidth,pgHeight = letter
        layoutW,layoutH = self.pdf.drawImage(ImageReader(imgdata), (pgWidth-imWidth)/2, inch/2, width=imWidth, height=imHeight, preserveAspectRatio=True)
        
        # Add the text in the boxes on the page
        self.addSmallText(self.pdf, smText, (pgWidth-imWidth)/2, inch/2)
        self.addBigText(self.pdf, bigText, (pgWidth-imWidth)/2, inch/2)
        
        # Finalize the page
        self.pdf.showPage() # Create a page break
    
    def createPdfDoc(self, path):
        """ Create a PDF document object that will be written to path """
        self.pdf = Canvas(path, pagesize=letter)
        
    def finalizePdfDoc(self):
        """ Write the doc to a file and close it"""
        self.pdf.save() # save to file and close
        
    def run(self):
        self.parseCmdLine()
        
        if self.args.csvFile:
            # Read file into self.pageData
            self.readCsvFile(self.args.csvFile)
        else:
            # Put args into self.pageData
            self.pageData.append([self.args.qrCode, self.args.bigText, self.args.smallText])
        
        # Generate the PDF document        
        print("making pdf")
        self.createPdfDoc(self.args.outFile)
        
        for qrText,bigText,smallText in self.pageData:
            print("Page: {}, {}, {}".format(qrText, bigText, smallText))
            self.makePdfPage(self.args.image, qrText, smallText, bigText)
            
        self.finalizePdfDoc()
        print("done making pdf")

if __name__ == '__main__':
    app = QrMakerApp()
    app.run()
    sys.exit(0)
