from dataclasses import dataclass, asdict
import re
from bs4 import BeautifulSoup
import json
from db import db


@dataclass
class Word:
    word: str
    comment: str
    solution: str
    explain: str
def download_words():
    themes = [259, 358, 344, 348, 343, 351]



    all = []

    def parse_tasks(tasks, solutions):
        #print('\n'.join(strs))
        for i in range(len(tasks)):
            t = tasks[i][4:]
            s = solutions[i][4:]
            t = t.replace('*', '')
            words = t.split(', ')
            sols = s.split(', ')
            explains = []
            words_to_arr = []
            #print(words, sols)
            for j in range(len(words)):
                word = words[j]
                sol = sols[j]
                matches = re.findall(r'\((.*?)\)', word)
                comment = ', '.join(matches)
                only_word = word.split('(')[0].strip()
                matches = re.findall(r'\((.*?)\)', sol)
                explain = ''
                words_outside_brackets = re.findall(r'(?<!\()\b\w+\b(?!\))', sol)
                right_word = words_outside_brackets[0]
                if len(matches) > 0:
                    for m in matches:
                        if m != comment:
                            explain = m
                check_dash = sol.split('—')
                if len(check_dash) > 1:
                    explain = '—'.join(check_dash[1:])
                explain = explain.replace(';', '')
                explain = explain.replace('.', '')
                explain = explain.replace('ЧГ', 'чередующаяся гласная в корне')
                explain = explain.replace('НГ', 'непроверяемая гласная в корне')
                explain = explain.replace('ПГ', 'проверяемая гласная в корне')
                explains.append(explain != '')
                words_to_arr.append(Word(only_word.strip(), comment.strip(), right_word.strip(), explain.strip()))
                #print(only_word, comment, right_word, explain)
            if not explains[1] and explains[2]:
                words_to_arr[0].explain = words_to_arr[2].explain
                words_to_arr[1].explain = words_to_arr[2].explain
            if not explains[0] and explains[1]:
                words_to_arr[0].explain = words_to_arr[1].explain
            all.extend(words_to_arr)

    for i in range(90):
        if i in [9, 55, 72, 82]:
            continue
        text = open('259.html', 'r').read()
        soup = BeautifulSoup(text, 'html.parser')
        tasks = soup.findAll('div', class_='problem_container')
        t = tasks[i]
        #print(i + 1)
        pb = t.findAll('div', class_='pbody')[1] if i == 0 else t.findAll('div', class_='pbody')[0]
        strs = pb.findAll('p', class_='left_margin')
        sol = t.find('div', class_='solution')
        answers = sol.findAll('p', class_='left_margin')
        if len(strs[1:len(strs)]) > 5:
            continue
        parse_tasks([s.text for s in strs][1:len(strs)], [s.text for s in answers][2:])

    #print(len(all))
    #words = set([w.solution for w in all])
    res = set()
    tmp = []
    for w in all:
        if w.solution in res:
            continue
        res.add(w.solution)
        tmp.append(w)
    f = open('259.json', 'w')
    f.write(json.dumps([asdict(w) for w in tmp], ensure_ascii=False, indent=2))


def write_db():
    data = open('259.json', 'r').read()
    res = json.loads(data, object_hook=lambda dct: Word(dct['word'], dct['comment'], dct['solution'], dct['explain']))
    db.words.write_words(res)

#download_words()
write_db()