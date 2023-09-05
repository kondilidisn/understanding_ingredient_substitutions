import math
from math import floor
from typing import Optional, Generator, Set, Tuple, List, Union
from rdflib import Graph, Namespace, URIRef, RDF, OWL
from utils import *
from collections import defaultdict
import os
import numpy as np
import pickle
import copy


class Agent:
    def __init__(self, ingredient_properties: Optional[list[str]] = None,
                 property_filters: Optional[dict[str, float]] = None,
                 ing_prop_to_ing_prop_score_multiplier: int = 0,
                 recipe_prop_to_ing_prop_score_multiplier: int = 0,
                 ing_to_ing_score_multiplier: int = 1,
                 recipe_property_similarity_score_multiplier: int = 0,
                 original_ingredient_property_similarity_score_multiplier: int = 0,
                 introspection_ing_freq_multiplier: float = 0,
                 introspection_ing_prop_freq_multiplier: float = 0,
                 introspection_epsilon_greedy: float = 0.1,
                 load_ingredient_properties: bool = True
                 ):

        if property_filters is None:
            property_filters: dict[str, float] = dict()
            property_filters["top_prop_percent"] = 100

        if ingredient_properties is None:
            ingredient_properties: list[str] = ["foodOn", "foodOn_one_hop"]
        # ingredient_knowledge_source_per_ontology_filename_prefix = "ingredient_properties_from_ontology_obo.ttl"
        # [Optional] you can load property frequencies to be used as idf
        self.ingredient_knowledge: Graph = Graph()
        self.ingredient_properties_list = ingredient_properties
        self.property_filters = property_filters
        if load_ingredient_properties:
            self.load_ingredient_properties()

        # learning ingredient substitution scores based on learnt property matching scores
        # property to property
        self.original_ingredient_to_new_ingredient_matching_property_counter = defaultdict(create_int_defaultdict)
        self.ing_prop_to_ing_prop_score_multiplier: int = ing_prop_to_ing_prop_score_multiplier
        # property to property
        self.recipe_to_new_ingredient_matching_property_counter = defaultdict(create_int_defaultdict)
        self.recipe_prop_to_ing_prop_score_multiplier: int = recipe_prop_to_ing_prop_score_multiplier

        # we also have a counter that keeps track of each directed ingredient substitution, in a directional manner
        # ingredient to ingredient
        self.ingredient_to_ingredient_substitution_counter = defaultdict(create_int_defaultdict)
        self.ing_to_ing_score_multiplier: int = ing_to_ing_score_multiplier

        # unsupervised ingredient substitution multipliers
        self.recipe_property_similarity_score_multiplier: int = recipe_property_similarity_score_multiplier
        self.original_ingredient_property_similarity_score_multiplier: int = original_ingredient_property_similarity_score_multiplier

        # introspection_parameters
        # self.introspection_policy = introspection_policy
        self.introspection_ing_freq_multiplier = introspection_ing_freq_multiplier
        self.introspection_ing_prop_freq_multiplier = introspection_ing_prop_freq_multiplier
        self.introspection_epsilon_greedy = introspection_epsilon_greedy

        self.variables_names_to_save: list[str] = ["ingredient_to_ingredient_substitution_counter",
                                                   "original_ingredient_to_new_ingredient_matching_property_counter",
                                                   "recipe_to_new_ingredient_matching_property_counter",
                                                   "ingredient_knowledge",
                                                   "ingredient_properties_list",
                                                   "property_filters",
                                                   "ing_prop_to_ing_prop_score_multiplier",
                                                   "recipe_prop_to_ing_prop_score_multiplier",
                                                   "ingredient_to_ingredient_substitution_counter",
                                                   "ing_to_ing_score_multiplier",
                                                   "recipe_property_similarity_score_multiplier",
                                                   "original_ingredient_property_similarity_score_multiplier",
                                                   "introspection_ing_freq_multiplier",
                                                   "introspection_ing_prop_freq_multiplier",
                                                   "introspection_epsilon_greedy"]

    def load_agent(self, load_filename) -> None:
        with open(load_filename, 'rb') as handle:
            agent_instance_variables: dict = pickle.load(handle)

        for variable_name in self.variables_names_to_save:
            setattr(self, variable_name, agent_instance_variables[variable_name])

    def save_agent(self, save_filename):
        agent_instance_variables = dict()
        for variable_name in self.variables_names_to_save:
            agent_instance_variables[variable_name] = self.__getattribute__(variable_name)

        with open(save_filename, 'wb') as handle:
            pickle.dump(agent_instance_variables, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def get_copy(self):
        other_agent = Agent(load_ingredient_properties=False)

        for variable_name in self.variables_names_to_save:
            setattr(other_agent, variable_name, copy.deepcopy(self.__getattribute__(variable_name)))

        return other_agent

    def reset_agents_dynamic_knowledge(self):
        # reset agents ingredient substitution related knowledge
        self.original_ingredient_to_new_ingredient_matching_property_counter = defaultdict(create_int_defaultdict)
        self.recipe_to_new_ingredient_matching_property_counter = defaultdict(create_int_defaultdict)
        self.ingredient_to_ingredient_substitution_counter = defaultdict(create_int_defaultdict)

        # reset agents knowledge of training data
        self.ingredient_substitutions: List[URIRef] = []
        self.all_recipe_ingredients: List[Set[URIRef]] = [set()]
        self.original_ingredients: List[URIRef] = []
        self.number_of_remaining_subs_to_learn = 0

        # reset agents introspection related variables
        self.original_ingredient_frequencies: defaultdict[URIRef:int] = defaultdict(int)
        self.original_ingredient_property_frequencies: defaultdict[URIRef:int] = defaultdict(int)

    def save_agents_ingredient_substitution_knowledge(self, save_directory: str):
        # create the directory
        os.mkdir(save_directory)
        # save the following variables to files using pickle
        # self.ingredient_to_ingredient_substitution_counter = defaultdict(lambda: defaultdict(int))
        # self.original_ingredient_to_new_ingredient_matching_property_counter = defaultdict(lambda: defaultdict(int))
        # self.recipe_to_new_ingredient_matching_property_counter = defaultdict(lambda: defaultdict(int))
        with open(os.path.join(save_directory, "ing2ing_sub_counter.pkl"), 'wb') as handle:
            pickle.dump(self.ingredient_to_ingredient_substitution_counter, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(os.path.join(save_directory, "ingProp2ingProp_sub_counter.pkl"), 'wb') as handle:
            pickle.dump(self.original_ingredient_to_new_ingredient_matching_property_counter, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)

        with open(os.path.join(save_directory, "recProp2ingProp_sub_counter.pkl"), 'wb') as handle:
            pickle.dump(self.recipe_to_new_ingredient_matching_property_counter, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)

    def load_agents_ingredient_substitution_knowledge(self, save_directory: str):
        # load the following variables from the drive in pickle form
        self.ingredient_to_ingredient_substitution_counter = defaultdict(lambda: defaultdict(int))
        self.original_ingredient_to_new_ingredient_matching_property_counter = defaultdict(lambda: defaultdict(int))
        self.recipe_to_new_ingredient_matching_property_counter = defaultdict(lambda: defaultdict(int))

        with open(os.path.join(save_directory, "ing2ing_sub_counter.pkl"), 'rb') as handle:
            self.ingredient_to_ingredient_substitution_counter = pickle.load(handle)

        with open(os.path.join(save_directory, "ingProp2ingProp_sub_counter.pkl"), 'rb') as handle:
            self.original_ingredient_to_new_ingredient_matching_property_counter = pickle.load(handle)

        with open(os.path.join(save_directory, "recProp2ingProp_sub_counter.pkl"), 'rb') as handle:
            self.recipe_to_new_ingredient_matching_property_counter = pickle.load(handle)

    def get_agent_ing_perception_str_description(self) -> str:
        if self.ing_prop_to_ing_prop_score_multiplier == 0 and self.recipe_prop_to_ing_prop_score_multiplier == 0 and \
                self.introspection_ing_freq_multiplier == 0 and self.introspection_ing_prop_freq_multiplier == 0:
            return "No_Ingredient_Perception_Used"

        ingredient_perception_str_description: str = "ing_perception=" + "_".join(self.ingredient_properties_list)
        if self.property_filters["top_prop_percent"] != 100:
            ingredient_perception_str_description += "_least_" + str(
                self.property_filters["top_prop_percent"]) + "_freq_props"

        return ingredient_perception_str_description

    def get_agent_policy_str_description(self) -> str:
        policy_descriptions: list[str] = []

        if self.ing_to_ing_score_multiplier != 0:
            policy_descriptions.append("ing2ing=" + str(self.ing_to_ing_score_multiplier))
        if self.ing_prop_to_ing_prop_score_multiplier != 0:
            policy_descriptions.append("ingP2ingP=" + str(self.ing_prop_to_ing_prop_score_multiplier))
        if self.recipe_prop_to_ing_prop_score_multiplier != 0:
            policy_descriptions.append("recP2ingP=" + str(self.recipe_prop_to_ing_prop_score_multiplier))
        if self.recipe_property_similarity_score_multiplier != 0:
            policy_descriptions.append("unsRecP=" + str(self.recipe_property_similarity_score_multiplier))
        if self.original_ingredient_property_similarity_score_multiplier != 0:
            policy_descriptions.append("unsIngP=" + str(self.original_ingredient_property_similarity_score_multiplier))

        return "__".join(policy_descriptions)

    def get_agent_introspection_policy_str_description(self) -> str:
        introspection_policy_description: str = ""

        if self.introspection_ing_freq_multiplier == 0 and self.introspection_ing_prop_freq_multiplier == 0:
            introspection_policy_description = "_random"
        else:
            introspection_policy_description = "_epsilon_greedy_" + str(self.introspection_epsilon_greedy)

        if self.introspection_ing_freq_multiplier != 0:
            introspection_policy_description += "_ing_" + str(self.introspection_ing_freq_multiplier)

        if self.introspection_ing_prop_freq_multiplier != 0:
            introspection_policy_description += "_ing_prop_" + str(self.introspection_ing_prop_freq_multiplier)

        return introspection_policy_description

    def uses_introspection(self) -> bool:
        if self.introspection_ing_freq_multiplier == 0 and self.introspection_ing_prop_freq_multiplier == 0:
            return False
        else:
            return True

    def load_ingredient_properties(self, skip_classes: list[str] = [str(OWL.Thing)],
                                   skip_namespaces: list[str] = ["_:"]) -> None:

        top_prop_percent: float = self.property_filters["top_prop_percent"]
        self.property_frequencies: dict[URIRef, int] = defaultdict(int)
        # line_counter: int = 0

        for ingredient_properties_prefix in self.ingredient_properties_list:
            properties_filepath = ingredient_property_category_to_query_result_csv_filepath(
                ingredient_properties_prefix)
            print("The agent is loading the ingredient properties from file:", properties_filepath)

            with open(properties_filepath, "r") as ingredient_properties_csv_file:
                # we skip the first line with the headers
                ingredient_properties_csv_file.readline()

                line = ingredient_properties_csv_file.readline()
                while line is not None and line != "":
                    # if line_counter % 1000 == 0:
                    # print("Properties read:", line_counter)
                    # print(line)
                    # line_counter += 1
                    ingredient_IRI, ingredient_class = line[:-1].split(",")
                    if ingredient_class in skip_classes:
                        line = ingredient_properties_csv_file.readline()
                        continue
                    #
                    for skip_namespace in skip_namespaces:
                        if ingredient_class.startswith(skip_namespace):
                            line = ingredient_properties_csv_file.readline()
                            continue

                    self.ingredient_knowledge.add((URIRef(ingredient_IRI), RDF.type, URIRef(ingredient_class)))
                    if top_prop_percent != 100:
                        self.property_frequencies[URIRef(ingredient_class)] += 1
                    line = ingredient_properties_csv_file.readline()

        # use only the leas frequent ingredient properties, if requested
        if top_prop_percent != 100:
            raise ValueError(
                "make sure that the agent has at least one property per ingredient! Then also change the hardcoded vocabulary size of ingredients in evaluate_agent function!")
            ranked_properties_by_freq = [(property, self.property_frequencies[property]) for
                                         property in self.property_frequencies]
            ranked_properties_by_freq.sort(reverse=False, key=lambda x: x[1])
            num_of_properties = math.ceil((top_prop_percent / 100) * len(ranked_properties_by_freq))

            least_frequent_properties = set([property for property, _ in ranked_properties_by_freq[:num_of_properties]])

            filtered_ingredient_knowledge = Graph()
            for ingredient, property_type, property in self.ingredient_knowledge:
                if property in least_frequent_properties:
                    filtered_ingredient_knowledge.add((ingredient, property_type, property))

            self.ingredient_knowledge = filtered_ingredient_knowledge

    def write_ingredient_knowledge(self, exp_dir: str) -> None:
        #     write to a file the ingredient knowledge
        ingredient_knowledge_filename = os.path.join(exp_dir, "ingredient_knowledge.ttl")
        # self.ingredient_knowledge.serialize(destination=ingredient_knowledge_filename, format='turtle')
        print("Ingredient knowledge was writen in file:", ingredient_knowledge_filename)
        properties: set = set()
        ingredients: set = set()
        for ingredient, _, ing_property in self.ingredient_knowledge.triples((None, None, None)):
            ingredients.add(ingredient)
            properties.add(ing_property)
        print("Total number of ingredients:", len(ingredients))
        print("Total number of properties:", len(properties))
        print("Total number of ingredient-property relations:", len(self.ingredient_knowledge))

    # retrieve properties of ingredient
    def perceive_ingredient(self, ingredient: URIRef) -> set:
        return set(self.ingredient_knowledge.objects(subject=ingredient, predicate=RDF.type))

    # retrieve the set of all ingredient properties' within a recipe
    def perceive_recipe(self, recipe_ingredients: set[URIRef], exclude_ingredient: Optional[URIRef]) -> Set[URIRef]:
        recipe_properties: set = set()

        for ingredient in recipe_ingredients:
            if exclude_ingredient is not None and ingredient == exclude_ingredient:
                continue
            ingredient_properties = self.perceive_ingredient(ingredient)
            # print(ingredient_properties)
            # add ingredient properties to the set of recipe properties
            recipe_properties.update(ingredient_properties)
        return recipe_properties

    def calculate_ingredient_similarity_score(self, new_ingredient: URIRef, original_ingredient: URIRef) -> float:
        return self.calculate_ingredient_f1_property_similarity_score(new_ingredient, original_ingredient)

    def calculate_ingredient_f1_property_similarity_score(self, ingredient_a_iri: URIRef,
                                                          ingredient_b_iri: URIRef) -> float:
        ingredient_a_properties: set = self.perceive_ingredient(ingredient_a_iri)
        ingredient_b_properties: set = self.perceive_ingredient(ingredient_b_iri)
        return calculate_f1_score(ingredient_a_properties, ingredient_b_properties)

    def calculate_ingredient_and_recipe_f1_property_similarity_score(self, ingredient_iri: URIRef,
                                                                     recipe_ingredients: Optional[set[URIRef]] = None,
                                                                     recipe_properties: Optional[
                                                                         set[URIRef]] = None) -> float:
        if recipe_ingredients is None and recipe_properties is None:
            raise ValueError("Neither recipe ingredients nor recipe properties were provided!")
        if recipe_ingredients is not None and recipe_properties is not None:
            raise ValueError("Both recipe ingredients and recipe properties were provided!")
        if recipe_properties is None and recipe_ingredients is not None:
            recipe_properties = self.perceive_recipe(recipe_ingredients, exclude_ingredient=ingredient_iri)

        ingredient_properties: set = self.perceive_ingredient(ingredient_iri)
        return calculate_f1_score(ingredient_properties, recipe_properties)

    def get_all_ingredients_with_any_of_the_provided_properties(self, properties: set[URIRef]) -> set:
        ingredients_set: set = set()
        for ing_property in properties:
            ingredients_set.update(set(self.ingredient_knowledge.subjects(predicate=RDF.type, object=ing_property)))
        return ingredients_set

    # learn
    def learn_from_example(self, recipe_ingredients: set[URIRef], original_ingredient: URIRef, new_ingredient: URIRef):
        rest_recipe_properties = self.perceive_recipe(recipe_ingredients, exclude_ingredient=original_ingredient)
        original_ingredient_properties = self.perceive_ingredient(original_ingredient)
        new_ingredient_properties = self.perceive_ingredient(new_ingredient)

        if self.recipe_prop_to_ing_prop_score_multiplier != 0:
            # update recipe properties counter
            for recipe_property in rest_recipe_properties:
                for new_ingredient_property in new_ingredient_properties:
                    self.recipe_to_new_ingredient_matching_property_counter[recipe_property][
                        new_ingredient_property] += 1

        if self.ing_prop_to_ing_prop_score_multiplier != 0:
            # update ingredient properties counter
            for original_ingredient_property in original_ingredient_properties:
                for new_ingredient_property in new_ingredient_properties:
                    self.original_ingredient_to_new_ingredient_matching_property_counter[original_ingredient_property][
                        new_ingredient_property] += 1

        if self.ing_to_ing_score_multiplier != 0:
            # update ingredient to ingredient counter
            self.ingredient_to_ingredient_substitution_counter[original_ingredient][new_ingredient] += 1

    # infer
    def infer_on_ingredient_substitution_query(self, recipe_ingredients: set[URIRef], original_ingredient: URIRef,
                                               return_scores: bool = False) -> list[
        Union[URIRef, Tuple[URIRef, float]]]:

        recipe_properties = self.perceive_recipe(recipe_ingredients, exclude_ingredient=original_ingredient)
        original_ingredient_properties = self.perceive_ingredient(original_ingredient)
        candidate_ingredient_property_scores = defaultdict(float)
        candidate_ingredient_scores = defaultdict(float)

        if self.ing_prop_to_ing_prop_score_multiplier != 0:
            # infer using any learnt knowledge from experience
            # utilize ingredient properties to ingredient properties counters (recipe agnostic)
            for original_ingredient_property in original_ingredient_properties:
                for candidate_property in self.original_ingredient_to_new_ingredient_matching_property_counter[
                    original_ingredient_property]:
                    candidate_ingredient_property_scores[candidate_property] += \
                        self.ing_prop_to_ing_prop_score_multiplier * \
                        self.original_ingredient_to_new_ingredient_matching_property_counter[
                            original_ingredient_property][candidate_property]

        if self.recipe_prop_to_ing_prop_score_multiplier != 0:
            # utilize recipe properties to ingredient properties counters (recipe aware)
            for recipe_ingredient_property in recipe_properties:
                for candidate_property in self.recipe_to_new_ingredient_matching_property_counter[
                    recipe_ingredient_property].keys():
                    candidate_ingredient_property_scores[candidate_property] += \
                        self.recipe_prop_to_ing_prop_score_multiplier * \
                        self.recipe_to_new_ingredient_matching_property_counter[recipe_ingredient_property][
                            candidate_property]

        if self.ing_prop_to_ing_prop_score_multiplier != 0 or self.recipe_prop_to_ing_prop_score_multiplier != 0:
            # translate property scores to ingredient scores
            # get all related (candidate) ingredients
            learnt_related_ingredients_via_properties: set = self.get_all_ingredients_with_any_of_the_provided_properties(
                set(candidate_ingredient_property_scores.keys()))
            for candidate_ingredient in learnt_related_ingredients_via_properties:
                for ingredient_property in self.perceive_ingredient(candidate_ingredient):
                    candidate_ingredient_scores[candidate_ingredient] += candidate_ingredient_property_scores[
                        ingredient_property]

        if self.ing_to_ing_score_multiplier != 0:
            # utilize ingredient to ingredient substitutions counters (recipe agnostic)
            for candidate_ingredient in self.ingredient_to_ingredient_substitution_counter[original_ingredient].keys():
                candidate_ingredient_scores[candidate_ingredient] += \
                    self.ing_to_ing_score_multiplier * \
                    self.ingredient_to_ingredient_substitution_counter[original_ingredient][candidate_ingredient]

        if self.recipe_property_similarity_score_multiplier != 0:
            # infer using unsupervised f1 scores
            unsupervised_recipe_related_ingredients_via_properties = self.get_all_ingredients_with_any_of_the_provided_properties(
                recipe_properties)
            for candidate_ingredient in unsupervised_recipe_related_ingredients_via_properties:
                # utilize the recipe to candidate ingredient similarity score
                candidate_ingredient_scores[candidate_ingredient] += \
                    self.recipe_property_similarity_score_multiplier * \
                    self.calculate_ingredient_and_recipe_f1_property_similarity_score(
                        ingredient_iri=candidate_ingredient, recipe_properties=recipe_properties)
            #     utilize the original ingredient to candidate ingredient similarity score

        if self.original_ingredient_property_similarity_score_multiplier != 0:
            unsupervised_ingredient_related_ingredients_via_properties = self.get_all_ingredients_with_any_of_the_provided_properties(
                original_ingredient_properties)
            for candidate_ingredient in unsupervised_ingredient_related_ingredients_via_properties:
                # utilize the recipe to candidate ingredient similarity score
                candidate_ingredient_scores[candidate_ingredient] += \
                    self.original_ingredient_property_similarity_score_multiplier * \
                    self.calculate_ingredient_f1_property_similarity_score(original_ingredient, candidate_ingredient)

        # print(len(candidate_ingredient_scores))
        ranked_ingredient_candidates_and_scores = [(ingredient_iri, candidate_ingredient_scores[ingredient_iri]) for
                                                   ingredient_iri in candidate_ingredient_scores]
        ranked_ingredient_candidates_and_scores.sort(reverse=True, key=lambda x: x[1])

        if return_scores:
            return ranked_ingredient_candidates_and_scores

        ranked_ingredient_candidates = [ingredient_iri for ingredient_iri, _ in ranked_ingredient_candidates_and_scores]

        return ranked_ingredient_candidates

    def justify_ingredient_substitution_recommendation(self, recipe_ingredients: set[URIRef],
                                                       original_ingredient: URIRef, new_ingredient: URIRef) \
            -> dict[str, dict[str, dict[str, int]]]:

        relevant_observations: dict[str, dict[str, dict[str, int]]] = dict()

        if self.ing_to_ing_score_multiplier != 0:
            relevant_observations["ing2ing"] = dict()
            ing2ing_counter = self.ingredient_to_ingredient_substitution_counter[original_ingredient][new_ingredient]

            if ing2ing_counter != 0:
                relevant_observations["ing2ing"] = {original_ingredient: {new_ingredient: ing2ing_counter}}

        original_ingredient_properties = self.perceive_ingredient(original_ingredient)
        new_ingredient_properties = self.perceive_ingredient(new_ingredient)

        if self.ing_prop_to_ing_prop_score_multiplier != 0:
            relevant_observations["ing_prop2ing_prop"] = defaultdict(create_int_defaultdict)
            for original_ingredient_property in original_ingredient_properties:
                for new_ingredient_property in new_ingredient_properties:
                    if new_ingredient_property in self.original_ingredient_to_new_ingredient_matching_property_counter[
                        original_ingredient]:
                        relevant_observations["ing_prop2ing_prop"][original_ingredient_property][
                            new_ingredient_property] = \
                        self.original_ingredient_to_new_ingredient_matching_property_counter[original_ingredient][
                            new_ingredient_property]

        if self.recipe_prop_to_ing_prop_score_multiplier != 0:
            relevant_observations["rec_prop2ing_prop"] = defaultdict(create_int_defaultdict)
            recipe_properties = self.perceive_recipe(recipe_ingredients, exclude_ingredient=original_ingredient)
            for recipe_property in recipe_properties:
                for new_ingredient_property in new_ingredient_properties:
                    if new_ingredient_property in self.recipe_to_new_ingredient_matching_property_counter[
                        recipe_property]:
                        relevant_observations["rec_prop2ing_prop"][recipe_property][new_ingredient_property] = \
                        self.recipe_to_new_ingredient_matching_property_counter[recipe_property][
                            new_ingredient_property]

        return relevant_observations

    def receive_available_training_data(self, ingredient_substitutions: List[URIRef],
                                        all_recipe_ingredients: List[Set[URIRef]], source_ingredients: List[URIRef]):
        self.ingredient_substitutions: List[URIRef] = ingredient_substitutions
        self.all_recipe_ingredients: List[Set[URIRef]] = all_recipe_ingredients
        self.original_ingredients: List[URIRef] = source_ingredients
        self.number_of_remaining_subs_to_learn = len(self.ingredient_substitutions)

    def init_introspection(self):
        self.original_ingredient_frequencies: defaultdict[URIRef:int] = defaultdict(int)
        self.original_ingredient_property_frequencies: defaultdict[URIRef:int] = defaultdict(int)

        for original_ingredient in self.original_ingredients:
            if self.introspection_ing_freq_multiplier != 0:
                self.original_ingredient_frequencies[original_ingredient] += 1

            if self.introspection_ing_prop_freq_multiplier != 0:
                for original_ingredient_property in self.perceive_ingredient(original_ingredient):
                    self.original_ingredient_property_frequencies[original_ingredient_property] += 1

    def decide_which_substitution_to_reveal_next(self) -> Optional[tuple[URIRef, set[URIRef], URIRef]]:
        # in case we run out of training data:
        if self.number_of_remaining_subs_to_learn == 0:
            return None

        expected_informativeness_scores: list[float] = []
        for i in range(self.number_of_remaining_subs_to_learn):
            recipe_ingredients = self.all_recipe_ingredients[i]
            original_ingredient = self.original_ingredients[i]
            expected_informativeness_score = self.get_expected_substitution_informativeness(recipe_ingredients,
                                                                                            original_ingredient)
            expected_informativeness_scores.append(expected_informativeness_score)

        assert self.number_of_remaining_subs_to_learn == len(expected_informativeness_scores)

        # normalize values and prepare for epsilon greedy sampling
        epsilon_greedy_scores = np.asarray(expected_informativeness_scores)
        # normalize
        epsilon_greedy_scores /= np.sum(epsilon_greedy_scores)
        # add epsilon
        epsilon_greedy_scores += self.introspection_epsilon_greedy / self.number_of_remaining_subs_to_learn
        # re-normalize
        epsilon_greedy_scores /= np.sum(epsilon_greedy_scores)

        # we get the estimated most informative substitution, probabilistically
        index_of_highest_expected_informative_substitution = np.random.choice(
            list(range(self.number_of_remaining_subs_to_learn)), p=epsilon_greedy_scores)
        # non-probabilistic option:
        # index_of_highest_expected_informative_substitution = np.argmax(expected_informativeness_scores)

        # we retrieve the substitution
        selected_substitution_iri = self.ingredient_substitutions[index_of_highest_expected_informative_substitution]
        selected_recipe_ingredients = self.all_recipe_ingredients[index_of_highest_expected_informative_substitution]
        selected_original_ingredient = self.original_ingredients[index_of_highest_expected_informative_substitution]

        # we update the source ingredients frequencies
        if self.introspection_ing_freq_multiplier != 0:
            self.original_ingredient_frequencies[selected_original_ingredient] -= 1

        if self.introspection_ing_prop_freq_multiplier != 0:
            for original_ingredient_property in self.perceive_ingredient(selected_original_ingredient):
                self.original_ingredient_property_frequencies[original_ingredient_property] -= 1

        # we remove this substitution from the candidate learning pool
        del self.ingredient_substitutions[index_of_highest_expected_informative_substitution]
        del self.all_recipe_ingredients[index_of_highest_expected_informative_substitution]
        del self.original_ingredients[index_of_highest_expected_informative_substitution]
        self.number_of_remaining_subs_to_learn -= 1

        return selected_substitution_iri, selected_recipe_ingredients, selected_original_ingredient

    def get_expected_substitution_informativeness(self, recipe_ingredients: set[URIRef],
                                                  original_ingredient: URIRef) -> float:
        ingredient_informativeness_score: float = 0
        if self.introspection_ing_freq_multiplier != 0:
            ingredient_informativeness_score = np.log(self.original_ingredient_frequencies[original_ingredient] + 1)

        ingredients_property_informativeness_score: float = 0
        if self.introspection_ing_prop_freq_multiplier != 0:
            for source_ingredient_property in self.perceive_ingredient(original_ingredient):
                ingredients_property_informativeness_score += np.log(
                    self.original_ingredient_property_frequencies[source_ingredient_property] + 1)

        return self.introspection_ing_freq_multiplier * ingredient_informativeness_score + \
               self.introspection_ing_prop_freq_multiplier * ingredients_property_informativeness_score
