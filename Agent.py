from typing import Optional, Generator, Set, Tuple
from rdflib import Graph, Namespace, URIRef, RDF, Node
from utils import *
from collections import defaultdict


class Agent:
    def __init__(self, ingredient_property_knowledge_sources_to_namespace_dict: Optional[dict[str, str]] = None,
                 ingredient_knowledge_source_per_ontology_filename_prefix: str = "Dataset/ingredient_properties_from_ontology_"):

        if ingredient_property_knowledge_sources_to_namespace_dict is None:
            # ingredient_property_knowledge_sources_to_namespace_dict: dict[str:str] = {"obo": "http://purl.obolibrary.org/obo/", "b_node": "_:"}
            ingredient_property_knowledge_sources_to_namespace_dict: dict[str:str] = {
                "obo": "http://purl.obolibrary.org/obo/"}

        # ingredient_knowledge_source_per_ontology_filename_prefix = "ingredient_properties_from_ontology_obo.ttl"
        # [Optional] you can load property frequencies to be used as idf

        self.ingredient_knowledge = Graph()

        for knowledge_source_ontology_name in ingredient_property_knowledge_sources_to_namespace_dict:
            knowledge_source_filename = ingredient_knowledge_source_per_ontology_filename_prefix + knowledge_source_ontology_name + ".ttl"
            knowledge_source_graph = Graph()
            knowledge_source_graph.parse(knowledge_source_filename)
            self.ingredient_knowledge += knowledge_source_graph


        # learning ingredient substitution scores based on learnt property matching scores
        # property to property
        self.original_ingredient_to_new_ingredient_matching_property_counter = defaultdict(lambda: defaultdict(int))
        self.ing_prop_to_ing_prop_score_multiplier:float = 1
        # property to property
        self.recipe_to_new_ingredient_matching_property_counter = defaultdict(lambda: defaultdict(int))
        self.recipe_prop_to_ing_prop_score_multiplier:float = 1

        # we also have a counter that keeps track of each directed ingredient substitution, in a directional manner
        # ingredient to ingredient
        self.ingredient_to_ingredient_substitution_counter = defaultdict(lambda: defaultdict(int))
        self.ing_to_ing_score_multiplier:float = 1

        # unsupervised ingredient substitution multipliers
        self.recipe_property_similarity_score_multiplier: float = 1
        self.original_ingredient_property_similarity_score_multiplier: float = 1


    # retrieve properties of ingredient
    def perceive_ingredient(self, ingredient: str) -> set[Node]:
        return set(self.ingredient_knowledge.objects(subject=URIRef(ingredient), predicate=RDF.type))

    # retrieve the set of all ingredient properties' within a recipe
    def perceive_recipe(self, recipe_ingredients: set[URIRef],  exclude_ingredient: Optional[URIRef]) -> Set[URIRef]:
        recipe_properties: Set[URIRef] = set()

        if exclude_ingredient is not None:
            recipe_ingredients.remove(exclude_ingredient)

        for ingredient in recipe_ingredients:
            ingredient_properties = self.perceive_ingredient(ingredient)
            # add ingredient properties to the set of recipe properties
            recipe_properties.update(ingredient_properties)
        return recipe_properties

    def calculate_ingredient_similarity_score(self, new_ingredient: URIRef, original_ingredient: URIRef) -> float:
        return self.calculate_ingredient_f1_property_similarity_score(new_ingredient, original_ingredient)

    def calculate_ingredient_f1_property_similarity_score(self, ingredient_a_iri: URIRef, ingredient_b_iri: URIRef) -> float:
        ingredient_a_properties: set[Node] = self.perceive_ingredient(ingredient_a_iri)
        ingredient_b_properties: set[Node] = self.perceive_ingredient(ingredient_b_iri)
        return calculate_f1_score(ingredient_a_properties, ingredient_b_properties)

    def calculate_ingredient_and_recipe_f1_property_similarity_score(self, ingredient_iri:URIRef , recipe_ingredients: Optional[set[URIRef]]=None, recipe_properties: Optional[set[URIRef]]=None) -> float:
        if recipe_ingredients is None and recipe_properties is None:
            raise ValueError("Neither recipe ingredients nor recipe properties were provided!")
        if recipe_ingredients is not None and recipe_properties is not None:
            raise ValueError("Both recipe ingredients and recipe properties were provided!")
        if recipe_properties is None and recipe_ingredients is not None:
            recipe_properties = self.perceive_recipe(recipe_ingredients, exclude_ingredient=ingredient_iri)

        ingredient_properties: set[Node] = self.perceive_ingredient(ingredient_iri)
        return calculate_f1_score(ingredient_properties, recipe_properties)

    def get_all_ingredients_with_any_of_the_provided_properties(self, properties:set[URIRef]) -> set[Node] :
        ingredients_set: set[Node] = set()
        for ing_property in properties:
            ingredients_set.update(set(self.ingredient_knowledge.subjects(predicate=RDF.type, object=ing_property)))
        return ingredients_set

    # learn
    def learn_from_example(self, recipe_ingredients: set[URIRef], original_ingredient: URIRef, new_ingredient: URIRef):
        rest_recipe_properties = self.perceive_recipe(recipe_ingredients, exclude_ingredient=original_ingredient)
        original_ingredient_properties = self.perceive_ingredient(original_ingredient)
        new_ingredient_properties = self.perceive_ingredient(new_ingredient)

        # update recipe properties counter
        for recipe_property in rest_recipe_properties:
            for new_ingredient_property in new_ingredient_properties:
                self.recipe_to_new_ingredient_matching_property_counter[recipe_property][new_ingredient_property] += 1

        # update ingredient properties counter
        for original_ingredient_property in original_ingredient_properties:
            for new_ingredient_property in new_ingredient_properties:
                self.recipe_to_new_ingredient_matching_property_counter[original_ingredient_property][new_ingredient_property] += 1

        # update ingredient to ingredient counter
        self.ingredient_to_ingredient_substitution_counter[original_ingredient][new_ingredient] += 1

    # infer
    def infer_on_ingredient_substitution_query(self, recipe_ingredients: set[URIRef], original_ingredient: URIRef) -> list[URIRef]:

        recipe_properties = self.perceive_recipe(recipe_ingredients, exclude_ingredient=original_ingredient)
        original_ingredient_properties = self.perceive_ingredient(original_ingredient)
        candidate_ingredient_property_scores = defaultdict(float)
        candidate_ingredient_scores = defaultdict(float)

    # infer using any learnt knowledge from experience
        # utilize ingredient properties to ingredient properties counters (recipe agnostic)
        for original_ingredient_property in original_ingredient_properties:
            for candidate_property in self.original_ingredient_to_new_ingredient_matching_property_counter[original_ingredient_property]:
                candidate_ingredient_property_scores[candidate_property] += \
                self.ing_prop_to_ing_prop_score_multiplier * self.original_ingredient_to_new_ingredient_matching_property_counter[original_ingredient_property][candidate_property]

        # utilize recipe properties to ingredient properties counters (recipe aware)
        for recipe_ingredient_property in recipe_properties:
            for candidate_property in self.recipe_to_new_ingredient_matching_property_counter[recipe_ingredient_property].keys():
                candidate_ingredient_property_scores[candidate_property] += \
                self.recipe_prop_to_ing_prop_score_multiplier * self.recipe_to_new_ingredient_matching_property_counter[recipe_ingredient_property][candidate_property]

        # translate property scores to ingredient scores
        # get all related (candidate) ingredients
        learnt_related_ingredients_via_properties: set[Node] = self.get_all_ingredients_with_any_of_the_provided_properties(set(candidate_ingredient_property_scores.keys()))
        for candidate_ingredient in learnt_related_ingredients_via_properties:
            for ingredient_property in self.perceive_ingredient(candidate_ingredient):
                candidate_ingredient_scores[candidate_ingredient] += candidate_ingredient_property_scores[ingredient_property]

        # utilize ingredient to ingredient substitutions counters (recipe agnostic)
        for candidate_ingredient in self.ingredient_to_ingredient_substitution_counter[original_ingredient].keys():
            candidate_ingredient_scores[candidate_ingredient] += \
            self.ing_to_ing_score_multiplier * self.ingredient_to_ingredient_substitution_counter[original_ingredient][candidate_ingredient]

    # infer using unsupervised f1 scores
        unsupervised_recipe_related_ingredients_via_properties = self.get_all_ingredients_with_any_of_the_provided_properties(recipe_properties)
        for candidate_ingredient in unsupervised_recipe_related_ingredients_via_properties:
            # utilize the recipe to candidate ingredient similarity score
            candidate_ingredient_scores[candidate_ingredient] += \
            self.recipe_property_similarity_score_multiplier * \
            self.calculate_ingredient_and_recipe_f1_property_similarity_score(ingredient_iri=candidate_ingredient, recipe_properties=recipe_properties)
        #     utilize the original ingredient to candidate ingredient similarity score

        unsupervised_ingredient_related_ingredients_via_properties = self.get_all_ingredients_with_any_of_the_provided_properties(original_ingredient_properties)
        for candidate_ingredient in unsupervised_ingredient_related_ingredients_via_properties:
            # utilize the recipe to candidate ingredient similarity score
            candidate_ingredient_scores[candidate_ingredient] += \
            self.original_ingredient_property_similarity_score_multiplier * \
            self.calculate_ingredient_f1_property_similarity_score(original_ingredient, candidate_ingredient)

        ranked_ingredient_candidates_and_scores = [(ingredient_iri, candidate_ingredient_scores[ingredient_iri]) for ingredient_iri in candidate_ingredient_scores]
        ranked_ingredient_candidates_and_scores.sort(key=lambda x: x[1])
        ranked_ingredient_candidates = [ingredient_iri for (ingredient_iri, _) in ranked_ingredient_candidates_and_scores]

        return ranked_ingredient_candidates
