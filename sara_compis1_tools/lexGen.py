from Format import Format
from directAFD import AFD
from StateAFD import StateAFD

import networkx as nx
from graphviz import Digraph
import sys


class Token:
        def __init__(self, name):
            self.name = name
            self.regex = None
            self.line_no = None
    
        def __str__(self):
            return f"Token({self.name}, {self.regex})"


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

        lines_with_n = [n[:-1] for n in lines]
        check_comments = [lll.split(' ') for lll in lines_with_n]  

        joined = [' '.join(line) for line in check_comments]
        for lj in joined:
            if '(*' in lj and '*)' not in lj:
                raise Exception("Error en comentario, linea "+ str(joined.index(lj)+1))
            elif '(*' not in lj and '*)' in lj:
                raise Exception("Error en comentario, linea "+ str(joined.index(lj)+1))

        for i in range(len(check_comments)):
            if 'let' in check_comments[i] and len(check_comments[i]) > 4:
                if check_comments[i][3][-1] == ']' or check_comments[i][3][-1] == ')': 
                    if check_comments[i][4] == '(*' and check_comments[i][-1] == '*)':
                        left_idx = check_comments[i].index('(*')
                        right_idx = check_comments[i].index('*)')
                        check_comments[i] = check_comments[i][:left_idx] + check_comments[i][right_idx + 1:]
            
        lines_c = [' '.join(line) for line in check_comments]
        return self.remove_spaces(lines_c)  
        return lines


    def getTokens(self):
        lines = self.getLines()
        for line_no, line in enumerate(lines, start=1):
            # generando tokens
            if line[:3] == 'let':
                name, regex = line[3:].split('=')
                token = Token(name)
                token.regex = regex
                token.line_no = line_no
                self.tokens.append(token)


    def range_maker(self, start, end, no):
        if len(start) == 3 and len(end) == 3:
            start, end = start[1], end[1]

        if start.isalpha() and end.isalpha():
            if ord(start) > ord(end):
                raise Exception("Error: Rango incorrecto, linea " + str(no))
            elements = [chr(i) for i in range(ord(start), ord(end) + 1)]
            aaa = 123

        elif start.isdigit() and end.isdigit():
            start, end = int(start), int(end)
            if start > end:
                raise Exception("Error: Rango incorrecto, linea " + str(no))
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

                p_left = token.regex.count("(")
                p_right = token.regex.count(")")
                if (p_left + p_right) % 2 != 0:
                    raise Exception("Error: Los parentesis no estan balanceados, "+ "linea " + str(token.line_no))
                
                c_left = token.regex.count("[") 
                c_right = token.regex.count("]") 
                if (c_left + c_right )% 2 != 0:
                    raise Exception("Error: Los corchetesno estan balanceados, "+ "linea " + str(token.line_no))

                
                if token.regex[i] == '[':
                    if token.regex.count("'") % 2 != 0:
                        raise Exception("Error en comillas, " + "linea " + str(token.line_no))
                    
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
                                elements += self.range_maker(start, end, token.line_no)

                        if elements:
                            content = '|'.join(elements)

                    else:
                        if '-' in content:
                            if content.count('-') > 1:
                                raise Exception("Formato de regex incorrecto,"+ "linea " + str(token.line_no))
                            start, end = content.split('-')
                            elements = self.range_maker(start, end, token.line_no)
                            content = '|'.join(elements)
                        elif '-' not in content:
                            content = content[1:-1]
                            elements = [content[i] for i in range(len(content))]
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
    

    def remove_double_parentheses(self, token):
        i = 0
        output = ""
        while i < len(token):
            if token[i] == '(':
                content = "("
                count_open = 1
                count_control = 1
                i += 1
                while count_open != 0:
                    if token[i] == '(':
                        count_open += 1
                        count_control += 1
                    elif token[i] == ')':
                        count_open -= 1
                    content += token[i]
                    i += 1
                
                start = content[:count_control]
                end = content[-count_control:]
                opp = '('*count_control
                clp = ')'*count_control
                if start == opp and end == clp and count_control > 1: 
                    output += content[count_control-1:-count_control+1]
                else:
                    output += content
                
            else:
                output += token[i]
                i += 1
        return output

    def draw_mega_afd(self, afd):

        G = nx.MultiDiGraph()
        for state in afd:
            node_attrs = {'shape': 'circle'}
            if state.start:
                node_attrs.update({'color': 'green', 'style': 'filled'})
            if state.accepting:
                node_attrs.update({'peripheries': '2'})
            G.add_node(str(state.name), **node_attrs)

            for transition, final_dest in state.transitions.items():
                G.add_node(str(final_dest))
                
                if int(transition) not in [el for el in range(0, 35)]:
                    transition = str(chr(int(transition)))

                G.add_edge(str(state.name), str(final_dest), label=transition, dir='forward')    

        dot = Digraph()
        for u, v, data in G.edges(data=True):
            dot.edge(u, v, label=data['label'], dir=data['dir'])
        for node in G.nodes:
            attrs = G.nodes[node]
            dot.node(node, **attrs)

        dot.render('mega/megaautomata', format='png')

    
    def generate_automatas(self):
        mega_content = []
        count = 0
        for token in self.tokens:
            ff = Format(token.regex)
            token.regex = ff.positiveId(token.regex + '#')
            token.regex = ff.zeroOrOneId(token.regex)
            token.regex = self.remove_double_parentheses(token.regex)
            token.regex = ff.concat(token.regex)
            
            afdd = AFD(token)
            new_afd = afdd.generateAFD(count)
            mega_content.append(new_afd)
            count += len(new_afd)
        return mega_content
    

    def unify(self, mega_content):
        stack = []    
        for element in mega_content:
            for state in element:
                if state.start:
                    state.start = False
                    init_state = StateAFD(name='init', start=True, transitions={})
                    init_state.transitions['949'] = state.name
                    stack.append(init_state)
                stack.append(state)
        return stack
    

    def read(self):
        self.getTokens()
        self.change_range_format()
        self.surround_dot()
        self.replace_tokens()
    


    
if __name__ == '__main__':

    # if len(sys.argv) < 2:
    #     print("Por favor ingrese el archivo .yal")
    #     sys.exit(1)

    yal_file = 'sara_compis1_tools/lexer.yal'
    # yal_file = sys.argv[1]
    lexer = Lexer(yal_file)
    
    lexer.read()
    mega_content = lexer.generate_automatas()
    mega_automata = lexer.unify(mega_content)
    lexer.draw_mega_afd(mega_automata)

#     script_content = '''
# import sys
# import sara_compis1_tools.readLex as tool

# if len(sys.argv) < 2:
#     print("Por favor ingrese el archivo .yal")
#     sys.exit(1)

# yal_file = sys.argv[1]
# lex_var = tool.Lexer(yal_file)
# lex_var.read()
# mega_content = lex_var.generate_automatas()
# mega_automata = lex_var.unify(mega_content)
# lex_var.draw_mega_afd(mega_automata)
#     '''

#     with open('generated.py', 'w') as script_file:
#         script_file.write(script_content)

