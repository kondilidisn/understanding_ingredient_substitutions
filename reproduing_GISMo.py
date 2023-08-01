import json
import os.path
import pickle
from foodkg_graphdb_interface import FoodKGGraphDBInterface
from tqdm import tqdm
from collections import defaultdict


def load_recipe1M_ingredient_2_id_dictionaries(recipe_Subs1M_prepro_dir="/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/Recipe1M Requirements/recipe1m/preprocessed_flavorgraph_substitutions_fixed_3_no_flavorgraph/"):
    recipe_Subs1M_ingredients_vocab_filename: str = "final_recipe1m_vocab_ingrs.pkl"

    # from inv_cooking.datasets.recipe1m.parsing.titles import TitleParser
    # from inv_cooking.datasets.vocabulary import Vocabulary
    ingredient_vocabulary_filepath: str = "/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/Recipe1M Requirements/recipe1m/preprocessed_flavorgraph_substitutions_fixed_3_no_flavorgraph/final_recipe1m_vocab_ingrs.pkl"
    # Number of ingredients: 1488
    # Number of ingredient names: 15250

    # ingredient_vocabulary_filepath: str = "/Users/kondy/PycharmProjects/gismo/gismo/checkpoints/vocab_ingrs.pkl"
    # Number of ingredients: 6634
    # Number of ingredient names: 10132

    # ingredient_vocabulary_filepath: str = "/Users/kondy/PycharmProjects/gismo/data/Downloaded finals from github links/Inverse Cooking/final_recipe1m_vocab_ingrs.pkl"
    # Number of ingredients: 6634
    # Number of ingredient names: 10132

    with open(os.path.join(recipe_Subs1M_prepro_dir, recipe_Subs1M_ingredients_vocab_filename), 'rb') as pkl_handle:
        recipe_Subs1M_ingredients_vocab_pickle = pickle.load(pkl_handle)
        id2ingredient = recipe_Subs1M_ingredients_vocab_pickle.idx2word
        ingredient2id = recipe_Subs1M_ingredients_vocab_pickle.word2idx

    return ingredient2id, id2ingredient


def check_ingredient_vocabularies(foodkg_graphdb_interface, subs1m_comment_subs_dir="/Users/kondy/PycharmProjects/gismo/gismo/checkpoints",
     recipe_Subs1M_prepro_dir="/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/Recipe1M Requirements/recipe1m/preprocessed_flavorgraph_substitutions_fixed_3_no_flavorgraph/") -> None:

    #     Total number of ingredients

    # baselines: random, Freq (freq is what I do ), LT+Freq,

    # match all ingredients
    # create a file with matched ingredients and one with unmatched ingredients

    # load_recipe_ingredients



    recipe_Subs1M_ingredients_vocab_filename: str = "final_recipe1m_vocab_ingrs.pkl"

    recipe_Subs1M_prepro_filename_prefix = "final_recipe1m_"

    all_1Msubs_ingredients_set: set[str] = set()
    ingredient_subs: dict[str, tuple]


    for split in ["train", "val", "test"]:
        with open(os.path.join(recipe_Subs1M_prepro_dir,
                               recipe_Subs1M_prepro_filename_prefix + split + ".pkl"), 'rb') as pkl_handle:
            recipe_Subs1M_prepro = pickle.load(pkl_handle)
            for preprocessed_recipe in tqdm(recipe_Subs1M_prepro):
                recipe_id = preprocessed_recipe["id"]
                recipe_ingredients = preprocessed_recipe["ingredients"]
                for ingredient in recipe_ingredients:
                    if ingredient not in all_1Msubs_ingredients_set:
                        all_1Msubs_ingredients_set.add(ingredient)


    print("All preprocessed Recipe_1M ingredients (forms / synonyms are treated independently):", len(all_1Msubs_ingredients_set))

    # with open(os.path.join(recipe_Subs1M_prepro_dir, recipe_Subs1M_ingredients_vocab_filename), 'rb') as pkl_handle:
    #     recipe_Subs1M_ingredients_vocab_pickle = pickle.load(pkl_handle)



    ing_to_ing_subs = defaultdict(lambda: defaultdict(int))

    original_ingredients: set = set()
    new_ingredients: set = set()

    for split in ["train", "val", "test"]:
        # read subs1m preprocessed files of substitutions
        subs1m_comment_subs = os.path.join(subs1m_comment_subs_dir, split + "_comments_subs.pkl")
        with open(subs1m_comment_subs, 'rb') as file:
            subs1m_comment_subs_pickle = pickle.load(file)

            for substitution_entry in tqdm(subs1m_comment_subs_pickle):
                # recipe_id = substitution_entry["id"]
                # retrieve all ingredients of this recipe from FoodKG
                # recipe_url = recipe1m_ID_to_URL_dict[recipe_id]
                # recipe_IRIs = get_recipe_IRIs_given_recipe_URL(recipe_url)

                # get ingredients involved in substitution
                substitution = substitution_entry["subs"]
                original_ingredient, new_ingredient = substitution
                original_ingredients.add(original_ingredient)
                new_ingredients.add(new_ingredient)

                if split == "train":
                    ing_to_ing_subs[original_ingredient][new_ingredient] += 1
                else:
                    # candidate_subs = ing_to_ing_subs[original_ingredient]
                    candicate_subs_freqs = [(new_ingredient, ing_to_ing_subs[original_ingredient][new_ingredient]) for new_ingredient in ing_to_ing_subs[original_ingredient]]
                    candicate_subs_freqs.sort(key=lambda x: x[1])


    print("All original substitution ingredients:", len(original_ingredients))
    print("All new substitution ingredients:", len(new_ingredients))
    print("All ingredients_involved in substitutions:", len(original_ingredients.union(new_ingredients)))


foodkg_graphdb_interface = FoodKGGraphDBInterface(load_ingredient_indexes_from_files=True)

# check_ingredient_vocabularies(foodkg_graphdb_interface)

ingredient2id, id2ingredient = load_recipe1M_ingredient_2_id_dictionaries()
print("number of ingredients (synonyms are treated equally):", len(id2ingredient))
