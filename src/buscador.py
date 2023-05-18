
import json
import os
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import itertools
from inverted_index import normalize_date

class Buscador:

    def __init__(self, directorio_indice, directorio_tweets):
        self.directorio_indice = directorio_indice
        self.directorio_tweets = directorio_tweets
        self.dir_postings = f"./{directorio_indice}/postings.json"
        self.dir_tweets_to_ID = f"./{directorio_indice}/diccionario_documentos.json"
        self.dir_terms = f"./{directorio_indice}/terminos.json"
        self.dir_IDs = f"./{directorio_indice}/diccionario_IDs.json"
        self._key_search_words = ["AND", "OR", "NOT", "and", "or", "not"]
        self._stop_words = frozenset(stopwords.words("spanish"))
        self._stemmer = SnowballStemmer("spanish", ignore_stopwords=False)

        self.dict_pal_to_termID = self.__cargar_pal_to_termID()
        self.postings = self.__cargar_postings()
        self.docID_to_doc = self.__cargar_docIDs()

    def buscar(self, query, limite):
        tweetIDs = set()
        queryID = self.__query_toID(query)
        tweetIDs = self.postings[int(queryID[0])]

        if len(queryID) == 1:
            return self.recuperar_tweets(tweetIDs, limite)

        for i in range(1, len(queryID), 2):
            tweetIDs = self.resolver_operacion(
                queryID[i], tweetIDs, int(queryID[i+1]))

        return self.recuperar_tweets(tweetIDs, limite)

    def date_search(self,input_from, input_to):
        value_from = normalize_date(input_from)
        value_to = normalize_date(input_to)

        dates_path = os.path.join(f'./{self.directorio_indice}', 'fechas.json')
        date_posting = os.path.join(f'./{self.directorio_indice}', 'date_postings.json')
        docs = os.path.join(f'./{self.directorio_indice}', 'diccionario_documentos.json')

        with open(dates_path, "r") as dates_file, \
                open(date_posting, "r") as postings_file, \
                open(docs, "r") as docs_file:

            data_retrieved = []
            for d, p in json.load(dates_file).items():
                if value_from <= d and d <= value_to:
                    data_retrieved.append(p)
            
            postings = json.load(postings_file)
            tweets_id = [postings[x] for x in data_retrieved]

            lista = []
            for x in tweets_id:
                lista += x

            return lista
    
    
    def __query_toID(self, query):
        busqueda = query.split()
        for pal in busqueda:
            if pal not in self._key_search_words:
                aux = busqueda.index(pal)
                pal = self._stemmer.stem(pal)
                busqueda[aux] = str(self.dict_pal_to_termID[pal])

        return busqueda

    def recuperar_tweets(self, tweetsIDs, limite):
        tweets_originales = []
        files = os.listdir(self.directorio_tweets)
        for id in itertools.islice(tweetsIDs, limite):

            file = files[(id // 5000)]

            with open(f'{self.directorio_tweets}/{file}', "r") as tweets_disco:
                dic_tweets = json.load(tweets_disco)
                tweets_originales.append(
                    dic_tweets[self.docID_to_doc[str(id)]])
        return tweets_originales

    def __cargar_docIDs(self):
        with open(self.dir_IDs, "r") as file:
            return json.load(file)

    def __cargar_pal_to_termID(self):
        with open(self.dir_terms, "r") as file:
            return json.load(file)

    def __cargar_postings(self):
        with open(self.dir_postings) as f:
            return json.load(f)

    def resolver_operacion(self, operador, tweets_operados, pal2):
        match operador:
            case "and":
                return set(tweets_operados).intersection(self.postings[pal2])
            case "or":
                return set(tweets_operados).union(self.postings[pal2])
            case "and not":
                pass
            

