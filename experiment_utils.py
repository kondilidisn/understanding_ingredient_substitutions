import copy
import os.path
from typing import Optional, Tuple, Generator, List
from Agent import Agent
from rdflib import Graph, URIRef, Namespace
from tqdm import tqdm
import pickle
from Datasets import BasicSubstitutionsDataset, TrainingDatasetActiveLearningDataset
import numpy as np
import shutil
from collections import defaultdict
from multiprocessing.pool import ThreadPool
# from multiprocessing.dummy import Pool as ThreadPool
from copy import deepcopy



def aggregate_agent_performance_over_exp_repetitions(agent_performance:list[dict[int,dict]]) \
    -> Tuple[dict[int,dict], dict[int,dict]]:

    agent_av_performance:dict[int,dict[int,dict]] = defaultdict(dict)
    agent_std_performance:dict[int,dict[int,dict]] = defaultdict(dict)

    # agent_performa
    for training_step in agent_performance[0]:
        for metric in agent_performance[0][training_step]:
            aggregated_metric_performance_list:list = []
            for repetition in range(len(agent_performance)):
                aggregated_metric_performance_list.append(agent_performance[repetition][training_step][metric])
            np_array = np.asarray(aggregated_metric_performance_list)
            agent_av_performance[training_step][metric] = np.mean(np_array)
            agent_std_performance[training_step][metric] = np.std(np_array)

    return agent_av_performance, agent_std_performance



def aggregate_statistics_of_dictionary_of_list_of_values(input_dict):
    av_dict = {}
    std_dict = {}
    for key in input_dict:
        object = input_dict[key]
        if isinstance(object, list) and isinstance(object[0], (int, float)):
            np_object = np.asarray(object)
            av_dict[key] = np.mean(np_object)
            std_dict[key] = np.std(np_object)
        else:
            av_dict[key] = object
    return av_dict, std_dict

def append_to_list_from_one_dictionary_to_other(source_dict, target_dict, keys_to_append_list=[]):
    for key in keys_to_append_list:
        # we make sure that we don't have lists of lists, but everything is kept in the same original 1-d list
        if isinstance(source_dict[key], list):
            target_dict[key] += source_dict[key]
        else:
            target_dict[key].append(source_dict[key])


def create_exp_dir(args, agent) -> str:
    experiment_directory: str = ""

    experiment_directory += agent.get_agent_policy_str_description()

    experiment_directory += "__" + agent.get_agent_ing_perception_str_description()

    agents_introspection_policy_description = agent.get_agent_introspection_policy_str_description()
    experiment_directory += "__introspection" + agents_introspection_policy_description

    experiment_directory = os.path.join(args.exp_dir, experiment_directory)

    if args.run_complete_epoch:
        experiment_directory += "__complete_epoch"
    else:
        experiment_directory += "__max_steps_" + str(args.max_steps)

    if args.exp_dir_addition != "":
        experiment_directory += "__" + args.exp_dir_addition

    # args.del_existing_exp_dir = True
    print("Experiment directory:", experiment_directory)

    if os.path.exists(experiment_directory):
        if args.del_existing_exp_dir:
            print(f"Directory {experiment_directory} already existed, but was deleted.")
            shutil.rmtree(experiment_directory)
        else:
            print("Experiment directory already exists!")
            exit()
            # raise ValueError("Experiment directory already exists!")

    os.mkdir(experiment_directory)

    print("Running experiment to be saved in:\n" + experiment_directory)

    return experiment_directory


def load_data_splits(args) -> Tuple[TrainingDatasetActiveLearningDataset,
                                    Optional[BasicSubstitutionsDataset], Optional[BasicSubstitutionsDataset]]:
    print("Loading training and validation splits")

    train_dataset = TrainingDatasetActiveLearningDataset("Dataset/substitutions_graph_train.ttl")
    print("Training data loaded, containing ingredient substitutions:",
          train_dataset.get_number_of_substitution_samples_in_graph())

    val_dataset: Optional[BasicSubstitutionsDataset] = None
    if not args.skip_val:
        val_dataset = BasicSubstitutionsDataset("Dataset/substitutions_graph_val.ttl")
        print("Validation data loaded, containing ingredient substitutions:",
              val_dataset.get_number_of_substitution_samples_in_graph())

    test_dataset: Optional[BasicSubstitutionsDataset] = None

    if args.report_test:
        test_dataset = BasicSubstitutionsDataset("Dataset/substitutions_graph_test.ttl")
        print("Test data loaded, containing ingredient substitutions:",
              test_dataset.get_number_of_substitution_samples_in_graph())

    return train_dataset, val_dataset, test_dataset




