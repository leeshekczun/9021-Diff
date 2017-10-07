import re
import os
from copy import deepcopy


class DiffCommands:
    def __init__(self,file_name):
        self.text = ''
        last_line = [[0,0],[0,0]]
        with open (file_name) as file:
            for line in file:
                if not check(line,last_line):
                    raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                else:
                    self.text += line
                    last_line = check(line,last_line)

    def __str__(self):
        return self.text[:-1]


def check(line,last_line):
    if re.match(r'^(\d+)a(\d+)(?:,(\d+))?$', line):
        m = re.match(r'^(\d+)a(\d+)(?:,(\d+))?$', line)
        the_line = [[int(m.group(1))],[int(m.group(2))]]
        if m.group(3):
            if m.group(3)<=m.group(2):
                return False
            else:
                the_line[1].append(m.group(3))
        if int(the_line[0][-1]) - int(last_line[0][-1]) + len(the_line[1]) == int(the_line[1][-1]) - int(last_line[1][-1]) and int(the_line[1][-1]) - \
                int(last_line[1][-1]) != 1:
            last_line = the_line
            return last_line
        else:
            return False
    elif re.match(r'^(\d+)(?:,(\d+))?d(\d+)$', line):
        m = re.match(r'^(\d+)(?:,(\d+))?d(\d+)$', line)
        the_line = [[int(m.group(1))], [int(m.group(3))]]
        if m.group(2):
            if m.group(2)<=m.group(1):
                return False
            else:
                the_line[0].append(m.group(2))
        if int(the_line[0][-1]) - int(last_line[0][-1]) - len(the_line[0]) == int(the_line[1][-1]) - int(last_line[1][-1]) and int(the_line[1][-1]) - \
                int(last_line[1][-1]) != 1:
            last_line = the_line
            return last_line
        else:
            return False
    elif re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line):
        m = re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line)
        the_line = [[int(m.group(1))], [int(m.group(3))]]
        if m.group(2):
            the_line[0].append(m.group(2))
        if m.group(4):
            the_line[1].append(m.group(4))
        if int(the_line[0][-1]) - int(last_line[0][-1]) - (int(the_line[0][-1]) - int(the_line[0][0]) + 1) + (
                int(the_line[1][-1]) - int(the_line[1][0]) + 1) == int(the_line[1][-1]) - int(last_line[1][-1]) and int(the_line[1][-1]) - \
                int(last_line[1][-1]) != 1:
            last_line = the_line
            return last_line
        else:
            return False
    else:
        return False


class DiffCommandsError(Exception):
    def __init__(self,text):
        self.text = text


