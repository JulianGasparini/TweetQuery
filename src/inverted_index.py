import datetime as dt
import itertools
import re
import demoji
from nltk.stem import SnowballStemmer  
from nltk.corpus import stopwords  
import json
import os
import string
import time


class II_BSBI:
    def __init__(self, documentos, salida, temp="./temp", blocksize=102400, language='spanish'):
        ''' documentos: carpeta con archivos a indexar
            salida: carpeta donde se guardará el índice invertido'''
        self.documentos = documentos
        self.salida = salida
        self._blocksize = blocksize
        self._temp = temp
        self._stop_words = frozenset(
            stopwords.words(language))  
        self._stemmer = SnowballStemmer(language, ignore_stopwords=False)
        self._term_to_termID = {}
        self._date_to_dateID = {}

        self.__generar_docID()
        self.__indexar_palabras()
        self.__indexar_fechas()

    def __generar_docID(self):
        doc_to_docID = {}
        docID_to_doc = {}
        lista_documentos = [os.path.join(self.documentos, nombre_doc)  
                            for nombre_doc in os.listdir(self.documentos)
                            if os.path.isfile(os.path.join(self.documentos, nombre_doc))]

        print("Found collections:")

        for f,file in enumerate(lista_documentos):
            print(f'{f+1}.',file[2:])

        print()
        print("Processing information")

        for i in range(len(lista_documentos)):
            aux = 5000*i
            with open(lista_documentos[i], "r") as file:
                tweets = json.load(file)
                for j, id in enumerate(tweets):
                    doc_to_docID[id] = j+aux
                    docID_to_doc[j+aux] = id
        self._lista_documentos = lista_documentos
        self._doc_to_docID = doc_to_docID
        self._docID_to_doc = docID_to_doc

    def lematizar(self, palabra):
        ''' Usa el stemmer para lematizar o recortar la palabra, previamente elimina todos
        los signos de puntuación que pueden aparecer. El stemmer utilizado también se
        encarga de eliminar acentos y pasar todo a minúscula, sino habría que hacerlo
        a mano'''

        
        palabra = palabra.strip(string.punctuation + "»" + "\x97" + "¿" + "¡" + "\u201c" +
                                "\u201d" + "\u2014" + "\u2014l" + "\u00bf")
        

        palabra_lematizada = self._stemmer.stem(palabra)
        return palabra_lematizada

    def __indexar_palabras(self):
        n = 0
        lista_bloques = []

        for bloque in self.__parse_next_words_block():
            bloque_invertido = self.__invertir_bloque(bloque)
            lista_bloques.append(
                self.__guardar_bloque_intermedio(bloque_invertido, n))
            n += 1
        start = time.process_time()
        self.__intercalar_bloques(lista_bloques)
        end = time.process_time()
        print("Intercalar Bloques Elapsed time: ", end-start)

        self.__guardar_diccionario('terminos', self._term_to_termID)
        self.__guardar_diccionario_documentos()
        self.__guardar_diccionario_IDs()

    def __indexar_fechas(self):
        n = 0
        lista_bloques = []

        for bloque in self.__parse_next_dates_block():
            bloque_invertido = self.__invertir_bloque(bloque)
            lista_bloques.append(
                self.__guardar_bloque_intermedio(bloque_invertido, n))
            n += 1
        start = time.process_time()
        self.__intercalar_bloques(lista_bloques)
        end = time.process_time()
        print("Intercalar Bloques Elapsed time: ", end-start)

        self.__guardar_diccionario('fechas', self._date_to_dateID)

    def __invertir_bloque(self, bloque):
        bloque_invertido = {}
        bloque_ordenado = sorted(
            bloque, key=lambda tupla: (tupla[0], tupla[1]))
        for par in bloque_ordenado:
            posting = bloque_invertido.setdefault(par[0], set())
            posting.add(par[1])
        return bloque_invertido

    def __guardar_bloque_intermedio(self, bloque, nro_bloque):
        archivo_salida = "b"+str(nro_bloque)+".json"
        archivo_salida = os.path.join(self._temp, archivo_salida)
        for clave in bloque:
            bloque[clave] = list(bloque[clave])
        with open(archivo_salida, "w") as contenedor:
            json.dump(bloque, contenedor)
        return archivo_salida

    def __intercalar_bloques(self, temp_files):

        lista_termID = [str(i) for i in range(len(self._term_to_termID))]
        lista_dateID = [str(i) for i in range(len(self._date_to_dateID))]

        posting_file = os.path.join(self.salida, "postings.json")
        date_posting_file = os.path.join(self.salida, "date_postings.json")

        open_files = [open(f, "r") for f in temp_files]

        postings = []
        with open(posting_file, "w") as salida:
            for termID in lista_termID:
                posting = set()
                for data in open_files:
                    data.seek(0)
                    bloque = json.load(data)
                    try:
                        posting = posting.union(set(bloque[termID]))
                        print(posting)
                    except:
                        pass

                postings.append(list(posting))

            json.dump(postings, posting_file)

        postings = []
        with open(date_posting_file, "w") as salida:
            for dateID in lista_dateID:
                posting = set()
                for data in open_files:
                    data.seek(0)
                    bloque = json.load(data)
                    try:
                        posting = posting.union(set(bloque[dateID]))
                    except:
                        pass
                postings.append(list(posting))
            json.dump(postings, date_posting_file)

    def __guardar_diccionario(self, filename, dicc):
        path = os.path.join(self.salida, f'{filename}.json')
        with open(path, "w") as contenedor:
            json.dump(dicc, contenedor)

    def __guardar_diccionario_documentos(self):
        path = os.path.join(self.salida, "diccionario_documentos.json")
        with open(path, "w") as contenedor:
            json.dump(self._doc_to_docID, contenedor)

    def __guardar_diccionario_IDs(self):
        path = os.path.join(self.salida, "diccionario_IDs.json")
        with open(path, "w") as contenedor:
            json.dump(self._docID_to_doc, contenedor)

    def __parse_next_words_block(self):
        n = self._blocksize 

        termID = 0  

        bloque = [] 
        for i in range(len(self._lista_documentos)):
            with open(self._lista_documentos[i]) as file:
                tweets = dict(json.load(file))
                for dato in tweets:
                    cuerpo_tweet = normalize(tweets[dato]["data"]["text"])
                    n -= len(cuerpo_tweet.encode('utf-8'))

                    palabras = cuerpo_tweet.split()

                    doc = dato
                    for pal in palabras:
                        if pal not in self._stop_words:
                            pal = self.lematizar(pal)
                            if pal not in self._term_to_termID:
                                self._term_to_termID[pal] = termID
                                termID += 1
                            bloque.append(
                                (self._term_to_termID[pal], self._doc_to_docID[doc]))
                    if n <= 0:
                        yield bloque
                        n = self._blocksize
                        bloque = []
                yield bloque

    def __parse_next_dates_block(self):
        n = self._blocksize 

        dateID = 0

        bloque = []
        for i in range(len(self._lista_documentos)):
            with open(self._lista_documentos[i]) as file:
                tweets = dict(json.load(file))
                for dato in tweets:
                    tweet_date = normalize_date(
                        tweets[dato]["data"]["fecha_creacion"])

                    n -= len(tweet_date.encode('utf-8'))
                    
                    if tweet_date not in self._date_to_dateID:
                        self._date_to_dateID[tweet_date] = dateID
                        dateID += 1

                    bloque.append(
                        (self._date_to_dateID[tweet_date], self._doc_to_docID[dato]))

                if n <= 0:
                    yield bloque
                    n = self._blocksize
                    bloque = []
        yield bloque


def normalize(text):
    '''
    @returns texto sin emojis y links
    '''
    result = re.sub(r'https:+[^\s]+[\w]', '', text)
    result = demoji.replace(result, '')
    return result


def normalize_date(tweet_date):
    return str(int(dt.datetime.strptime(tweet_date[:19], "%Y-%m-%d %H:%M:%S").timestamp()))

if __name__ == '__main__':
    II_BSBI("./tweets_mundial2", "./salida_mundial2")