

import unittest
import codecs
import ebcdik

### make allias of encoding
@codecs.register
def getregentry(name):
    if name == 'ebcdik2':
        return codecs.CodecInfo(
            name='ebcdik2',
            encode=codecs.getencoder("ebcdik"),
            decode=codecs.getdecoder("ebcdik"),
            incrementalencoder=codecs.getincrementalencoder("ebcdik"),
            incrementaldecoder=codecs.getincrementaldecoder("ebcdik"),
            streamreader=codecs.getreader("ebcdik"),
            streamwriter=codecs.getwriter("ebcdik")
        )
    else:
        return None

class TestCase(unittest.TestCase):

    def test_basic(self):
        """ allias of encodings """
        self.assertEqual(str(b'\xf0\xf1\xf2','ebcdik'),
                         str(b'\xf0\xf1\xf2','ebcdik2'))
    

if __name__ == "__main__":
    unittest.main()


d"""

class Codec(codecs.Codec):

    def encode(self,input,errors='strict'):
        return codecs.charmap_encode(input,errors,encoding_table)

    def decode(self,input,errors='strict'):
        return codecs.charmap_decode(input,errors,decoding_table)

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return codecs.charmap_encode(input,self.errors,encoding_table)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return codecs.charmap_decode(input,self.errors,decoding_table)[0]

class StreamWriter(Codec,codecs.StreamWriter):
    pass

class StreamReader(Codec,codecs.StreamReader):
    pass

"""


    
