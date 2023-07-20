from typing import Optional, Tuple
from Agent import Agent
from rdflib import Graph, URIRef, Namespace

# def get_namespace_of_ontology(prefix:str) -> str:
#     pass

def calculate_rank_of_target(ranked_candidates:list[URIRef], target:URIRef) -> Optional[int]:
    try:
        return ranked_candidates.index(target) + 1
    except:
        return None


def iterate_over_substitution_examples_of_given_graph(substitutions_graph: Graph,
        ingredient_substitutions_ontology_prefix= "http://lr.cs.vu.nl/ingredient_substitutions#")\
                        -> Tuple[list[URIRef], URIRef, URIRef]:

    ingredient_substitutions_ontology_namespace = Namespace(ingredient_substitutions_ontology_prefix)
    has_suggested_substitution_predicate = ingredient_substitutions_ontology_namespace.term("has_suggested_substitution")
    uses_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("uses_ingredient")
    new_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("ingredient_a_iri")
    original_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("ingredient_b_iri")

    for recipe_iri, _, ingredient_substitution_iri in substitutions_graph.triples((None, has_suggested_substitution_predicate, None)):
        recipe_ingredients = substitutions_graph.subjects(object=recipe_iri, predicate=uses_ingredient_predicate)
        original_ingredient = substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=original_ingredient_predicate)
        new_ingredient = substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=new_ingredient_predicate)

        yield recipe_ingredients, original_ingredient, new_ingredient

    # yield None

def evaluate_agent(agent: Agent, substitutions_graph: Graph, penalize_not_found_with_rank:int = 16779):
    target_candidate_rank: list[int] = list()
    ingredient_not_found_counter: int = 0

    # while example is not None
    for recipe_ingredients, original_ingredient, new_ingredient in iterate_over_substitution_examples_of_given_graph(substitutions_graph):
        ranked_ingredients:list[URIRef] = agent.infer_on_ingredient_substitution_query(recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient)
        rank_of_target = calculate_rank_of_target(ranked_candidates=ranked_ingredients, target=new_ingredient)
        if rank_of_target is None:
            ingredient_not_found_counter += 1
            # if the ingredient is not among the retrieved candidates, then we penalize as defined. Default value equal to number of ingredients.
            target_candidate_rank.append(penalize_not_found_with_rank)
        else:
            target_candidate_rank.append(rank_of_target)

def train_agent(agent: Agent, substitutions_graph: Graph, eval_every:int, max_epochs:int):
    training_steps = 0
    for epoch in range(max_epochs):
        for recipe_ingredients, original_ingredient, new_ingredient in iterate_over_substitution_examples_of_given_graph(substitutions_graph):
            agent.learn_from_example(recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient, new_ingredient=new_ingredient)
            training_steps += 1
            if training_steps % eval_every == 0:
                evaluate_agent(agent, substitutions_graph)

