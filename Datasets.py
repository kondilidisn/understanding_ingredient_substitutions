from rdflib import Graph, Namespace, URIRef
from typing import Optional, Generator, Set, Tuple, List

class BasicSubstitutionsDataset:
    def __init__(self, substitutions_graph_filepath: str):
        self.substitutions_graph:Graph = Graph()
        self.substitutions_graph.parse(substitutions_graph_filepath)

        self.substitutions_namespace = Namespace("http://lr.cs.vu.nl/ingredient_substitutions#")
        self.uses_ingredient_predicate = self.substitutions_namespace.term("uses_ingredient")
        self.has_suggested_substitution_predicate = self.substitutions_namespace.term("has_suggested_substitution")
        self.original_ingredient_predicate = self.substitutions_namespace.term("original_ingredient")
        self.new_ingredient_predicate = self.substitutions_namespace.term("new_ingredient")

    def get_number_of_substitution_samples_in_graph(self) -> int:
        return len(set(self.substitutions_graph.triples((None, self.has_suggested_substitution_predicate, None))))

    def get_random_substitution_sample_generator(self) -> Generator[Tuple[Tuple[set[URIRef], URIRef, URIRef]], None, None]:
        for recipe_iri, _, ingredient_substitution_iri in self.substitutions_graph.triples((None, self.has_suggested_substitution_predicate, None)):
            recipe_ingredients = set(self.substitutions_graph.objects(subject=recipe_iri, predicate=self.uses_ingredient_predicate))
            original_ingredient = next(self.substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=self.original_ingredient_predicate))
            new_ingredient = next(self.substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=self.new_ingredient_predicate))
            yield recipe_ingredients, original_ingredient, new_ingredient


    def reveal_new_ingredient_of_substitution(self, substitution_iri) -> URIRef:
        return next(self.substitutions_graph.objects(subject=substitution_iri, predicate=self.new_ingredient_predicate))



class TrainingDatasetActiveLearningDataset(BasicSubstitutionsDataset):
    def __init__(self, substitutions_graph_filepath: str):
        super().__init__(substitutions_graph_filepath)

    def return_all_subs_iris_recipe_ings_and_source_ings(self) -> Tuple[List[URIRef], List[Set[URIRef]], List[URIRef]]:
        # get all ingredient substitutions
        # for recipe_iri, _, substitution_entry in self.substitutions_graph.triples((None, self.has_suggested_substitution_predicate, None)):

        ingredient_substitutions:list[URIRef] = []
        all_recipe_ingredients:list[set[URIRef]] = []
        original_ingredients:list[URIRef] = []

        for recipe_iri, _, ingredient_substitution_iri in self.substitutions_graph.triples((None, self.has_suggested_substitution_predicate, None)):
            recipe_ingredients = set(self.substitutions_graph.objects(subject=recipe_iri, predicate=self.uses_ingredient_predicate))
            original_ingredient = next(self.substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=self.original_ingredient_predicate))
            # new_ingredient = next(self.substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=self.new_ingredient_predicate))
            ingredient_substitutions.append(ingredient_substitution_iri)
            all_recipe_ingredients.append(recipe_ingredients)
            original_ingredients.append(original_ingredient)

        return ingredient_substitutions, all_recipe_ingredients, original_ingredients



# <http://idea.rpi.edu/heals/kb/recipe/000928de-Creme%20Brulee> ns1:has_suggested_substitution <http://lr.cs.vu.nl/ingredient_substitutions#substitution_suggestion/10f80d6844/0>,


#         <http://lr.cs.vu.nl/ingredient_substitutions#substitution_suggestion/73f77a1a2e/1> ;


#     ns1:uses_ingredient <http://idea.rpi.edu/heals/kb/ingredientname/brown%20sugar>,
#         <http://idea.rpi.edu/heals/kb/ingredientname/egg%20yolks>,
#         <http://idea.rpi.edu/heals/kb/ingredientname/heavy%20cream>,
#         <http://idea.rpi.edu/heals/kb/ingredientname/sugar>,
#         <http://idea.rpi.edu/heals/kb/ingredientname/vanilla%20bean> .


# <http://lr.cs.vu.nl/ingredient_substitutions#substitution_suggestion/73f77a1a2e/1> ns1:new_ingredient <http://idea.rpi.edu/heals/kb/ingredientname/vanilla%20essence> ;
#     ns1:original_ingredient <http://idea.rpi.edu/heals/kb/ingredientname/vanilla%20bean> .
