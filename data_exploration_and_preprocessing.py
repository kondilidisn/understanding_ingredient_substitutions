import os.path
from typing import Iterable, Optional, Tuple, Union, cast, Any, List, Type, Dict, DefaultDict
import json
from collections import defaultdict

import rdflib
from rdflib import Graph, Dataset, Literal
from rdflib.term import Node
from rdflib.namespace import RDF, URIRef, OWL

from rdflib import Namespace

import csv

def load_json_file(json_filename):
    with open(json_filename) as json_file:
        return json.load(json_file)


# EaT-PIM directory:
# small version with 2 recipes
# eat_pim_processed_recipes_dir: str = "/Users/kondy/Desktop/PhD/Recipes/EaT-PIM/data/test_out_dir"

# # bigger version with 1000 recipes
eat_pim_processed_recipes_dir:str = "/Users/kondy/Desktop/PhD/Recipes/EaT-PIM/data/1000_out"

# EaT-PIM files:
# outputs of First step:
parsed_recipes_csv_filename: str = "selected_recipes.csv"
parsed_recipes_pickle_filename: str = "parsed_recipes.pkl"
# outputs of Second step:
ingredient_vocabulary_filename: str = "ingredient_list.json"  # contains a list
ingredient_linking_information_filename: str = "word_cleanup_linking.json"  # contents example:

    # obj_to_ing
    #   e.g. "cooking spray": [], "egg": ["egg"]
    # obj_to_subobj
    #   e.g. "12 minute": ["minute"], "flour mixture": []
    # obj_leftovers
    #   e.g. "baking sheet": "baking sheet", "dough": "dough"
    # ing_to_ing
    #   e.g. "baking soda": [], "salt": []
    # ing_to_foodon
    #   e.g.
    #         {  "vodka": ["http://purl.obolibrary.org/obo/FOODON_03305518"],
    #         "dried tart cherry": ["http://purl.obolibrary.org/obo/FOODON_03302954"],
    # obj_to_foodon
    #   e.g.
    #         {  "flour": ["http://purl.obolibrary.org/obo/FOODON_00001056"],
    #         “egg": ["http://purl.obolibrary.org/obo/FOODON_00001274"]
    # obj_to_equipment
    #   e.g.
    #         {"measuring cup": ["http://www.wikidata.org/entity/Q907099"],
    #         "egg": ["http://www.wikidata.org/entity/Q3006816"],
    # verb_to_preparations
    #   e.g.
    #         {"bake": ["http://www.wikidata.org/entity/Q720398"],
    #         “brown": ["http://www.wikidata.org/entity/Q2760809"]

# outputs of Third step:
entity_relations_filename: str = "entity_relations.json"  # contains relations between entities like for example sub -> probably meaning subclass
recipe_flow_graph_filename: str = "recipe_tree_data.json"  # contains dictionaries with recipe IDs as keys, and each of them has:
# edges: a list of lists of length two e.g.
# - ["pred_level_239786_2", "pred_combine_239786_3"],
# - ["pred_combine_239786_3", "pred_cream_239786_5"], …
# edge_labels: a list of equal length with the above, with string elements that describe the type of edges of the previous list. E.g.
# "RECIPE OUTPUT", "pred combine", “pred cream”, “pred stir”...
# output_node: the “name” of the output node of the recipe  e.g. “RECIPE_OUTPUT_232849”


kaggle_ingredient_substitutions_dir: str = "/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/Ingredient Substitution/FoodSubstitutionDataScripts/parse_fooddotcom_reviews/out_files"
ingredient_substitution_URI_pairs_json_filename: str = "fooddotcom_review_sub_data_URIs.json"


foodkg_iswc_dir: str = "/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/foodkg.github.io/src/recipe-handler/out/iswc"
foodkg_core_filename: str = "foodkg-core.trig"
foodkg_foodon_links_filename: str = "foodon-links.trig"
foodkg_usda_links_filename: str = "usda-links.trig"


usda_ingredient_nutritional_information_csv_filename: str = "Dataset/usda.csv"



