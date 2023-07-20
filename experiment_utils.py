from typing import Optional, Tuple, Generator
from Agent import Agent
from rdflib import Graph, URIRef, Namespace
from tqdm import tqdm

# def get_namespace_of_ontology(prefix:str) -> str:
#     pass

def calculate_rank_of_target(ranked_candidates:list[URIRef], target:URIRef) -> Optional[int]:
    try:
        return ranked_candidates.index(target) + 1
    except:
        return None

def iterate_over_substitution_examples_of_given_graph(substitutions_graph: Graph,
        ingredient_substitutions_ontology_prefix= "http://lr.cs.vu.nl/ingredient_substitutions#")\
                        -> Generator[Tuple[Tuple[set[URIRef], URIRef, URIRef]], None, None]:

    ingredient_substitutions_ontology_namespace = Namespace(ingredient_substitutions_ontology_prefix)
    has_suggested_substitution_predicate = ingredient_substitutions_ontology_namespace.term("has_suggested_substitution")
    uses_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("uses_ingredient")
    new_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("new_ingredient")
    original_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("original_ingredient")

    for recipe_iri, _, ingredient_substitution_iri in substitutions_graph.triples((None, has_suggested_substitution_predicate, None)):
        recipe_ingredients = set(substitutions_graph.objects(subject=recipe_iri, predicate=uses_ingredient_predicate))
        original_ingredient = next(substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=original_ingredient_predicate))
        new_ingredient = next(substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=new_ingredient_predicate))

        yield recipe_ingredients, original_ingredient, new_ingredient



def evaluate_agent(agent: Agent, substitutions_graph: Graph, penalize_not_found_with_rank:int = 16779):

    print("Evaluation is starting:")
    ingredient_not_found_counter: int = 0
    hit_at_1:float = 0
    hit_at_10:float = 0
    hit_at_100:float = 0
    target_rank_sum:int = 0
    number_of_samples:int = 0

    average_number_of_results: float = 0
    eval_sample_generator = iterate_over_substitution_examples_of_given_graph(substitutions_graph)
    # while True:
        # try:
    for recipe_ingredients, original_ingredient, new_ingredient in tqdm(eval_sample_generator):

         # while example is not None
        ranked_ingredients:list[URIRef] = agent.infer_on_ingredient_substitution_query(recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient)
        average_number_of_results += len(ranked_ingredients)
        rank_of_target = calculate_rank_of_target(ranked_candidates=ranked_ingredients, target=new_ingredient)
        number_of_samples += 1
        if rank_of_target is None:
            ingredient_not_found_counter += 1
            # if the ingredient is not among the retrieved candidates, then we penalize as defined. Default value equal to number of ingredients.
            rank_of_target = penalize_not_found_with_rank

        target_rank_sum += rank_of_target

        if rank_of_target <= 100:
            hit_at_1 += 1
            hit_at_10 += 1
            hit_at_100 += 1
        elif rank_of_target <= 10:
            hit_at_1 += 1
            hit_at_10 += 1
        elif rank_of_target == 1:
            hit_at_1 += 1
        # except StopIteration:
        #     break

    hit_at_1 /= number_of_samples
    hit_at_10 /= number_of_samples
    hit_at_100 /= number_of_samples
    average_number_of_results /= number_of_samples

    average_rank = target_rank_sum / number_of_samples
    print(f"Eval: {hit_at_1} h@1, {hit_at_10} h@10, {hit_at_100} h@100, {average_rank} av_rank, {average_number_of_results} av_results, {ingredient_not_found_counter} not_found.")

def train_agent(agent: Agent, train_substitutions_graph: Graph, val_substitutions_graph: Graph, eval_every:int, max_steps:int):
    training_steps = 0
    training_sample_generator = iterate_over_substitution_examples_of_given_graph(train_substitutions_graph)
    while True:
        for recipe_ingredients, original_ingredient, new_ingredient in training_sample_generator:
            agent.learn_from_example(recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient, new_ingredient=new_ingredient)
            training_steps += 1
            if training_steps % eval_every == 0:
                evaluate_agent(agent, val_substitutions_graph)
            if training_steps == max_steps:
                print(f"Training reached the maximum number of steps {max_steps}, and will now terminate")
                break
    # except StopIteration:
    # training_sample_generator = iterate_over_substitution_examples_of_given_graph(train_substitutions_graph)


    # evaluate_agent(agent, val_substitutions_graph)