class OriginalNewFiles:
    def __init__(self, file1_name, file2_name):
        self.file_1 = [[]]
        self.file_2 = [[]]
        with open(file1_name) as file:
            for line in file:
                self.file_1.append([line[:-1]])
        with open(file2_name) as file:
            for line in file:
                self.file_2.append([line[:-1]])

    def is_a_possible_diff(self, diff):
        # real = os.popen('self.file_1','self.file_2').diff()
        # if real == diff:
        #     return True
        # else:
        #     return False
        file1 = deepcopy(self.file_1)
        file2 = deepcopy(self.file_2)
        if diff.text == '':
            if file1==file2:
                return True
            else:
                return False

        commands = diff.text.split('\n')
        commands.pop()

        for line in commands:
            try:
                if re.match(r'^(\d+)a(\d+)(?:,(\d+))?$', line):
                    m = re.match(r'^(\d+)a(\d+)(?:,(\d+))?$', line)
                    if m.group(3):
                        for i in range(int(m.group(2)), (int(m.group(3))+1)):
                            file1[int(m.group(1))].append(file2[i][0])
                    else:
                        file1[int(m.group(1))].append(file2[int(m.group(2))][0])

                elif re.match(r'^(\d+)(?:,(\d+))?d(\d+)$', line):
                    m = re.match(r'^(\d+)(?:,(\d+))?d(\d+)$', line)
                    if m.group(2):
                        for i in range(int(m.group(1)), (int(m.group(2))+1)):
                            file1[i].pop()
                    else:
                        file1[int(m.group(1))].pop()

                elif re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line):
                    m = re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line)
                    if m.group(2) and m.group(4):
                        for i in range(int(m.group(1)), (int(m.group(2))+1)):
                            file1[i].pop()
                        file1[int(m.group(1))].append(file2[int(m.group(3)):(int(m.group(4)) + 1)])
                    elif m.group(2) and not m.group(4):
                        for i in range(int(m.group(1)), (int(m.group(2))+1)):
                            file1[i].pop()
                        file1[int(m.group(1))].append(file2[int(m.group(3))])
                    elif not m.group(2) and m.group(4):
                        file1[int(m.group(1))].pop()
                        file1[int(m.group(1))].append(file2[int(m.group(3)):(int(m.group(4)) + 1)])
                    elif not m.group(4) and not m.group(2):
                        file1[int(m.group(1))].pop()
                        file1[int(m.group(1))].append(file2[int(m.group(3))])
            except IndexError:
                return False

        func = lambda x: [y for l in x for y in func(l)] if type(x) is list else [x]
        file3 = func(file1)
        file4 = func(file2)
        while '' in file3:
            file3.remove('')
        while '' in file4:
            file4.remove('')

        if file3 == file4:
            return True
        else:
            return False



    def output_diff(self, diff):
        file1 = deepcopy(self.file_1)
        file2 = deepcopy(self.file_2)
        if diff.text == '':
            return
        commands = diff.text.split('\n')
        commands.pop()

        for line in commands:
            if re.match(r'^(\d+)a(\d+)(?:,(\d+))?$', line):
                m = re.match(r'^(\d+)a(\d+)(?:,(\d+))?$', line)
                print(line)
                if m.group(3):
                    for i in range(int(m.group(2)), (int(m.group(3))+1)):
                        print('>', file2[i][0])
                else:
                    print('>', file2[int(m.group(2))][0])

            elif re.match(r'^(\d+)(?:,(\d+))?d(\d+)$', line):
                m = re.match(r'^(\d+)(?:,(\d+))?d(\d+)$', line)
                print(line)
                if m.group(2):
                    for i in range(int(m.group(1)), (int(m.group(2))+1)):
                        print('<', file1[i][0])
                else:
                    print('<', file1[int(m.group(1))][0])

            elif re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line):
                m = re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line)
                print(line)
                if m.group(2) and m.group(4):
                    for i in range(int(m.group(1)), (int(m.group(2))+1)):
                        print('<', file1[i][0])
                    print('---')
                    for i in range(int(m.group(3)), (int(m.group(4)) + 1)):
                        print('>', file2[i][0])
                elif m.group(2) and not m.group(4):
                    for i in range(int(m.group(1)), (int(m.group(2))+1)):
                        print('<', file1[i][0])
                    print('---')
                    print('>', file2[int(m.group(3))][0])
                elif not m.group(2) and m.group(4):
                    print('<', file1[int(m.group(1))][0])
                    print('---')
                    for i in range(int(m.group(3)), (int(m.group(4)) + 1)):
                        print('>', file2[i][0])
                elif not m.group(2) and not m.group(4):
                    print('<', file1[int(m.group(1))][0])
                    print('---')
                    print('>', file2[int(m.group(3))][0])
        return

    def output_unmodified_from_original(self, diff):
        file1 = deepcopy(self.file_1)
        file2 = deepcopy(self.file_2)
        if diff.text == '':
            for i in file1[1:]:
                print(i[0])
                return
        commands = diff.text.split('\n')
        commands.pop()
        for line in commands:
            if re.match(r'^(\d+)(?:,(\d+))?d(\d+)$', line):
                m = re.match(r'^(\d+)(?:,(\d+))?d(\d+)$', line)
                if not m.group(2):
                    file1[int(m.group(1))] = ['...']
                else:
                    for i in range(int(m.group(1)), int(m.group(2))):
                        file1[i] = []
                    file1[int(m.group(2))] = ['...']
            elif re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line):
                m = re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line)
                if not m.group(2):
                    file1[int(m.group(1))] = ['...']
                else:
                    for i in range(int(m.group(1)), int(m.group(2))):
                        file1[i] = []
                    file1[int(m.group(2))] = ['...']            
            else:
                continue
        for i in range(1,len(file1)):
            if file1[i] != []:
                print(file1[i][0])
        return
    
    def output_unmodified_from_new(self, diff):
        file1 = deepcopy(self.file_1)
        file2 = deepcopy(self.file_2)
        if diff.text == '':
            for i in file2[1:]:
                print(i[0])
                return
        commands = diff.text.split('\n')
        commands.pop()
        for line in commands:
            if re.match(r'^(\d+)a(\d+)(?:,(\d+))?$', line):
                m = re.match(r'^(\d+)a(\d+)(?:,(\d+))?$', line)
                if not m.group(3):
                    file2[int(m.group(2))] = ['...']
                else:
                    for i in range(int(m.group(2)), int(m.group(3))):
                        file2[i] = []
                    file2[int(m.group(3))] = ['...']
            elif re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line):
                m = re.match(r'^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line)
                if not m.group(4):
                    file2[int(m.group(3))] = ['...']
                else:
                    for i in range(int(m.group(3)), int(m.group(4))):
                        file2[i] = []
                    file2[int(m.group(4))] = ['...']
            else:
                continue
        for i in range(1,len(file2)):
            if file2[i] != []:
                print(file2[i][0])
        return

    def get_all_diff_commands(self):
        all = []
        all.append(self.text[:1])
        return all


# diff_1 = DiffCommands('diff_1.txt')
# pair_of_files = OriginalNewFiles('file_1_1.txt', 'file_1_2.txt')
# print(pair_of_files.is_a_possible_diff(diff_1))
