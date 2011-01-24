import nltk
import re

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

def getScore(constraints, sentence):
    return 0

def getBestAnswer(question, constraints, story):
    words = map(lambda x: x[0], question)
    weight = dict(question)
    sentences = nltk.tokenize.PunktSentenceTokenizer().tokenize(story)

    cnt = map(lambda x: sum(map(lambda y: 1 if x in y else 0, sentences)), words)
    idf = dict(map(lambda x,y: (x,0) if y==0 else (x, len(sentences)*1.0/y), words, cnt))

    score = map(lambda sent: sum(map(lambda w: idf[w]*weight[w]*(1+getScore(constraints,sent)) if w in stemString(sent) else 0, words)), sentences)
    bestAnswer = score.index(max(score))
    
    return sentences[bestAnswer]

if __name__ == '__main__':
    print getBestAnswer([('did', 0.1), ('young', 0.2), ('chris', 0.3), ('live', 0.4)], 
                        [('a', 0.7), ('b', 0.3)],
                        getStory('../resources/remedia_release/level2/org/rm2-1.txt'))
