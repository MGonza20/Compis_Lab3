

class Token:
        def __init__(self, name):
            self.name = name
            self.regex = None
    
        def __str__(self):
            return f"Token({self.name}, {self.regex})"


class Tokenizer:
     
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.tokens):
            raise StopIteration
        token = self.tokens[self.index]
        self.index += 1
        return token
    
    def peek(self):
        if self.index >= len(self.tokens):
            raise StopIteration
        return self.tokens[self.index]
    
    def next(self):
        if self.index >= len(self.tokens):
            raise StopIteration
        token = self.tokens[self.index]
        self.index += 1
        return token
    
    def hasNext(self):
        return self.index < len(self.tokens)
    
    def hasPeek(self):
        return self.index + 1 < len(self.tokens)
    
    def reset(self):
        self.index = 0

class Lexer:
    def __init__(self, filename):
        self.filename = filename
        self.tokens = []
        self.tokenizer = None

    
    def remove_spaces(self, lines):
        wo_spaces = []
        # Si hay comillas dobles reemplazar por simples
        for i in range(len(lines)):
            lines[i] = lines[i].replace('"', "'")

        for line in lines:
            new_line = []
            between_q = False
            for char in line:
                if char == "'":
                    between_q = not between_q
                if char != " " or between_q:
                    new_line.append(char)
            wo_spaces.append("".join(new_line))
        return wo_spaces


    def getLines(self):
        f = open(self.filename, "r", encoding="utf-8")
        lines = f.readlines()
        f.close()

        lines = [line.encode('utf-8').decode('unicode_escape') for line in lines]
        lines = [line.strip() for line in lines if line.strip() != ""]
        return self.remove_spaces(lines)  
        return lines


    def getTokens(self):
        lines = self.getLines()
        for line in lines:
            # generando tokens
            if line[:3] == 'let':
                name, regex = line[3:].split('=')
                token = Token(name)
                token.regex = regex
                self.tokens.append(token)


    def range_maker(self, start, end):
        if len(start) == 3 and len(end) == 3:
            start, end = start[1], end[1]
        elif len(start) != 1 or len(end) != 1:
            raise Exception("Formato de regex incorrecto")

        if start.isalpha() and end.isalpha():
            if ord(start) > ord(end):
                raise Exception("Rango incorrecto")
            elements = [chr(i) for i in range(ord(start), ord(end) + 1)]

        elif start.isdigit() and end.isdigit():
            start, end = int(start), int(end)
            if start > end:
                raise Exception("Rango incorrecto")
            elements = [str(i) for i in range(start, end + 1)]
        else:
            raise Exception("Formato de regex incorrecto")

        return elements

    
    def change_range_format(self):
        tokens = self.tokens
        for token in tokens:
            if token.regex.startswith('[') and token.regex.endswith(']'):
                # Si las comillas no estan balanceadas
                if token.regex.count("'") % 2 != 0:
                    raise Exception("Comillas no balanceadas")
                
                # Si hay mas de 2 comillas consecutivas 
                for i in range(len(token.regex) - 2):
                    if token.regex[i] == token.regex[i+1] == [i+2]:
                        raise Exception("Error en comillas")
                
                # Si hay mas de 1 comilla al inicio o al final
                if token.regex[:-1].endswith("''") or token.regex[1:].startswith("''"):
                    raise Exception("Error en comillas")
                
                if token.regex.count("''") > 0:
                    if token.regex.startswith('[') and token.regex.endswith(']'):
                        token.regex = token.regex.replace("''", "'|'")
                        tokens_list = token.regex[1:-1].split("|")

                    elements = []
                    for i in range(len(tokens_list)):
                        if '-' in tokens_list[i]:
                            start, end = tokens_list[i].split('-')
                            elements += self.range_maker(start, end)
                    token.regex = ''
                    if elements:    
                        token.regex += '|'.join(elements)
                        more = False
                        add_list = []
                        for el in tokens_list:
                            if el not in elements and '-' not in el:
                                add_list.append(el)
                                more = True
                        if more:
                            token.regex += '|' + '|'.join(add_list)
                    else:
                        token.regex += '|'.join(tokens_list)
                else:
                    if '-' in token.regex:
                        if token.regex.count('-') > 1:
                            raise Exception("Formato de regex incorrecto")
                        start, end = token.regex[1:-1].split('-')
                        elements = self.range_maker(start, end)
                        token.regex = '|'.join(elements) 
                    else:
                        if token.regex.startswith("['") and token.regex.endswith("']"):
                            token.regex = token.regex[2:-2]
                        elif token.regex.startswith('[') and token.regex.endswith(']'):
                            token.regex = token.regex[1:-1]

    def replace_tokens(self):
        for tk in self.tokens:
            for token in self.tokens:
                if token.name in tk.regex:
                    tk.regex = tk.regex.replace(token.name, '('+token.regex+')')
    
    
if __name__ == '__main__':
    lexer = Lexer('thompsonTools/lexer.yal')
    tokenizer = lexer.getTokens()
    lexer.change_range_format()
    lexer.replace_tokens()
    aa = 0