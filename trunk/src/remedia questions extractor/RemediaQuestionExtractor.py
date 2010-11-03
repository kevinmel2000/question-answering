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
        qre = re.compile("(\d)(\s*[.])(.*[?])")
        levelre = re.compile("level\d")
        for root, dirs, files in os.walk(self.remedia_root):
            if 'CVS' in dirs:
                dirs.remove('CVS')  # don't visit CVS directories
            if '.svn' in dirs:
                dirs.remove('.svn')  # don't visit CVS directories
            m = re.search(levelre,root)
            if (m == None):
				print root
            for qfile in files:
                self.extractQuestionsFromFile(qfile,root,qre,m.group(0))
        self.output_file.close()
     
    def extractQuestionsFromFile(self,qfile,qdir,qre, level):
        f = open(path.join(qdir,qfile),'r')
        while 1:
            line = f.readline()
            if not line:
                break
            line = line.strip(" \t\n")
            m = re.match(qre,line)
            if (m != None):
                escaped = replace(m.group(0),'"','""')
                escaped2 = replace(m.group(3),'"','""').strip(" \t\n")
                output_line = '"' + escaped + '","' + escaped2 + '",' + level + ',' + qfile +  '\n'
                self.output_file.write(unicode(output_line))
                print output_line
        f.close()
class InvalidPathException(Exception):
    def __init__(self):
        return
    
    def __str__(self):
        return "", "Missing path"
    
    
