import csv
import nltk
import re

def getStory(path):
    file = open(path, 'r')
    text = file.read()
    story = text[text.find(')')+1:text.index(re.search('1.(\s+)Wh',text).group(0))]
    story = story.replace('."','".')
    story = story[story.index(re.search('[A-Z]',story).group(0)):]
    return story.strip()

def stemString(text):
    tokens = nltk.tokenize.TreebankWordTokenizer().tokenize(text)
    return map(lambda x: nltk.PorterStemmer().stem(x).lower(), tokens)
    
def getScore(constraints, sentence):
    return 1

def getBestAnswer(question, constraints, story):
    words = map(lambda x: x[0], question)
    weight = dict(question)
    sentences = nltk.tokenize.PunktSentenceTokenizer().tokenize(story)

    cnt = map(lambda x: sum(map(lambda y: 1 if x in y else 0, sentences)), words)
    idf = dict(map(lambda x,y: (x,0) if y==0 else (x, len(sentences)*1.0/y), words, cnt))

    score = map(lambda sent: sum(map(lambda w: idf[w]*weight[w]*getScore(constraints,sent) if w in stemString(sent) else 0, words)), sentences)
    bestAnswer = score.index(max(score))
    
    return sentences[bestAnswer]

def analyzeQuestion(q_text,weights):
    tokens = nltk.word_tokenize(q_text);
    pos = nltk.pos_tag(tokens);
    weighted_tokens=(map(lambda (x,y): (x,weights[y]),pos));
    return (weighted_tokens,[]);

def getPossibleAnswer(question, story_path):
    return 'a'

def correctAnswer(text1, text2):
    print "-----------------------------------"
    print text1
    print text2
    if text1==text2:
        print "MATCH"
        return 1;
    else:
        return 0;


stories_path='../resources/remedia_release'
questions_csv='../resources/remedia_questions/questions1.csv'

scores=[.0, .0, .0, .0];
counters=[.1, .1, .1, .1];

weights={'PRP$':1,'VBG':1,
         'VBD':1,'VBN':1, ',':0, 'VBP':1, 'WDT':1, 'JJ':1,
         'WP':1, 'VBZ':1, 'DT':1, 'RP':1, '$':0, 'NN':1,
         'POS':1, '.':0, 'TO':1, 'PRP':1, 'RB':1, ':':0,
         'NNS':1, 'NNP':1, 'VB':1, 'WRB':1, 'CC':1,
         'RBR':1, 'CD':1, '-NONE-':0, 'IN':1, 'MD':1,
         'NNPS':1, 'JJS':1, 'JJR':1}

##weights={'PRP$':1,'VBG':2,
##         'VBD':2,'VBN':2, ',':0, 'VBP':2, 'WDT':1, 'JJ':1,
##         'WP':1, 'VBZ':1, 'DT':1, 'RP':1, '$':0, 'NN':1,
##         'POS':1, '.':0, 'TO':1, 'PRP':1, 'RB':1, ':':0,
##         'NNS':1, 'NNP':1, 'VB':1, 'WRB':1, 'CC':1,
##         'RBR':1, 'CD':1, '-NONE-':0, 'IN':1, 'MD':1,
##         'NNPS':1, 'JJS':1, 'JJR':1}

i=1
for entry in csv.reader(open(questions_csv, 'r')): 
    q = analyzeQuestion(entry[3],weights);
    pa = getBestAnswer(q[0], q[1], getStory(stories_path+entry[0]));
    ra = entry[4];
    scores[int(entry[1])-2] += correctAnswer(pa,ra[2:len(ra)-2]);
    counters[int(entry[1])-2] = counters[int(entry[1])-2] + 1;
    i = i+1
    #if i==10:
    #    break

print 'Scores:';
print map(lambda s, c: s*100.0/c, scores, counters);
