import re
import glob
import nltk
import math
from string import replace


def stemSentence(text):
    tokens = nltk.tokenize.TreebankWordTokenizer().tokenize(text)
    return map(lambda x: nltk.PorterStemmer().stem(x).lower(), tokens)

def plain(text):
    text = replace(text,'\n',' ');
    text = replace(text,'\t',' ');
    while '  ' in text:
        text = replace(text,'  ',' ');
    text = text.strip(' ');
    return text;

def getGroup(item):
    if(item):
        return item.group(1).lower()

def getNamedEntities(path):
	lines = map(lambda line: line, open(path).xreadlines())
	locations = list(set(filter(lambda x: x != None, map(lambda line: getGroup(re.search('<ENAMEX TYPE="LOCATION">([^<>]*)</ENAMEX>',line)),lines))))
	persons = list(set(filter(lambda x: x != None, map(lambda line: getGroup(re.search('<ENAMEX TYPE="PERSON">([^<>]*)</ENAMEX>',line)),lines))))
	times = list(set(filter(lambda x: x != None, map(lambda line: getGroup(re.search('<TIMEX TYPE="DATE">([^<>]*)</TIMEX>',line)),lines))))
	return locations, persons, times


def cleanOtherTags(text_to_clean):
    # clean tags from text
    tagre = re.compile('[<][^<]*[>][^<>]*[</][^<]*[>]');
    valuere = re.compile('[<][^<]*[>]([^<>]*)[</][^<]*[>]');
    tags = re.findall(tagre,text_to_clean);
    values = re.findall(valuere,text_to_clean);
    clean_text = reduce(lambda x,y: replace(x,y[0],y[1]), [text_to_clean] + map(lambda x,y : (x,y),tags,values));
    return [clean_text,tags];


def extractAnswerParts(line,qno):
    half='([<]ANSQ' + qno + '[>])(.*)([<]/ANSQ' + qno +  '[>])';
    are = re.compile(half + '(.*)' +  half);
    hre = re.compile(half);
    x = re.search(are,line);
    if x != None:
        t1 = x.group(1) + x.group(2) + x.group(3);
        t2 = x.group(5) + x.group(6) + x.group(7);
        return extractAnswerParts(t1,qno) + extractAnswerParts(t2,qno);
    else:
        x = re.search(hre,line);
        if x != None:
            t = cleanOtherTags(x.group(2))[0];
            return [t];
        else:
            return [];

def getAnswers(snraStory,ansre):
    snraFile = open(snraStory,'r');
    answers=dict();
    corrections={'Mr.':'Mr','Dr.':'Dr','Oct.':'Oct','Mrs.':'Mrs','St.':'St','ST.':'ST','P.T.':'PT','MT.':'MT','Mt.':'Mt','A.D.':'AD'};
    while 1:
        line = snraFile.readline();
        if not line:
            break;
        line = plain(line);
        a = re.findall(ansre,line);
        for tagans in a:
            number = tagans[1];
            answer = extractAnswerParts(line,number);
            if len(answer) > 0:
                answers[number] = str(answer);
                for k in corrections.keys():
                    answers[number]=replace(answers[number],k,corrections[k]);  
    snraFile.close();
    return answers;

def getQuestions(corefStory,qre,answers):
    corefFile = open(corefStory,'r')
    questions=dict()
    while 1:
        line = corefFile.readline();
        if not line:
            break;
        line = plain(line);
        m = re.match(qre,line);
        if (m != None):
            if m.group(1) in answers.keys():
                questions[int(m.group(1))]=[m.group(3),answers[m.group(1)]];
            else:
                questions[int(m.group(1))]=[m.group(3),''];
    corefFile.close()
    return questions;

