from project import DataCollecting  #, Preprocessing
import shutil


if __name__ == '__main__':
    def do_nothing():
        # Collect wikipedia URLs for initializing the data collecting process.
        # The URLs are stored in "data/wikipedia/initial_urls.csv":
        wikipedia_urls = ['/wiki/Dictionary_of_chemical_formulas',
                          '/wiki/List_of_biomolecules',
                          '/wiki/List_of_inorganic_compounds']
        DataCollecting.collect_initial_urls(wikipedia_urls)
    
        # After the initial urls are collected they are transferred to "data/wikipedia/waitlist_urls.csv":
        shutil.copyfile(DataCollecting.FN_WIKI_URLS_INITIAL, DataCollecting.FN_WIKI_URLS_TO_DO)
    
        # Start the wikipedia data collecting process. The collected data is stored 
        # in "data/wikipedia/database_raw.json". The HTML files are stored in "data/wikipedia/html_pages".
        wikiparser = DataCollecting.WikipediaParser()
        wikiparser.run()
    
        # Collect PubChem urls from wikipedia HTML database. Urls are stored in "data/pubchem/urls.csv":
        DataCollecting.collect_pubchem_urls()
    
        pubchem_id_data = DataCollecting.get_pubchem_ids_from_file()
        pubchem_ids = list()
        for ids in pubchem_id_data.values():
            pubchem_ids.extend(ids)
        DataCollecting.collect_pubchem_data(pubchem_ids)
