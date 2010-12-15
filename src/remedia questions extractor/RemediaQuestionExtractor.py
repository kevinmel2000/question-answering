from os import path
import os
import re
from string import replace

class RemediaQuestionExtractor:
    " " " browses the remedia corpus " " "
    def __init__ (self, remedia_root = None, output_dir = None):
        # compute absolute paths and check if are valid
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
        self.output_file = open(self.output_dir + "questions.csv", "w") # create or overwrite outputfile
        self.output_file.write('File,Level,Order in file,Clean Question,Tagged Elements,Full Question,Answer\n')
        # some regex needed
        self.qre = re.compile('(\d)(\s*[.]\s*)([^\s].*[?])')
        self.ansre = re.compile('([<]ANSQ)(\d)([>])')
        self.levelre = re.compile("(level)(\d)")
        self.tagre = re.compile('[<][^<]*[>][^<>]*[</][^<]*[>]')
        self.valuere = re.compile('[<][^<]*[>]([^<>]*)[</][^<]*[>]')
        # browse folder for files
        for root, dirs, files in os.walk(self.remedia_root):
            if 'CVS' in dirs:
                dirs.remove('CVS')  # don't visit CVS directories
            if '.svn' in dirs:
                dirs.remove('.svn')  # don't visit CVS directories
            m = re.search(self.levelre,root) # extract level from path
            for qfile in files:
                self.extractQuestionsFromFile(qfile,root,m.group(2))
        self.output_file.close() # close output file

    def cleanOtherTags(self,text_to_clean):
        # clean tags from text
        tags = re.findall(self.tagre,text_to_clean)
        values = re.findall(self.valuere,text_to_clean)
        clean_text = reduce(lambda x,y: replace(x,y[0],y[1]), [text_to_clean] + map(lambda x,y : (x,y),tags,values))
        print clean_text
        return [clean_text,tags]

    def extractAnswerParts(self,line,qno):
        half='([<]ANSQ' + qno + '[>])(.*)([<]/ANSQ' + qno +  '[>])'
        are = re.compile(half + '(.*)' +  half)
        hre = re.compile(half)
        x = re.search(are,line)
        if x != None:
            t1 = x.group(1) + x.group(2) + x.group(3)
            t2 = x.group(5) + x.group(6) + x.group(7)
            return self.extractAnswerParts(t1,qno) + self.extractAnswerParts(t2,qno)
        else:
            x = re.search(hre,line)
            if x != None:
                t = self.cleanOtherTags(x.group(2))[0]
                return [t]
            else:
                return []
        
    def extractQuestionsFromFile(self,qfile,qdir,level):
        f = open(path.join(qdir,qfile),'r')
        answers=dict()
        while 1:
            line = f.readline()
            if not line:
                break
            line = line.strip(" \t\n")
            a = re.findall(self.ansre,line)
            for tagans in a:
                number = tagans[1]
                answer = self.extractAnswerParts(line,number)
                if len(answer) > 0:
                    answers[number] = str(answer)
            m = re.match(self.qre,line)
            if (m != None):
                [clean_text, tags] = self.cleanOtherTags(m.group(3))
                newline = [replace(path.join(qdir,qfile),self.remedia_root,""),level,m.group(1), clean_text, str(tags), m.group(0)]
                if m.group(1) in answers.keys():
                    newline = newline + [answers[m.group(1)]]
                else:
                    newline = newline + ['']
                output_line = reduce(lambda x,y : x + ',' + y, map(lambda x: '"' + replace(x,'"','""') + '"', newline)) + '\n'
                self.output_file.write(unicode(output_line))
        f.close()

class InvalidPathException(Exception):
    def __init__(self):
        return
    
    def __str__(self):
        return "", "Missing path"
    
    
