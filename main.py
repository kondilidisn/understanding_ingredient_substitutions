import argparse
import os
import shutil

from experiments import *
from utils import *
from experiment_utils import *
from Agent import Agent

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp_dir', type=str, default="experiments")
    parser.add_argument('--exp_dir_addition', type=str, default="")
    parser.add_argument("--del_existing_exp_dir", action="store_true")

    # Experiment parameters
    # parser.add_argument("--repetitions", default=10, type=int)
    parser.add_argument("--max_steps", default=10000, type=int) # one epoch is currently 38142 training samples
    parser.add_argument("--eval_every", default=1000, type=int)
    parser.add_argument("--run_complete_epoch", action="store_true",
                    help="train for a complete epoch & --eval_every 5000")

    parser.add_argument("--ing2ing", default=5, type=int, help="ingredient_to_ingredient_substitution_counter")
    parser.add_argument("--ingP2ingP", default=1, type=int, help="ing_prop_to_ing_prop_score_multiplier")
    parser.add_argument("--recP2ingP", default=0, type=int, help="recipe_prop_to_ing_prop_score_multiplier")
    parser.add_argument("--unsRecP", default=0, type=int, help="recipe_property_similarity_score_multiplier")
    parser.add_argument("--unsIngP", default=0, type=int, help="original_ingredient_property_similarity_score_multiplier")


    # Dataset Parameters
    parser.add_argument('--dataset_dir', type=str, default="Dataset")
    parser.add_argument('--ing_prop_from_ont_filename_starts_with', type=str, default="ingredient_properties_from_ontology_")
    parser.add_argument('--ing_props', '--list', nargs='+', help='["foodOn", "foodOn_one_hop", "foodOn_all_hops"]', default=["foodOn"]) # [foodOn, foodOn_one_hop, foodOn_all_hops]
    # parser.add_argument('--ing_properties_sources_ont', '--list', nargs='+', help='<Required> Set flag', default=["obo"])
    # python main.py -ing_properties_sources obo usda flavor
    args = parser.parse_args()

    # make sure all ingredient properties make sense
    for ingredient_property_category in args.ing_props:
        ingredient_property_category_to_query_result_csv_filepath(ingredient_property_category)
    #     if it is not found, an error will occur


    # print("_".join(args.ing_properties_sources_ont))
    # exit()

    # check dataset path exists
    # if not os.path.exists(args.dataset_dir):
    #     raise ValueError(f"Dataset path '{args.dataset_dir}' could not be found!")

    agent = Agent(
                  ingredient_properties=args.ing_props, ing_to_ing_score_multiplier=args.ing2ing,
                  ing_prop_to_ing_prop_score_multiplier=args.ingP2ingP,
                  recipe_prop_to_ing_prop_score_multiplier=args.recP2ingP,
                  recipe_property_similarity_score_multiplier=args.unsRecP,
                  original_ingredient_property_similarity_score_multiplier=args.unsIngP)

    experiment_directory: str = ""

    experiment_directory += agent.get_agent_policy_str_description()
    experiment_directory += "__" + agent.get_agent_ing_perception_str_description()

    experiment_directory = os.path.join(args.exp_dir, experiment_directory)

    if args.run_complete_epoch:
        experiment_directory += "__complete_epoch"

    if args.exp_dir_addition != "":
        experiment_directory += "__" + args.exp_dir_addition

    args.del_existing_exp_dir = True

    if os.path.exists(experiment_directory):
        if args.del_existing_exp_dir:
            print(f"Directory {experiment_directory} already existed, but was deleted.")
            shutil.rmtree(experiment_directory)
        else:
            raise ValueError("Experiment directory already exists!")

    os.mkdir(experiment_directory)


    log_filename = os.path.join(experiment_directory, "experiment.log")

    print("Running experiment to be saved in:\n" + experiment_directory)

    print("Loading training and validation splits")

    train_substitutions_graph = Graph()
    # train_substitutions_graph.parse("Dataset/substitutions_graph_val.ttl")
    train_substitutions_graph.parse("Dataset/substitutions_graph_train.ttl")
    num_of_training_samples: int = get_number_of_substitution_samples_in_graph(train_substitutions_graph)
    print("Training data loaded, containing ingredient substitutions:", num_of_training_samples)
    val_substitutions_graph = Graph()
    val_substitutions_graph.parse("Dataset/substitutions_graph_val.ttl")
    print("Validation data loaded, containing ingredient substitutions:", get_number_of_substitution_samples_in_graph(val_substitutions_graph))

    if args.run_complete_epoch:
        args.max_steps = num_of_training_samples


    # test_substitutions_graph = Graph()
    # test_substitutions_graph.parse("Dataset/substitutions_graph_test.ttl")
    # print("Test data loaded, containing ingredient substitutions:", get_number_of_substitution_samples_in_graph(test_substitutions_graph))


    train_agent(agent, train_substitutions_graph, val_substitutions_graph,
                eval_every=args.eval_every, max_steps=args.max_steps,
                one_epoch=args.run_complete_epoch, log_filename=log_filename)