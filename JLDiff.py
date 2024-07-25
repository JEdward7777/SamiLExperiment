#!/usr/bin/python

#Copyright (c) 2016, Joshua Lansford @ LaserLinc
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:

#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import with_statement
from collections import defaultdict

import sys
import cgi
import codecs

if hasattr( cgi, "escape" ):
    cgi_escape = cgi.escape
else:
    import html
    cgi_escape = html.escape


STATE_PASSING_1ST = 0
STATE_PASSING_2ND = 1
STATE_MATCH = 2


class lineCompIndex(object):
    __slots__ = ['errorCount', 'previous', 'state', 'content' ]
    def __init__( self ):
        self.errorCount = 0
        self.previous = None
        self.state = STATE_PASSING_1ST
        self.content = ""

u_intern_dict = {}
def u_intern( value ):
    if value in u_intern_dict:
        return u_intern_dict[value]
    u_intern_dict[value]=value
    return value

def compute_diff( file1, file2, talk=True ):
    lastLine = []
    thisLine = []

    #init the root root
    thisIndex = lineCompIndex()
    thisIndex.state = STATE_MATCH
    thisLine.append( thisIndex )

    #init the root top case
    columnIndex = 1
    for char2 in file2:
        thisIndex = lineCompIndex()
        thisIndex.previous = thisLine[ columnIndex-1 ]
        thisIndex.errorCount = thisIndex.previous.errorCount+1
        thisIndex.content = u_intern(char2)
        thisIndex.state = STATE_PASSING_2ND
        thisLine.append( thisIndex )
        columnIndex += 1

    for char1 in file1:
        lastLine = thisLine
        thisLine = []

        if talk:
            try:
                sys.stdout.write( char1 )
            except Exception:
                pass

        #init the root left case
        thisIndex = lineCompIndex()
        thisIndex.previous = lastLine[ 0 ]
        thisIndex.errorCount = thisIndex.previous.errorCount+1
        thisIndex.content = u_intern(char1)
        thisIndex.state = STATE_PASSING_1ST
        thisLine.append( thisIndex )

        columnIndex = 1
        for char2 in file2:
            thisIndex = lineCompIndex()

            if( char2 == char1 ):
                thisIndex.previous = lastLine[ columnIndex-1 ]
                #To keep from getting spurious single matches,
                #see about adding some error in for the first matches.
                if thisIndex.previous.state == STATE_MATCH:
                    thisIndex.errorCount = thisIndex.previous.errorCount
                else:
                    thisIndex.errorCount = thisIndex.previous.errorCount #+ 1

                thisIndex.state = STATE_MATCH
                thisIndex.content = u_intern(char2)
            else:
                if lastLine[ columnIndex ].errorCount < thisLine[ columnIndex-1 ].errorCount:
                    thisIndex.previous = lastLine[ columnIndex ]
                    thisIndex.content = u_intern(char1)
                    thisIndex.state = STATE_PASSING_1ST
                else:
                    thisIndex.previous = thisLine[ columnIndex-1 ]
                    thisIndex.content = u_intern(char2)
                    thisIndex.state = STATE_PASSING_2ND

                thisIndex.errorCount = thisIndex.previous.errorCount+1

            thisLine.append( thisIndex )
            columnIndex += 1

    backwardsList = []
    currentNode = thisLine[ len( thisLine )-1 ]
    while not currentNode is None:
        backwardsList.append( currentNode )
        currentNode = currentNode.previous

    backwardsList.reverse()
    return backwardsList


def printDiffs( nodesToPrint, outputFile ):
    isblack = True
    isred = False
    isgreen = False

    def escape( inputStr ):
        answer = ""
        if inputStr == " ":
            answer = "&nbsp;"
        elif inputStr == "\t":
            answer = "&nbsp;&nbsp;&nbsp;"
        else:
            answer = cgi_escape( inputStr )
        return answer


    for nodeToPrint in nodesToPrint:
        if nodeToPrint.content == "\n":
            outputFile.write( "<br>\n" )
        else:
            if(nodeToPrint.state == STATE_MATCH):
                if not isblack:
                    outputFile.write( "</span>" )
                    isblack = True
                    isred = False
                    isgreen = False
            elif(nodeToPrint.state == STATE_PASSING_2ND ):
                if not isred:
                    if not isblack:
                        outputFile.write( "</span>" )
                    outputFile.write( "<span class='new'>" )
                    isblack = False
                    isred = True
                    isgreen = False
            else:
                if not isgreen:
                    if not isblack:
                        outputFile.write( "</span>" )
                    outputFile.write( "<span class='old'>" )
                    isblack = False
                    isred = False
                    isgreen = True

            outputFile.write( escape( nodeToPrint.content ) )

    if not isblack:
        outputFile.write( "</span>" )
        isblack = True
        isred = False
        isgreen = False

def main( argv ):

    filename1 = None
    filename2 = None
    output =    None
    same_size = False

    for arg in argv:
        if arg.startswith( "-" ):
            if arg == "--same_size":
                same_size = True
            else:
                raise Exception( "Unknown arg " + arg )
        else:
            if not filename1:
                filename1 = arg
            elif not filename2:
                filename2 = arg
            elif not output:
                output = arg
            else:
                raise Exception( "Extra argument " + arg ) 
        

    if not filename1 or not filename2 or not output:
        print( "Usage: JLDiff file1 file2 resultFile [--same_size]" )
        exit(1)

    with codecs.open( filename1, 'r', 'utf-8', errors='ignore' ) as fileHandle1:
        with codecs.open( filename2, 'r', 'utf-8', errors='ignore' ) as fileHandle2:
            file1 = fileHandle1.read()
            file2 = fileHandle2.read()

            result = compute_diff( file1, file2 )

    with codecs.open( output, 'w', 'utf-8', errors='ignore' ) as outFile:
        outFile.write( "<!DOCTYPE html>\n" )
        outFile.write( "<html>\n" )
        outFile.write( "<head>\n" )
        outFile.write( "<meta charset='utf-8'>\n" )
        outFile.write( "<title>diff of " + cgi_escape( filename1 ) + " and " + cgi_escape( filename2 ) + "</title>\n" )
        outFile.write( "<style>\n" )
        if same_size:
            outFile.write( ".new{color:darkgreen}\n" )
            outFile.write( ".old{color:red}\n" )
        else:
            outFile.write( ".new{color:darkgreen;font-size: 25px;}\n" )
            outFile.write( ".old{color:red;font-size: 25px;}\n" )
        outFile.write( "</style>\n" )
        outFile.write( "</head>\n" )
        outFile.write( "<body>\n" )

        printDiffs( result, outFile )
        
        outFile.write( "</body>\n" )
        outFile.write( "</html>\n" )


if __name__ == "__main__":
    main(sys.argv[1:])