def processQuestion(question,corefre1,corefre2,corefre3,corefre4,corefre5,corefre6,weights):
    ids=dict();
    text=question[0];
    corrections={'Mr.':'Mr','Dr.':'Dr','Oct.':'Oct','Mrs.':'Mrs','St.':'St','ST.':'ST','P.T.':'PT','MT.':'MT','Mt.':'Mt','A.D.':'AD'};
    text=plain(text);
    for k in corrections.keys():
        text=replace(text,k,corrections[k]);    
    corefs=re.findall(corefre4,text);
    for coref in corefs:
        alltag=reduce(lambda x, y: x+y, coref);
        text=replace(text,alltag,coref[1]);
    corefs=re.findall(corefre4,text);
    for coref in corefs:
        alltag=reduce(lambda x, y: x+y, coref);
        text=replace(text,alltag,coref[1]);
    corefs=re.findall(corefre3,text)+re.findall(corefre2,text)+re.findall(corefre1,text)
    for coref in corefs:
        alltag=reduce(lambda x, y: x+y, coref);
        text=replace(text,alltag,coref[3]);
        words=tokens = nltk.tokenize.TreebankWordTokenizer().tokenize(coref[3]);
        word=reduce(lambda x, y: x if len(x) > len(y) else y, words);
        ids[word]=coref[1];
    corefs=re.findall(corefre5,text) + re.findall(corefre6,text)
    for coref in corefs:
        alltag=reduce(lambda x, y: x+y, coref);
        text=replace(text,alltag,coref[3]);
    corefs=re.findall(corefre4,text);
    for coref in corefs:
        alltag=reduce(lambda x, y: x+y, coref);
        text=replace(text,alltag,coref[1]);

        #print text;
    
    tokens = nltk.tokenize.TreebankWordTokenizer().tokenize(text);
    pos = nltk.pos_tag(tokens);
    weighted_tokens=(map(lambda (x,y): (nltk.PorterStemmer().stem(x).lower(),weights[y],int(ids[x]) if x in ids.keys() else 0),pos));
    constraints=[];
    if weighted_tokens[0][0] == 'when':
        constraints=[('t',1)];
    if weighted_tokens[0][0] == 'where':
        constraints=[('l',1)];
    if weighted_tokens[0][0] == 'who':
        constraints=[('n',1)];
    #print weighted_tokens;
    return [weighted_tokens,question[1],constraints];

def splitHeader(header):
    #print '================'
    #print '================'
    #print header
    s1=header[:header.find(')')+1];
    s1=plain(s1);
    if s1[:5] == 'COREF':
        s1='(<'+s1;
    elif s1[:5] == 'MARKA':
        s1='(<'+s1;
    elif s1[0:1] <> '(':
        s1='('+s1; 
    s2=header[header.find(')')+1:];
    s2=s2.strip(' -');
    s2=plain(s2);
    #print '================'
    #print 's1: ' + s1;
    #print '================'
    #print 's2: ' + s2;
    #print '================'
    return [s1,s2]

