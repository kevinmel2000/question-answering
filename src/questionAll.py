import csv
import nltk

def analyzeQuestion(q_text,weights):
    tokens = nltk.word_tokenize(q_text);
    pos = nltk.pos_tag(tokens);
    weighted_tokens=(map(lambda (x,y): (x,weights[y]),pos));
    return (weighted_tokens,[]);

def getPossibleAnswer(question, story_path):
    return 'a'

def correctAnswer(text1, text2):
    if text1==text2:
        return 1;
    else:
        return 0;


stories_path='../resources/remedia_release'
questions_csv='../resources/remedia_questions/questions1.csv'

scores=[.0, .0, .0, .0];
counters=[.0, .0, .0, .0];

weights={'PRP$':1,'VBG':2,
         'VBD':2,'VBN':2, ',':0, 'VBP':2, 'WDT':1, 'JJ':1,
         'WP':1, 'VBZ':1, 'DT':1, 'RP':1, '$':0, 'NN':1,
         'POS':1, '.':0, 'TO':1, 'PRP':1, 'RB':1, ':':0,
         'NNS':1, 'NNP':1, 'VB':1, 'WRB':1, 'CC':1,
         'RBR':1, 'CD':1, '-NONE-':0, 'IN':1, 'MD':1,
         'NNPS':1, 'JJS':1, 'JJR':1}

for entry in csv.reader(open(questions_csv, 'r')):
    q = analyzeQuestion(entry[3],weights);
    pa = getPossibleAnswer(q, stories_path+entry[0]);
    ra = entry[4];
    scores[int(entry[1])-2]=correctAnswer(pa,ra[2:len(ra)-2]);
    counters[int(entry[1])-2] = counters[int(entry[1])-2] + 1;

print 'Scores:';
print map(lambda s, c: s*100.0/c, scores, counters);
