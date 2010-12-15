import nltk
import csv

def stemString(text):
    tokens = nltk.tokenize.TreebankWordTokenizer().tokenize(text)
    return map(lambda x: nltk.PorterStemmer().stem(x).lower(), tokens)

def getStory(path):
    file = open(path, 'r')
    text = file.read()
    story = text[text.find(')')+1:text.find('1. ')]
    story = story.replace('."','".')
    for i in range(0,len(story)-1):
        if story[i].isalpha():
            break
    story = story[i:]
    return story.strip()

def answerQuestion(question, story, answer):
    stems = stemString(question)
    stopWords = nltk.corpus.stopwords.words('english')
    sentences = nltk.tokenize.PunktSentenceTokenizer().tokenize(story)
    keywords = reduce(lambda x,y: x+[y] if y != '' else x, map(lambda x: x if x not in stopWords and x != '?' else '', stems), [])
    noMatches = map(lambda x: reduce(lambda y,z: y+z, map(lambda k: 1 if k in stemString(x) else 0, keywords), 0), sentences)
    bestAnswer = noMatches.index(max(noMatches))

    answer = answer[2:len(answer)-2]
    
    print '============================================'
    print story
    print '----------------------'
    print question
    print sentences[bestAnswer]
    print answer
    print sentences[bestAnswer]==answer

    return sentences[bestAnswer]==answer

if __name__ == '__main__':
    z = map(lambda x: answerQuestion(x[3], getStory('remedia_release'+x[0]), x[4]), csv.reader(open('questions1.csv', 'r')))
    print (z.count(True)*100.0)/len(z)
