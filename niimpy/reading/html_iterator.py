import re


def strip_html_tags(text):
    text = text.replace('<br>', '\n')
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    text = re.sub(r'[^\S\n]+', ' ', text).strip()
    return text


class ContentDivIterator:
    def __init__(self, html):
        self.html = html
        self.pos = 0
        self.div_level = 0
        self.start_div_level = None
        self.start_position = None

        self.div_start_pattern = re.compile(r'<div[^>]*>') 
        self.div_end_pattern = re.compile(r'</div>')

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.pos >= len(self.html):
            raise StopIteration
        
        while self.pos < len(self.html):
            start_match = self.div_start_pattern.search(self.html, self.pos)
            end_match = self.div_end_pattern.search(self.html, self.pos)

            if not start_match or not end_match:
                raise StopIteration
        
            if start_match and start_match.start() < end_match.start():
                match_string = self.html[start_match.start():start_match.end()]
                if "content-cell" in match_string:
                    self.start_position = start_match.start()
                    self.start_div_level = self.div_level
                self.pos = start_match.end()
                self.div_level += 1
        
            if end_match and end_match.start() < start_match.start():
                self.pos = end_match.end()
                self.div_level -= 1
                if self.div_level == self.start_div_level:
                    div = self.html[self.start_position:end_match.end()]
                    return strip_html_tags(div)



