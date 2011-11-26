from genshi.builder     import Element
from BeautifulSoup      import UnicodeDammit

import unicodedata


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
        value = self.transform(value) if self.transform else value

        #
        # Ugh - BeerXMLv1 is ASCII (ISO-8859-1), so we need to coerce
        # accented and other international characters to normalized ASCII
        # equivalents as best we can.
        #
        if isinstance(value, basestring):
            value = unicodedata.normalize(
                'NFKD', 
                UnicodeDammit(value).unicode
            ).encode('ascii', 'ignore')

        return {self.name: value}


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
    
    def __init__(self, entity=None, **kw):
        # If an entity with an XML namespace is passed, use it
        if entity is not None and hasattr(entity, 'xmlns'):
            kw.update(entity.xmlns)

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
        items = sorted(ns.items(), lambda x,y: cmp(x[0].lower(), y[0].lower()))

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


class Hop(Node):

    name                = Field()

    alpha               = Field() # Percent alpha of hops - for example "5.5"
                                  # represents 5.5% alpha

    amount              = Field() # Weight in Kilograms of the hops used in
                                  # the recipe.

    use                 = Field() # May be "Boil", "Dry Hop", "Mash", 
                                  # "First Wort" or "Aroma".

    time                = Field() #  The time as measured in minutes.  Meaning
                                  #  is dependent on the "USE" field.  For 
                                  #  "Boil" this is the boil time.  For "Mash" 
                                  #  this is the mash time.  For "First Wort" 
                                  #  this is the boil time.  For "Aroma" this 
                                  #  is the steep time.  For "Dry Hop" this is 
                                  #  the amount of time to dry hop.

    notes               = Field()
    form                = Field() # May be "Pellet", "Plug" or "Leaf".
    origin              = Field()


class Fermentable(Node):

    name                = Field()

    type                = Field() # May be "Grain", "Sugar", "Extract", 
                                  # "Dry Extract" or "Adjunct".  Extract 
                                  # refers to liquid extract.

    amount              = Field() # Weight of the fermentable, extract or
                                  # sugar in Kilograms.

    YIELD               = Field() # yield (lower) is a reserved keyword
                                  # Percent dry yield (fine grain) for the
                                  # grain, or the raw yield by weight if This
                                  # is an extract adjunct or sugar.

    color               = Field() # The color of the item in Lovibond Units
                                  # (SRM for liquid extracts).

    origin              = Field()


class Yeast(Node):

    name                = Field()

    type                = Field() # May be "Ale", "Lager", "Wheat", "Wine" or
                                  # "Champagne".

    form                = Field() # May be "Liquid", "Dry", "Slant" or
                                  # "Culture".

    amount              = Field() # The amount of yeast, measured in liters.
                                  # For a starter this is the size of the 
                                  # starter.

    attenuation         = Field()
    add_to_secondary    = Field()


class Misc(Node):

    name                = Field()

    type                = Field() # May be "Spice", "Fining", "Water Agent",
                                  # "Herb", "Flavor" or "Other".

    use                 = Field() # May be "Boil", "Mash", "Primary",
                                  # "Secondary", "Bottling".

    time                = Field() # Amount of time the misc was boiled,
                                  # steeped, mashed, etc in minutes.

    amount              = Field() #  Amount of item used.  The default
                                  #  measurements are by weight, but this may 
                                  #  be the measurement in volume units if 
                                  #  AMOUNT_IS_WEIGHT is set to TRUE for this 
                                  #  record.  If a liquid it is in liters, if a 
                                  #  solid the weight is measured in 
                                  #  kilograms.

    amount_is_weight    = Field()


class Style(Node):
    name                = Field()

    category            = Field() #  Category that this style belongs to
                                  #  - usually associated with a group of 
                                  #  styles such as "English Ales" or
                                  #  "Amercian Lagers".

    category_number     = Field() #  Number or identifier associated with this
                                  #  style category.  For example in the BJCP 
                                  #  style guide, the "American Lager" category 
                                  #  has a category number of "1".

    style_letter        = Field() #  The specific style number or subcategory
                                  #  letter associated with this particular 
                                  #  style.  For example in the BJCP style 
                                  #  guide, an American Standard Lager would be 
                                  #  style letter "A" under the main category.  
                                  #  Letters should be upper case.

    style_guide         = Field() #  The name of the style guide that this
                                  #  particular style or category belongs to.  
                                  #  For example "BJCP" might denote the BJCP 
                                  #  style guide, and "AHA" would be used for 
                                  #  the AHA style guide.

    type                = Field() #  May be "Lager", "Ale", "Mead", "Wheat",
                                  #  "Mixed" or "Cider".  Defines the type of 
                                  #  beverage associated with this category.

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


class Recipe(Node):

    name                = Field()
    type                = Field()
    style               = Field()
    brewer              = Field()
    batch_size          = Field()
    boil_size           = Field()
    boil_time           = Field()
    efficiency          = Field()

    hops                = NodeSet(Hop)
    fermentables        = NodeSet(Fermentable)
    miscs               = NodeSet(Misc)
    yeasts              = NodeSet(Yeast)

    notes               = Field()
    fermentation_stages = Field()
    primary_age         = Field()
    primary_temp        = Field()
    secondary_age       = Field()
    secondary_temp      = Field()
    tertiary_age        = Field()
    tertiary_temp       = Field()
