from os import system, name
import time
import os
from inverted_index import II_BSBI
from buscador import Buscador
from VersionTweepy import tweepy_collector


class Menu:
    def __init__(self):
        self._current_key = "main"
        self._current_solutions = []

        _menu = {
            "main": {
                "title": "Main menu",
                "input_label": "Please, select an option",
                "options": [
                    {
                        "label": "Collect tweets by topic",
                        "method": lambda: self.collect_tweets()
                    },
                    {
                        "label": "Arrange tweets retrieved for search",
                        "method": lambda: self.process_inverted_index()
                    },
                    {
                        "label": "Search tweets",
                        "menu_key": "search"
                    },
                ]
            },
            "search": {
                "title": "Search tweets",
                "input_label": "Please select a search mode",
                "options": [
                    {
                        "label": "Search by query",                      
                        "method": lambda: self.search_through_query(),
                    },
                    {
                        "label": "Search by date range", 
                        "method": lambda: self.search_through_date(),
                    },

                ]
            },

        }

        # Start
        while True:

            current_menu = _menu[self._current_key]

            self.clear()

            self.print_line(current_menu['title'], .2)

            # iterate over options from the current menu selected
            for o, option in enumerate(current_menu['options']):
                print(f'[{o+1}] - {option["label"]}')

            print() # Space
            self.print_line(current_menu['input_label'], .1)

            try:
                choice = int(input('> '))

                if choice == 0:
                    self._current_key = 'main'
                    continue

                # Como se indexan las opciones a traves de i+1, es necesario disminuir choice en 1
                choice = choice-1

                if choice >= len(current_menu['options']) or choice < 0:
                    self.not_found_message(choice)  # TODO Aca hay un error
                else:
                    if (self._current_key == 'main'):
                        if 'menu_key' not in current_menu['options'][choice]:
                            current_menu['options'][choice]['method']()
                        else:
                            self._current_key = current_menu['options'][choice]['menu_key']
                    else:
                        self.clear()

                        self.print_line(
                            current_menu['options'][choice]['label'], .5)
                        # condicionar input label
                        if 'input_label' in current_menu['options'][choice]:
                            self.print_line(
                                current_menu['options'][choice]['input_label'], .2)

                            value = input('> ')
                            current_menu['options'][choice]['method'](value)
                        else:
                            current_menu['options'][choice]['method']()
            except KeyboardInterrupt:
                self.clear()
                self.print_line('Bye bye!')
                break
            except ValueError:
                print('Ingrese una opción válida')
            except Exception as e:
                print(e)
                break
    
    def process_inverted_index(self):
        """
            Procesa los indices invertidos de un tema
        """
        self.clear()
        topic = self.handle_dir_require('proccess',lambda d: d[:7] == 'tweets_' and not os.path.exists(f'./salida_{d[7:]}'))

        if topic:
            topic = topic[7:]
            
            if not os.path.isdir(f"./salida_{topic}"):
                os.mkdir(f"./salida_{topic}")
                
            self.clear()
            II_BSBI(f"./tweets_{topic}",f"./salida_{topic}")

        self._current_key = 'main'
        input("Press any key to return > ")
        
    
    def collect_tweets(self):
        self.clear()
        self.print_line('Collect tweets')
        print()

        try:
            tweepy_collector()

            self.clear()
            self.print_line('Tweets collected')
            self.print_line('Be sure to arrange retrieved tweets for search (Main menu option: 2)')
        except Exception as ex:
            print(ex)

        input("Press any key to return > ")
        self._current_key = 'main'

    def search_through_query(self):
        topic = self.handle_dir_require('search',lambda d: d[:7] == 'salida_')

        if topic:
            topic = topic[7:]
            query = input('Enter a query > ')
            amount = int(input('Amount of tweets to find > '))
            
            buscador = Buscador(f"salida_{topic}", f"tweets_{topic}")
            
            try:
                self.print_tweets(buscador.buscar(query, amount))
            except Exception:
                print()
                print('Upss!')
                self.print_line("We couldn't find anything, please make sure you enter the data correctly")
        

        input("Press any key to return > ")
        self._current_key = 'main'

    def search_through_date(self):
        topic = self.handle_dir_require('search',lambda d: d[:7] == 'salida_')

        if topic:
            topic = topic[7:]
            print()
            self.print_line('make sure you use the format YYYY-MM-DD HH:MM:SS')
            from_date = input('Enter date from > ')
            to_date = input('Enter date to > ')
            amount = int(input('Amount of tweets to find > '))

            try:
                buscador = Buscador(f"salida_{topic}", f"tweets_{topic}")
                date_searcher = buscador.date_search(from_date, to_date)

                data = buscador.recuperar_tweets(date_searcher,amount)
                
                if len(data):
                    while True:
                        r = input('Filter data by user? y/n > ')
                        if r == 'y' or r == 'n':
                            break
                    
                    if r == 'y':
                        user = input('Enter username > ')
                        filtered = [t for t in data if t['data']['user_name'] == user]

                        # Print
                        self.print_tweets(filtered)
                    else:
                        # Print
                        self.print_tweets(data)

            except Exception:
                print()
                print('Upss!')
                self.print_line("We couldn't find anything, please make sure you enter the data correctly")

        input("Press any key to return > ")
        self._current_key = 'main'


    def handle_dir_require(self,label,dir_filter):
        self.clear()
        dirs = [d for d in os.listdir() if os.path.isdir(f'./{d}') and dir_filter(d)]

        if len(dirs):
            self.print_line(f'Topics found to {label}')

            for t,topic in enumerate(dirs): 
                print(f'[{t}] {topic[7:]}')
            
            print()
            choice = input('Please, select a topic by its option number > ')

            return dirs[int(choice)]

        else:
            self.print_line(f'No topics were found to {label}')
            return None

    def print_tweets(self,tweets):
        self.print_line(f'{len(tweets)} tweets obtenidos',1)
        if len(tweets):
            
            for t in tweets:
                tweet = t['data']

                print()
                self.print_line("",.5)
                print(tweet['user_name'], '\t' , tweet['fecha_creacion'][:19])
                print()
                self.print_line(tweet['text'],.25)
                print()

    def clear(self):
        # for windows
        if name == 'nt':
            system('cls')

        # for mac and linux
        else:
            system('clear')

    def not_found_message(self, choice):
        for i in range(4):
            self.clear()
            print(f'La opción {choice+1} no existe{"."*i}')
            time.sleep(.4)

    def print_line(self, data, sleep=.25):
        print(data + "\n")
        time.sleep(sleep)

    def print_continue(self):
        self.print_line("Press any key to continue", .1)

    def set_menu_key(self, key):
        self._current_key = key