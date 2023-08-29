import os.path
from typing import Optional, Tuple, Generator
from Agent import Agent
from rdflib import Graph, URIRef, Namespace
from tqdm import tqdm
import pickle
from Datasets import BasicSubstitutionsDataset, TrainingDatasetActiveLearningDataset
from collections import defaultdict

# def get_namespace_of_ontology(prefix:str) -> str:
#     pass


def calculate_rank_of_target(ranked_candidates:list[URIRef], target:URIRef) -> Optional[int]:
    try:
        return ranked_candidates.index(target) + 1
    except:
        return None

# def get_number_of_substitution_samples_in_graph(substitutions_graph: Graph,
#         ingredient_substitutions_ontology_prefix= "http://lr.cs.vu.nl/ingredient_substitutions#") -> int:
#
#     ingredient_substitutions_ontology_namespace = Namespace(ingredient_substitutions_ontology_prefix)
#     has_suggested_substitution_predicate = ingredient_substitutions_ontology_namespace.term("has_suggested_substitution")
#     uses_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("uses_ingredient")
#     new_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("new_ingredient")
#     original_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("original_ingredient")
#
#     return len(set(substitutions_graph.triples((None, has_suggested_substitution_predicate, None))))
#
# def randomly_iterate_over_substitution_examples_of_given_graph(substitutions_graph: Graph,
#                                                                ingredient_substitutions_ontology_prefix= "http://lr.cs.vu.nl/ingredient_substitutions#")\
#                         -> Generator[Tuple[Tuple[set[URIRef], URIRef, URIRef]], None, None]:
#
#     ingredient_substitutions_ontology_namespace = Namespace(ingredient_substitutions_ontology_prefix)
#     has_suggested_substitution_predicate = ingredient_substitutions_ontology_namespace.term("has_suggested_substitution")
#     uses_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("uses_ingredient")
#     new_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("new_ingredient")
#     original_ingredient_predicate = ingredient_substitutions_ontology_namespace.term("original_ingredient")
#
#     for recipe_iri, _, ingredient_substitution_iri in substitutions_graph.triples((None, has_suggested_substitution_predicate, None)):
#         recipe_ingredients = set(substitutions_graph.objects(subject=recipe_iri, predicate=uses_ingredient_predicate))
#         original_ingredient = next(substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=original_ingredient_predicate))
#         new_ingredient = next(substitutions_graph.objects(subject=ingredient_substitution_iri, predicate=new_ingredient_predicate))
#
#         yield recipe_ingredients, original_ingredient, new_ingredient
#

def report_eval_performance(split, training_steps, performance_record_dict, experiment_directory, tensorboardwriter=None) -> None:
    hit_at_1 = performance_record_dict["Hit@1"]
    hit_at_3 = performance_record_dict["Hit@3"]
    hit_at_10 = performance_record_dict["Hit@10"]
    hit_at_100 = performance_record_dict["Hit@100"]
    average_rank = performance_record_dict["Target_Rank"]
    average_number_of_results = performance_record_dict["Results"]
    ingredient_not_found_counter = performance_record_dict["|Not_Found|"]

    performance_print_str = f"{split}, steps:{training_steps}| h@1:{hit_at_1:.4f}, h@3:{hit_at_3:.4f}, h@10:{hit_at_10:.4f}, h@100:{hit_at_100:.4f}, av_rank:{average_rank:.1f}, av_results:{average_number_of_results:.1f}, #not_found:{ingredient_not_found_counter}"

    split_log_filename = os.path.join(experiment_directory, "performance_on_" + split + ".log")
    with open(split_log_filename, "a") as log_file:
        log_file.write(performance_print_str + "\n")

    print(performance_print_str)

    if tensorboardwriter is not None:
        tensorboardwriter.add_scalar("Hit@1", hit_at_1, training_steps)
        tensorboardwriter.add_scalar("Hit@3", hit_at_3, training_steps)
        tensorboardwriter.add_scalar("Hit@10", hit_at_10, training_steps)
        tensorboardwriter.add_scalar("Hit@100", hit_at_100, training_steps)
        tensorboardwriter.add_scalar("Target_Rank", average_rank, training_steps)
        tensorboardwriter.add_scalar("Results", average_number_of_results, training_steps)
        tensorboardwriter.add_scalar("|Not_Found|", ingredient_not_found_counter, training_steps)


