import requests


api_url_root = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/'
input_specification = 'compound/'
operation_specification = '294764/'
output_specification = 'JSON'


def download_page(url):
    page = requests.get(url)
    html_string = page.content.decode('utf-8')
    print(html_string)
    with open('data/downloads/' + url.split('/')[-1] + '.html', 'w') as output_file:
        output_file.write(html_string)


# api_url = api_url_root+input_specification+operation_specification+output_specification
download_page('https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/294765/JSON')

# <input specification>/<operation specification>/[<output specification>][?<operation_options>]
