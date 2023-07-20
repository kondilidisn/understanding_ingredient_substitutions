from rdflib import URIRef, Graph, Namespace

def ingredient_prefix_to_namespace(prefix:str):
    ontology_prefix_to_namespace_dict: dict = dict()
    ontology_prefix_to_namespace_dict["obo"] = "http://purl.obolibrary.org/obo/"
    if prefix in ontology_prefix_to_namespace_dict:
        return ontology_prefix_to_namespace_dict[prefix]
    else:
        raise ValueError(f"ontology prefix {prefix} not found!")

def calculate_f1_score(set_a: set, set_b: set) -> float:
    intersection_set_size = len(set_a.intersection(set_b))
    if intersection_set_size == 0:
        return 0
    precision = intersection_set_size / len(set_a)
    recall = intersection_set_size / len(set_b)
    f1_score: float = 2 * (precision + recall) / (precision + recall)
    return f1_score
