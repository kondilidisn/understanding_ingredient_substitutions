
from typing import Iterable, Optional, Tuple, Union, cast, Any, List, Type
from rdflib import Graph, Dataset
from rdflib.term import Node
from rdflib.namespace import RDF, URIRef, OWL

class Recipe:
    def __init__(self, recipe_id) -> None:
        self.recipe_id = recipe_id
        self.recipe_tree = Graph()

        pass
