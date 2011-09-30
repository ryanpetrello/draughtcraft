from pecan              import conf
from pecan.templating   import RendererFactory
from genshi.builder     import Element


class Field(object):
    def __init__(self, transform=None):
        self.name = None
        self.transform = transform
    
    def get_value(self, value):
        return {self.name: self.transform(value) if self.transform else value}


class NodeSet(object):
    pass


class Node(object):

    version = Field()

    class __metaclass__(type):
        def __init__(cls, name, bases, ns):
            cls.__fields__ = {}
            for base in bases:
                cls.__fields__.update(getattr(base, '__fields__', {}))
            for key, value in ns.items():
                if not isinstance(value, Field): continue                
                cls.__fields__[key] = value
                value.name = key
    
    def __init__(self, **kw):
        kw.update({'version':1})
        self.__values__ = kw
    
    def render(self):
        ns = dict()
        for key, value in self.__values__.items():
            if key in self.__fields__:
                field = self.__fields__[key]
                fval = field.get_value(value)
                ns.update(fval)
        name = self.__class__.__name__.upper()
        items = sorted(ns.items(), lambda x,y: cmp(x[0], y[0]))
        return Element(name)(
            *[Element(k.upper())(v) for k,v in items]
        ).generate().render('xml')


class Hop(Node):

    name    = Field()
    alpha   = Field()
    amount  = Field()
    use     = Field()
    time    = Field()
    notes   = Field()
    form    = Field()
    origin  = Field()
