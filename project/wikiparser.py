from project import htmlparser
import requests
from threading import Thread
from time import sleep
import json


TESTED_URLS = set()
WAITLIST_URLS = set()
TERMINATE = False


def get_initial_urls():
    wiki_domain = 'https://en.wikipedia.org'
    data_urls = ['/wiki/Dictionary_of_chemical_formulas',
                 '/wiki/List_of_biomolecules',
                 '/wiki/List_of_inorganic_compounds']

    initial_urls = set()
    for data_url in data_urls:
        page = htmlparser.parse_from_url(wiki_domain + data_url)
        for link in page.get_elements('a'):
            try:
                wiki_link = link.attributes['href']
                if wiki_link[:5] == '/wiki':
                    initial_urls.add(wiki_domain + wiki_link)
                    print(wiki_domain + wiki_link)
            except KeyError:
                pass
    with open('data/initial_urls', 'w') as output_file:
        for url in initial_urls:
            output_file.write(url + '\n')


def get_info_table(page):
    for table in page.get_elements('table'):
        is_info_table = True
        for tag_name in ['Names', 'Identifiers', 'Properties']:  # todo: exclude Names
            if tag_name not in table.to_text():
                is_info_table = False
        if is_info_table:
            return table


def parse_info_table(info_table):
    # todo: parse single line values (i.e.: SMILES)
    for row in info_table:
        try:
            row.remove('sup')
            key = row[0].to_text()
            # todo: parse list values
            value = row[1].to_text()
            yield key, value
        except IndexError:
            pass


def download_page(url):
    page = requests.get(url)
    html_string = page.content.decode('utf-8')
    with open('data/downloads/' + url.split('/')[-1] + '.html', 'w') as output_file:
        output_file.write(html_string)


def load_data():
    with open('data/tested_urls') as file:
        for line in file:
            TESTED_URLS.add(line.strip())
    with open('data/waitlist_urls') as file:
        for line in file:
            if line.strip() not in TESTED_URLS:
                WAITLIST_URLS.add(line.strip())


def page_parser_thread():
    while not TERMINATE:
        current_url = WAITLIST_URLS.pop()
        if current_url in TESTED_URLS:
            continue
        TESTED_URLS.add(current_url)
        try:
            page = htmlparser.parse_from_url(current_url)
        except ValueError:
            continue
        info_table = get_info_table(page)
        if info_table:
            table_data = dict()
            for key, value in parse_info_table(info_table):
                table_data[key] = value
            with open('data/wiki_data_tables/' + current_url.split('/')[-1] + '.json', 'w') as json_file:
                json_file.write(json.dumps(table_data, separators=(',', ':'), sort_keys=True, indent=4))

            wiki_domain = 'https://en.wikipedia.org'
            for link in page.get_elements('a'):
                try:
                    wiki_link = link.attributes['href']
                    if wiki_link[:5] == '/wiki':
                        if wiki_domain + wiki_link not in TESTED_URLS:
                            WAITLIST_URLS.add(wiki_domain + wiki_link)
                except KeyError:
                    pass
            print(current_url.split('/')[-1] + ' parsed to json.')


def file_update_thread():
    while not TERMINATE:
        sleep(5)
        with open('data/tested_urls', 'w') as file:
            file_string = ''
            for url in TESTED_URLS.copy():
                file_string += url + '\n'
            file.write(file_string)
        with open('data/waitlist_urls', 'w') as file:
            file_string = ''
            for url in WAITLIST_URLS.copy():
                file_string += url + '\n'
            file.write(file_string)


def input_thread():
    global TERMINATE
    while not TERMINATE:
        inp = input('Enter command: ')
        if inp.lower() in ['quit', 'q']:
            TERMINATE = True


def run():
    load_data()
    Thread(target=file_update_thread).start()
    Thread(target=input_thread).start()
    for _ in range(15):
        Thread(target=page_parser_thread).start()


# download_page('https://en.wikipedia.org/wiki/Adenosine_triphosphate')
# page = htmlparser.parse_from_file('data/downloads/Methane.html')
# info_table = get_info_table(page)
# parse_info_table(info_table)
# get_initial_urls()
# run()
