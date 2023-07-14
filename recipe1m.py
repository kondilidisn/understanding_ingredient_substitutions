import json
import os.path
import pickle
from collections import defaultdict
from tqdm import tqdm

from foodkg_graphdb_interface import *

def clean_ingredient_name(ingredient_name):
    return ingredient_name.replace('"', "")

def load_recipe1m_and_save_URL_to_ID_mappings(layer1_path:str="/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/Recipe1M Requirements/recipe1m/layer1.json",
                                              recipe1m_URL_to_ID_dict_pickle_path:str="Dataset/recipe1m_ID_to_URL_dict.pickle") -> None:

    with open(layer1_path, "r") as f:
        data = json.load(f)

    # recipe_URL_to_ID: dict[str:str] = dict()
    recipe_ID_to_URL: dict[str:str] = dict()

    for recipe in data:
        recipe_url = recipe["url"]
        recipe_id = recipe["id"]
        recipe_ID_to_URL[recipe_id] = recipe_url


    with open(recipe1m_URL_to_ID_dict_pickle_path, 'wb') as handle:
        pickle.dump(recipe_ID_to_URL, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("Number of recipes read:", len(recipe_ID_to_URL))
    print("Recipe ID to URL mappings saved at:", recipe1m_URL_to_ID_dict_pickle_path)


    # with open('filename.pickle', 'rb') as handle:
    #     b = pickle.load(handle)


def needs_update_explore_subs1m_recipe_ingredients(
        subs1m_pickle_dir: str = "/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/Recipe1M Requirements/recipe1m/preprocessed_flavorgraph_substitutions_fixed_3_no_flavorgraph",
        split: str = "val", recipe1m_URL_to_ID_dict_pickle_path: str = "Dataset/recipe1m_ID_to_URL_dict.pickle",
        subs1m_comment_subs_dir="/Users/kondy/PycharmProjects/gismo/gismo/checkpoints") -> None:
    # read subs1m preprocessed files of recipes
    subs1m_filepath = os.path.join(subs1m_pickle_dir, "final_recipe1m_" + split + ".pkl")
    with open(subs1m_filepath, 'rb') as file:
        subs1m_recipes = pickle.load(file)

    # read subs1m preprocessed files of substitutions
    subs1m_comment_subs = os.path.join(subs1m_comment_subs_dir, split + "_comments_subs.pkl")
    with open(subs1m_comment_subs, 'rb') as file:
        subs1m_comment_subs_pickle = pickle.load(file)

    with open(recipe1m_URL_to_ID_dict_pickle_path, 'rb') as file:
        recipe1m_ID_to_URL_dict = pickle.load(file)

    ingredient_found_as_IRI: set[str] = set()

    ingredient_not_found_at_all: set[str] = set()

    ingredient_not_found_by_IRI_but_found_by_name: set[str] = set()

    print("Number of recipes in split '" + split + "':", len(subs1m_recipes))

    for recipe in subs1m_recipes:
        recipe_id: str = recipe["id"]
        recipe_ingredients: list[str] = recipe["ingredients"]
        # recipe_title:list[str] = recipe["title"]
        # print(recipe_id)
        # print(recipe_ingredients)
        # print(recipe1m_ID_to_URL_dict[recipe_id])
        # break

        for ingredient_name in recipe_ingredients:
            # remove any quotes
            ingredient_name_clean = ingredient_name.replace('"', "")
            # if we have seen this ingredient before:
            if ingredient_name_clean in ingredient_found_as_IRI or \
                    ingredient_name_clean in ingredient_not_found_by_IRI_but_found_by_name or \
                    ingredient_name_clean in ingredient_not_found_at_all:
                continue
            # print(ingredient)
            ingredient_name_as_IRI = ingredient_name_clean.replace("_", "%20")
            ingredient_exists = check_if_ingredient_name_exists_in_foodKG_as_IRI(ingredient_iri=ingredient_name_as_IRI)
            # print(ingredient_name, ingredient_exists)
            if ingredient_exists:
                ingredient_found_as_IRI.add(ingredient_name_clean)
            else:
                if check_if_ingredient_name_exists_as_rdfs_label(
                        ingredient_name=ingredient_name_clean.replace("_", " ")):
                    ingredient_not_found_by_IRI_but_found_by_name.add(ingredient_name_clean)
                else:
                    ingredient_not_found_at_all.add(ingredient_name_clean)

        # break

    total_ingredients = len(ingredient_found_as_IRI) + len(ingredient_not_found_by_IRI_but_found_by_name) + len(
        ingredient_not_found_at_all)
    print("Total number of ingredients:", total_ingredients)
    print("Number of ingredients matched by IRI:", len(ingredient_found_as_IRI))
    print("Number of ingredients matched only by name:", len(ingredient_not_found_by_IRI_but_found_by_name))
    print("Number of ingredients not matched at all:", len(ingredient_not_found_at_all))



def create_recipe_substitution_foodkg_mappings(
        subs1m_pickle_dir: str = "/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/Recipe1M Requirements/recipe1m/preprocessed_flavorgraph_substitutions_fixed_3_no_flavorgraph",
        split: str = "val", recipe1m_URL_to_ID_dict_pickle_path: str = "Dataset/recipe1m_ID_to_URL_dict.pickle",
        subs1m_comment_subs_dir="/Users/kondy/PycharmProjects/gismo/gismo/checkpoints") -> None:
    # read subs1m preprocessed files of recipes
    subs1m_filepath = os.path.join(subs1m_pickle_dir, "final_recipe1m_" + split + ".pkl")
    with open(subs1m_filepath, 'rb') as file:
        subs1m_recipes = pickle.load(file)

    # read subs1m preprocessed files of substitutions
    subs1m_comment_subs = os.path.join(subs1m_comment_subs_dir, split + "_comments_subs.pkl")
    with open(subs1m_comment_subs, 'rb') as file:
        subs1m_comment_subs_pickle = pickle.load(file)

    with open(recipe1m_URL_to_ID_dict_pickle_path, 'rb') as file:
        recipe1m_ID_to_URL_dict = pickle.load(file)

    ratio_of_synonym_foodkg_matches_per_ingredient = 0

    total_original_sub_ingredient_mapped = 0
    total_new_sub_ingredient_mapped = 0
    complete_sub_ingredients_mapped = 0

    number_of_substitutions_per_recipe = defaultdict(int)

    ingredient_synonym_found: dict[str:str] = dict()

    ingredient_synonym_not_found: set[str] = set()

    total_substitutions_in_split = len(subs1m_comment_subs_pickle)

    average_ingredients_matched_per_recipe = 0



    recipe_IDs_with_ingredient_substitutions: dict[str:list[tuple[str, str]]] = dict()


    for substitution_entry in tqdm(subs1m_comment_subs_pickle):
        recipe_id = substitution_entry["id"]
        number_of_substitutions_per_recipe[recipe_id] += 1
        substitution = substitution_entry["subs"]
        # attempt to map ingredients involved in substitution to foodkg
        original_ingredient, new_ingredient = substitution
        original_ingredient_name_cleaned = clean_ingredient_name(original_ingredient)
        original_ingredient_IRI = match_ingredient_from_1Msubs_to_foodKG_by_IRI_or_name(original_ingredient_name_cleaned)
        if original_ingredient_IRI is not None:
            total_original_sub_ingredient_mapped += 1
        new_ingredient_name_cleaned = clean_ingredient_name(new_ingredient)
        new_ingredient_IRI = match_ingredient_from_1Msubs_to_foodKG_by_IRI_or_name(new_ingredient_name_cleaned)
        if new_ingredient_IRI is not None:
            total_new_sub_ingredient_mapped += 1
        if original_ingredient_IRI is not None and new_ingredient_IRI is not None:
            complete_sub_ingredients_mapped += 1
        # proceed with mapping all ingredients and their synonyms in this substitution entry
        ingredients_list_with_synonyms: list[list[str]] = substitution_entry["ingredients"]
        number_of_ingredients_in_recipe = len(ingredients_list_with_synonyms)
        number_of_matched_ingredients = 0
        food_KG_IRIs: list[list[str]] = list()
        for ingredient_with_synonyms in ingredients_list_with_synonyms:
            if

            number_of_synonym_matches = 0
            food_KG_IRIs.append(list())
            ingredient_matched = False
            for ingredient_name in ingredient_with_synonyms:

                # if we have found this ingredient in the past
                if ingredient_name in ingredient_synonym_found:
                    ingredient_matched = True
                    number_of_synonym_matches += 1
                    continue
                # if we know that we haven't found this ingredient before
                elif ingredient_name in ingredient_synonym_not_found:
                    continue
                # if we have not come across this ingredient before
                else:
                    # "clean" ingredient name:
                    ingredient_name_cleaned = clean_ingredient_name(ingredient_name)

                    ingredient_IRI = match_ingredient_from_1Msubs_to_foodKG_by_IRI_or_name(ingredient_name_cleaned)
                    if ingredient_IRI is None:
                        ingredient_synonym_not_found.add(ingredient_name)
                    else:
                        ingredient_synonym_found[ingredient_name] = ingredient_IRI
                        ingredient_matched = True
                        number_of_synonym_matches += 1
            if ingredient_matched:
                number_of_matched_ingredients += 1


        recipe_ingredients_matched_ratio = number_of_matched_ingredients / number_of_ingredients_in_recipe
        average_ingredients_matched_per_recipe += recipe_ingredients_matched_ratio

    average_ingredients_matched_per_recipe /= total_substitutions_in_split

    total_ingredient_synonyms = len(ingredient_synonym_found) + len(ingredient_synonym_not_found)

    ratio_of_synonym_foodkg_matches_per_ingredient = len(ingredient_synonym_found) / total_ingredient_synonyms

    histogram_number_of_recipes_wrt_number_of_subs = defaultdict(int)

    for recipe_id in number_of_substitutions_per_recipe:
        histogram_number_of_recipes_wrt_number_of_subs[number_of_substitutions_per_recipe[recipe_id]] += 1



    # split stats:
    print("Statistics regarding Substitution data in split:", split)
    print("Number of substitutions:", total_substitutions_in_split)
    print("Number of recipes WRT number of subs histogram :", histogram_number_of_recipes_wrt_number_of_subs)

    # ingredient synonym mapping info, regardless of which recipe they belong to:
    print("Total number of ingredient synonyms:", total_ingredient_synonyms)
    print("Number of ingredient synonyms matched to FoodKG IRI:", len(ingredient_synonym_found))
    print("Number of ingredient synonyms not matched at all:", len(ingredient_synonym_not_found))
    print("Synonym to FoodKG mappings ratio:", ratio_of_synonym_foodkg_matches_per_ingredient)

    # substitution statistics:
    print("Substitutions with both ingredients matched:", complete_sub_ingredients_mapped)
    print("Substitutions with original ingredient matched:", total_original_sub_ingredient_mapped)
    print("Substitutions with new ingredient matched:", total_new_sub_ingredient_mapped)

    print("Average ingredients mapped per recipe ratio:", average_ingredients_matched_per_recipe)


    # Statistics regarding Substitution data in split: val
    # Number of substitutions: 10729
    # Number of recipes WRT number of subs histogram :
    #   defaultdict(<class 'int'>, {1: 4863, 4: 140, 5: 82, 2: 1034, 3: 379, 6: 51, 9: 13, 12: 8, 10: 17, 8: 24, 7: 19, 11: 12, 13: 5, 18: 3, 23: 1, 19: 4, 14: 3, 20: 1, 17: 1, 15: 3, 33: 1, 45: 1, 29: 2, 30: 1, 16: 1, 21: 1})
    # Total number of ingredient synonyms: 5756
    # Number of ingredient synonyms matched by IRI: 4322
    # Number of ingredient synonyms not matched at all: 1434
    # Synonym to FoodKG mappings ratio: 0.750868658790827
    # Substitutions with both ingredients matched: 7892
    # Substitutions with original ingredient matched: 8907
    # Substitutions with new ingredient matched: 8897
    # Average ingredients mapped per recipe ratio: 0.9526823613737557



# explore_subs1m_recipe_ingredients()
create_recipe_substitution_foodkg_mappings()