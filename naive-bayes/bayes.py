#!/usr/bin/env python

import math
import os
import subprocess
import sys

class Language():
    
    def __init__(self, char_counts, total_chars, documents, name=''):
        self.char_counts = char_counts
        self.total_chars = total_chars
        self.documents = documents
        self.name = name
    
    def __unicode__(self):
        return self.name

def is_alpha_or_space(char):
    'Returns True if char is [a-z], False otherwise.'
    return char == ' ' or (ord(char) >= 97 and ord(char) <= 122)

def get_chars(language, directory):
    """
    Given a language ('English', 'Spanish', or 'Japanese'), returns a
    tuple of character counts, total character count, and document
    count.
    """
    chars = {chr(c + 97): 0 for c in range(26)}
    chars.update({' ': 0}) # include spaces in probabilities
    num_documents = 0
    num_chars = 0
    import random
    for fname in os.listdir(directory):
        num_documents += 1
        with open(directory + fname) as f:
            for char in f.read():
                if is_alpha_or_space(char):
                    num_chars += 1
                    chars[char] += 1
    return chars, num_chars, num_documents

def prob_language(document, language):
    'Returns the probability of the document being in the language.'
    char_list = [chr(c + 97) for c in range(26)]
    char_list.append(' ')
    return sum([(math.log(language.char_counts[c]) if language.char_counts[c] else 0) - math.log(language.total_chars)
                for c in document if is_alpha_or_space(c)]) + language.probability

def classify(document, languages):
    'Returns the name of the language most likely to have produced the data.'
    probs = [(prob_language(document, language), language) for language in languages]
    lang = max(probs, key=lambda x: x[0])
    return lang[1].name

def create_matrix(matrix):
    'Prints the confusion matrix in a clean way.'
    s = '''\\documentclass{article}
\\renewcommand{\\maketitle}{
  \\begin{center}
    \\begin{flushright}
      Fogg, Rippey, Shoham \\\\
      CS364 \\\\
      Naive Bayes Confusion Matrix
    \\end{flushright}
    \\rule{\\linewidth}{0.1mm}
  \\end{center}
}
\\begin{document}
\\maketitle
\\begin{center}
\\begin{tabular}{|c|c|c|c|}
\\hline & %s & %s & %s \\\\ \\hline
''' % tuple(matrix.keys())
    for k, v in matrix.items():
        s += '%s & %s & %s & %s \\\\ \\hline\n' % tuple([k] + v.values())
    return s + '\\end{tabular}\n\\end{center}\n\\end{document}\n'

def test(languages, directory):
    'Tests all languages in the given test directory, returning a table of error counts.'
    error_count = {language.name: {language.name: 0 for language in languages} for language in languages}
    for language in languages:
        for fname in os.listdir(directory + language.name + '/'):
            with open(directory + language.name + '/' + fname) as document:
                text = document.read()
                classified = classify(text, languages)
                if classified != language.name:
                    error_count[classified][language.name] += 1
    return error_count

def main():
    if len(sys.argv) != 3:
        print('Bro. Gotta give me some data.')
        sys.exit(0)
    training = sys.argv[1] + '/'
    testing = sys.argv[2] + '/'
    languages = [Language(*get_chars(lang, training + lang + '/'), name=lang)
                 for lang in ['Japanese', 'English', 'Spanish']]
    
    total_documents = math.log(sum(map(lambda x: x.documents, languages)))
    
    for language in languages:
        language.probability = math.log(language.documents) - total_documents
        print('P(%s): %s' % (language.name, math.e**language.probability))
        for char, count in language.char_counts.items():
            print('P(%s | %s: %s)' % (char,
                                      language.name,
                                      math.e**((math.log(count) if count != 0 else 0) -
                                               math.log(language.total_chars))))
        print('')
    with open('bayes.tex', 'w') as f:
         f.write(create_matrix(test(languages, testing)))
    subprocess.call(['pdflatex', 'bayes.tex'])
    output_filename = 'bayes.pdf'
    if(sys.platform == 'win32'):
        os.system("start "+ output_filename)
    elif(sys.platform == 'darwin'):
        os.system("open " + output_filename)
    elif(sys.platform == 'linux2'):
        os.system('xdg-open ' + output_filename)
    
if __name__ == '__main__':
    main()
