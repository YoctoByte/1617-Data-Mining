import json
import requests


PUBCHEM_ROOT_DIR = 'data/pubchem/'


class PubChemPage:
    def __init__(self, pubchem_id):
        self.pubchem_id = str(pubchem_id)
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/' + self.pubchem_id + '/JSON'
        json_request = requests.get(url)
        self.json_string = json_request.content.decode('utf-8')
        with open(PUBCHEM_ROOT_DIR+'json_raw/'+self.pubchem_id+'.json', 'w') as json_file:
            json_file.write(self.json_string)
        self.json_data = json.loads(self.json_string)
        self.data, self.descriptions = self._to_dict()

    def _to_dict(self):
        data = dict()
        descriptions = dict()
        record = self.json_data['Record']
        main_section = record['Section']

        def extract_values(section):
            for item in section:
                if 'Section' in item:
                    extract_values(item['Section'])
                elif 'Information' in item:
                    heading, information = item['TOCHeading'], item['Information']
                    try:
                        description = item['Description']
                    except KeyError:
                        description = None
                    data[heading] = information
                    descriptions[heading] = description

        extract_values(main_section)

        return data, descriptions

    def iupac_name(self):
        try:
            return self.data['IUPAC Name'][0]['StringValue']
        except KeyError:
            return ''

    def save(self, file_path=''):
        filename = self.iupac_name()
        if not filename:
            filename = self.pubchem_id

        if not file_path:
            file_path = PUBCHEM_ROOT_DIR+'json_stage_1/'+filename+'.json'
        try:
            with open(file_path, 'w') as json_file:
                json_file.write(json.dumps(self.data, separators=(',', ':'), sort_keys=True, indent=4))
        except OSError:
            with open(PUBCHEM_ROOT_DIR+'json_stage_1/'+self.pubchem_id+'.json', 'w') as json_file:
                json_file.write(json.dumps(self.data, separators=(',', ':'), sort_keys=True, indent=4))

    def __iter__(self):
        for attr, val in self.data.items():
            yield attr, val
