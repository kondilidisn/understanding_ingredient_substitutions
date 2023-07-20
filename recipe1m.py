import json
import os.path
import pickle
from collections import defaultdict
from tqdm import tqdm
from rdflib import Graph, Literal, RDF, URIRef, Namespace

from foodkg_graphdb_interface import *


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


def depricated_get_statistics_of_substitution_data_and_foodKG_mappings(foodkg_graphdb_interface:FoodKGGraphDBInterface,
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

    # with open(recipe1m_URL_to_ID_dict_pickle_path, 'rb') as file:
    #     recipe1m_ID_to_URL_dict = pickle.load(file)

    ratio_of_synonym_foodkg_matches_per_ingredient = 0



    total_original_sub_ingredient_mapped = 0
    total_new_sub_ingredient_mapped = 0
    complete_sub_ingredients_mapped = 0

    number_of_substitutions_per_recipe = defaultdict(int)

    ingredient_synonym_found: dict[str:str] = dict()

    ingredient_synonym_not_found: set[str] = set()

    total_substitutions_in_split = len(subs1m_comment_subs_pickle)

    average_ingredients_matched_per_recipe = 0



    # recipe_IDs_with_ingredient_substitutions: dict[str:list[tuple[str, str]]] = dict()


    for substitution_entry in tqdm(subs1m_comment_subs_pickle):



        recipe_id = substitution_entry["id"]

        # retrieve all ingredients of this recipe from FoodKG
        # recipe_url = recipe1m_ID_to_URL_dict[recipe_id]
        # remaining_unmatched_recipe_ingredients_foodKG_IRIs_set:set[str] = set(get_FoodKG_ingredient_IRIs_of_recipe_given_url(recipe_url=recipe_url))

        # attempt to map ingredients involved in substitution to foodkg
        original_ingredient_IRI = foodkg_graphdb_interface.get_ingredient_short_IRI_from_1Msubs_to_foodKG_by_IRI_or_name(
            original_ingredient)
        if original_ingredient_IRI is not None:
            total_original_sub_ingredient_mapped += 1

        new_ingredient_IRI = foodkg_graphdb_interface.get_ingredient_short_IRI_from_1Msubs_to_foodKG_by_IRI_or_name(
            new_ingredient)
        if new_ingredient_IRI is not None:
            total_new_sub_ingredient_mapped += 1
        if original_ingredient_IRI is not None and new_ingredient_IRI is not None:
            complete_sub_ingredients_mapped += 1

        original_ingredient_index_in_list_of_ingredient_synonyms:Optional[int] = None

        number_of_substitutions_per_recipe[recipe_id] += 1
        substitution = substitution_entry["subs"]
        original_ingredient, new_ingredient = substitution

        # proceed with mapping all ingredients and their synonyms in this substitution entry
        ingredients_list_with_synonyms: list[list[str]] = substitution_entry["ingredients"]
        number_of_ingredients_in_recipe = len(ingredients_list_with_synonyms)
        number_of_matched_ingredients = 0
        food_KG_IRIs: list[set[str]] = list()
        for ingredient_index, ingredient_with_synonyms in enumerate(ingredients_list_with_synonyms):
            number_of_synonym_matches = 0
            food_KG_IRIs.append(set())
            if original_ingredient in ingredient_with_synonyms:
                original_ingredient_index_in_list_of_ingredient_synonyms = ingredient_index
            for ingredient_name in ingredient_with_synonyms:

                # if we have found this ingredient in the past
                if ingredient_name in ingredient_synonym_found:
                    food_KG_IRIs[-1].add(ingredient_synonym_found[ingredient_name])
                    ingredient_matched = True
                    number_of_synonym_matches += 1
                    continue
                # if we know that we haven't found this ingredient before
                elif ingredient_name in ingredient_synonym_not_found:
                    continue
                # if we have not come across this ingredient before
                else:
                    ingredient_IRI = foodkg_graphdb_interface.get_ingredient_short_IRI_from_1Msubs_to_foodKG_by_IRI_or_name(ingredient_name)
                    if ingredient_IRI is None:
                        ingredient_synonym_not_found.add(ingredient_name)
                    else:
                        food_KG_IRIs[-1].add(ingredient_synonym_found[ingredient_name])
                        ingredient_synonym_found[ingredient_name] = ingredient_IRI
                        ingredient_matched = True
                        number_of_synonym_matches += 1
            # if at least some synonyms were mapped to FoodKG IRIs
            if len(food_KG_IRIs[-1]) > 0:
                number_of_matched_ingredients += 1
                # let's see if at least one of the matched FoodKG IRIs of the synonyms
                # matches one of the ingredients in FoodKG ingredient knowledge of this recipe
                # if

        # # let's map the original ingredient of the substitution to the index of its list of synonyms from the recipe
        # for
        #
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


def create_graph_with_recipes_and_substitutions_in_FoodKG(foodkg_graphdb_interface:FoodKGGraphDBInterface,
        # subs1m_pickle_dir: str = "/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/Recipe1M Requirements/recipe1m/preprocessed_flavorgraph_substitutions_fixed_3_no_flavorgraph",
        split: str = "val", recipe1m_URL_to_ID_dict_pickle_path: str = "Dataset/recipe1m_ID_to_URL_dict.pickle",
        subs1m_comment_subs_dir="/Users/kondy/PycharmProjects/gismo/gismo/checkpoints") -> None:


    output_graph_filename = 'Dataset/substitutions_graph_' + split + '.ttl'
    log_file_path: str = "Dataset/log_of_creating_subs_graph_foodkg_" + split + '.log'

    not_found_ingredients:set[str] = set()


    log_file = open(log_file_path, 'w')

    log_file.write("original_ing_not_found" + "\t" + "recipe_url" + "\n")

    # read subs1m preprocessed files of recipes
    # subs1m_filepath = os.path.join(subs1m_pickle_dir, "final_recipe1m_" + split + ".pkl")
    # with open(subs1m_filepath, 'rb') as file:
    #     subs1m_recipes = pickle.load(file)

    # read subs1m preprocessed files of substitutions
    subs1m_comment_subs = os.path.join(subs1m_comment_subs_dir, split + "_comments_subs.pkl")
    with open(subs1m_comment_subs, 'rb') as file:
        subs1m_comment_subs_pickle = pickle.load(file)

    with open(recipe1m_URL_to_ID_dict_pickle_path, 'rb') as file:
        recipe1m_ID_to_URL_dict = pickle.load(file)

    # create the rdflib graph and define the appropriate URIRefs
    substitutions_foodKG_graph = Graph()
    substitutions_namespace = Namespace("http://lr.cs.vu.nl/ingredient_substitutions#")
    uses_ingredient_predicate = substitutions_namespace.term("uses_ingredient")
    has_suggested_substitution_predicate = substitutions_namespace.term("has_suggested_substitution")
    original_ingredient_predicate = substitutions_namespace.term("ingredient_b_iri")
    new_ingredient_predicate = substitutions_namespace.term("ingredient_a_iri")

    registered_substitutions_per_recipe_id_counter = defaultdict(int)

    new_ingredient_not_identified_in_foodKG_counter = 0
    original_ingredient_not_identified_in_foodKG_counter = 0
    identified_both_ingredients_counter = 0
    original_ingredient_matched_with_foodkg_iri_but_not_with_the_recipe_ingredients_counter = 0


    for substitution_entry in tqdm(subs1m_comment_subs_pickle):

        recipe_id = substitution_entry["id"]

        # retrieve all ingredients of this recipe from FoodKG
        recipe_url = recipe1m_ID_to_URL_dict[recipe_id]
        recipe_IRIs = get_recipe_IRIs_given_recipe_URL(recipe_url)

        # get ingredients involved in substitution
        substitution = substitution_entry["subs"]
        original_ingredient, new_ingredient = substitution

        if new_ingredient not in not_found_ingredients:
            # attempt to identify new ingredient in FoodKG
            new_ingredient_short_IRI = foodkg_graphdb_interface.get_ingredient_short_IRI_from_1Msubs_to_foodKG_by_IRI_or_name(new_ingredient)

        if new_ingredient in not_found_ingredients or new_ingredient_short_IRI is None:
            new_ingredient_not_identified_in_foodKG_counter += 1
            log_file.write("New:" + "\t" + new_ingredient + "\t" + recipe_url + "\n")
            not_found_ingredients.add(new_ingredient)
            continue

        if original_ingredient not in not_found_ingredients:

            # let's identify the original ingredient
            original_ingredient_short_iri: Optional[str] = None
            matched_recipe_uriref: Optional[URIRef] = None
            recipe_ingredients_foodKG_short_IRIs: Optional[List[str]] = None
            for recipe_iri in recipe_IRIs:

                recipe_ingredients_foodKG_short_IRIs: list[str] = foodkg_graphdb_interface.get_FoodKG_ingredient_short_IRIs_of_given_recipe_IRI(recipe_iri=recipe_iri)

                ingredients_list_with_synonyms: list[list[str]] = substitution_entry["ingredients"]

                # first let's try to directly match the original ingredient with its IRI in FoodKG
                # attempt to identify new ingredient in FoodKG
                original_ingredient_short_iri = foodkg_graphdb_interface.get_ingredient_short_IRI_from_1Msubs_to_foodKG_by_IRI_or_name(
                    original_ingredient)


                # if we have mapped the ingredient to some ingredient in FoodKG but not with any ingredient in the recipe ... WIP
                # if original_ingredient_short_iri is not None and original_ingredient_short_iri not in recipe_ingredients_foodKG_short_IRIs:
                # original_ingredient_matched_with_foodkg_iri_but_not_with_the_recipe_ingredients_counter += 1



                # if we didn't find the original ingredient in FoodKG,
                # or if we did, but it is not among the ingredients of the recipe
                if original_ingredient_short_iri is None or original_ingredient_short_iri not in recipe_ingredients_foodKG_short_IRIs:
                    # we make sure it doesn't have a wrong IRI at the moment, and try to identify the correct one
                    original_ingredient_short_iri = None
                    # We find its synonyms from the Subs1M dataset
                    # and try to match any of these with the ingredients of the recipe
                    # So, for all the lists of ingredients with their "synonyms"
                    for ingredient_with_synonyms in ingredients_list_with_synonyms:
                        # if the original ingredient was found in this list of synonyms
                        if original_ingredient in ingredient_with_synonyms:
                            # see which of the synonyms, matches one of the ingredient IRIs registered in FoodKG for this recipe
                            for ingredient_synonym_name in ingredient_with_synonyms:
                                # attempt to retrieve the FoodKG IRI of this ingredient form FoodKG
                                ingredient_short_IRI = foodkg_graphdb_interface.get_ingredient_short_IRI_from_1Msubs_to_foodKG_by_IRI_or_name(ingredient_synonym_name)
                                if ingredient_short_IRI in recipe_ingredients_foodKG_short_IRIs:
                                    original_ingredient_short_iri = ingredient_short_IRI
                                    break
                        else:
                            continue
                        # if we have identified the original ingredient's IRI
                        if original_ingredient_short_iri is not None:
                            break
                #  if we managed to identify the original ingredient in any of the matched recipe IRIs from FoodKG, we continue
                if original_ingredient_short_iri is not None:
                    # we also store the FoodKG IRI of the recipe that in which the original ingredient was identified
                    matched_recipe_uriref = URIRef(recipe_iri)
                    break

        if original_ingredient in not_found_ingredients or original_ingredient_short_iri is None:
            original_ingredient_not_identified_in_foodKG_counter += 1
            log_file.write("Old:" + "\t" + original_ingredient + "\t" + recipe_url + "\n")
            not_found_ingredients.add(original_ingredient)
            # print("Original Ingredient not identified:", ingredient_b_iri,  "recipe URL:", recipe_url)
            continue

        # # the original ingredient should always be identified
        # assert original_ingredient_short_iri is not None

        #  if both ingredients have been identified in FoodKG, then we can create an entry for this substitution.

        # if it is the first time we register a substitution for this recipe,
        # we need to also register the recipe and the ingredients
        if registered_substitutions_per_recipe_id_counter[recipe_id] == 0:
            # add all used ingredients to the graph
            for ingredient__short_iri in recipe_ingredients_foodKG_short_IRIs:
                ingredient_iri = URIRef(foodkg_graphdb_interface.get_foodk_ingredient_iri_prefix() + ingredient__short_iri)
                substitutions_foodKG_graph.add((matched_recipe_uriref, uses_ingredient_predicate, URIRef(ingredient_iri)))

        # create a new node for this specific substitution for this specific recipe
        substitution_node = substitutions_namespace.term("substitution_suggestion/"+ recipe_id + "/" \
                                            + str(registered_substitutions_per_recipe_id_counter[recipe_id]))

        # register the directed substitution node for this recipe (new node per substitution suggestion)
        substitutions_foodKG_graph.add((matched_recipe_uriref, has_suggested_substitution_predicate, substitution_node))
        # register the ingredients involved in this substitution
        original_ingredient_iri = foodkg_graphdb_interface.get_full_ingredient_iri_given_short_iri(original_ingredient_short_iri)
        substitutions_foodKG_graph.add((substitution_node, original_ingredient_predicate, URIRef(original_ingredient_iri)))
        new_ingredient_iri = foodkg_graphdb_interface.get_full_ingredient_iri_given_short_iri(new_ingredient_short_IRI)
        substitutions_foodKG_graph.add((substitution_node, new_ingredient_predicate, URIRef(new_ingredient_iri)))
        # increase the counter of substitutions registered successfully for this recipe
        registered_substitutions_per_recipe_id_counter[recipe_id] += 1
        identified_both_ingredients_counter += 1

    print(f"Total number of substitutions in split {split}, : {len(subs1m_comment_subs_pickle)}")
    log_file.write(f"Total number of substitutions in split {split}, : {len(subs1m_comment_subs_pickle)}\m")
    print("Times identified both ingredients of the suggested substitution:", identified_both_ingredients_counter)
    log_file.write("Times identified both ingredients of the suggested substitution: " + str(identified_both_ingredients_counter) + "\n")
    print("Times original ingredient not found:", original_ingredient_not_identified_in_foodKG_counter)
    log_file.write("Times original ingredient not found: " + str(original_ingredient_not_identified_in_foodKG_counter) + "\n")
    print("Times new ingredient not found:", new_ingredient_not_identified_in_foodKG_counter)
    log_file.write("Times new ingredient not found: " + str(new_ingredient_not_identified_in_foodKG_counter) + "\n")
    print("Total ingredients not found:", len(not_found_ingredients))
    log_file.write("Total ingredients not found: "  + str(len(not_found_ingredients)) + "\n")
    print("Serializing produced substitutions graph at:", output_graph_filename)
    log_file.write("Serializing produced substitutions graph at: " + str(output_graph_filename) + "\n")
    log_file.close()

    # 100%|██████████| 49044/49044 [3:28:59<00:00,  3.91it/s]
    # Total number of substitutions in split train, : 49044
    # Times identified both ingredients of the suggested substitution: 38142
    # Times original ingredient not found: 3666
    # Times new ingredient not found: 7236
    # Total ingredients not found: 849
    # Serializing produced substitutions graph at: Dataset/substitutions_graph_train.ttl

    # 100%|██████████| 10729/10729 [27:22<00:00,  6.53it/s]
    # Total number of substitutions in split val, : 10729
    # Times identified both ingredients of the suggested substitution: 8451
    # Times original ingredient not found: 674
    # Times new ingredient not found: 1604
    # Total ingredients not found: 427
    # Serializing produced substitutions graph at: Dataset/substitutions_graph_val.ttl

    # 100%|██████████| 10747/10747 [37:35<00:00,  4.77it/s]
    # Total number of substitutions in split test, : 10747
    # Times identified both ingredients of the suggested substitution: 8582
    # Times original ingredient not found: 625
    # Times new ingredient not found: 1540
    # Total ingredients not found: 422
    # Serializing produced substitutions graph at: Dataset/substitutions_graph_test.ttl
    

    # serialize the constructed graph to a file
    substitutions_foodKG_graph.serialize(destination=output_graph_filename, format='turtle')

# explore_subs1m_recipe_ingredients()
# get_statistics_of_substitution_data_and_foodKG_mappings()

foodkg_graphdb_interface = FoodKGGraphDBInterface(load_ingredient_indexes_from_files=True)

# print(foodkg_graphdb_interface.get_ingredient_short_IRI_from_1Msubs_to_foodKG_by_IRI_or_name("potato"))

create_graph_with_recipes_and_substitutions_in_FoodKG(foodkg_graphdb_interface, split="train")

# foodkg_graphdb_interface.write_class_memberships_of_ingredients_to_file_with_their_frequencies()