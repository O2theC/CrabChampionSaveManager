""" 

.sav is a binary file

has header property at begining

first 4 bytes are just GVAS as bytes, intresting choice
save game version - int 32
package version - int 32
engine version parts, 3 int 16, major.minor.patch
engine build - uint 32
engine branch - str
custom version format int 32
num of custom versions - int 32
read that many custom versions
- custom version 
- some kind of id - 16 bytes
- some kind of value - int 32

save game class name - str

rest of file is an array of propertys with no length number


property
can be
bool
int
int64
uint32
float
enum
struct 
byte
str
name
set
array
object
softobject
multicast inline delegate
map

who knows what some of those even are, i'd imagine struct and stuff like object and array are gonna be recursive 
"""

import datetime
import io
from struct import unpack, pack

# this part was annoying to do with so many data types, got some help from chatgpt


# Function to read a boolean value (1 byte)
def readBool(f: io.BufferedReader | io.BytesIO):
    return unpack("<?", f.read(1))[0]


# Function to read a signed 16-bit integer (2 bytes)
def readInt16(f: io.BufferedReader | io.BytesIO):
    return unpack("<h", f.read(2))[0]


# Function to read an unsigned 16-bit integer (2 bytes)
def readUInt16(f: io.BufferedReader | io.BytesIO):
    return unpack("<H", f.read(2))[0]


# Function to read a signed 32-bit integer (4 bytes)
def readInt32(f: io.BufferedReader | io.BytesIO):
    return unpack("<i", f.read(4))[0]


# Function to read an unsigned 32-bit integer (4 bytes)
def readUInt32(f: io.BufferedReader | io.BytesIO):
    return unpack("<I", f.read(4))[0]


# Function to read a signed 64-bit integer (8 bytes)
def readInt64(f: io.BufferedReader | io.BytesIO):
    return unpack("<q", f.read(8))[0]


# Function to read an unsigned 64-bit integer (8 bytes)
def readUInt64(f: io.BufferedReader | io.BytesIO):
    return unpack("<Q", f.read(8))[0]


# Function to read a 32-bit floating point number (4 bytes)
def readFloat32(f: io.BufferedReader | io.BytesIO):
    return unpack("<f", f.read(4))[0]


# Function to read a 64-bit floating point number (double precision, 8 bytes)
def readFloat64(f: io.BufferedReader | io.BytesIO):
    return unpack("<d", f.read(8))[0]


# Function to read a single character (1 byte)
def readChar(f: io.BufferedReader | io.BytesIO):
    return unpack("<c", f.read(1))[0].decode()


# Function to read a signed char (1 byte)
def readInt8(f: io.BufferedReader | io.BytesIO):
    return unpack("<b", f.read(1))[0]


# Function to read an unsigned char (1 byte)
def readUInt8(f: io.BufferedReader | io.BytesIO):
    return unpack("<B", f.read(1))[0]


def readString(f: io.BufferedReader | io.BytesIO):
    length = readInt32(f)
    string = f.read(length - 1).decode("utf-8")
    f.read(1)  # null term byte
    return string


def readSpecialString(f: io.BufferedReader | io.BytesIO):
    length = readInt32(f)
    if length < 0:  # dev choice to signal this uses utf-16-le rather than uft-8
        # wide stuff coming in
        string = f.read(abs(length) * 2 - 2).decode("utf-16-le")
        f.read(2)  # null term
    else:
        string = f.read(length - 1).decode("utf-8")
        f.read(1)  # null term

    return string, length < 0  # if big thing


def readDate(f: io.BufferedReader | io.BytesIO):
    ticks = readInt8(f)
    try:
        calculated_time = datetime.utcfromtimestamp(
            (ticks // 10000 - 62135596800000) / 1000.0
        )
    except:
        calculated_time = ticks
    return calculated_time


def readHeader(f: io.BufferedReader | io.BytesIO):
    f.read(4)  # just bytes being GVAS


def readSav(f: io.BufferedReader | io.BytesIO):
    sav = dict()
    sav["header"] = readHeader(f)
    sav["root"] = readProperty(f)
