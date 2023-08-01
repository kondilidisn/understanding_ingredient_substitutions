import os.path
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

def get_number_of_substitution_samples_in_graph(substitutions_graph: Graph,
        ingredient_substitutions_ontology_prefix= "http://lr.cs.vu.nl/ingredient_substitutions#") -> int:

    ingredient_substitutions_ontology_namespace = Namespace(ingredient_substitutions_ontology_prefix)
    has_suggested_substitution_predicate = ingredient_substitutions_ontology_namespace.term("has_suggested_substitution")
    uses_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("uses_ingredient")
    new_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("new_ingredient")
    original_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("original_ingredient")

    return len(set(substitutions_graph.triples((None, has_suggested_substitution_predicate, None))))

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


def report_eval_performance(split, training_steps, hit_at_1, hit_at_10, hit_at_100, average_rank, average_number_of_results, ingredient_not_found_counter, log_filename=None, tensorboardwriter=None) -> None:
    performance_print_str = f"{split}, steps:{training_steps}| h@1:{hit_at_1:.4f}, h@10:{hit_at_10:.4f}, h@100:{hit_at_100:.4f}, av_rank:{average_rank:.1f}, av_results:{average_number_of_results:.1f}, #not_found:{ingredient_not_found_counter}"
    if log_filename is not None:
        with open(log_filename, "a") as log_file:
            log_file.write(performance_print_str + "\n")
    print(performance_print_str)
    tensorboardwriter.add_scalar("Hit@1", hit_at_1, training_steps)
    tensorboardwriter.add_scalar("Hit@10", hit_at_10, training_steps)
    tensorboardwriter.add_scalar("Hit@100", hit_at_100, training_steps)
    tensorboardwriter.add_scalar("Target_Rank", average_rank, training_steps)
    tensorboardwriter.add_scalar("|Results|", average_number_of_results, training_steps)
    tensorboardwriter.add_scalar("Not_Found_Counter", average_number_of_results, training_steps)


def evaluate_agent(agent: Agent, substitutions_graph: Graph, log_filename, penalize_not_found_with_rank:int = 16779,
                   split="val", training_steps=0, tensorboardwriter=None):

    # print("Evaluation is starting:")
    ingredient_not_found_counter: int = 0
    hit_at_1: float = 0
    hit_at_10: float = 0
    hit_at_100: float = 0
    target_rank_sum: int = 0
    number_of_samples: int = 0

    average_number_of_results: float = 0
    eval_sample_generator = iterate_over_substitution_examples_of_given_graph(substitutions_graph)
    # while True:
        # try:
    for recipe_ingredients, original_ingredient, new_ingredient in tqdm(eval_sample_generator ):

         # while example is not None
        ranked_ingredients: list[URIRef] = agent.infer_on_ingredient_substitution_query(recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient)
        average_number_of_results += len(ranked_ingredients)
        rank_of_target = calculate_rank_of_target(ranked_candidates=ranked_ingredients, target=new_ingredient)
        number_of_samples += 1
        if rank_of_target is None:
            ingredient_not_found_counter += 1
            # if the ingredient is not among the retrieved candidates, then we penalize as defined. Default value equal to number of ingredients.
            rank_of_target = penalize_not_found_with_rank
        # else:
        #     print(rank_of_target)

        target_rank_sum += rank_of_target
        if rank_of_target == 1:
            hit_at_1 += 1
            hit_at_10 += 1
            hit_at_100 += 1
        elif rank_of_target <= 10:
            hit_at_10 += 1
            hit_at_100 += 1
        elif rank_of_target <= 100:
            hit_at_100 += 1
        # except StopIteration:
        #     break

    hit_at_1 /= number_of_samples
    hit_at_10 /= number_of_samples
    hit_at_100 /= number_of_samples
    average_number_of_results /= number_of_samples

    average_rank = target_rank_sum / number_of_samples

    # performance_print_str = f"{split}, steps:{training_steps}| h@1:{hit_at_1:.4f}, h@10:{hit_at_10:.4f}, h@100:{hit_at_100:.4f}, av_rank:{average_rank:.1f}, av_results:{average_number_of_results:.1f}, #not_found:{ingredient_not_found_counter}"

    report_eval_performance(split, training_steps, hit_at_1, hit_at_10, hit_at_100, average_rank, average_number_of_results, ingredient_not_found_counter, log_filename, tensorboardwriter)

    # with open(log_filename, "a") as log_file:
    #     log_file.write(performance_print_str + "\n")
    # print(performance_print_str)

def train_agent(agent: Agent, train_substitutions_graph: Graph, val_substitutions_graph: Graph, log_filename,
                eval_every:int, max_steps:int, eval_split="val", one_epoch: bool = False, tensorboardwriter=None):
    training_steps = 0
    training_sample_generator = iterate_over_substitution_examples_of_given_graph(train_substitutions_graph)
    terminate:bool = False
    while not terminate:
        for _ in tqdm(range(eval_every)):
            try:
                substitution_example = next(training_sample_generator)
            except:
                if one_epoch:
                    print("Training of one epoch was completed.")
                    # evaluate_agent(agent, val_substitutions_graph, log_filename, split=eval_split,
                    #                training_steps=training_steps)
                    terminate = True
                    break
                training_sample_generator = iterate_over_substitution_examples_of_given_graph(train_substitutions_graph)
                substitution_example = next(training_sample_generator)
            recipe_ingredients, original_ingredient, new_ingredient = substitution_example
            agent.learn_from_example(recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient, new_ingredient=new_ingredient)
            training_steps += 1
            if training_steps == max_steps:
                print(f"Training reached the maximum number of steps {max_steps}, and will now terminate")
                terminate = True
                break
        evaluate_agent(agent, val_substitutions_graph, log_filename, split="Val", training_steps=training_steps, tensorboardwriter=tensorboardwriter)


    # except StopIteration:
    # training_sample_generator = iterate_over_substitution_examples_of_given_graph(train_substitutions_graph)


    # evaluate_agent(agent, val_substitutions_graph)
