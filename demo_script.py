from Agent import Agent
import os
from rdflib import Graph, Namespace, URIRef
from typing import Tuple
import argparse
from collections import defaultdict

def remove_ingredient_prefix(ingredient_iri: URIRef) -> str:
    prefix = "http://idea.rpi.edu/heals/kb/ingredientname/"
    return str(ingredient_iri)[len(prefix):]

def get_demo_recipe_graph() -> Graph:

    # https://gitlab.ai.vub.ac.be/ehai/babel/-/blob/development/applications/muhai-cookingbot/recipe-annotations/almond-crescent-cookies-3.lisp

    # ;; "120 grams salted butter, at room temperature" <recipe-kb:ingredientname/salted%20butter>
    #     (fetch-and-proportion ?proportioned-butter ?ks-with-butter ?kitchen ?target-container-1 salted-butter 120 g)
    #     (bring-to-temperature ?warm-butter ?ks-with-warm-butter ?ks-with-butter ?proportioned-butter ?room-temp-qty ?room-temp-unit)
    #
    # ;; "40 grams confectioners' sugar, plus 30 grams extra for dusting" <recipe-kb:ingredientname/powdered%20sugar>
    #     (fetch-and-proportion ?proportioned-sugar ?ks-with-sugar ?ks-with-warm-butter ?target-container-2 powdered-white-sugar 40 g)
    #     (fetch-and-proportion ?proportioned-dusting-sugar ?ks-with-dusting-sugar ?ks-with-sugar ?target-container-3 powdered-white-sugar 30 g)
    #
    # ;; "1 teaspoon vanilla extract" <recipe-kb:ingredientname/vanilla%20extract>
    #     (fetch-and-proportion ?proportioned-vanilla ?ks-with-vanilla ?ks-with-dusting-sugar ?target-container-4 vanilla-extract 1 teaspoon)
    #
    # ;; "1 teaspoon almond extract" <recipe-kb:ingredientname/almond%20extract>
    #     (fetch-and-proportion ?proportioned-almond-extract ?ks-with-almond ?ks-with-vanilla ?target-container-5 almond-extract 1 teaspoon)
    #
    # ;; "1/8 teaspoon salt" <recipe-kb:ingredientname/salt>
    #     (fetch-and-proportion ?proportioned-salt ?ks-with-salt ?ks-with-almond ?target-container-6 salt 0.125 teaspoon)
    #
    # ;; "90 grams all-purpose flour, sifted"  <recipe-kb:ingredientname/all%20-%20purpose%20flour>
    #     (fetch-and-proportion ?proportioned-flour ?ks-with-flour ?ks-with-salt ?target-container-7 all-purpose-flour 90 g)
    #     (sift ?sifted-flour ?ks-with-sifted-flour ?ks-with-flour ?large-bowl ?proportioned-flour ?sifting-tool)
    #

    # <http://idea.rpi.edu/heals/kb/recipe/demo_almond_cookies> ns1:uses_ingredient <http://idea.rpi.edu/heals/kb/ingredientname/salted%20butter>,
    # <http://idea.rpi.edu/heals/kb/ingredientname/powdered%20sugar>,
    # <http://idea.rpi.edu/heals/kb/ingredientname/vanilla%20extract>,
    # <http://idea.rpi.edu/heals/kb/ingredientname/almond%20extract>,
    # <http://idea.rpi.edu/heals/kb/ingredientname/salt>,
    # <http://idea.rpi.edu/heals/kb/ingredientname/all%20-%20purpose%20flour> .

    demo_recipe_graph = Graph()
    demo_recipe_iri = URIRef("http://idea.rpi.edu/heals/kb/recipe/demo_almond_cookies")
    uses_ingredient_iri = URIRef("http://lr.cs.vu.nl/ingredient_substitutions#uses_ingredient")

    foodkg_namespace:Namespace = Namespace("http://idea.rpi.edu/heals/kb/ingredientname/")

    used_ingredient_short_iris = ["salted%20butter", "powdered%20sugar", "vanilla%20extract", "almond%20extract",
                                "salt",
                                "all%20-%20purpose%20flour"]

    for ingredient_short_iri in used_ingredient_short_iris:
        ingredient_iri = foodkg_namespace.term((ingredient_short_iri))
        demo_recipe_graph.add((demo_recipe_iri, uses_ingredient_iri, ingredient_iri))

    return demo_recipe_graph


def get_demo_recipe_ingredients() -> set[URIRef]:
    demo_recipe_graph:Graph = get_demo_recipe_graph()
    uses_ingredient_iri = URIRef("http://lr.cs.vu.nl/ingredient_substitutions#uses_ingredient")

    demo_recipe_ingredients:set[URIRef] = set()

    for _, _, ingredient_iri in demo_recipe_graph.triples(
        (None, uses_ingredient_iri, None)):
        demo_recipe_ingredients.add(ingredient_iri)

    return demo_recipe_ingredients

