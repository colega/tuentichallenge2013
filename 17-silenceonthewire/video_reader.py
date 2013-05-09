
class AviRiffFile(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.f = open(self.filename, 'rb')
        self.initialize()

    #
    # Just init the variables and open the stream for reading
    #
    def initialize(self):
        self.currentPosition = 0
        self.sectionLengths = []
        self.sectionStarts = []
        self.sectionNames = []
        self.readHeader()
        self.openStream()
        self.framesRead = 0
        self.indexRead = False

    #
    # Re-initialize the stream after each 2Gb list section ends
    #
    def reInitialize(self):
        self.closeStream()
        self.skipWord('RIFF')
        riffLength = self.readDWORD()
        self.skipWord('AVIX')
        self.openStream()

    #
    # Reads a frame from the stream and returns a Frame object
    # 
    def readFrame(self):
        self.framesRead += 1

        print "Reading frame ",self.framesRead
        if self.getCurrentSectionRemainingLength() == 0:
            print "Current stream finished, re-initializing it"
            self.reInitialize()
        
        self.skipWord('00db')
        frameLength = self.readDWORD()
        size = self.frameWidth * self.frameHeight * 3
        if (frameLength != size):
            raise Exception('We thought frameLength would be ' + str(size) + ' but it is ' + str(frameLength))

        return Frame(self.frameWidth, self.frameHeight, self.read(frameLength))

    #
    # Reads the RIFF format header
    # 
    def readHeader(self):
        self.skipWord('RIFF')
        fileSize = self.readDWORD()
        self.skipWord('AVI ')
        self.skipWord('LIST')
        listLength = self.readDWORD()
        self.startSection(listLength, 'hdrl')
        self.skipWord('hdrl')
        self.readAviMainHeader()
        self.readAviStreamHeaders()
        self.endSection()

        # Virtual DUB junk, it would be great to automatically detect it
        self.skipWord('JUNK')
        junkLength = self.readDWORD()
        self.startSection(junkLength, 'JUNK')
        self.endSection()

    #
    # Reads the main avi header with the video information
    #
    def readAviMainHeader(self):
        self.skipWord('avih')
        cb = self.readDWORD()

        self.startSection(cb, 'avih')
        
        dwMicroSecPerFrame = self.readDWORD()
        dwMaxBytesPerSec = self.readDWORD()
        dwPaddingGranularity = self.readDWORD()
        dwFlags = self.readDWORD()
        
        # Total frames in this movie
        self.totalFrames = self.readDWORD()
        print 'self.totalFrames',self.totalFrames
        dwInitialFrames = self.readDWORD()
        dwStreams = self.readDWORD()
        dwSuggestedBufferSize = self.readDWORD()
        dwWidth = self.readDWORD()
        dwHeight = self.readDWORD()
        dwReserved = self.readDWORD()

        self.endSection()

        self.frameWidth = dwWidth
        self.frameHeight = dwHeight
        print 'Width: ' + str(dwWidth)
        print 'Height: ' + str(dwHeight)

    #
    # Reads all the Avi Stream Headers (header and format)
    # http://msdn.microsoft.com/en-us/library/windows/desktop/dd318189%28v=vs.85%29.aspx
    #
    def readAviStreamHeaders(self):
        self.skipWord('LIST')
        listLength = self.readDWORD()
        self.skipWord('strl')
        self.readAviStreamHeader()
        self.readAviStreamFormat()

    #
    # Reads the Avi Stream Header
    # http://msdn.microsoft.com/en-us/library/windows/desktop/dd318183%28v=vs.85%29.aspx
    #
    def readAviStreamHeader(self):
        self.skipWord('strh')
        cb = self.readDWORD()
        
        self.startSection(cb, 'strh')
        self.endSection()

    #
    # Reads the Avi Stream Format
    # http://msdn.microsoft.com/en-us/library/windows/desktop/dd318229%28v=vs.85%29.aspx
    # 
    def readAviStreamFormat(self):
        self.skipWord('strf')
        
        biSize = self.readDWORD()
        
        self.startSection(biSize, 'strf')

        # same 40 as biSize
        unknownDword = self.readDWORD()
        
        biWidth = self.readLONG()
        biHeight = self.readLONG()
        biPlanes = self.readWORD()
        biBitCount = self.readWORD()
        biCompression = self.readDWORD()
        biSizeImage = self.readDWORD()

        print str(biWidth) + 'x' + str(biHeight)
        print str(biBitCount) + ' bits per pixel'
        self.endSection()

    #
    # Open the stream header LIST movi00db
    # and let it prepared for the frame reading
    #
    def openStream(self):
        self.skipWord('LIST')
        streamLength = self.readDWORD()
        self.startSection(streamLength, 'movi')
        self.skipWord('movi')

    #
    # Close the stream and read the index on the end
    # This is not really used, but would be needed if we had to read an >4Gb AVI file
    #
    def closeStream(self):
        self.endSection()
        if not self.indexRead:
            self.readIndex()
            self.indexRead = True

    #
    # Read the optional AVI 1.0 index idx1
    #
    def readIndex(self):
        self.skipWord('idx1')
        indexLength = self.readDWORD()
        self.startSection(indexLength, 'idx1')
        self.endSection()
    
    #
    # Read a DWORD (32bit unsigned int)
    #    
    def readDWORD(self):
        n = self.bytesToInt(self.read(4))
        return n
    
    #
    # Read a WORD (16bit unsigned int)
    #    
    def readWORD(self):
        n = self.bytesToInt(self.read(2))
        return n
    
    #
    # Read a LONG (32bit signed int)
    #    
    def readLONG(self):
        # TODO: should be signed
        n = self.bytesToInt(self.read(4))
        return n

    #
    # Encapsulates reading operation taking the responsibility of
    # updating the current position pointer
    #
    def read(self, n):
        data = self.f.read(n);
        self.currentPosition += len(data)
        #print 'Read ', len(data)
        return data

    #
    # Encapsulates seeking operation taking the responsibility of
    # updating the current position pointer
    #
    def seek(self, n):
        # 1 === from current position
        self.f.seek(n, 1);
        #print 'Seek ', n
        self.currentPosition += n
    
    #
    # Start a section (LIST, etc.)
    #
    def startSection(self, length, sectionName):
        print 'Starting section ' + sectionName + ' on ' + str(self.currentPosition) + ' with length ' + str(length)
        self.sectionLengths.append(length)
        self.sectionStarts.append(self.currentPosition)
        self.sectionNames.append(sectionName)

    #
    # End a section going to its end point. If we already have
    # passed that point, throws an exception
    #
    def endSection(self):
        lastSectionLength = self.sectionLengths.pop()
        lastSectionStart = self.sectionStarts.pop()
        lastSectionName = self.sectionNames.pop()
        print 'Ending section ' + lastSectionName + ' which started on ' + \
            str(lastSectionStart) + ' and had length ' + str(lastSectionLength) + \
            ' so should have ended on ' + str(lastSectionStart + lastSectionLength) + \
            ' and we are now on ' + str(self.currentPosition)
        
        if (lastSectionStart + lastSectionLength < self.currentPosition):
            raise Exception('Section was longer than expected')
        else:
            self.seek((lastSectionStart + lastSectionLength) - self.currentPosition)

    #
    # Returns the current section remaining length
    #
    def getCurrentSectionRemainingLength(self):
        crrentSectionLength = self.sectionLengths[-1]
        currentSectionStart = self.sectionStarts[-1]
        return (currentSectionStart + crrentSectionLength) - self.currentPosition
    
    #
    # Converts multibyte number into an integer
    #
    def bytesToInt(self, b):
        return sum([int(self.paddedBin(ord(b[i])), 2) << 8*i for i in range(len(b))])

    #
    # Padding converts an integer into a binary with 0 paddings on the left (until 8 bits)
    #
    def paddedBin(self, n):
        b = bin(n)[2:]
        while len(b) < 8:
            b = '0' + b
        return b

    #
    # Reads and asserts a given word
    #
    def skipWord(self, word):
        readWord = self.read(len(word))
        if readWord != word:
            raise Exception("'" + word + "' expected, got '" + readWord + "' and then: "+self.read(100))


class Frame(object):
    def __init__(self, width, height, data):
        #print "creating frame",width,"x",height,"datalen",len(data)
        self.width = width
        self.height = height
        self.data = data

    def getPixelColor(self, x, y):
        r = ord(self.data[3*((self.height-y-1)*self.width + x)])
        g = ord(self.data[3*((self.height-y-1)*self.width + x) + 1])
        b = ord(self.data[3*((self.height-y-1)*self.width + x) + 2])
        return (b,g,r)


#
# Loads all your video to RAM, don't run on the large input
# Click to see next frame
# Requires pygame
#
def playWithPygame(avi):
    frames = []
    try:
        while True:
            frames.append(avi.readFrame())
    except:
        # Okay, no more readable frames
        pass
    
    import pygame
    import sys
    pygame.init()
    window = pygame.display.set_mode((avi.frameWidth, avi.frameHeight))
    i = 0
    running = True
    while running: 
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                pygame.quit()
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                frame = frames[i]
                i = (i+1) % len(frames)
                for x in range(avi.frameWidth):
                    for y in range(avi.frameHeight):
                        pygame.draw.line(window, frame.getPixelColor(x, y), (x, y), (x,y))
                
                pygame.display.flip() 
                print event


if __name__ == '__main__':
    avi = AviRiffFile('video.avi')
    #playWithPygame(avi)

    avg = 3 * (127**2)
    message = ''
    bit = 0
    s = ''
    # Read ALL the frames we can, don't mess with frames number provided by headers
    try:
        while True:
            if bit == 8:
                message += chr(int(s,2))
                s = ''
                bit = 0
            frame = avi.readFrame()
            if sum([c**2 for c in frame.getPixelColor(482, 350)]) > avg:
                s += '1'
            else:
                s += '0'
            bit += 1
    except:
        # Okay, no more readable frames
        pass
    if s != '':
        message += chr(int(s,2))
        
    print "Finished"
    print '"'+message+'"'  
