from project import HTMLParser
import requests
from threading import Thread
from time import sleep
import json
import os


DATA_LOCATION = '/media/dwout/75F9-FA9C/1617-12-Data-Mining/project/data/'


def wikipedia_html_files():
    for filename in os.listdir('data/downloads'):
        yield 'data/downloads/'+filename


class WikipediaPage(HTMLParser.HTMLPage):
    def get_info_table(self):
        for table in self.get_elements('table'):
            is_info_table = True
            for tag_name in ['Identifiers', 'Properties']:
                if tag_name not in str(table):
                    is_info_table = False
            if is_info_table:
                return table


class WikipediaParser:
    def __init__(self):
        self.terminate = False

        self.data_filename = DATA_LOCATION+'database_raw02.json'
        self.urls_done_filename = DATA_LOCATION+'tested_urls'
        self.urls_to_do_filename = DATA_LOCATION+'waitlist_urls'

        self.urls_done = set()
        self.urls_to_do = set()
        self.data = dict()  # dict with molecules as keys. Molecule values are also dicts, with properties from the
        # wikipedia info table as keys.
        self.downloaded_files = set()

        self.load_data()

    def load_data(self):
        with open(self.urls_done_filename) as file:
            for line in file:
                self.urls_done.add(line.strip())
        with open(self.urls_to_do_filename) as file:
            for line in file:
                self.urls_to_do.add(line.strip())
        with open(self.data_filename) as json_file:
            self.data = json.loads(json_file.read())
        for filename in wikipedia_html_files():
            self.downloaded_files.add(filename.rsplit('.', 1)[0])
        print('number of molecules: ' + str(len(self.data)))
        print('length of wait-list: ' + str(len(self.urls_to_do)))
        print('length of tested urls: ' + str(len(self.urls_done)))

    def save_data(self):
        with open(self.urls_done_filename, 'w') as file:
            file_string = ''
            for url in self.urls_done.copy():
                file_string += url + '\n'
            file.write(file_string)
        with open(self.urls_to_do_filename, 'w') as file:
            file_string = ''
            for url in self.urls_to_do.copy():
                file_string += url + '\n'
            file.write(file_string)
        with open(self.data_filename, 'w') as json_file:
            json_file.write(json.dumps(self.data, separators=(',', ':'), sort_keys=True, indent=4))
        print('number of molecules: ' + str(len(self.data)))
        print('length of waitlist: ' + str(len(self.urls_to_do)))
        print('length of tested urls: ' + str(len(self.urls_done)))

    @staticmethod
    def get_initial_urls():
        initial_urls_filename = 'data/initial_urls'

        wiki_domain = 'https://en.wikipedia.org'
        data_urls = ['/wiki/Dictionary_of_chemical_formulas',
                     '/wiki/List_of_biomolecules',
                     '/wiki/List_of_inorganic_compounds']

        initial_urls = set()
        for data_url in data_urls:
            page = WikipediaPage(url=wiki_domain+data_url)
            for link in page.get_links():
                if link[:5] == '/wiki':
                    link = link.rsplit('#', 1)[0]
                    initial_urls.add(wiki_domain+link)
        with open(initial_urls_filename, 'w') as output_file:
            for url in initial_urls:
                output_file.write(url + '\n')

    @staticmethod
    def parse_info_table(info_table):
        for row in info_table:
            key = None
            value = None
            row.remove('sup')
            if len(row) == 2:
                key = str(row[0])
                try:
                    list_element = row[1].get_elements('ul')
                except AttributeError:
                    continue
                if list_element:
                    value = list()
                    for item in list_element[0]:
                        value.append(str(item))
                else:
                    value = str(row[1])
            elif len(row) == 1:
                list_element = row.get_elements('ul')
                if list_element:
                    value = list()
                    for item in list_element[0]:
                        value.append(str(item))
                    key = str(row).replace(str(list_element[0]), '')
            if key and value:
                yield key, value

    def page_parser_thread(self):
        while not self.terminate:
            current_url = self.urls_to_do.pop()
            if current_url in self.urls_done:
                continue
            self.urls_done.add(current_url)

            molecule_name = current_url.split('/')[-1]
            try:
                if molecule_name in self.downloaded_files:
                    with open('data/downloads/' + molecule_name + '.html') as file:
                        page_string = file.read()
                else:
                    try:
                        page_string = requests.get(current_url).content.decode('utf-8')
                    except requests.exceptions.ConnectionError as e:
                        print(e)
                        self.urls_done.remove(current_url)
                        self.urls_to_do.add(current_url)
                        continue
                page = WikipediaPage(html_string=page_string)
            except ValueError:
                continue

            info_table = page.get_info_table()
            if info_table:
                table_data = dict()
                for key, value in self.parse_info_table(info_table):
                    table_data[key] = value
                self.data[molecule_name] = table_data
                if not os.path.exists('data/' + molecule_name + '.html'):
                    with open('data/downloads/' + molecule_name + '.html', 'w') as file:
                        file.write(page_string)
                wiki_domain = 'https://en.wikipedia.org'
                for link in page.get_links():
                    if link[:5] == '/wiki':
                        if wiki_domain + link not in self.urls_done:
                            self.urls_to_do.add(wiki_domain+link)
                print(current_url.split('/')[-1] + ' parsed to database.')

    def save_data_thread(self):
        while not self.terminate:
            sleep(5)
            self.save_data()
            for filename in os.listdir('data/downloads'):
                self.downloaded_files.add(filename.rsplit('.', 1)[0])

    def input_thread(self):
        while not self.terminate:
            inp = input('Enter command: ')
            if inp.lower() in ['quit', 'q']:
                self.terminate = True

    def run(self):
        t_data = Thread(target=self.save_data_thread)
        t_data.start()
        t_input = Thread(target=self.input_thread)
        t_input.start()
        t_parsers = list()
        for _ in range(40):
            t_parser = Thread(target=self.page_parser_thread)
            t_parser.start()
            t_parsers.append(t_parser)

        t_data.join()
        t_input.join()
        for t in t_parsers:
            t.join()


def get_urls_from_tables(attribute):
    for filename in wikipedia_html_files():
        wiki_page = WikipediaPage(filename=filename)
        info_table = wiki_page.get_info_table()
        for row in info_table:
            urls = list()
            row.remove('sup')
            if len(row) == 2:
                if str(row[0]).lower() == attribute:
                    a_list = row[1].get_elements(name='a')
                    for a in a_list:
                        if 'href' in a.attributes:
                            urls.append(a.attributes['href'])
                    print(filename, urls)
                    continue


def download_page(url):
    page = requests.get(url)
    html_string = page.content.decode('utf-8')
    with open('data/downloads/' + url.split('/')[-1] + '.html', 'w') as output_file:
        output_file.write(html_string)


def rename_database():
    for filename in os.listdir('data/downloads'):
        pass
        # todo


# wikiparser = WikipediaParser()
# wikiparser.run()
get_urls_from_tables('chemspider')
get_urls_from_tables('pubchem')
