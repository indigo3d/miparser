import sys
import ply.lex as lex


reserved = [ 'INCLUDE', 'INCPATH', 
'AMBIENTOCCLUSION', 'ACCELERATION', 'ACCURACY', 'ADAPTIVE', 'ALL', 'ALPHA', 'ANGLE', 'ANY', 
'APERTURE', 'APPLY', 'APPROXIMATE', 'ARRAY', 'ASPECT', 'ASSEMBLY', 'ATTRIBUTE', 'AUTOVOLUME', 
'B', 'BACK', 'BASIS', 'BEZIER', 'BIAS', 'BINARY', 'BLUE', 'BOOLEAN', 'BORDER', 'BOTH', 'BOX', 
'BSDF', 'BSP', 'BSP2', 'BSPLINE', 'BUFFER', 'BUMP', 'CALL', 'CAMERA', 'CARDINAL', 'CAUSTIC', 
'CCMESH', 'CG', 'CHILD', 'CLASSIFICATION', 'CLIP', 'CODE', 'COLLECT', 'COLOR', 'COLORCLIP', 
'COLORPROFILE', 'COMPRESS', 'COMPRESSION', 'CONE', 'CONIC', 'CONNECT', 'CONST', 'CONSTANT', 
'CONTOUR', 'CONTRAST', 'CONTROL', 'CORNER', 'CP', 'CREASE', 'CURVATURE', 'CURVE', 'CUSP', 
'CYLINDER', 'D', 'D2', 'DART', 'DATA', 'DATATYPE', 'DEBUG', 'DECLARE', 'DEFAULT', 'DEGREE', 
'DELAUNAY', 'DELETE', 'DENSITY', 'DEPTH', 'DERIVATIVE', 'DESATURATE', 'DETAIL', 'DIAGNOSTIC', 
'DIRECTION', 'DISC', 'DISPLACE', 'DISTANCE', 'DITHER', 'DOD', 'DOF', 'DPI', 'ECHO', 'EMITTER', 
'END', 'ENVIRONMENT', 'EVEN', 'ENERGY', 'EULUMDAT', 'EXPONENT', 'FACE', 'FALLOFF', 'FALSE', 'FAN', 
'FAST', 'FASTLOOKUP', 'FIELD', 'FILENAME', 'FILETYPE', 'FILE', 'FILTER', 'FILTERING', 
'FINALGATHER', 'FINE', 'FLAGS', 'FOCAL', 'FORCE', 'FORMAT', 'FRAGMENT', 'FRAME', 'FRAMEBUFFER', 
'FREEZE', 'FRONT', 'GAMMA', 'GAUSS', 'GEOMETRY', 'GLOBAL', 'GLOBILLUM', 'GRADING', 'GREEN', 'GRID', 
'GROUP', 'GUI', 'HAIR', 'HARDWARE', 'HERMITE', 'HIDE', 'HOLE', 'HULL', 'IBL', 'IES', 'IMP', 
'IMPLICIT', 'IMPORTANCE', 'INCREMENTAL', 'INFINITY', 'INHERITANCE', 'INSTANCE', 'INSTGROUP', 
'INTEGER', 'INTERFACE', 'INTERSECTION', 'IRRADIANCE', 'JITTER', 'LANCZOS', 'LARGE', 'LENGTH', 
'LENS', 'LEVEL', 'LIGHT', 'LIGHTMAP', 'LIGHTPROFILE', 'LINK', 'LOCAL', 'LUMINANCE', 'M', 'MAPSTO', 
'MASK', 'MATERIAL', 'MATRIX', 'MAX', 'MEMORY', 'MERGE', 'MI', 'MIN', 'MITCHELL', 'MIXED', 
'MOTION', 'N', 'NAMESPACE', 'NATIVE', 'NOCONTOUR', 'NOSMOOTHING', 'NORMAL', 'NULL', 'NTSC', 
'OBJECT', 'ODD', 'OFF', 'OFFSET', 'OFFSCREEN', 'ON', 'ONLY', 'OPAQUE', 'OPENGL', 'OPTIONS', 
'ORIGIN', 'OUTPUT', 'OVERRIDE', 'P', 'PARALLEL', 'PARAMETRIC', 'PASS', 'PHENOMENON', 'PHOTON', 
'PHOTONMAP', 'PHOTONS', 'PHOTONVOL', 'POLYGON', 'POSITION', 'PREMULTIPLY', 'PREP', 'PRESAMPLE', 
'PRIMARY', 'PRIORITY', 'PRIVATE', 'PROTOCOL', 'QUALITY', 'RADIUS', 'RAPID', 'RAST', 'RATIONAL', 
'RAY', 'RAYCL', 'RAW', 'READ', 'REBUILD', 'RECTANGLE', 'RECURSIVE', 'RED', 'REFLECTION', 
'REFRACTION', 'REGISTRY', 'REGULAR', 'RENDER', 'RESOLUTION', 'RGB', 'ROOT', 'SAMPLELOCK', 
'SAMPLES', 'SCALE', 'SCALAR', 'SCANLINE', 'SECONDARY', 'SEGMENTS', 'SELECT', 'SESSION', 'SET', 
'SHADER', 'SHADING', 'SHADOW', 'SHADOWMAP', 'SHARP', 'SHUTTER', 'SIZE', 'SOFTNESS', 'SORT', 'SPACE', 
'SPATIAL', 'SPDL', 'SPECIAL', 'SPECTRUM', 'SPHERE', 'SPREAD', 'STATE', 'STEPS', 'STORE', 'STRING', 
'STRIP', 'STRUCT', 'SUBDIVISION', 'SURFACE', 'SYSTEM', 'T', 'TAG', 'TAGGED', 'TASK', 'TAYLOR', 
'TEXTURE', 'TIME', 'TOPOLOGY', 'TOUCH', 'TRACE', 'TRANSFORM', 'TRANSPARENCY', 'TRAVERSAL', 'TREE', 
'TRIANGLE', 'TRILIST', 'TRIM', 'TRUE', 'U', 'UNIFORM', 'USEOPACITY', 'USEPRIMARY', 'USER', 'V', 
'VALUE', 'VECTOR', 'VENDOR', 'VERBOSE', 'VERSION', 'VERTEX', 'VIEW', 'VISIBLE', 'VOLUME', 'W', 
'WEIGHT', 'WHITE', 'WIDTH', 'WINDOW', 'WORLD', 'WRITABLE', 'WRITE']


