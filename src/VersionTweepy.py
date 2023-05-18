import tweepy
import json
import os


def tweepy_collector():

    # Keys
    consumer_key = ""
    consumer_secret = ""
    access_token_key = ""
    access_token_secret = ""

    # Se crea el cliente, para acceder a los metodos de Tweepy
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)
    auth = tweepy.OAuth2AppHandler(consumer_key, consumer_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Palabra clave es la query
    palabra_clave = input("Enter a topic to search, you can use the OR operator > ")

    # Cantidad de tweets
    while True:
        try:
            cantidad_tweets = int(input("Enter the amount of tweets you want to retrive > "))
            break
        except ValueError:
            print('Please, make sure to enter only numbers')


    dic = {}
    indice_auxiliar = 0

    newpath = f"./tweets_{palabra_clave}"
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Busca todos los tweets, con la query como parametro, lenguaje, y la cantidad de registros
    for tweet in tweepy.Cursor(api.search_tweets, q=palabra_clave + " -filter:retweets", lang="es").items(cantidad_tweets):
        # Si es menor a 500, guardo el dato en el dic
        if len(dic) < 5000:
            dic.setdefault(tweet.id, {
                'data': {
                    "text": tweet.text,
                    "fecha_creacion": str(tweet.created_at),
                    "user_name": tweet.user.name
                }
            })
        # Sino Lo guardo en el archivo, vacio el dic, y guardo el dato con el que esta actualmente, para asi generar otro json
        else:
            with open(f'./tweets_{palabra_clave}/{palabra_clave}{f"{indice_auxiliar:02d}"}.json', 'w') as file:
                json.dump(dic, file)
            indice_auxiliar += 1

            dic = {}
            dic.setdefault(tweet.id, {
                'data': {
                    "text": tweet.text,
                    "fecha_creacion": str(tweet.created_at),
                    "user_name": tweet.user.name
                }
            })

    # Guardo lo sobrante, si no llego a 500
    with open(f'./tweets_{palabra_clave}/{palabra_clave}{f"{indice_auxiliar:02d}"}.json', 'w') as file:
        json.dump(dic, file)
