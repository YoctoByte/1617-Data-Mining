from project import DataCollecting  #, Preprocessing
import shutil


def get_pubchem_ids_from_file():
    with open('data/pubchem/urls.csv') as file:
        data = dict()
        for line in file:
            urls = line.strip().split(',')
            molecule = urls.pop(0)
            data[molecule] = list()
            for url in urls:
                pubchem_id = url.rsplit('/', 1)[-1]
                if pubchem_id.isnumeric():
                    data[molecule].append(pubchem_id)
        return data


if __name__ == '__main__':
    # Collect wikipedia URLs for initializing the data collecting process.
    # The URLs are stored in "data/wikipedia/initial_urls.csv":
    # wikipedia_urls = ['/wiki/Dictionary_of_chemical_formulas',
    #                   '/wiki/List_of_biomolecules',
    #                   '/wiki/List_of_inorganic_compounds']
    # DataCollecting.collect_initial_urls(wikipedia_urls)

    # After the initial urls are collected they are transferred to "data/wikipedia/waitlist_urls.csv" :
    # shutil.copyfile(DataCollecting.FN_WIKI_URLS_INITIAL, DataCollecting.FN_WIKI_URLS_TO_DO)

    # Start the wikipedia data collecting process:
    #

    # collect data from pubchem:
    pubchem_id_data = get_pubchem_ids_from_file()
    pubchem_ids = list()
    for ids in pubchem_id_data.values():
        pubchem_ids.extend(ids)
    DataCollecting.collect_pubchem_data(pubchem_ids)
