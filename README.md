
## Sobre el proyecto
Este proyecto permite obtener grandes cantidades de información proveniente de la red social Twitter por medio de sus APIS, dicha información será procesada mediante técnicas utilizadas en el libro "Introduction to Information Retrieval"

## Instalación
Para poder correr el código, es necesario instalar los siguientes paquetes [demoji](hhttps://pypi.org/project/demoji/), [ntlk](https://www.nltk.org/), [tweepy](https://www.tweepy.org/)

    > pip install demoji
    > prip install ntlk
    > pip install tweepy

## Ejecutar
Es necesario entrar en el directorio _src_ :

    > cd src
    > python main.py

## Almacenamiento de la información
Al utilizar el __collector__ de tweets, este requiere un tema o tópico a buscar, esta será la _query_ para encontrar tweets. Los tweets se almacenan en bloques de 5000 en archivos de tipo _.json_, estos archivos se almacenan en un directorio destinado para cada tema, precedido por la palabra _"tweets_"_. Una vez estructurada la información, luego de procesarla mediante el objeto II_BSBI, los indices obtenidos se almacenan en un nuevo directorio precedido por el string _"salida_"_. Además se utiliza el directorio temp para almacenar los bloques.

Por ejemplo si el tema buscado es "maradona", se generaran los siguientes directorios:

    /src
        /tweets_maradona
            maradona0.json
            maradona00.json
            maradona01.json
            ...

        /salida_maradona
            date_postings.json
            diccionario_documentos.json
            diccionario_IDs.json
            fechas.json
            postings.json
            terminos.json

        /temp
            b0.json
            b1.json
            ...


