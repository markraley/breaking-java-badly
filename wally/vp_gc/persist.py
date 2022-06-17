# Software released under the MIT license (see project root for license file)

from pyamf import amf3

# ------------------------------------------------------------------------------

class Header():
    def __init__(self, version = 1, tag = "not set"):
        self.version = version
        self.tag = tag

class GC:
    def __init__(self):
        self.start_time_ms = -1
        self.duration_ms = 0
        self.tenured_start_kb = -1
        self.tenured_end_kb = -1
        self.perm_start_kb = -1
        self.perm_end_kb = -1
        self.paused = 0


class LogContents:
    def __init__(self):
        self.entries = []

# ------------------------------------------------------------------------------

def buffer_to_file(file_name, encoder):
    output_buffer = amf3.DataOutput(encoder)
    f = open(file_name, "wb")
    bytes = output_buffer.stream.getvalue()
    f.write(bytes)
    f.close()
    return len(bytes)

def file_to_buffer(file_name):
    f_in = open(file_name, "rb")
    istream = amf3.util.BufferedByteStream(f_in)
    f_in.close()
    return istream

# ------------------------------------------------------------------------------

class write_context:
    def __init__(self, ver = 1):
        self.stream = amf3.util.BufferedByteStream()
        self.encoder = amf3.Encoder(self.stream)
        self.encoder.string_references = False # disables string caching
        self.reorder_map = {}
        self.ver = ver
        self.set_version(ver)

    def set_version(self, ver):
        self.ver = ver

class read_context:
    def __init__(self, file_name, ver = 1):
        self.istream = file_to_buffer(file_name)
        self.decoder = amf3.Decoder(self.istream)
        self.bytes_read = len(self.istream)
        print(file_name, len(self.istream), 'bytes read')
        self.reorder_map = {}
        self.ver = ver
        self.set_version(ver)

    def set_version(self, ver):
        self.ver = ver

# ------------------------------------------------------------------------------
from vp_gc.vp_gc import *

def save_logs(file_name, le):

    wc = write_context(1) # header version is always 1

    h = Header(get_high_version(), 'VP_LOGENTRIES')
    write_Header(wc, h)

    wc.set_version(get_high_version())
    write_LogContents(wc, le)

    bytes_written = buffer_to_file(file_name, wc.encoder)

    print('write: ', file_name,
            ', version=', get_high_version(), sep='', end='')
    print(', entries=', len(le.entries), sep='', end='')
    print(', bytes=', bytes_written, sep='')

    return(bytes_written)