def getText(corefStory,corefre1,corefre2,corefre3,corefre4,corefre5,corefre6):
    corefFile = open(corefStory, 'r')
    text = corefFile.read()
    text=plain(text);
    story = text[text.find('('):text.index(re.search('1.(\s+)Wh',text).group(0))]
    corrections={'Mr.':'Mr','Dr.':'Dr','Oct.':'Oct','Mrs.':'Mrs','St.':'St','ST.':'ST','P.T.':'PT','MT.':'MT','Mt.':'Mt','A.D.':'AD','A.T.':'AT'};
    for k in corrections.keys():
        story=replace(story,k,corrections[k]);    
    story = story.replace('."','".')
    story = story[story.index(re.search('[A-Z]',story).group(0)):]
    corefFile.close();
    sentences=nltk.tokenize.PunktSentenceTokenizer().tokenize(story);
    
    #if sentences[0][:5] == 'COREF':
    #    sentences[0]='(<'+sentences[0];
    #elif sentences[0][:5] == 'MARKA':
    #    sentences[0]='(<'+sentences[0];
    #else:
    #    print 'adaug ( la ' + sentences[0]
    #    sentences[0]='('+sentences[0];

    #s1 = sentences[0][:sentences[0].find(')')+2];
    
    #sentences[0] = replace(sentences[0],s1+'-','');
    #sentences[0] = replace(sentences[0],s1,'');

    #sentences = [s1] + sentences;


    sentences=splitHeader(sentences[0])+sentences[1:];
    
    sent2=[];
    for s in sentences:
        text=s;
        text = plain(text);
        ids=[];
        gasit = True;
        while gasit == True:
            gasit=False;
            corefs=re.findall(corefre4,text);
            for coref in corefs:
                alltag=reduce(lambda x, y: x+y, coref);
                text=replace(text,alltag,coref[1]);
                gasit=True
            corefs=re.findall(corefre3,text)+re.findall(corefre2,text)+re.findall(corefre1,text)
            for coref in corefs:
                alltag=reduce(lambda x, y: x+y, coref);
                text=replace(text,alltag,coref[3]);
                ids=ids+[int(coref[1])];
                gasit=True
            corefs=re.findall(corefre6,text)+re.findall(corefre5,text);
            for coref in corefs:
                alltag=reduce(lambda x, y: x+y, coref);
                text=replace(text,alltag,coref[3]);
                gasit=True
            corefs=re.findall(corefre4,text);
            for coref in corefs:
                alltag=reduce(lambda x, y: x+y, coref);
                text=replace(text,alltag,coref[1]);
                gasit=True
        #print text
        sent2=sent2+[(text,ids)];
    #print "==========++++++++========="
    #print sent2;
    #print "==========++++++++========="
    return sent2;


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
    stemmed=stemSentence(sentence[0]);
    for word in question:
        if (word[0] in stemmed):
            score += idf[word[0]]*word[1]
        elif(word[2] in sentence[1]):
            #print 'Un cacat on ploaie!'
            score += 0.6*word[1];#idf[word[0]]*word[1]
        ###print 'Cai-utam ' + word[0] + ' in ' + str(stemmed);
    return score*getScore(constraints, sentence[0], entities)

def correctAnswer(text1, text2):
    text2 = text2.replace('."','".');
    if text2[-2:]==' -':
        text2 = text2.replace(' -','');

    #print text1
    #print text2

    ret = 0
    lst = text2.split("', '")
    for ans in lst:
        if ans.startswith("'"):
            ans = ans[1:]
        if ans.endswith("'"):
            ans = ans[0:len(ans)-1]
        if text1==ans:
            #print "MATCH"
            ret = 1
    #print "-----------------------------------"

    return ret

def getBestAnswer(question, constraints, sentences, entities):
    #question = [(word, weight, refid), ...]
    #constraints = [(constraint, weight), ...]
    #sentences = [(sent, [refid, ...]), ...]
    #entities = ([name, ...], [location, ...], [date, ...])
    
    cnt = map(lambda w: sum(map(lambda sent: 1 if w[0] in stemSentence(sent[0]) else 0, sentences)), question)
    idf = dict(map(lambda w,c: (w[0],0) if c==0 else (w[0], math.log(len(sentences)*1.0/c)), question, cnt))

    score = map(lambda sent: similarity(question, idf, constraints, sent, entities), sentences)
    bestAnswer = score.index(max(score))

    #for i in range(0,len(score)):
    #    print "%.2f" % score[i],
    #    print " " + sentences[i][0]
    
    return sentences[bestAnswer][0]





textsPath = '../resources/remedia_release/';
ansre = re.compile('([<]ANSQ)(\d)([>])');
qre = re.compile('(\d)(\s*[.]\s*)([^\s].*[?])');