def load_foodon_foodkg_links(link_filepath: str = None) -> Graph:

    foodon_to_foodkg_equivalent_classes_filename: str = "Dataset/foodon_foodkd_eq_classes_graph.ttl"
    foodon_to_foodkg_equivalent_classes_graph: Graph = Graph()

    # see if preprocessed file already exists
    if os.path.exists(foodon_to_foodkg_equivalent_classes_filename):
        foodon_to_foodkg_equivalent_classes_graph.parse(foodon_to_foodkg_equivalent_classes_filename)
        # return foodon_to_foodkg_equivalent_classes_graph
    else:
        if link_filepath is None:
            raise ValueError("Path to load foodon-foodkg links was not provided")

        foodkd_ingredients: set[Node] = set()
        foodon_ingredients: set[Node] = set()

        foodkg_alignments_iswc_dataset = Dataset()
        foodkg_alignments_iswc_dataset.parse(link_filepath)

        for foodkg_IRI, _, foodon_IRI, _ in foodkg_alignments_iswc_dataset.quads((None, OWL.equivalentClass, None, None)):
            foodkd_ingredients.add(foodkg_IRI)
            foodon_ingredients.add(foodon_IRI)
            foodon_to_foodkg_equivalent_classes_graph.add((foodon_IRI, OWL.equivalentClass, foodkg_IRI))

        foodon_to_foodkg_equivalent_classes_graph.serialize(destination=foodon_to_foodkg_equivalent_classes_filename)

        print("Number of FoodKG-FoodOn links read from file:", len(foodon_to_foodkg_equivalent_classes_graph))
        # Number of FoodKG-FoodOn links read from file: 16780
        print("Number of FoodKG IRIs:", len(foodkd_ingredients))
        # Number of FoodKG IRIs: 16780
        print("Number of FoodOn IRIs:", len(foodon_ingredients))
        # Number of FoodOn IRIs: 2267
        print("Links saved in RDFLib graph form in:", foodon_to_foodkg_equivalent_classes_filename)

    return foodon_to_foodkg_equivalent_classes_graph


def load_foodkg_usda_links(link_filepath: str = None) -> Graph:

    foodkg_to_usda_equivalent_classes_filename: str = "Dataset/foodkg_usda_eq_classes_graph.ttl"
    foodkg_to_usda_equivalent_classes_graph: Graph = Graph()

    # see if preprocessed file already exists
    if os.path.exists(foodkg_to_usda_equivalent_classes_filename):
        foodkg_to_usda_equivalent_classes_graph.parse(foodkg_to_usda_equivalent_classes_filename)
        # return foodon_to_foodkg_equivalent_classes_graph
    else:
        if link_filepath is None:
            raise ValueError("Path to load foodkg-usda links was not provided")

        foodkd_ingredients: set[Node] = set()
        usda_ingredients: set[Node] = set()

        foodkg_alignments_iswc_dataset = Dataset()
        foodkg_alignments_iswc_dataset.parse(link_filepath)

        for foodkg_IRI, _, usda_IRI, _ in foodkg_alignments_iswc_dataset.quads((None, OWL.equivalentClass, None, None)):
            foodkd_ingredients.add(foodkg_IRI)
            usda_ingredients.add(usda_IRI)
            foodkg_to_usda_equivalent_classes_graph.add((foodkg_IRI, OWL.equivalentClass, usda_IRI))

        foodkg_to_usda_equivalent_classes_graph.serialize(destination=foodkg_to_usda_equivalent_classes_filename)

        print("Number of FoodKG-USDA links read from file:", len(foodkg_to_usda_equivalent_classes_graph))
        # Number of FoodKG-USDA links read from file: 16203
        print("Number of FoodKG IRIs:", len(foodkd_ingredients))
        # Number of FoodKG IRIs: 16203
        print("Number of USDA IRIs:", len(usda_ingredients))
        # Number of USDA IRIs: 1481
        print("Links saved in RDFLib graph form in:", foodkg_to_usda_equivalent_classes_graph)

    return foodkg_to_usda_equivalent_classes_graph


def usda_ID_to_IRI(usda_ID:int) -> Node:
    return URIRef("http://idea.rpi.edu/heals/kb/usda#" + str(usda_ID))

def usda_IRI_to_ID(usda_IRI: Node) -> int:
    return int(str(usda_IRI).split("#")[-1])

def calculate_histogram_and_total_key_value_pairs(dictionary: dict[set]) -> Tuple[dict[int:int], int]:
    histogram = defaultdict(int)
    total_key_value_pairs = 0
    for key in dictionary:
        number_of_values = len(dictionary[key])
        histogram[number_of_values] += 1
        total_key_value_pairs += number_of_values
    return dict(histogram), total_key_value_pairs



