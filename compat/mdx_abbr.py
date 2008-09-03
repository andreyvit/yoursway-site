'''
Abbreviation Extension for Python-Markdown
==========================================

This extension adds abbreviation handling to markdown.

Note: This extension addes an inline syntax to the previously established syntax.

Simple Usage (Run this file from the command line to test):

    >>> import markdown
    >>> text = """
    ... Some text with an [ABBR]{Abbreviation} and a REF. Ignore REFERENCE and ref.
    ...
    ... *[REF]: Abbreviation Reference
    ... """
    >>> md = markdown.Markdown(text, ['abbr'])
    >>> str(md)
    '\\n<p>Some text with an <abbr title="Abbreviation">ABBR</abbr> and a <abbr title="Abbreviation Reference">REF</abbr>. Ignore REFERENCE and ref.\\n</p>\\n\\n\\n'

Passing in ABBR defs as a dict:

    >>> text = 'Some text with HTML and W3C.'
    >>> md = markdown.Markdown(text, 
    ...     extensions = ['abbr'], 
    ...     extension_configs = {'abbr': [('abbrs', {'HTML' : 'Hypertext Markup Language',
    ...                                              'W3C' : 'World Wide Web Consortium'})]}, 
    ...     encoding='utf-8',
    ...     safe_mode = True)
    >>> str(md)
    '\\n<p>Some text with <abbr title="Hypertext Markup Language">HTML</abbr> and <abbr title="World Wide Web Consortium">W3C</abbr>.\\n</p>\\n\\n\\n'

Passing in ABBR defs from a file

    >>> text = 'BTW, YMMV. Well, I hope not.'
    >>> md = markdown.Markdown(text, 
    ...     extensions = ['abbr'],
    ...     extension_configs = {'abbr': [('file', 'abbr.txt')]},
    ...     encoding='utf-8')
    >>> str(md)
    '\\n<p><abbr title="By the way">BTW</abbr>, <abbr title="Your mileage may vary">YMMV</abbr>. Well, I hope not.\\n</p>\\n\\n\\n'

Use Meta Data (from mdx_meta.py extension) to point to ABBR defs in files

    >>> text = """Abbr_Files:  abbr.txt
    ... 
    ... Some text with HTML and W3C.
    ... """
    >>> md = markdown.Markdown(text, ['meta', 'abbr'])
    >>> str(md)
    '\\n<p>Some text with <abbr title="Hypertext Markup Language">HTML</abbr> and <abbr title="World Wide Web Consortium">W3C</abbr>.\\n</p>\\n\\n\\n'

    
Authors:
* [Waylan Limberg](http://achinghead.com/)
* [Seemant Kulleen](http://www.kulleen.org/)
	
Project website: http://achinghead.com/markdown/abbr/
Contact: waylan [at] gmail [dot] com

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)

Version: 0.1 (Aug 21, 2007)

Dependencies:
* [Python 2.3+](http://python.org)
* [Markdown 1.6+](http://www.freewisdom.org/projects/python-markdown/)
'''

import markdown, re

# Global Vars
ABBR_REF_RE = re.compile(r'[*]\[(?P<abbr>[^\]]*)\][ ]?:\s*(?P<title>.*)')

class AbbrExtension (markdown.Extension) :
    def __init__(self, configs):
        # set extension defaults - empty - for documentation purposes only
        self.config = { \
                'file' : ['', 'path/name to file holding abbr definitions.'],
                'abbrs' : [{}, 'A Dict of abbr definitions'],
        }
        
        # create preproccessor instance to store abbr defs.
        self.preprocessor = AbbrPreprocessor()
        self.preprocessor.abbrs = {}
        
        # Apply configs: Author gets final say so abbrs
        # defined in code come first. Then abbrs defined
        # in files (presumably author editable) and
        # finally abbrs defined in the document. The last
        # definition overrides any previous definitions
        # of that abbr.
        configs = dict(configs)
        if configs.has_key('abbrs'):
            for k, v in configs['abbrs'].items():
                    self.preprocessor.abbrs[k] = v
        if configs.has_key('file'):
            self.preprocessor.get_from_file(configs['file'])

        
    def extendMarkdown(self, md, md_globals) :
        self.md = md

        ABBR_RE = r'\[(?P<abbr>.+?)\]\{(?P<title>[^{]+?)\}'

        # Insert preprocessor before ReferencePreprocessor
        index = md.preprocessors.index(md_globals['REFERENCE_PREPROCESSOR'])
        self.preprocessor.md = md
        md.preprocessors.insert(index, self.preprocessor)
        
        md.inlinePatterns.append(AbbrPattern(ABBR_RE, None))

        
class AbbrPreprocessor(markdown.Preprocessor) :
    
    def run(self, lines) :
        '''
        Finds and removes all Abbreviation references from the text.
        Each reference is set as a new AbbrPattern in the markdown instance.
        '''
        if hasattr(self.md, 'Meta') and self.md.Meta.has_key('abbr_files'):
            # Pull abbrs from files defined in Meta Data
            for file in self.md.Meta['abbr_files']:
                self.get_from_file(file)
        
        new_text = self.get_abbrs(lines)
        
        for key, value in self.abbrs.items():
            self.md.inlinePatterns.append(AbbrPattern(self._generate_pattern(key), value))
            
        return new_text
    
    def get_abbrs(self, lines):
        '''
        Finds and removes all Abbreviation references from the text.
        References are stored in self.abbrs
        '''
        new_text = []
        for line in lines:
            m = ABBR_REF_RE.match(line)
            if m:
                self.abbrs[m.group('abbr').strip()] = m.group('title').strip()
            else:
                new_text.append(line)
        return new_text
    
    def get_from_file(self, file_name):
        '''
        Opens the given file and extracts Abbreviation references.
        Ignores all non-references in file.
        '''
        try:
            f = open(file_name)
        except IOError:
            pass # fail silently
        else:
            self.get_abbrs(f.readlines())
            f.close()
    
    def _generate_pattern(self, text):
        '''
        Given a string, returns an regex pattern to match that string as group('abbr'). 
        
        'HTML' -> r'(?P<abbr>[H][T][M][L])' 
        
        Note: we force each char as a literal match (in brackets) as we don't know what 
        they will be beforehand.
        '''
        chars = list(text)
        for i in range(len(chars)):
            chars[i] = r'[%s]' % chars[i]
        return r'(?P<abbr>\b%s\b)' % (r''.join(chars))


class AbbrPattern (markdown.Pattern) :
    def __init__ (self, pattern, title) :
        markdown.Pattern.__init__(self, pattern)
        self.title = title

    def handleMatch(self, m, doc) :
        abbr = doc.createElement('abbr')
        abbr.appendChild(doc.createTextNode(m.group('abbr')))
        if self.title:
            # From Reference - Use title from Reference
            abbr.setAttribute('title', self.title)
        else:
            # Inline Def - Get title from match
            abbr.setAttribute('title', m.group('title'))
        return abbr

def makeExtension(configs=None) :
    return AbbrExtension(configs=configs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()