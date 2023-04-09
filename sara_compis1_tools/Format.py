
class Format:
    def __init__(self, regex):
        self.regex = regex
        self.sims = {'(': 1, '|': 2, '.': 3, '*': 4, '+': 4, '?': 4}


    def prec(self, value):
        return 5 if value.isalnum() else self.sims[value]


    def idempotenciesApp(self):
        regexStr = self.regex
        i = 0
        while i < len(regexStr)-1:
            if regexStr[i] == regexStr[i+1] and regexStr[i] in "+?":
                regexStr = regexStr[:i] + regexStr[i+1:]
            else:
                i += 1
        self.regex = regexStr


    def positiveId(self, regexx):
        expression = regexx
        count_plus = expression.count('+')
        count_plus_lit = expression.count("'+'")
        count_t = count_plus - count_plus_lit
        while count_t > 0:

            count_plus = expression.count('+')
            count_plus_lit = expression.count("'+'")
            count_t = count_plus - count_plus_lit
            
            for i in range(len(expression)):
                if expression[i] == '+':
                    if expression[i-1] == ')':
                        j = i-2
                        continuee = True
                        closeParen = 1
                        while continuee:
                            if expression[j] == ')':
                                closeParen += 1
                            elif expression[j] == '(':
                                closeParen -= 1
                            j -= 1
                            if closeParen == 0:
                                continuee = False
                        expression = f'{expression[:j+1]}{expression[j+1:i]*2}*{expression[i+1:]}'

                    elif expression[i-1].isalnum():
                        before = expression[:i-1]
                        after = expression[i+1:]
                        middle = expression[i-1]*2
                        expression = f'{before}{middle}*{after}'    
        return expression

    
    def zeroOrOneId(self, regexx):
        expression = regexx
        count_q = expression.count('?')
        count_q_lit = expression.count("'?'")
        count_t = count_q - count_q_lit
        while count_t > 0:

            count_q = expression.count('?')
            count_q_lit = expression.count("'?'")
            count_t = count_q - count_q_lit

            for i in range(len(expression)):

                

                if expression[i] == '?':
                    if expression[i-1] == ')':
                        j = i-2
                        continuee = True
                        closeParen = 1
                        while continuee:
                            if expression[j] == ')':
                                closeParen += 1
                            elif expression[j] == '(':
                                closeParen -= 1
                            j -= 1
                            if closeParen == 0:
                                continuee = False
                        expression = f'{expression[:j+1]}({expression[j+1:i]}|ε){expression[i+1:]}'

                    elif expression[i-1].isalnum():
                        before = expression[:i-1]
                        after = expression[i+1:]
                        middle = expression[i-1]
                        expression = f'{before}({middle}|ε){after}' 
                    elif i-2 >= 0:
                        ck = expression[i-3:i]
                        if ck[0] == "'" and ck[-1] == "'":
                            expression = f'{expression[:i-3]}({ck}|ε){expression[i+1:]}'

                               

                    
        return expression


    def concat(self, regexx):
        newRegex, ops = "", list(self.sims.keys())
        ops.remove('(')

        i = 0
        while i < len(regexx):
            val = regexx[i]
            if i + 2 < len(regexx):
                if regexx[i] == "'" and regexx[i + 2] == "'":
                    val = regexx[i + 1]
                    val = str(ord(val))
                    if len(val) == 2:
                        val = '0' + val
                    elif len(val) == 1:
                        val = '00' + val
                    i += 2
                elif val.isalnum() or val in ["#", '_']:
                    val = str(ord(val))
                    if len(val) == 2:
                        val = '0' + val
                    elif len(val) == 1:
                        val = '00' + val

            elif regexx[i].isalnum() or regexx[i] in ['#', '_']:
                val = str(ord(val)) 
                if len(val) == 2:
                    val = '0' + val
                elif len(val) == 1:
                    val = '00' + val
                    
            if i + 1 < len(regexx):
                val_p1 = regexx[i + 1]
                newRegex += val

                if val != '(' and val_p1 != ')' and val != '|' and val_p1 not in ops:
                    newRegex += '.'

            i += 1

        if regexx[-1] == ')' or regexx[-1] in ops:
            newRegex += regexx[-1]
        else:
            if len(str(ord(regexx[-1]))) == 1:
                newRegex += '00' + str(ord(regexx[-1]))
            elif len(str(ord(regexx[-1]))) == 2:
                newRegex += '0' + str(ord(regexx[-1]))

        return newRegex


    def infixPostfix(self):
        postfix, stack = '', []
        concatRegex = self.concat()

        for value in concatRegex:
            if value == '(':
                stack.append(value)

            elif value == ')':
                while stack[-1] != '(':
                    postfix += stack.pop()
                stack.pop()

            else:
                while stack and self.prec(value) <= self.prec(stack[-1]):
                    postfix += stack.pop()
                stack.append(value)

        while stack:
            postfix += stack.pop()
        return postfix



# a = Format("12c++(d|q)??e")
# a.zeroOrOneSus()
# a.positiveSus()
# print(a.regex)
# a.idempotenciesApp()
# a.zeroOrOneId()
# a.positiveId()
# print(a.infixPostfix())
# print(a.regex)
