from os import path
import os
import re
from string import replace

class RemediaQuestionExtractor:
    " " " browses the remedia corpus " " "
    def __init__ (self, remedia_root = None, output_dir = None):
        if (remedia_root == None):
            self.remedia_root = path.abspath("../../resources/remedia_release/")
        else:
            self.remedia_root = remedia_root
        if (output_dir == None):
            self.output_dir = path.abspath("../../resources/remedia_questions/")
        else:
            self.output_dir = output_dir
        if (self.output_dir[-1] != '/'):
                self.output_dir = self.output_dir + '/'
        if (path.isdir(self.remedia_root) == False):
            self.remedia_root = None
            raise InvalidPathException
        if (path.isdir(self.output_dir) == False):
            self.output_dir = None
            raise InvalidPathException

    def extractQuestions(self):
        self.output_file = open(self.output_dir + "questions.csv", "w")
        self.output_file.write("File,Level,Order in file,Clean Question,Tagged Elements,Full Question\n")
        qre = re.compile("(\d)(\s*[.]\s*)([^\s].*[?])")
        levelre = re.compile("(level)(\d)")
        tagre = re.compile('[<][^<]*[>][^<>]*[</][^<]*[>]')
        valuere = re.compile('[<][^<]*[>]([^<>]*)[</][^<]*[>]')
        for root, dirs, files in os.walk(self.remedia_root):
            if 'CVS' in dirs:
                dirs.remove('CVS')  # don't visit CVS directories
            if '.svn' in dirs:
                dirs.remove('.svn')  # don't visit CVS directories
            m = re.search(levelre,root)
            for qfile in files:
                self.extractQuestionsFromFile(qfile,root,qre,m.group(2),tagre,valuere)
        self.output_file.close()
     
    def extractQuestionsFromFile(self,qfile,qdir,qre,level,tagre,valuere):
        f = open(path.join(qdir,qfile),'r')
        while 1:
            line = f.readline()
            if not line:
                break
            line = line.strip(" \t\n")
            m = re.match(qre,line)
            if (m != None):
                tags = re.findall(tagre,m.group(3))
                values = re.findall(valuere,m.group(3))
                clean_text = reduce(lambda x,y: replace(x,y[0],y[1]), [m.group(3)] + map(lambda x,y : (x,y),tags,values))
                newline = [replace(path.join(qdir,qfile),self.remedia_root,""),level,m.group(1), clean_text, str(tags), m.group(0)]
                output_line = reduce(lambda x,y : x + ',' + y, map(lambda x: '"' + replace(x,'"','""') + '"', newline)) + '\n'
                self.output_file.write(unicode(output_line))
        f.close()

class InvalidPathException(Exception):
    def __init__(self):
        return
    
    def __str__(self):
        return "", "Missing path"
    
    
