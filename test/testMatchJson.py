def matchJSONStr(toBeMatched):
    if toBeMatched.startswith('{\"type\":'):
        flag = 0
        length = len(toBeMatched)
        for i in range(length):
            if toBeMatched[i] == '{':
                flag += 1
            elif toBeMatched[i] == '}':
                flag -= 1
            elif toBeMatched[i] == '\n' and flag == 0 and i != 0:
                return (toBeMatched[:i], toBeMatched[i+1:])
        return ('', toBeMatched)
    elif toBeMatched[0] == '\n':
        if len(toBeMatched) == 1:
            return ('', '')
        else:
            return matchJSONStr(toBeMatched[1:])
    else:
        return ('', toBeMatched)

if __name__ == '__main__':
    initial = ''
    matched = []
    reserved = ''
    with open('testJSONMatch.txt', 'r') as f:
        for line in f:
            initial += (line+'\n')
    m, r = matchJSONStr(initial)
    while m != '':
        matched.append(m)
        m, r = matchJSONStr(r)
    reserved = r
    print('matched:')
    for ms in matched:
        print(ms, end='---\n')
    print('unmatched:', reserved)