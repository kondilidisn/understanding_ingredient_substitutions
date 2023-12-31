from typing import Iterable, Optional, Tuple, Union, cast, Any
import json


def load_json_file(json_filename):
    with open(json_filename) as json_file:
        return json.load(json_file)


# EaT-PIM directory:
# small version with 2 recipes
eat_pim_processed_recipes_dir: str = "/Users/kondy/Desktop/PhD/Recipes/EaT-PIM/data/test_out_dir"

# # bigger version with 1000 recipes
# eat_pim_processed_recipes_dir:str = "/Users/kondy/Desktop/PhD/Recipes/EaT-PIM/data/1000_out"

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


if __name__ == '__main__':
    pass
