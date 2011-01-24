import nltk
import csv
import re
import math

def stemString(text):
    tokens = nltk.tokenize.TreebankWordTokenizer().tokenize(text)
    return map(lambda x: nltk.PorterStemmer().stem(x).lower(), tokens)

def getStory(path):
    file = open(path, 'r')
    text = file.read()
    story = text[text.find(')')+1:text.index(re.search('1.(\s+)Wh',text).group(0))]
    story = story.replace('."','".')
    story = story[story.index(re.search('[A-Z]',story).group(0)):]
    return story.strip()

def answerQuestion(question, story, answer):
    stems = stemString(question)
    stopWords = nltk.corpus.stopwords.words('english')
    sentences = nltk.tokenize.PunktSentenceTokenizer().tokenize(story)
    
    cnt = map(lambda x: sum(map(lambda y: 1 if x in y else 0, sentences)), stems)
    idf = dict(map(lambda x,y: (x,0) if y==0 else (x, len(sentences)*1.0/y), stems, cnt))
    
    keywords = reduce(lambda x,y: x+[y] if y != '' else x, map(lambda x: x if x not in stopWords and x != '?' else '', stems), [])
    noMatches = map(lambda x: sum(map(lambda k: idf[k] if k in stemString(x) else 0, stems)), sentences)
    bestAnswer = noMatches.index(max(noMatches))

    answer = answer[2:len(answer)-2]
    answer = answer.replace('."','".')
    
    #print '============================================'
    #print story
    #print '----------------------'
    #print question
    #print sentences[bestAnswer]
    #print answer
    #print sentences[bestAnswer]==answer

    return sentences[bestAnswer]==answer

if __name__ == '__main__':
    z = map(lambda x: answerQuestion(x[3], getStory('../resources/remedia_release'+x[0]), x[4]), csv.reader(open('../resources/remedia_questions/questions1.csv', 'r')))
    print (z.count(True)*100.0)/len(z)
