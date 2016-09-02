import requests

non_closing_tag_names = ['area', 'base', 'br', 'col', 'command',
                         'embed', 'hr', 'img', 'input', 'link',
                         'meta', 'param', 'source', 'wbr', 'keygen',
                         'track', 'button']

# \u00b7 : multiplication dot
# \u200b : nothing (?)
# \u2212 : minus sign
# \u00b0 : degrees sign
# \u00b1 : plusminus sign
# \u2013 : longer minus sign


class HTMLElement:
    def __init__(self, name='', attributes=None, content=None):
        self.name = name
        self.attributes = dict()
        self.content = list()
        if attributes:
            self.attributes = attributes
        if content:
            self.content = content

    def add(self, content, depth):
        if depth < 0:
            raise ValueError('depth too high')
        if depth == 0:
            if isinstance(content, HTMLElement) or isinstance(content, str):
                self.content.append(content)
            else:
                raise ValueError('Added content should be one of the following types: string, Element.')
        else:
            for item in reversed(self.content):
                if isinstance(item, HTMLElement):
                    item.add(content, depth-1)
                    break

    def get_elements(self, name, recursive=True):
        elements = list()
        for content in (item for item in self.content if isinstance(item, HTMLElement)):
            if content.name == name:
                elements.append(content)
            if recursive:
                elements.extend(content.get_elements(name))
        return elements

    def remove(self, name=None, attribute=None, recursive=True):
        if not name and not attribute:
            return

        # The function that checks whether or not the attribute is in the content item:
        def attr_match(cont_attrs):
            if not attribute:
                return True
            if not cont_attrs:
                return False
            try:
                key, value = attribute[0], attribute[1]
            except IndexError:
                raise ValueError('attributes should be a pair (tuple, list, .. ).')
            if key == '*' and value == '*':
                return True
            if key == '*':
                for k in cont_attrs:
                    if cont_attrs[k] == value:
                        return True
                return False
            else:
                if key in cont_attrs and value == '*':
                    return True
                elif key in cont_attrs:
                    if cont_attrs[key] == value:
                        return True
                    else:
                        return False
                else:
                    return False

        for i, content in enumerate(self.content):
            if isinstance(content, HTMLElement):
                if (content.name == name or not name) and attr_match(content.attributes):
                    del self.content[i]
                    continue
                if recursive:
                    content.remove(name=name, attribute=attribute, recursive=recursive)

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        for item in self.content:
            yield item

    def __getitem__(self, index):
        return self.content[index]

    def __str__(self):
        text = ''
        if self.name == 'br':
            text = '\n' + text
        if self.name in ['head']:
            return text
        if 'style' in self.attributes and 'display:none' in self.attributes['style']:
            return text
        for content in self.content:
            text += str(content)
        return text

    def to_html(self):
        def indent(string):
            new_string = ''
            for line in (line for line in string.split('\n') if line):
                line = '    ' + line + '\n'
                new_string += line
            return new_string

        attr_string = ''
        for attr in self.attributes:
            attr_string += ' ' + attr + '="' + self.attributes[attr] + '"'

        content_string = ''
        for item in self:
            if isinstance(item, str):
                content_string += item + '\n'
            else:
                content_string += item.to_html()
        content_string = indent(content_string)

        end_tag = ''
        if self.name not in non_closing_tag_names:
            end_tag = '</' + self.name + '>\n'

        return '<' + self.name + attr_string + '>\n' + content_string + end_tag

    def copy(self):
        element_copy = HTMLElement()
        for item in self.content:
            if not isinstance(item, str):
                element_copy.content.append(item.copy())
            else:
                element_copy.content.append(item)
        return element_copy

    def get_links(self):
        links = list()
        for link in self.get_elements('a'):
            if 'href' in link.attributes:
                links.append(link.attributes['href'])
        return links


class HTMLPage(HTMLElement):
    def __init__(self, filename=None, url=None, html_string=None):
        HTMLElement.__init__(self)
        if html_string:
            self.parse_from_string(html_string)
        elif filename:
            self.parse_from_file(filename)
        elif url:
            self.parse_from_url(url)

    def parse_from_url(self, url):
        page = requests.get(url)
        html_string = page.content.decode('utf-8')
        self.parse_from_string(html_string)

    def parse_from_file(self, filename):
        with open(filename, 'r') as file:
            html_string = file.read()
            file.close()
        self.parse_from_string(html_string)

    def parse_from_string(self, html_string):
        depth = 0
        for token in self.tokenize(html_string):
            if token[0] == '<':  # Token is a tag or comment
                if token[1] == '!':  # Token is a comment
                    continue
                elif token[1] == '/':  # Token is an end-tag
                    if token[2:-1] not in non_closing_tag_names:
                        depth -= 1
                else:  # Token is a start-tag
                    element = self.parse_tag_token(token)
                    self.add(element, depth)
                    if element.name not in non_closing_tag_names:
                        depth += 1
            else:  # Token is text
                self.add(token, depth)

    @staticmethod
    def tokenize(html_string):
        """
        :param html_string: The HTML string to be tokenized.
        :return: Yield tag tokens and plain text tokens until end of string. Yielded tag tokens do include the brackets
        """

        # Compress the string to a single line:
        new_string = ''
        for line in html_string.split('\n'):
            new_string += line.strip()
        html_string = new_string

        # Start yielding tokens:
        pos_left = html_string.find('<')
        text_token = html_string[0:pos_left]
        if text_token:
            yield text_token.replace('&#160;', ' ').replace('&#160', ' ')
        while True:
            pos_right = html_string.find('>', pos_left)
            tag_token = html_string[pos_left:pos_right+1]
            yield tag_token
            if pos_right == -1:
                raise ValueError('Error during tokenizing of the html string.')
            pos_left = html_string.find('<', pos_right)
            if pos_left == -1:  # If end of string
                text_token = html_string[pos_right+1:]
                if text_token:
                    yield text_token.replace('&#160;', ' ').replace('&#160', ' ')
                break
            text_token = html_string[pos_right+1:pos_left]
            if text_token:
                yield text_token.replace('&#160;', ' ').replace('&#160', ' ')

    @staticmethod
    def parse_tag_token(tag_token):
        # tokenize the token even further:
        tag_token = tag_token.lstrip('<').rstrip('>')
        attribute_strings = tag_token.split(' ')
        tag_name = attribute_strings.pop(0)

        # Parse the attributes of the tag:
        attributes_dict = dict()
        for attribute in attribute_strings:
            if attribute in ['/']:
                continue
            try:
                key, value = attribute.split('=', 1)
            except ValueError:
                key, value = attribute, ''
            attributes_dict[key] = value.strip('"')
        return HTMLElement(name=tag_name, attributes=attributes_dict)