def get_top_k_suggested_substitutions_per_ingredient_of_recipe(agent:Agent, recipe_ingredients:set[URIRef], k:int=10, show_scores:bool=False) -> dict[URIRef,list[tuple[URIRef,float]]]:

    print("The recipe consists of the following ingredients:")
    for original_ingredient in recipe_ingredients:
        print(remove_ingredient_prefix(original_ingredient))

    print("\nIngredients Substitution Suggestions per ingredient:")

    all_ingredient_substitution_suggestions_and_scores: dict[URIRef, list[Tuple[URIRef, float]]] = dict()

    for original_ingredient in recipe_ingredients:
        print("-Original- ", remove_ingredient_prefix(original_ingredient) + ":")

        all_ingredient_substitution_suggestions_and_scores[original_ingredient] = agent.infer_on_ingredient_substitution_query(
            recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient, return_scores=True)[:k]

        for suggested_substitution, score in all_ingredient_substitution_suggestions_and_scores[original_ingredient]:
            ingredient_name = remove_ingredient_prefix(suggested_substitution)
            if show_scores:
                print(ingredient_name, score)
            else:
                print(ingredient_name)
        print()

    return all_ingredient_substitution_suggestions_and_scores



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--steps", default="100", type=str, help='["100", "1000", "complete"]')
    parser.add_argument("--learning", default="HC", type=str, help='["HC", "LT+Freq"]')
    parser.add_argument("--AL", default="AL", type=str, help='["AL", "PL"]')
    parser.add_argument("--demo_dir", default="Demo", type=str)
    parser.add_argument("--k", default=1, type=int, help='Number of substitutions to suggest per ingredient')
    parser.add_argument("--show_scores", action="store_true", help="Show recommendation scores")

    args = parser.parse_args()


    demo_dir:str = args.demo_dir

    # if args.learning == "HC" and args.AL == "AL" and args.steps

    exp_paths = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))


    # 100 SAMPLES
    # LT+Freq - PL
    exp_paths["LT+Freq"]["PL"]["100"] = "ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_100"
    # agent_dir: str = "Demo/ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_100/0"
    # LT+Freq - AL
    exp_paths["LT+Freq"]["AL"]["100"] = "ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100"
    # agent_dir: str = "Demo/ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100/0"
    # HC - PL
    exp_paths["HC"]["PL"]["100"] = "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_100"
    # agent_dir: str = "Demo/ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_100/0"
    # HC- AL
    exp_paths["HC"]["AL"]["100"] = "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100"
    # agent_dir: str = "Demo/ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100/0"

    # 1000 SAMPLES
    # LT+Freq - PL
    exp_paths["LT+Freq"]["PL"]["1000"] = "ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_1000"
    # agent_dir: str = "Demo/ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_1000/0"
    # LT+Freq - AL
    exp_paths["LT+Freq"]["AL"]["1000"] = "ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_1000"
    # agent_dir: str = "Demo/ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_1000/0"
    # HC - PL
    exp_paths["HC"]["PL"]["1000"] = "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_1000"
    # agent_dir: str = "Demo/ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_1000/0"
    # HC- AL
    exp_paths["HC"]["AL"]["1000"] = "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_1000"
    # agent_dir: str = "Demo/ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_1000/0"


    # COMPLETE EPOCH
    # LT+Freq - PL
    exp_paths["LT+Freq"]["PL"]["complete"] = "ing2ing=1__No_Ingredient_Perception_Used__introspection_random__complete_epoch"
    exp_paths["LT+Freq"]["AL"]["complete"] = "ing2ing=1__No_Ingredient_Perception_Used__introspection_random__complete_epoch"
    # ing2ing=1__No_Ingredient_Perception_Used__introspection_random__complete_epoch
    # HC- PL
    exp_paths["HC"]["PL"]["complete"] = "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__complete_epoch"
    exp_paths["HC"]["AL"]["complete"] = "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__complete_epoch"
    # ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__complete_epoch

    agent_filepath = os.path.join(os.path.join(args.demo_dir, exp_paths[args.learning][args.AL][args.steps]), "agent_state_final.pkl")

    # load trained agent
    agent = Agent(load_ingredient_properties=False)
    agent.load_agent(agent_filepath)

    demo_recipe_ingredients = get_demo_recipe_ingredients()

    get_top_k_suggested_substitutions_per_ingredient_of_recipe(agent, demo_recipe_ingredients, k=args.k, show_scores=args.show_scores)


#
# python3 demo_script.py --k 10 --learning LT+Freq --AL PL --steps 100 --show_scores  > Demo/ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_100/ingredient_recommendations.txt
# python3 demo_script.py --k 10 --learning LT+Freq --AL AL --steps 100 --show_scores  > Demo/ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100/ingredient_recommendations.txt
#
# python3 demo_script.py --k 10 --learning HC --AL PL --steps 100 --show_scores  > Demo/ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_100/ingredient_recommendations.txt
# python3 demo_script.py --k 10 --learning HC --AL AL --steps 100 --show_scores  > Demo/ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100/ingredient_recommendations.txt
#
# python3 demo_script.py --k 10 --learning LT+Freq --AL PL --steps 1000 --show_scores  > Demo/ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_1000/ingredient_recommendations.txt
# python3 demo_script.py --k 10 --learning LT+Freq --AL AL --steps 1000 --show_scores  > Demo/ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_1000/ingredient_recommendations.txt
#
# python3 demo_script.py --k 10 --learning HC --AL PL --steps 1000 --show_scores  > Demo/ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_1000/ingredient_recommendations.txt
# python3 demo_script.py --k 10 --learning HC --AL AL --steps 1000 --show_scores  > Demo/ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_1000/ingredient_recommendations.txt
#
# python3 demo_script.py --k 10 --learning LT+Freq --AL PL --steps complete --show_scores  > Demo/ing2ing=1__No_Ingredient_Perception_Used__introspection_random__complete_epoch/ingredient_recommendations.txt
#
# python3 demo_script.py --k 10 --learning HC --AL PL --steps complete --show_scores  > Demo/ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__complete_epoch/ingredient_recommendations.txt
