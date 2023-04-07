from Format import Format

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
            aaa = 123

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
            new_regex = ''
            i = 0
            while i < len(token.regex):
                if token.regex[i] == '[':
                    content = ""
                    j = i + 1
                    while token.regex[j] != ']':
                        content += token.regex[j]
                        j += 1

                    if content.count("''") > 0:
                        content = content.replace("''", "'|'")
                        tokens_list = content.split("|")

                        elements = []
                        for k in range(len(tokens_list)):
                            if tokens_list[k] == "'-'":
                                continue
                            elif '-' in tokens_list[k]:
                                start, end = tokens_list[k].split('-')
                                elements += self.range_maker(start, end)

                        if elements:
                            content = '|'.join(elements)

                    else:
                        if '-' in content:
                            if content.count('-') > 1:
                                raise Exception("Formato de regex incorrecto")
                            start, end = content.split('-')
                            elements = self.range_maker(start, end)
                            content = '|'.join(elements)
                    new_regex += '(' + content + ')'
                    i = j
                else:
                    check = ""
                    j = i
                    while token.regex[j] not in ['+', '*', '?']:
                        check += token.regex[j]
                        j += 1
                    keys = [tk.name for tk in tokens]
                    if check in keys:
                        i = j - 1
                        new_regex += check
                    else:
                        new_regex += token.regex[i]
                i += 1

            count_all = int((new_regex.count('(') + new_regex.count(')')) /2)
            if not count_all or new_regex[-1] in ['+', '*', '?']:
                new_regex = f'({new_regex})'

            token.regex = new_regex


    def replace_tokens(self):
        for tk in self.tokens:
            for token in self.tokens:
                index = tk.regex.find(token.name)
                while index != -1:
                    right_side = (index + len(token.name) == len(tk.regex) or not ((tk.regex[index + len(token.name)])).isalnum()) 

                    if right_side:
                        tk.regex = tk.regex[:index] + token.regex + tk.regex[index + len(token.name):]
                    index = tk.regex.find(token.name, index + 1)

    
    def surround_dot(self):
        for token in self.tokens:
            if token.regex.count('.') > 0:
                token.regex = token.regex.replace('.', "'.'" )
            
    
if __name__ == '__main__':
    lexer = Lexer('thompsonTools/lexer.yal')
    tokenizer = lexer.getTokens()
    lexer.change_range_format()
    lexer.surround_dot()
    lexer.replace_tokens()

    for token in lexer.tokens:
        ff = Format(token.regex)
        token.regex = ff.positiveId(token.regex)
        token.regex = ff.zeroOrOneId(token.regex)
        token.regex = ff.concat(token.regex)

    # for token in lexer.tokens:
    #     ff = Format(token.regex)
    #     token.regex = ff.concat()
    #     aa = 12


    aa = 0