corefre1 = re.compile('([<]COREF ID="\d*" REF=")(\d*)("[>])([^<]*)([<]/COREF[>])');
corefre2 = re.compile('([<]COREF ID="\d*" REF=")(\d*)("[>][<]MARKABLE[>])([^<]*)([<]/MARKABLE[>][<]/COREF[>])');
corefre3 = re.compile('([<]MARKABLE[>][<]COREF ID="\d*" REF=")(\d*)("[>])([^<]*)([<]/COREF[>][<]/MARKABLE[>])');
corefre4 = re.compile('([<]MARKABLE[>])([^<]*)([<]/MARKABLE[>])');
corefre5 = re.compile('([<]COREF ID=")(\d*)("[>])([^<]*)([<]/COREF[>])');
corefre6 = re.compile('([<]COREF ID=")(\d*)("[>][<]MARKABLE[>])([^<]*)([<]/MARKABLE[>][<]/COREF[>])');

weights={'PRP$':1,'VBG':1,
         'VBD':1,'VBN':1, ',':0, 'VBP':1, 'WDT':1, 'JJ':1,
         'WP':1, 'VBZ':1, 'DT':1, 'RP':1, '$':0, 'NN':1,
         'POS':1, '.':0, 'TO':1, 'PRP':1, 'RB':1, ':':0,
         'NNS':1, 'NNP':1, 'VB':1, 'WRB':1, 'CC':1,
         'RBR':1, 'CD':1, '-NONE-':0, 'IN':1, 'MD':1,
         'NNPS':1, 'JJS':1, 'JJR':1}

weights4={'WRB': 0.39628601626111559, 'PRP$': 0.71584275114738904, 'VBG': 0.41544848640434506, 'VBD': 1.4762872745169731, 'CC': 0.63750733211878219, 'IN': 1.4972648780578646, 'VBN': 1.2799632527744693, 'POS': 0.39628601626111559, '-NONE-': 0, 'VBP': 1.3184399912206954, 'WDT': -0.23174647487149924, 'JJ': 1.8127739578666003, 'WP': -2.3025850929940455, 'VBZ': 1.4337370850951192, 'DT': 0, 'CD': 1.1872499018914846, 'MD': 1.2225502301940836, 'NNPS': 0.21584275114738904, 'RP': 0.89628601626111559, '$': -30.3025850929940455, 'NN': 1.7035887925742386, 'RBR': 1.23174647487149924, 'JJS': 0.18116446150742038, ',': 0, '.': 0, 'VB': 1.379068570587922, 'TO': 4.2961913175294344, 'PRP': 1.7433749904311804, 'RB': 0.9801850546085602, ':': -2.3025850929940455, 'NNS': 1.3737529457364159, 'JJR': -1.3025850929940455, 'NNP': 0.4186174249648332}


scores=[.0, .0, .0, .0];
counters=[-1, -1, -1, -1];


for level in range(2,6):
    print 'Starting level ' + str(level);
    levelPath = textsPath + 'level' + str(level) + '/';
    corefStories = glob.glob(levelPath + 'coref/*.coref');
    for corefStory in corefStories:
        origStory=replace(corefStory[:-6],"coref","org");
        snraStory=replace(corefStory,"coref","snra");
        neStory=replace(corefStory,"coref","ne");
        
        print 'Working on ' + replace(origStory,textsPath,'');
        
        answers=getAnswers(snraStory,ansre);
        questions=getQuestions(corefStory,qre,answers);
        sentences=getText(corefStory,corefre1,corefre2,corefre3,corefre4,corefre5,corefre6);
        locations,persons,times=getNamedEntities(neStory);
        for q in range(1,6):
            [question,answer,constraints]=processQuestion(questions[q],corefre1,corefre2,corefre3,corefre4,corefre5,corefre6,weights4);
            result=getBestAnswer(question,constraints,sentences,(locations,persons,times));
            scores[level-2]=scores[level-2]+correctAnswer(result,answer[2:len(answer)-2]);
            counters[level-2]=counters[level-2]+1;
print 'Scores:',;
sc=map(lambda s, c: s*100.0/c, scores, counters);
print sc
print 'Average:',
print sum(sc)/len(sc);