def read_USDA_ingredient_nutritional_information_from_csv(usda_csv_filepath:str="Dataset/usda.csv") -> Tuple[list[str], dict[int: str], dict[int: list[Union[float, int]]]]:
    # read the usda nutritional info

    usda_id_to_name_dict: dict[int: str] = dict()

    usda_id_to_nutritional_info: dict[int: list[Union[float, int]]] = dict()

    with open(usda_csv_filepath, newline='') as csvfile:

        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        # read column names:
        for row in csv_reader:
            nutritional_info_categories: list[str] = row[2:-1]
            break

        # for each next row, read and store ingredient ID, ingredient Name, and its nutritional information
        for row in csv_reader:
            ingredient_id = int(row[0])
            ingredient_name = row[1]
            usda_id_to_name_dict[ingredient_id] = ingredient_name
            ingredient_nutritional_info = row[2:-1]
            usda_id_to_nutritional_info[ingredient_id] = ingredient_nutritional_info

        print("Read nutritional information from file:", usda_csv_filepath, ", for ", len(usda_id_to_name_dict), "number of ingredients.")

        return nutritional_info_categories, usda_id_to_name_dict, usda_id_to_nutritional_info


def relate_usda_ingredients_with_foodkg_IRIs(foodkg_to_usda_equivalent_classes_graph:Graph, usda_id_to_name_dict:dict[int: str], foodon_to_foodkg_equivalent_classes_graph:Graph ) -> None:
    # see how many of the ingredients that have information in USDA_IDs are in the usda foodkg mappings
    subset_of_used_usda_foodkg_mappings_used = Graph()

    usda_ID_to_food_on_IRI: DefaultDict[int:set[Node]] = defaultdict(set)

    # unique_usda_IDs = set()

    number_of_used_usda_foodkg_mappings_used: int = 0

    # for each foodkg - usda mapping
    for foodkg_IRI, _, usda_ID_IRI in foodkg_to_usda_equivalent_classes_graph.triples((None, OWL.equivalentClass, None)):
        usda_ID = usda_IRI_to_ID(usda_ID_IRI)

        # extract the usda ID from the IRI
        if usda_ID in usda_id_to_name_dict:
            # subset_of_used_usda_foodkg_mappings_used.add((usda_ID_IRI, OWL.equivalentClass, foodkg_IRI))
            number_of_used_usda_foodkg_mappings_used += 1

            # food_kg_IRI_to_usda_name_dict[foodkg_IRI] = usda_id_to_name_dict[usda_ID]
            # unique_usda_IDs.add(usda_ID)

            for foodon_IRI in foodon_to_foodkg_equivalent_classes_graph.subjects(OWL.equivalentClass, foodkg_IRI):
                usda_ID_to_food_on_IRI[usda_ID].add(foodon_IRI)



    print("Used USDA-FoodKG mappings:", number_of_used_usda_foodkg_mappings_used)
    # Used USDA-FoodKG mappings: 15467
    print("Over", len(usda_ID_to_food_on_IRI), "number of USDA distinct ingredients.")
    # Over 1379 number of USDA distinct ingredients.

    foodon_IRI_to_usda_ID: DefaultDict[Node:set[int]] = defaultdict(set)

    number_of_used_foodOn_foodkg_mappings_used:int = 0

    # for each foodOn - foodkg mapping
    for foodon_IRI, _, foodkg_IRI in foodon_to_foodkg_equivalent_classes_graph.triples((None, OWL.equivalentClass, None)):

        for usda_ID_IRI in foodkg_to_usda_equivalent_classes_graph.objects(foodkg_IRI, OWL.equivalentClass):
            usda_ID = usda_IRI_to_ID(usda_ID_IRI)
            # if we have nutritional information about this ingredient
            if usda_ID in usda_ID_to_food_on_IRI:
                foodon_IRI_to_usda_ID[foodon_IRI].add(usda_ID)
                number_of_used_foodOn_foodkg_mappings_used += 1


    print("Used FoodOn-FoodKG mappings:", number_of_used_foodOn_foodkg_mappings_used)
    # Used FoodOn-FoodKG mappings: 15143
    print("Over", len(foodon_IRI_to_usda_ID), "number of FoodOn distinct entities.")
    # Over 2037 number of FoodOn distinct entities.

    foodon_to_usda_ID_histogram, food_on_to_usda_total_mappings = calculate_histogram_and_total_key_value_pairs(dict(foodon_IRI_to_usda_ID))
    print("Total FoodOn - USDA mappings:", food_on_to_usda_total_mappings)

    max_frequency_to_print = 10
    print("The histogram of their connections is: (max frequency printed is", max_frequency_to_print, ")")
    for i in range(1, min(max_frequency_to_print + 1, max(foodon_to_usda_ID_histogram.keys()) + 1)):
        if i in foodon_to_usda_ID_histogram:
            print(i, foodon_to_usda_ID_histogram[i])


    usda_to_foodon_histogram, usda_to_foodon_total_mappings = calculate_histogram_and_total_key_value_pairs(dict(usda_ID_to_food_on_IRI))
    # print("Total USDA - FoodOn mappings:", usda_to_foodon_total_mappings)

    print("The histogram of their connections is: (max frequency printed is", max_frequency_to_print, ")")
    for i in range(1, min(max_frequency_to_print + 1, max(usda_to_foodon_histogram.keys()) + 1)):
        if i in usda_to_foodon_histogram:
            print(i, usda_to_foodon_histogram[i])