def evaluate_agent(agent: Agent, substitution_dataset: BasicSubstitutionsDataset, penalize_not_found_with_rank:int = 16779):

    ingredient_not_found_counter: int = 0
    hit_at_1: float = 0
    hit_at_3: float = 0
    hit_at_10: float = 0
    hit_at_100: float = 0
    target_rank_sum: int = 0
    number_of_samples: int = 0

    average_number_of_results: float = 0

    for recipe_ingredients, original_ingredient, new_ingredient in tqdm(substitution_dataset.get_random_substitution_sample_generator()):

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
            hit_at_3 += 1
            hit_at_10 += 1
            hit_at_100 += 1
        elif rank_of_target <= 3:
            hit_at_3 += 1
            hit_at_10 += 1
            hit_at_100 += 1
        elif rank_of_target <= 10:
            hit_at_10 += 1
            hit_at_100 += 1
        elif rank_of_target <= 100:
            hit_at_100 += 1

    hit_at_1 /= number_of_samples
    hit_at_3 /= number_of_samples
    hit_at_10 /= number_of_samples
    hit_at_100 /= number_of_samples
    average_number_of_results /= number_of_samples

    average_rank = target_rank_sum / number_of_samples

    # record the performance in a dict
    performance_record_dict:dict = dict()
    performance_record_dict["Hit@1"] = hit_at_1
    performance_record_dict["Hit@3"] = hit_at_3
    performance_record_dict["Hit@10"] = hit_at_10
    performance_record_dict["Hit@100"] = hit_at_100
    performance_record_dict["Target_Rank"] = average_rank
    performance_record_dict["Results"] = average_number_of_results
    performance_record_dict["|Not_Found|"] = ingredient_not_found_counter

    return performance_record_dict

def train_agent(agent: Agent, train_dataset: TrainingDatasetActiveLearningDataset, val_dataset: BasicSubstitutionsDataset,
                test_dataset: Optional[BasicSubstitutionsDataset], experiment_directory:str, eval_every:int, max_steps:int,
                one_epoch: bool = False, tensorboardwriter=None, agent_asks_questions:bool=False):

    also_eval_on_test_set:bool = test_dataset is not None
    performance_record_on_test_set:dict[int:dict] = dict()

    training_steps = 0
    if agent_asks_questions:
        ingredient_substitutions, all_recipe_ingredients, source_ingredients = train_dataset.return_all_subs_iris_recipe_ings_and_source_ings()
        agent.receive_available_training_data(ingredient_substitutions, all_recipe_ingredients, source_ingredients)
        agent.init_introspection()
    else:
        training_sample_generator = train_dataset.get_random_substitution_sample_generator()

    terminate:bool = False

    while not terminate:
        # calculate agent's task performance
        performance_record_dict = evaluate_agent(agent, val_dataset)
        report_eval_performance(split="val", training_steps=training_steps, performance_record_dict= performance_record_dict,
                                experiment_directory=experiment_directory, tensorboardwriter=tensorboardwriter)
        if also_eval_on_test_set:
            performance_record_on_test_set[training_steps] = evaluate_agent(agent, test_dataset)

        for _ in tqdm(range(eval_every)):

            if agent_asks_questions:
                selected_substitution_iri, recipe_ingredients, original_ingredient = agent.decide_which_substitution_to_reveal_next()
                new_ingredient = train_dataset.reveal_new_ingredient_of_substitution(selected_substitution_iri)
            else:
                try:
                    substitution_example = next(training_sample_generator)
                except:
                    if one_epoch:
                        print("Training of one epoch was completed.")
                        # evaluate_agent(agent, val_substitutions_graph, log_filename, split=eval_split,
                        #                training_steps=training_steps)
                        terminate = True
                        break
                    training_sample_generator = train_dataset.get_random_substitution_sample_generator()
                    substitution_example = next(training_sample_generator)

                recipe_ingredients, original_ingredient, new_ingredient = substitution_example


            agent.learn_from_example(recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient, new_ingredient=new_ingredient)
            training_steps += 1
            if training_steps == max_steps:
                print(f"Training reached the maximum number of steps {max_steps}, and will now terminate")
                terminate = True
                break

    # calculate agent's task performance
    performance_record_dict = evaluate_agent(agent, val_dataset)
    report_eval_performance(split="val", training_steps=training_steps, performance_record_dict= performance_record_dict,
                            experiment_directory=experiment_directory, tensorboardwriter=tensorboardwriter)
    if also_eval_on_test_set:
        performance_record_on_test_set[training_steps] = evaluate_agent(agent, test_dataset)
        # we store the agent's test performance on the test set over time, in a pickle file
        test_performance_pickle_filename = os.path.join(experiment_directory, "test_performance.pkl")
        with open(test_performance_pickle_filename, 'wb') as handle:
            pickle.dump(performance_record_on_test_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # we also store the trained agent under the
