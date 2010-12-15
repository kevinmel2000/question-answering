import nltk
import csv

def stemString(text):
    tokens = nltk.tokenize.TreebankWordTokenizer().tokenize(text)
    return map(lambda x: nltk.PorterStemmer().stem(x).lower(), tokens)

def getStory(path, start, end):
    file = open(path, 'r')
    file.seek(start)
    return file.read(end-start)

def answerQuestion(question, story):
    stems = stemString(question)
    stopWords = nltk.corpus.stopwords.words('english')
    sentences = nltk.tokenize.PunktSentenceTokenizer().tokenize(story)
    keywords = reduce(lambda x,y: x+[y] if y != '' else x, map(lambda x: x if x not in stopWords and x != '?' else '', stems), [])
    noMatches = map(lambda x: reduce(lambda y,z: y+z, map(lambda k: 1 if k in stemString(x) else 0, keywords), 0), sentences)
    bestAnswer = noMatches.index(max(noMatches))
    
    print('-------------------------------------------')
    print(question)
    print(sentences[bestAnswer])

    return sentences[bestAnswer]

if __name__ == '__main__':
    map(lambda x: answerQuestion(x[3], getStory('remedia_release'+x[0], 100, 1000)), csv.reader(open('questions_filtered.csv', 'r')))
    
