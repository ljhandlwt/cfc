import os,sys
import shutil
import pdb

__version__ = '0.1'

class ActionIter(object):
    def __init__(self):
        pass

class PyFile(object):
    database = {}

    def __init__(self, filename):
        self.filename = filename
        self.raw_lines = None
        self.cur_lines = None

        # load file
        with open(self.filename) as f:
            self.raw_lines = [line.rstrip() for line in f.readlines()]
        # copy file
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        shutil.copy(self.filename, 'tmp/{}-{}'.format(self.fid,os.path.basename(self.filename)))
        # reset for cur_lines
        self.reset()
        
    def __new__(cls, filename):
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
            shutil.copy('tmp/{}-{}'.format(instance.fid,os.path.basename(filename)), filename)

    @_flush_deco
    def reset(self):
        self.cur_lines = [[line] for line in self.raw_lines]
        self.cur_lines.insert(0, '')

    @_flush_deco
    def replace(self, line, code):
        code = code.strip()
        indent = self._find_indent(line)
        self.cur_lines[line][-1] = indent+code

    @_flush_deco
    def insert(self, line, code):
        code = code.strip()
        indent = self._find_indent(line)
        self.cur_lines[line].insert(-1, indent+code)

    @_flush_deco
    def comment(self, line):
        indent = self._find_indent(line)
        s = self.cur_lines[line][-1]
        s1 = s.lstrip()
        if s1[0] != '#':
            self.cur_lines[line][-1] = indent+'# '+s1

    @_flush_deco
    def uncomment(self, line):
        indent = self._find_indent(line)
        s = self.cur_lines[line][-1]
        s1 = s.lstrip()
        if s1[0] == '#':
            self.cur_lines[line][-1] = indent+s1[1:].lstrip()


    def _flush(self):
        with open(self.filename, 'w') as f:
            for i,lines in enumerate(self.cur_lines):
                s = '\n'.join(lines)
                if i > 1:
                    s = '\n' + s
                f.write(s)

    def _find_indent(self, line):
        s = self.raw_lines[line]
        k = len(s) - len(s.lstrip())
        return s[:k]

    def _get_version_info(self, line):
        pass





if __name__ == "__main__":
    try:
        f = PyFile('aaa/b.py')
        '''
        pdb.set_trace()
        f.replace(6, r'print("???")')
        pdb.set_trace()
        f.reset()
        pdb.set_trace()
        f.insert(3, r'print("fef")')
        pdb.set_trace()
        f.reset()
        pdb.set_trace()
        f.comment(3)
        pdb.set_trace()
        f.reset()
        pdb.set_trace()
        f.uncomment(7)
        pdb.set_trace()
        f.reset()
        pdb.set_trace()
        f.comment(7)
        pdb.set_trace()
        f.reset()
        pdb.set_trace()
        f.uncomment(6)
        pdb.set_trace()
        '''
        f.replace(6, r'print("???")')
        pdb.set_trace()        
        f.insert(3, r'print("fef")')
        pdb.set_trace()        
        f.comment(3)
        pdb.set_trace()        
        f.uncomment(7)
        pdb.set_trace()        
    finally:
        PyFile.close_all()
    