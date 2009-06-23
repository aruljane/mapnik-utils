import os
import sys
import mapnik

class Load(object):
    def __init__(self,mapfile,variables={},from_string=False):
        self.mapfile = mapfile
        self.from_string = from_string
        self.variables = variables
        self.mapfile_types = {'xml':'XML mapfile','mml':'Mapnik Markup Language', 'py':'Python map variable'}
        if self.from_string:
            self.file_type = 'xml'
        else:
            self.file_type = self.get_type()
            self.validate()
        
    def validate(self):
        if not os.path.exists(self.mapfile):
            raise AttributeError('Mapfile not found')
        if not self.file_type in self.mapfile_types:
            raise AttributeError('Invalid mapfile type: only these extension allowed: %s' % ', '.join(self.mapfile_types.keys()))
        return True

    def get_type(self):
        if self.mapfile.endswith('xml'):
            return 'xml'
        elif self.mapfile.endswith('mml'):
            return 'mml'
        elif self.mapfile.endswith('py'):
            return 'py'
        else:
            raise ValueError("Unknown Mapfile type: '%s'" % self.mapfile)

    def variable_replace(self):
        import tempfile
        if self.from_string:
            mapfile_string = self.mapfile
        else:
            mapfile_string = open(self.mapfile).read()
        for line in mapfile_string.splitlines():
            for key,value in self.variables.items():
                line.replace(key,value)
        tmp = tempfile.NamedTemporaryFile(suffix='.xml', mode = 'w')
        tmp.write(mapfile_string)
        tmp.flush()
        return tmp.name

    def load_xml(self,m):
        if self.from_string:
            return mapnik.load_map_from_string(m,self.mapfile)
        else:
            return mapnik.load_map(m,self.mapfile)

    def load_mml(self,m):    
        from cascadenik import load_map as load
        load(m,self.mapfile)

    def load_py(self,m,map_variable='m'):
        """
        Instanciate a Mapnik Map object from an external python script.
        """
        py_path = os.path.abspath(self.mapfile)
        sys.path.append(os.path.dirname(py_path))
        py_module = os.path.basename(py_path).replace('.py','')
        module = __import__(py_module)
        py_map = getattr(module,map_variable,None)
        if not py_map:
            raise ValueError('No variable found in python file with the name: "%s"' % map_variable)
        py_map.width = m.width
        py_map.height = m.height
        return py_map
          
    def load_mapfile(self,m):
        if self.variables:
            self.mapfile = self.variable_replace()
        load = getattr(self,'load_%s' % self.file_type)
        load(m)

    def build_map(self,width,height):
        m = mapnik.Map(width,height)
        if self.file_type == 'py':
            return self.load_py(m)
        else:
            self.load_mapfile(m)
            return m