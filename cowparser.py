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
    Not perfect: only a single result per sentence! But for a corpus of this size that's fine.
    I think I got this from a StackExchange answer, but forgot to bookmark it."""
    for i in xrange(len(big)-len(small)+1):
        for j in xrange(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return i, i+len(small)
    return False

def pospattern(pattern_list,filename,path='./',gzipped=True,buffer_size=500):
    """Search for a particular sequence of parts-of-speech in the corpus.
    
    Usage example:
    >>> pospattern(['det__art', 'adj', 'nounsg'],'modified_noun_phrases.txt')
    
    A larger buffer will speed up the process (less i/o) but consume more memory.
    """
    gen = sentences_for_dir(path=path,gzipped=gzipped)  # create sentence generator
    write_buffer = []                                   # initialize buffer
    for metadata, sentence in gen:                     # Loop through the sentences
        contained = contains(pattern_list,sentence[1])  # check if the sentences contain the pattern
        if contained:                                   # if so, append to buffer.
            write_buffer.append(' '.join(sentence[0][contained[0]:contained[1]]).encode('utf-8') + '\n')
        if len(write_buffer) > buffer_size:             # and once the buffer is large enough
            with open(filename,'a') as f:              # open up a file
                f.writelines(write_buffer)              # and write out the results
            write_buffer = []                           # reset the buffer
    with open(filename,'a') as f:                      # open the file
        f.writelines(write_buffer)                      # write remaining results.