def calculate_usda_foodon_mappings() -> None:
    foodon_to_foodkg_equivalent_classes_graph = load_foodon_foodkg_links(os.path.join(foodkg_iswc_dir, foodkg_foodon_links_filename))
    foodkg_to_usda_equivalent_classes_graph = load_foodkg_usda_links(os.path.join(foodkg_iswc_dir, foodkg_usda_links_filename))
    nutritional_info_categories, usda_id_to_name_dict, usda_id_to_nutritional_info = \
        read_USDA_ingredient_nutritional_information_from_csv(usda_csv_filepath=usda_ingredient_nutritional_information_csv_filename)

    relate_usda_ingredients_with_foodkg_IRIs(
        foodkg_to_usda_equivalent_classes_graph=foodkg_to_usda_equivalent_classes_graph,
        usda_id_to_name_dict=usda_id_to_name_dict,
        foodon_to_foodkg_equivalent_classes_graph=foodon_to_foodkg_equivalent_classes_graph)



def link_recipe_ingredients(eat_pim_processed_recipes_dir:str, ingredient_vocabulary_filename:str, ingredient_linking_information_filename:str) -> None:

    ingredients_list = load_json_file(os.path.join(eat_pim_processed_recipes_dir, ingredient_vocabulary_filename))
    print("Number of Ingredients:", len(ingredients_list))

    linking_information_dict: dict = load_json_file(os.path.join(eat_pim_processed_recipes_dir, ingredient_linking_information_filename))

    ingredient_to_foodon_dict: dict[str, list[str]] = linking_information_dict["ing_to_foodon"]
    print("foodON mappings:", len(ingredient_to_foodon_dict))

    # print("total ingredients:", len(ingredients_list))
    number_of_ingredients_with_foodon_link: int = 0

    number_of_ingredients_with_multiple_mappings: int = 0

    number_of_ingredients_with_foodkg_link: int = 0

    foodon_to_foodkg_equivalent_classes_graph = load_foodon_foodkg_links(os.path.join(foodkg_iswc_dir, foodkg_foodon_links_filename))

    for ingredient in ingredients_list:
        if ingredient in ingredient_to_foodon_dict:
            number_of_ingredients_with_foodon_link += 1
            foodon_IRI = URIRef(ingredient_to_foodon_dict[ingredient][0])
            if len(ingredient_to_foodon_dict[ingredient]) > 1:
                number_of_ingredients_with_multiple_mappings += 1

            foodkg_IRI_list: list[Node] = list(foodon_to_foodkg_equivalent_classes_graph.objects(subject=foodon_IRI, predicate=OWL.equivalentClass))

            if len(foodkg_IRI_list) > 0:
                number_of_ingredients_with_foodkg_link += 1


    print("number of ingredient to FoodOn mappings:", number_of_ingredients_with_foodon_link)
    print("number of ingredient to Food KG mappings:", number_of_ingredients_with_foodkg_link)



def load_processed_recipe_flow_graphs(eat_pim_processed_recipes_dir:str, recipe_flow_graph_filename:str) -> dict[str, Graph]:
    recipe_graphs_dict: dict[str, Graph] = dict()

    recipe_trees_dict = load_json_file(os.path.join(eat_pim_processed_recipes_dir, recipe_flow_graph_filename))

    for recipe_id in recipe_trees_dict:
        recipe_graphs_dict[recipe_id] = Graph()

        recipe_length = len(recipe_trees_dict[recipe_id]["edge_labels"])
        for i in range(recipe_length):
            edge_node_A, edge_node_B = recipe_trees_dict[recipe_id]["edges"][i]
            edge_label = recipe_trees_dict[recipe_id]["edge_labels"][i]



            # for now we add construct the recipe graph with Literals.
            # TODO: make all connections between these literals and ontology IRIs.
            recipe_graphs_dict[recipe_id].add((Literal(edge_node_A), Literal(edge_label), Literal(edge_node_B)))

    return recipe_graphs_dict



if __name__ == '__main__':
    # calculate_usda_foodon_mappings()


    # load_processed_recipe_flow_graphs(eat_pim_processed_recipes_dir, recipe_flow_graph_filename)

    link_recipe_ingredients(eat_pim_processed_recipes_dir, ingredient_vocabulary_filename, ingredient_linking_information_filename)
    # pass
