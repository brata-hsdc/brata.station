# qrmaker.py

Stand-alone command line tool that creates signs in PDF format.  Each sign has
a background image, a QR code, and two pieces of text, in a fixed layout.
The layout is currently hardcoded to match a specific background image.

## Usage
'''
Usage: qrmaker.py [-h] -i IMAGE [-s SMALLTEXT] [-b BIGTEXT] [-q QRCODE]
                  [-f CSVFILE]
                  outFile

Generate QR code image, composite into another image, then convert to a PDF
document. Use either the -f option, or the -q/-b/-s options. If you use -f,
-q/-b/-s are ignored. The format of the lines in the CSV input file is:
qrText,bigText,smallText

positional arguments:
  outFile               Name of the PDF output file

optional arguments:
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        Background image

Args for single page PDF document:
  -s SMALLTEXT, --smallText SMALLTEXT
                        Text to be displayed in the small text box
  -b BIGTEXT, --bigText BIGTEXT
                        Text to be displayed in the large text box
  -q QRCODE, --qrCode QRCODE
                        URL or text for QR code

Args for multiple page PDF document:
  -f CSVFILE, --csvFile CSVFILE
                        A CSV file containing lines of
                        qrText,bigText,smallText
'''

## Examples

'''shell
% python ..\qrmaker.py -f TestSignInput.csv -i QRTemplate.png TestSigns.pdf
'''

'''shell
% python ..\qrmaker.py -q "This is not a qrcode" -b Arrival -s dock01 -i QRTemplate.png test.pdf
'''