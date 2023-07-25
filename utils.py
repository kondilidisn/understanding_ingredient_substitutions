from rdflib import URIRef, Graph, Namespace

def ingredient_prefix_to_namespace(prefix:str) -> str:
    ontology_prefix_to_namespace_dict: dict = dict()
    ontology_prefix_to_namespace_dict["obo"] = "http://purl.obolibrary.org/obo/"
    if prefix in ontology_prefix_to_namespace_dict:
        return ontology_prefix_to_namespace_dict[prefix]
    else:
        raise ValueError(f"ontology prefix {prefix} not found!")

def ingredient_property_category_to_query_result_csv_filepath(property_category:str) -> str:
    ingredient_properties_directory: str = "Dataset/Ingredient_properties/"
    property_category_to_filename: dict = dict()
    property_category_to_filename["foodOn"] = "foodOn_ing_properties.csv"
    property_category_to_filename["foodOn_one_hop"] = "one_hop_foodOn_ing_properties.csv"
    property_category_to_filename["foodOn_all_hops"] = "all_hops_foodOn_ing_properties.csv"
    if property_category in property_category_to_filename:
        return ingredient_properties_directory +  property_category_to_filename[property_category]
    else:
        raise ValueError(f"Property category {property_category} not found!")

def calculate_f1_score(set_a: set, set_b: set) -> float:
    intersection_set_size = len(set_a.intersection(set_b))
    if intersection_set_size == 0:
        return 0
    precision = intersection_set_size / len(set_a)
    recall = intersection_set_size / len(set_b)
    f1_score: float = 2 * (precision + recall) / (precision + recall)
    return f1_score
