from genshi.builder     import Element


class Field(object):
    """
    A declarative XML field.  `Node`s can have one or more of these, e.g.,

    class SomeNode(Node):
        name    = Field()
        color   = Field()
        ...

    Additionally, nodes can have `transform` modifiers that they apply to the
    value at rendering time.  For example:

    class SomeNode(Node):
        name_in_caps = Field(lambda x: x.upper())
    """

    def __init__(self, transform=None):
        self.name = None
        self.transform = transform
    
    def get_value(self, value):
        #
        # This is called when XML is being rendered.
        # If a `transform` callable was passed into the constructor, it will
        # be used to modify the passed value.
        #
        return {self.name: self.transform(value) if self.transform else value}


class NodeSet(object):
    """
    Represents a collection of <Node>'s, e.g., <HOPS></HOPS>.
    """

    def __init__(self, nodetype):
        self.name = None
        self.nodetype = nodetype


class Node(object):
    """
    Represents a node in the BeerXML standard.

    Can range from <RECIPE></RECIPE> to <HOP></HOP>.

    This class can be extended, and you can declaratively define "fields",
    e.g.,

    class Hop(Node):

        name        = Field()
        alpha_acid  = Field()
        ...

    """

    version = Field()

    class __metaclass__(type):
        def __init__(cls, name, bases, ns):

            # Keep track of the fields and node sets defined declaratively.
            cls.__fields__ = {}
            cls.__nodesets__ = {}

            # Inherit fields and nodesets from the base Node class.
            for base in bases:
                cls.__fields__.update(getattr(base, '__fields__', {}))
                cls.__fields__.update(getattr(base, '__nodesets__', {}))

            # For each class member...
            for key, value in ns.items():

                #
                # If it's a field, store it in the fields list and save the 
                # name of the field.
                #
                if isinstance(value, Field):
                    cls.__fields__[key] = value
                    value.name = key

                #
                # If it's a node set, store it in the fields list and save the 
                # name of the node set.
                #
                if isinstance(value, NodeSet):
                    cls.__nodesets__[key] = value
                    value.name = key
    
    def __init__(self, **kw):
        # Every node must specify <VERSION>1</VERSION>.
        kw.update({'version':1})

        # Store the values passed to the constructor
        self.__values__ = kw
    
    def render(self, xml=True):
        """
        Returns a genshi.builder.Element, or raw rendered XML, depending on the
        value of `xml`.
        """

        # Keep a namespace of XML nodes to render
        ns = dict()

        # Look at every key/value pair passed into the constructor...
        for key, value in self.__values__.items():

            # If the value is a list, it's a set of Nodes.
            if isinstance(value, list):
                # Update the namespace with {NodeSet.name: [Element, Element]}
                ns.update({
                    key: [node.render(xml=False) for node in value]
                })
            elif isinstance(value, Node):
                #
                # If the value is already a singular node, just add it to the
                # existing list of values.
                #
                ns.update({
                    key: value.render(xml=False)
                })
            elif key in self.__fields__:
                field = self.__fields__[key]
                # Get the `transform`'ed value and store it in the namespace.
                fval = field.get_value(value)
                ns.update(fval)

        # The tagname is the class name in uppercase, e.g., `Hop` -> `<HOP>`
        name = self.__class__.__name__.upper()

        # Sort the keys for consistency
        items = sorted(ns.items(), lambda x,y: cmp(x[0], y[0]))

        #
        # Create an `Element` for this node.
        # Its value should be the accumulated collection of its child
        # `Element`s.
        #
        element = Element(name)(
            *[v if isinstance(v, Element) else Element(k.upper())(v) for k,v in items]
        )

        # Return xml or a raw `Element`.
        if xml is False: return element
        return element.generate().render('xml')


class Recipe(Node):

    name                = Field()
    type                = Field()
    brewer              = Field()
    batch_size          = Field()
    boil_size           = Field()
    boil_time           = Field()
    efficiency          = Field()

    notes               = Field()
    fermentation_stages = Field()
    primary_age         = Field()
    primary_temp        = Field()
    secondary_age       = Field()
    secondary_temp      = Field()
    tertiary_age        = Field()
    tertiary_temp       = Field()

class Hop(Node):

    name                = Field()
    alpha               = Field()
    amount              = Field()
    use                 = Field()
    time                = Field()
    notes               = Field()
    form                = Field()
    origin              = Field()


class Fermentable(Node):

    name                = Field()
    type                = Field()
    amount              = Field()
    YIELD               = Field() # yield (lower) is a reserved keyword
    color               = Field()
    origin              = Field()


class Yeast(Node):

    name                = Field()
    type                = Field()
    form                = Field()
    amount              = Field()
    flocculation        = Field()
    attenuation         = Field()
    add_to_secondary    = Field()


class Misc(Node):

    name                = Field()
    type                = Field()
    use                 = Field()
    time                = Field()
    amount              = Field()
    amount_is_weight    = Field()


class Style(Node):
    name                = Field()
    category            = Field()
    category_number     = Field()
    style_letter        = Field()
    style_guide         = Field()
    type                = Field()
    og_min              = Field()
    og_max              = Field()
    fg_min              = Field()
    fg_max              = Field()
    ibu_min             = Field()
    ibu_max             = Field()
    color_min           = Field()
    color_max           = Field()
    abv_min             = Field()
    abv_max             = Field()
