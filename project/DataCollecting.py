from project import HTMLParser, PubChemAPI
import requests
from threading import Thread
from time import sleep
import json
import os


DATA_ROOT = '/media/dwout/75F9-FA9C/1617-12-Data-Mining/project/data/'

DIR_WIKI_ROOT = DATA_ROOT+'wikipedia/'
DIR_WIKI_PAGES = DIR_WIKI_ROOT+'html_pages/'
FN_WIKI_DATABASE_RAW = DIR_WIKI_ROOT+'database_raw.json'
FN_WIKI_URLS_INITIAL = DIR_WIKI_ROOT+'initial_urls.csv'
FN_WIKI_URLS_DONE = DIR_WIKI_ROOT+'tested_urls.csv'
FN_WIKI_URLS_TO_DO = DIR_WIKI_ROOT+'waitlist_urls.csv'

DIR_PUBCHEM_ROOT = DATA_ROOT+'pubchem'


class WikipediaPage(HTMLParser.HTMLPage):
    """
    inherits functions from HTMLPage and adds function to get info table from a wikipedia molecule page.
    """
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

        self.urls_done = set()
        self.urls_to_do = set()
        self.data = dict()  # dict with molecules as keys. Molecule values are also dicts, with properties from the
        # wikipedia info table as keys.
        self.downloaded_files = set()

        self._load_data()

    def _load_data(self):
        with open(FN_WIKI_URLS_DONE) as file:
            for line in file:
                self.urls_done.add(line.strip())
        with open(FN_WIKI_URLS_TO_DO) as file:
            for line in file:
                self.urls_to_do.add(line.strip())
        with open(FN_WIKI_DATABASE_RAW) as json_file:
            self.data = json.loads(json_file.read())
        for filename in os.listdir(DIR_WIKI_PAGES):
            self.downloaded_files.add(filename.rsplit('.', 1)[0])
        print('number of molecules: ' + str(len(self.data)))
        print('length of wait-list: ' + str(len(self.urls_to_do)))
        print('length of tested urls: ' + str(len(self.urls_done)))

    def _save_data(self):
        with open(FN_WIKI_URLS_DONE, 'w') as file:
            file_string = ''
            for url in self.urls_done.copy():
                file_string += url + '\n'
            file.write(file_string)
        with open(FN_WIKI_URLS_TO_DO, 'w') as file:
            file_string = ''
            for url in self.urls_to_do.copy():
                file_string += url + '\n'
            file.write(file_string)
        with open(FN_WIKI_DATABASE_RAW, 'w') as json_file:
            json_file.write(json.dumps(self.data, separators=(',', ':'), sort_keys=True, indent=4))
        print('number of molecules: ' + str(len(self.data)))
        print('length of waitlist: ' + str(len(self.urls_to_do)))
        print('length of tested urls: ' + str(len(self.urls_done)))

    @staticmethod
    def _parse_info_table(info_table):
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

    def _page_parser_thread(self):
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
                for key, value in self._parse_info_table(info_table):
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

    def _save_data_thread(self):
        while not self.terminate:
            sleep(5)
            self._save_data()
            for filename in os.listdir('data/downloads'):
                self.downloaded_files.add(filename.rsplit('.', 1)[0])

    def _input_thread(self):
        while not self.terminate:
            inp = input('Enter command: ')
            if inp.lower() in ['quit', 'q']:
                self.terminate = True

    def run(self):
        t_data = Thread(target=self._save_data_thread)
        t_data.start()
        t_input = Thread(target=self._input_thread)
        t_input.start()
        t_parsers = list()
        for _ in range(40):
            t_parser = Thread(target=self._page_parser_thread)
            t_parser.start()
            t_parsers.append(t_parser)

        t_data.join()
        t_input.join()
        for t in t_parsers:
            t.join()


def collect_initial_urls(wikipedia_urls):
    wiki_domain = 'https://en.wikipedia.org'

    initial_urls = set()
    for data_url in wikipedia_urls:
        page = WikipediaPage(url=wiki_domain+data_url)
        for link in page.get_links():
            if link[:5] == '/wiki':
                link = link.split('#', 1)[0]
                initial_urls.add(wiki_domain+link)
    with open(FN_WIKI_URLS_INITIAL, 'w') as output_file:
        for url in initial_urls:
            output_file.write(url + '\n')


def get_urls_from_tables(attribute):
    for filename in os.listdir(DIR_WIKI_PAGES):
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
                    yield filename.rsplit('/', 1)[-1][0:-5], urls
                    continue


def collect_chemspider_urls():
    with open(DATA_ROOT+'chemspider/urls.csv', 'w') as file:
        for molecule, urls in get_urls_from_tables('chemspider'):
            molecule_string = molecule.replace(',', '')
            for url in urls:
                molecule_string += ', ' + url.replace(',', '')
            file.write(molecule_string+'\n')
            print(molecule_string)


def collect_pubchem_urls():
    with open(DATA_ROOT+'pubchem/urls.csv', 'w') as file:
        for molecule, urls in get_urls_from_tables('pubchem'):
            molecule_string = molecule.replace(',', '')
            for url in urls:
                molecule_string += ', ' + url.replace(',', '')
            file.write(molecule_string+'\n')
            print(molecule_string)


def collect_pubchem_data(pubchem_id_list):
    def collecting_thread():
        while True:
            try:
                pubchem_id = pubchem_id_list.pop()
            except IndexError:
                break

            try:
                pubchem_data_obj = PubChemAPI.PubChemPage(pubchem_id)
                print(pubchem_data_obj.iupac_name())
                pubchem_data_obj.save()
            except (KeyError, UnicodeDecodeError):
                print(pubchem_id + ' DATA NOT COLLECTED!')

    collectors = list()
    for _ in range(10):
        thread = Thread(target=collecting_thread)
        thread.start()
        collectors.append(thread)

    for t in collectors:
        t.join()


def download_page(url):
    page = requests.get(url)
    html_string = page.content.decode('utf-8')
    with open('data/downloads/'+url, 'w') as output_file:
        output_file.write(html_string)


if __name__ == '__main__':
    # wikiparser = WikipediaParser()
    # wikiparser.run()
    # get_urls_from_tables('pubchem')
    # get_pubchem_urls()
    # download_page('https://pubchem.ncbi.nlm.nih.gov/compound/294764')
    pass
