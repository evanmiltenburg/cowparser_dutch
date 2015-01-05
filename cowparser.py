import gzip, glob
from lxml import etree

def cowfiles(path='./'):
    "Wrapper for the glob module."
    return glob.glob(path+'*.xml.gz')

def sentence_generator(filename,separate=True,gzipped=True):
    """Returns metadata and the sentence: [(words),(tags),(lemmas)]
    
    Arguments
    ---------
    filename: filename
    separate: if False, changes sentence format to [(w1,t1,l1),(w2,t2,l2),...]
    gzipped : assumes the file is gzipped. Change to False for unpacked files
    """
    source = gzip.GzipFile(filename) if gzipped else filename
    parser = etree.iterparse(source,html=True)
    for x,y in parser:
        try:
            # Trips is a list of the word, part-of-speech and the lemma.
            # by zipping that list, you get a format that I prefer (see details above)
            # The good thing about it is that you can search for sub-sequences
            # in the POS list. E.g. using the contains() function that I included
            # for convenience.
            trips = [w.split('\t') for w in y.text.strip().split('\n')]
            # y.attrib contains the sentence metadata.
            yield y.attrib, zip(*trips) if separate else trips
        except AttributeError:
            print 'No text for this element!'
            pass
        y.clear() # Save memory
        # Save more memory by deleting references to previous sentences
        for ancestor in y.xpath('ancestor-or-self::*'):
            while ancestor.getprevious() is not None:
                del ancestor.getparent()[0]

def sentences_for_dir(path='./',separate=True,gzipped=True):
    """Sentence generator for an entire corpus directory.
    Returns metadata and the sentence: [(words),(tags),(lemmas)]
    
    Arguments
    ---------
    path    : path to the COW files
    separate: if False, changes sentence format to [(w1,t1,l1),(w2,t2,l2),...]
    gzipped : assumes the file is gzipped. Change to False for unpacked files
    """
    for filename in cowfiles(path):
        for metadata, data in sentence_generator(filename,separate,gzipped):
            yield metadata, data

def contains(small, big):
    """Checks if a small sequence is contained in a larger sequence.
    
    I think I got this from a StackExchange answer, but forgot to bookmark it."""
    for i in xrange(len(big)-len(small)+1):
        for j in xrange(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return i, i+len(small)
    return False