tokens = reserved + ['T_SYMBOL', 'T_INTEGER', 'T_FLOAT', 'T_STRING', 'T_BYTE_STRING', 'T_VECTOR']
# ['INCLUDE'] +
literals = ['=', ',','(',')','{','}','[',']']


reserved_map = { }
for r in reserved:
    reserved_map[r.lower()] = r


class Entity(object):
    """
    Abstract base class
    """
    def __init__(self, type, text ):
        self._type = type
        self._text = text
    
    @property
    def type(self):
        return self._type 
     
    @property
    def text(self):
        return self._text
    
class Value(Entity):
    """
    Represents a value like a float, int, boolean, vector, transform, or constant
    """
    def __init__(self, type, text, data):
        Entity.__init__(self, type, text)
        self._data = data
        
    def __repr__(self):
        return '%s(%r,%r,%r)' % ( self.__class__.__name__, self._type, self._text, self._data  )
       
#    def __str__(self):
#        return self._text

    @property
    def data(self):
        return self._data


    
# Completely ignored characters
t_ignore           = ' \t\x0c'

# def t_INCLUDE(t):
#     r'\$include\s+["<]([^\n\"]+)[">]'
#     print t.value
#     return t
def t_INCLUDE(t):
     r'\$include'
     return t
    
def t_T_STRING(t):
    #r'([^"\n])|([^"\n\r]+)'
    r'("[^\n"]")|("[^\n\r"]+")'
    
    # remove quotes
    t.value = Value( 'string', t.value, t.value[1:-1] )
    return t
    
def t_INCPATH(t):
    #r'([^"\n])|([^"\n\r]+)'
    r'(<[^\n]>)|(<[^\n\r]+>)'
    return t
    
def t_T_FLOAT(t):
    r'([+-]?\d+[dDeE][+-]\d+)|([+-]?\d+\.\d*[dDeE][+-]\d+)|([+-]?\d+\.\d*)|([+-]?\d*\.\d+)'
    # matches floating point numbers like: 1. and 1.32
    #[+-]?{DIGIT}*"."{DIGIT}*
    #
    # or
    #
    # matches floating point numbers like: 1e+42
    #[+-]?{DIGIT}+[dDeE][+-]{DIGIT}+
    #
    # or
    #
    # matches floating point numbers like: 1.32e+42
    #[+-]?{DIGIT}+"."{DIGIT}*[dDeE][+-]{DIGIT}+
    
    # convert to float
    t.value = Value( 'float', t.value, float(t.value) )
    return t

def t_T_INTEGER(t):
    r'[+-]?\d+'
    #[+-]?{DIGIT}+ 
    
    # convert to int
    t.value = Value( 'int', t.value, int(t.value) )
    return t


def t_T_SYMBOL(t):
    r'\w+'
    t.type = reserved_map.get(t.value,"T_SYMBOL")
    return t



def t_NEWLINE(t):
    r'\n+|\r+'
    t.lexer.lineno += t.value.count("\n")

def t_comment(t):
    r'\#.*'
    t.lexer.lineno += 1

#def t_code_error(t):
#    raise RuntimeError

def t_error(t):
    print "%d: Illegal character '%s'" % (t.lexer.lineno, t.value[0])
    #print t.value
    t.lexer.skip(1)

#lex.lex()

if __name__ == "__main__":
    lex.runmain(lexer)
