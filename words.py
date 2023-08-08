from db import db

class WordsManager:

    def __init__(self, file_name):
        self.filename = file_name

    def optimize_file(self):
        words = open(self.filename).read()
        words = words.split('\n')
        for i in range(len(words)):
            word = words[i]
            word = word.split(' ')[0]
            word = word.replace(',', '')
            word = word.replace(';', '')
            word = word.replace('Ё', 'Е')
            words[i] = word
        open(self.filename, 'w').write('\n'.join(words))

    def get_words(self):
        file = open(self.filename)
        return file.read().split('\n')

    def write_to_db(self, rewrite: bool):
        db.write_words(self.get_words(), rewrite=rewrite)

wordsManager = WordsManager('words.txt')
#wordsManager.optimize_file()
wordsManager.write_to_db(rewrite=True)