# def get_namespace_of_ontology(prefix:str) -> str:
#     pass
#
# def aggregate_statistics_of_dictionary_of_list_of_values(input_dict):
#     av_dict = {}
#     std_dict = {}
#     for key in input_dict:
#         object = input_dict[key]
#         if isinstance(object, list) and isinstance(object[0], (int, float)):
#             np_object = np.asarray(object)
#             av_dict[key] = np.mean(np_object)
#             std_dict[key] = np.std(np_object)
#         else:
#             av_dict[key] = object
#     return av_dict, std_dict
#
#
# def append_to_list_from_one_dictionary_to_other(source_dict, target_dict, keys_to_append_list=[]):
#     for key in keys_to_append_list:
#         # we make sure that we don't have lists of lists, but everything is kept in the same original 1-d list
#         if isinstance(source_dict[key], list):
#             target_dict[key] += source_dict[key]
#         else:
#             target_dict[key].append(source_dict[key])


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
    mrr = performance_record_dict["MRR"]
    average_number_of_results = performance_record_dict["Results"]
    target_found_ratio = performance_record_dict["Tar_Found"]
    # ingredient_not_found_counter = performance_record_dict["|Not_Found|"]

    performance_print_str = f"{split}, steps:{training_steps}| h@1:{hit_at_1:.4f}, h@3:{hit_at_3:.4f}, h@10:{hit_at_10:.4f}, h@100:{hit_at_100:.4f}, MRR:{mrr:.4f}, av_results:{average_number_of_results:.1f}, #found:{target_found_ratio:.4f}"

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
        performance_record_dict["MRR"] = mrr
        tensorboardwriter.add_scalar("Results", average_number_of_results, training_steps)
        tensorboardwriter.add_scalar("Tar_Found", target_found_ratio, training_steps)
        # tensorboardwriter.add_scalar("|Not_Found|", ingredient_not_found_counter, training_steps)


def get_agents_inferred_target_ingredient_ranks(agent:Agent,
                                                substitution_examples:List[Tuple[set[URIRef],URIRef,URIRef]],
                                                total_ingredients:int) -> Tuple[List[int], List[int], int]:

    target_ingredient_ranks:list[int] = []
    number_of_results:list[int] = []
    ingredient_not_found_counter:int = 0

    agent_copy = deepcopy(agent)

    for substitution_example in substitution_examples:
        recipe_ingredients, original_ingredient, new_ingredient = substitution_example

         # while example is not None
        ranked_ingredients: list[URIRef] = agent_copy.infer_on_ingredient_substitution_query(recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient)
        number_of_returned_results = len(ranked_ingredients)
        number_of_results.append(number_of_returned_results)
        # average_number_of_results += number_of_returned_results
        rank_of_target = calculate_rank_of_target(ranked_candidates=ranked_ingredients, target=new_ingredient)
        # number_of_samples += 1
        if rank_of_target is None:
            ingredient_not_found_counter += 1

            remaining_ranks = total_ingredients - number_of_returned_results

            # if the ingredient is not among the retrieved candidates, then we randomly assign it one of the remaining rankings.
            # equivalent to ranking randomly the remaining / non-returned ingredients
            random_target_rank = np.random.randint(remaining_ranks, high=None) + number_of_returned_results + 1
            rank_of_target = random_target_rank
        target_ingredient_ranks.append(rank_of_target)

    return  target_ingredient_ranks, number_of_results, ingredient_not_found_counter


