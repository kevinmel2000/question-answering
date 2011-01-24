import csv
import nltk
import re

def getStory(path):
    file = open(path, 'r')
    text = file.read()
    story = text[text.find('(')-1:text.index(re.search('1.(\s+)Wh',text).group(0))]
    story = story.replace('."','".')
    story = story[story.index(re.search('[A-Z]',story).group(0)):]
    return story.strip()

def stemSentence(text):
    tokens = nltk.tokenize.TreebankWordTokenizer().tokenize(text)
    return map(lambda x: nltk.PorterStemmer().stem(x).lower(), tokens)

##sentences = nltk.tokenize.PunktSentenceTokenizer().tokenize(story)
#############################################################################

def hasEntity(sentence, entities):
    for ent in entities:
        if sentence.find(ent) >= 0:
            return 1
    return 0
    
def getScore(constraints, sentence, entities):
    score = 1;
    for constr in constraints:
        if constr[0] == 'l':
            score *= 1+constr[1]*hasEntity(sentence, entities[0])
        if constr[0] == 'p':
            score *= 1+constr[1]*hasEntity(sentence, entities[1])
        if constr[0] == 't':
            score *= 1+constr[1]*hasEntity(sentence, entities[2])
    return score

def similarity(question, idf, constraints, sentence, entities):
    score = 0;
    for word in question:
        if (word[0] in stemSentence(sentence[0])) or (word[2] in sentence[1]):
            score += idf[word[0]]*word[1]
    return score*getScore(constraints, sentence[0], entities)

def getBestAnswer(question, constraints, sentences, entities):
    #question = [(word, weight, refid), ...]
    #constraints = [(constraint, weight), ...]
    #sentences = [(sent, [refid, ...]), ...]
    #entities = ([name, ...], [location, ...], [date, ...])
    
    cnt = map(lambda w: sum(map(lambda sent: 1 if w[0] in stemSentence(sent[0]) else 0, sentences)), question)
    idf = dict(map(lambda w,c: (w[0],0) if c==0 else (w[0], len(sentences)*1.0/c), question, cnt))

    score = map(lambda sent: similarity(question, idf, constraints, sent, entities), sentences)
    bestAnswer = score.index(max(score))
    return sentences[bestAnswer][0]

##########################################################################

print getBestAnswer([('did', 0.1, 0), ('young', 0.2, 0), ('chris', 0.3, 1), ('live', 0.4, 2)],
                    [('n', 0.7), ('l', 0.3)],
                    [('Christopher Robin is alive, and well.', [1,2]),
                     ('He lives in England.', [5]),
                     ('His friends were animals.', [])
                     ],
                    (['Ana','Robin'],['England'],['yesterday']))
