Cowparser.py
-------

This repository contains a python script for the COW corpus data made available at [webcorpora.org](http://webcorpora.org/).
This corpus was created by Felix Bildhauer and Roland Schäfer.
A full description of the work behind this data can be found at [corporafromtheweb.org](http://corporafromtheweb.org/).

I tested the script on the Dutch portion on the data, but it should work on the other corpora as well, except if the XML format is different, like with English. I am currently working to provide a parser for English as well.


For those interested: the Dutch shuffle corpus contains 4,732,581,841 tokens. Rather than unpacking the corpus,
the script directly goes through the gzipped xml files, saving a lot of disk space.


### Examples

#### Basic usage
To just get all the sentences for a particular file, use `sentence generator`:

    from cowparser import sentence_generator
    gen = sentence_generator('nlcow14ax01.xml.gz')
    metadata, sentence = gen.next()

The metadata is not important for now (it mostly contains information about the crawl). What matters is the sentence:

    >>> sentence
    [('Van', '1952', 'tot', '1956', 'was', 'De', 'Bruijn', 'minister', 'zonder', 'portefeuille', 'in', 'het', 'kabinet', '-', 'Drees', '.'), ('prep', 'num__card', 'prep', 'num__card', 'verbpastsg', 'det__art', 'adj', 'nounsg', 'prep', 'nounsg', 'prep', 'det__art', 'nounsg', 'punc', 'nounprop', '$.'), ('van', '@card@', 'tot', '@card@', 'wezen|zijn', 'de', '(unknown)', 'minister', 'zonder', 'portefeuille', 'in', 'het', 'kabinet', '-', 'Drees', '.')]

Standardly, sentences consist of three tuples: the words in the sentence, the parts of speech, and the relevant lemmas. Alternatively, one might change this behavior by setting the `separate` flag to `False`:

    gen = sentence_generator('nlcow14ax01.xml.gz',separate=False)

The sentence will then be output as a list of lists containing the word, part-of-speech, and the lemma:

    [['Van', 'prep', 'van'], ['1952', 'num__card', '@card@'], ['tot', 'prep', 'tot'], ['1956', 'num__card', '@card@'], ...]

Abstracting away from the file level, one might use the following lines to create a generator for the entire directory:

    from cowparser import sentences_for_dir
    gen = sentences_for_dir('path/to/corpus/')

This works exactly the same way as a single-file generator.

#### Selecting high-quality sentences
Since the COW corpus is created through webcrawling, it is not the case that all data is equally reliable.
Therefore, each sentence comes with a quality score and a boilerplate score. To only use sentences from the
most reliable sources, one should select sentences with a boilerplate score ('bpc') of 'a' and a document quality score
('bdc') of 'a'. The following code might be used to create a 'high-quality generator':

    highest_quality = (data for metadata, data in sentences_for_dir()
                            if  metadata['bpc']=='a' and
                                metadata['bdc']=='a')
