

import unittest
import codecs
import ebcdik
import encodings

def make_file(file,contents):
    with open(file,"wb") as fh:
        fh.write(contents)

class Codec(codecs.Codec):

    def encode(self,input,errors='strict'):
        b = input.encode("ebcdik",errors=errors)
        return (b,len(input))

    def decode(self,input,errors='strict'):
        s = bytes(input).decode("ebcdik",errors=errors)
        return (s,len(input))

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return Codec().encode(input,errors=self.errors)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return Codec().decode(input,errors=self.errors)[0]

class StreamWriter(Codec,codecs.StreamWriter):
    pass

class StreamReader(Codec,codecs.StreamReader):
    pass

### make alias of encoding
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
    elif name == 'ebcdik3':
        return codecs.CodecInfo(
            name='ebcdik2',
            encode=Codec().encode,
            decode=Codec().decode,
            incrementalencoder=IncrementalEncoder,
            incrementaldecoder=IncrementalDecoder,
            streamreader=StreamReader,
            streamwriter=StreamWriter
        )
    else:
        return None

ebcbytes = b'\xf0\xf1\xf2\xf3\xf4\xf5'
unichars = '012345'

class TestCase(unittest.TestCase):

    def test_basic(self):
        """ alias of encodings """
        self.assertEqual(unichars,str(ebcbytes,'ebcdik'))

    def test_alias1(self):
        """ alias of encodings """
        self.assertEqual(unichars,str(ebcbytes,'ebcdik2'))

    def test_alias2(self):
        """ alias of encodings """
        encodings.aliases.aliases['ebcdik4'] = 'ebcdik'        
        self.assertEqual(unichars,str(ebcbytes,'ebcdik4'))

    def test_basic(self):
        """ test stream reader """
        make_file("xxx.txt",ebcbytes)
        with open("xxx.txt",encoding="ebcdik") as fh:
            contents = fh.read()
            self.assertEqual(contents,unichars)

    def test_basic2(self):
        """ test for codecs API """
        self.assertEqual(unichars,str(ebcbytes,'ebcdik3'))
            

if __name__ == "__main__":
    unittest.main()






    
