import os,sys
import shutil
import collections
import pdb

__version__ = '0.2'
TMP_DIR = None

class ActionIter(object):
    def __init__(self, file, cmd, *args, **kw):
        self.file = file
        self.cmd = cmd
        self.args = args
        self.kw = kw

        self.cnt = None

    def __iter__(self):
        self.cnt = 0
        return self

    def __next__(self):
        func = getattr(self, '_'+self.cmd)
        func()
        self.cnt += 1
        return self.cnt-1

    def _replace(self):
        line,code,vals = self.args
        if self.cnt < len(vals):
            self.file.replace(line, code.format(vals[self.cnt]))
        else:
            self.file.unreplace(line)
            raise StopIteration

    def _insert(self):
        line,code,vals = self.args
        if self.cnt > 0:
            self.file.uninsert(line, **self.kw)
        if self.cnt < len(vals):
            self.file.insert(line, code.format(vals[self.cnt]), **self.kw)
        else:
            raise StopIteration

    def _if_replace(self):
        line,code = self.args
        if self.cnt == 0:
            pass
        elif self.cnt == 1:
            self.file.replace(line, code)
        else:
            self.file.unreplace(line)
            raise StopIteration

    def _if_comment(self):
        line, = self.args
        if self.cnt == 0:
            self.file.uncomment(line)
        elif self.cnt == 1:
            self.file.comment(line)
        else:
            self.file.unreplace(line)
            raise StopIteration

    def _if_insert(self):
        line,code = self.args
        if self.cnt == 0:
            pass
        elif self.cnt == 1:
            self.file.insert(line, code, **self.kw)
        else:
            self.file.uninsert(line, **self.kw)
            raise StopIteration

class MultiActionIter(ActionIter):
    def __init__(self, file, cmd):
        self.file = file
        self.cmd = cmd
        self.cmds = []

        self.cnt = None


    def replace(self, *args, **kw):
        self.cmds.append(['replace',args,kw])
        return self

    def insert(self, *args, **kw):
        self.cmds.append(['insert',args,kw])
        return self

    def comment(self, *args, **kw):
        self.cmds.append(['comment',args,kw])
        return self

    def uncomment(self, *args, **kw):
        self.cmds.append(['uncomment',args,kw])
        return self


    def _if_do(self):
        if self.cnt == 0:
            pass
        else:
            for cmd,args,kw in self.cmds:
                func = getattr(self, '_if_'+cmd)
                self.args = args
                self.kw = kw
                try:
                    func()
                except StopIteration:
                    pass
            if self.cnt == 2:
                raise StopIteration

    def _if_uncomment(self):
        line, = self.args
        if self.cnt == 0:
            self.file.comment(line)
        elif self.cnt == 1:
            self.file.uncomment(line)
        else:
            self.file.unreplace(line)
            raise StopIteration



class PyFile(object):
    database = {}

    def __init__(self, filename):
        self.filename = filename
        self.raw_lines = None
        self.cur_lines = None

        # load file
        with open(self.filename) as f:
            self.raw_lines = [line.rstrip() for line in f.readlines()]
            self.raw_lines = [''] + self.raw_lines
        # copy file
        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)
        shutil.copy(self.filename, '{}/{}-{}'.format(TMP_DIR,self.fid,os.path.basename(self.filename)))
        # reset for cur_lines
        self.reset()
        
    def __new__(cls, filename):
        assert TMP_DIR is not None, 'you need to set the tmp dir before creating PyFile'
        if filename in cls.database:
            raise Exception('One file can be only instantiated once.')
        instance = object.__new__(cls)
        instance.fid = len(cls.database)
        cls.database[filename] = instance
        return instance

    def _flush_deco(func):
        def deco(self, *args, **kw):
            ret = func(self, *args, **kw)
            self._flush()
            return ret
        return deco


    @classmethod
    def close_all(cls):
        for filename,instance in cls.database.items():
            shutil.copy('{}/{}-{}'.format(TMP_DIR,instance.fid,os.path.basename(filename)), filename)

    @_flush_deco
    def reset(self):
        self.cur_lines = [[[],line,[]] for line in self.raw_lines]

    @_flush_deco
    def replace(self, line, code):
        code = code.strip()
        indent = self._find_indent(line)
        self.cur_lines[line][1] = indent+code

    @_flush_deco
    def unreplace(self, line):
        ite = range(line[0],line[1]+1) if isinstance(line, (list,tuple)) else [line]
        for line in ite:
            self.cur_lines[line][1] = self.raw_lines[line]

    @_flush_deco
    def insert(self, line, code, back=False):
        code = code.strip()
        indent = self._find_indent(line)
        if not back:
            self.cur_lines[line][0].append(indent+code)
        else:
            self.cur_lines[line][2].append(indent+code)

    @_flush_deco
    def uninsert(self, line, back=False):
        if not back:
            self.cur_lines[line][0].pop()
        else:
            self.cur_lines[line][2].pop()

    @_flush_deco
    def comment(self, line):
        ite = range(line[0],line[1]+1) if isinstance(line, (list,tuple)) else [line]
        for i,line in enumerate(ite):
            if i == 0:
                indent = self._find_indent(line)
            s = self.cur_lines[line][1]
            if i == 0:
                s1 = s.lstrip()
            else:
                s1 = s[len(indent):]
            if len(s1)>0 and s1[0] != '#':
                self.cur_lines[line][1] = indent+'# '+s1

    @_flush_deco
    def uncomment(self, line):
        ite = range(line[0],line[1]+1) if isinstance(line, (list,tuple)) else [line]
        for i,line in enumerate(ite):
            if i == 0:
                indent = self._find_indent(line)
            s = self.cur_lines[line][1]
            s1 = s.lstrip()
            if i == 0:
                beg_ix = len(s1[1:]) - len(s1[1:].lstrip())
            if len(s1)>0 and s1[0] == '#':
                self.cur_lines[line][1] = indent+s1[1:][beg_ix:]


    def iter_replace(self, line, code, vals):
        return ActionIter(self, 'replace', line, code, vals)

    def iter_insert(self, line, code, vals, back=False):
        return ActionIter(self, 'insert', line, code, vals, back=back)

    def iter_if_replace(self, line, code):
        return ActionIter(self, 'if_replace', line, code)

    def iter_if_comment(self, line):
        return ActionIter(self, 'if_comment', line)

    def iter_if_insert(self, line, code, back=False):
        return ActionIter(self, 'if_insert', line, code, back=back)

    def iter_if_do(self):
        return MultiActionIter(self, 'if_do')

    def _flush(self):
        with open(self.filename, 'w') as f:
            for i,lines in enumerate(self.cur_lines):
                if i == 0: continue
                s = '\n'.join(lines[0]+[lines[1]]+lines[2])
                if i > 1:
                    s = '\n' + s
                f.write(s)

    def _find_indent(self, line):
        s = self.raw_lines[line]
        k = len(s) - len(s.lstrip())
        return s[:k]

    def _get_version_info(self, line):
        pass