def evaluate_agent(agent: Agent, substitution_dataset: BasicSubstitutionsDataset, number_of_threads:int, total_ingredients:int = 16780):
    import datetime

    start_time = datetime.datetime.now()


    number_of_samples = substitution_dataset.get_number_of_substitution_samples_in_graph()

    # average_number_of_results: float = 0

    thread_inputs:List[Tuple[Agent,list, int]] = []

    for i in range(number_of_threads):
        thread_input = []
        # thread_input.append(agent)
        # thread_input.append([])
        # thread_input.append(total_ingredients)
        thread_input = (agent, [], total_ingredients)
        thread_inputs.append(thread_input)

    # substitution_examples_split_to_threads: list[list] = [[] for _ in range(number_of_threads)]

    thread_index: int = 0
    for substitution_example in substitution_dataset.get_random_substitution_sample_generator():
        thread_inputs[thread_index][1].append(substitution_example)
        thread_index = (thread_index + 1) % number_of_threads


    pool = ThreadPool(number_of_threads)

    results = pool.starmap(get_agents_inferred_target_ingredient_ranks, thread_inputs)
    # results = pool.map(get_agents_inferred_target_ingredient_ranks, agent, )

    pool.close()
    pool.join()

    complete_ranks_of_target = []
    complete_number_of_results = []
    complete_ingredient_not_found_counter = 0


    # print(results)


    for i in range(len(results)):
        complete_ranks_of_target += results[i][0]
        complete_number_of_results += results[i][1]
        complete_ingredient_not_found_counter += results[i][2]

    complete_ranks_of_target = np.asarray(complete_ranks_of_target)
    complete_number_of_results = np.asarray(complete_number_of_results)
    complete_ingredient_not_found_counter = np.asarray(complete_ingredient_not_found_counter)


    hit_at_1 = np.mean(complete_ranks_of_target == 1)
    hit_at_3 = np.mean(complete_ranks_of_target < 4)
    hit_at_10 = np.mean(complete_ranks_of_target < 11)
    hit_at_100 = np.mean(complete_ranks_of_target < 101)
    average_number_of_results = np.mean(complete_number_of_results)
    mrr = np.mean(1 / complete_ranks_of_target)
    average_rank = np.mean(complete_ranks_of_target)
    target_found_ratio = (number_of_samples - complete_ingredient_not_found_counter) / number_of_samples

    # record the performance in a dict
    performance_record_dict:dict = dict()
    performance_record_dict["Hit@1"] = hit_at_1
    performance_record_dict["Hit@3"] = hit_at_3
    performance_record_dict["Hit@10"] = hit_at_10
    performance_record_dict["Hit@100"] = hit_at_100
    performance_record_dict["Target_Rank"] = average_rank
    performance_record_dict["MRR"] = mrr
    performance_record_dict["Results"] = average_number_of_results
    performance_record_dict["Tar_Found"] = target_found_ratio


    end_time = datetime.datetime.now()

    print("Evaluation duration:", end_time - start_time)

    return performance_record_dict

    # we also store the trained agent under the

def eval_and_report_agent_performance(agent, val_dataset,test_dataset,
                                      performance_record_on_val_set, performance_record_on_test_set, training_steps,
                                      experiment_directory, tensorboardwriter=None, number_of_threads=1) \
        -> Tuple[Optional[dict[int,dict]], Optional[dict[int,dict]]]:

    if val_dataset is not None:
        performance_record_on_val_set[training_steps] = evaluate_agent(agent, val_dataset, number_of_threads)
        report_eval_performance(split="val", training_steps=training_steps,
                                performance_record_dict=performance_record_on_val_set[training_steps],
                                experiment_directory=experiment_directory, tensorboardwriter=tensorboardwriter,)

    if test_dataset is not None:
        performance_record_on_test_set[training_steps] = evaluate_agent(agent, test_dataset, number_of_threads)
        report_eval_performance(split="test", training_steps=training_steps,
                                performance_record_dict=performance_record_on_test_set[training_steps],
                                experiment_directory=experiment_directory, tensorboardwriter=None,)
        # we store the agent's test performance on the test set over time, in a pickle file
        test_performance_pickle_filename = os.path.join(experiment_directory, "test_performance.pkl")
        with open(test_performance_pickle_filename, 'wb') as handle:
            pickle.dump(performance_record_on_test_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return performance_record_on_val_set, performance_record_on_test_set
