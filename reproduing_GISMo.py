import json
import os.path
import pickle
from foodkg_graphdb_interface import FoodKGGraphDBInterface
from tqdm import tqdm


def check_ingredient_vocabularies(subs1m_comment_subs_dir="/Users/kondy/PycharmProjects/gismo/gismo/checkpoints",
     recipe_Subs1M_prepro_dir="/Users/kondy/Desktop/PhD/Recipes/datasets/FoodKG/Recipe1M Requirements/recipe1m/preprocessed_flavorgraph_substitutions_fixed_3_no_flavorgraph/") -> None:

    #     Total number of ingredients

    # baselines: random, Freq (freq is what I do ), LT+Freq,

    # match all ingredients
    # create a file with matched ingredients and one with unmatched ingredients


    # load_recipe_ingredients



    recipe_Subs1M_prepro_filename_prefix = "final_recipe1m_"

    all_1Msubs_ingredients: set = set()

    ingredient_subs:dict[str,tuple]

    foodkg_graphdb_interface = FoodKGGraphDBInterface(load_ingredient_indexes_from_files=True)

    for split in ["train", "val", "test"]:
        with open(os.path.join(recipe_Subs1M_prepro_dir,
                               recipe_Subs1M_prepro_filename_prefix + split + ".pkl")) as pkl_handle:
            recipe_Subs1M_prepro = pickle.load(pkl_handle)
            for preprocessed_recipe in tqdm(recipe_Subs1M_prepro):
                recipe_id = preprocessed_recipe["id"]
                recipe_ingredients = preprocessed_recipe["ingredients"]
                for ingredient in recipe_ingredients:
                    all_1Msubs_ingredients.add(ingredient)

    print("All Recipe_1M_ingredients:", len(all_1Msubs_ingredients))

    for split in ["train", "val", "test"]:
        # read subs1m preprocessed files of substitutions
        subs1m_comment_subs = os.path.join(subs1m_comment_subs_dir, split + "_comments_subs.pkl")
        with open(subs1m_comment_subs, 'rb') as file:
            subs1m_comment_subs_pickle = pickle.load(file)

            for substitution_entry in tqdm(subs1m_comment_subs_pickle):
                recipe_id = substitution_entry["id"]

                # retrieve all ingredients of this recipe from FoodKG
                # recipe_url = recipe1m_ID_to_URL_dict[recipe_id]
                # recipe_IRIs = get_recipe_IRIs_given_recipe_URL(recipe_url)

                # get ingredients involved in substitution
                substitution = substitution_entry["subs"]
                original_ingredient, new_ingredient = substitution
