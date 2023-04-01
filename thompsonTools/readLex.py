

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


    def getLines(self):
        f = open(self.filename, "r")
        lines = f.readlines()
        f.close()
    
        lines = [line.strip() for line in lines if line.strip() != ""]
        return [line.replace(" ", "") for line in lines]   


    def getTokens(self):
        lines = self.getLines()
        for line in lines:
            # generando tokens
            if line[:3] == 'let':
                name, regex = line[3:].split('=')
                token = Token(name)
                token.regex = regex
                self.tokens.append(token)

    
    def fixRegex(self):
        tokens = self.tokens
        for token in tokens:
            if token.regex.startswith('[') and token.regex.endswith(']'):
                start, end = token.regex[1:-1].split('-')
                if len(start) == 3 and len(end) == 3:
                    start, end = start[1], end[1]
                elif len(start) != 1 or len(end) != 1:
                    raise Exception("Formato de regex incorrecto")
                if start.isalpha() and end.isalpha():
                    elements = [chr(i) for i in range(ord(start), ord(end)+1)]
                    token.regex = '|'.join(elements) 
                elif start.isdigit() and end.isdigit():
                    start, end = int(start), int(end)
                    elements = [str(i) for i in range(start, end+1)]
                    token.regex = '|'.join(elements) 

                aaa = 123

    
    
if __name__ == '__main__':
    lexer = Lexer('thompsonTools/lexer.yal')
    tokenizer = lexer.getTokens()
    lexer.fixRegex()