from experiments import *
import shutil
from utils import *
from experiment_utils import *
from Agent import Agent
from Datasets import BasicSubstitutionsDataset, TrainingDatasetActiveLearningDataset

from tensorboardX import SummaryWriter

def train_and_eval_all_recipe_subs(args) -> None:

    # make sure all ingredient properties make sense
    for ingredient_property_category in args.ing_props:
        # if it is not found, an error will occur
        ingredient_property_category_to_query_result_csv_filepath(ingredient_property_category)



    property_filters: dict[str, float] = dict()
    property_filters["top_prop_percent"] = args.top_prop_percent
    # top_properties% = args.

    agent = Agent(
                  ingredient_properties=args.ing_props, property_filters=property_filters,
                  ing_to_ing_score_multiplier=args.ing2ing,
                  ing_prop_to_ing_prop_score_multiplier=args.ingP2ingP,
                  recipe_prop_to_ing_prop_score_multiplier=args.recP2ingP,
                  recipe_property_similarity_score_multiplier=args.unsRecP,
                  original_ingredient_property_similarity_score_multiplier=args.unsIngP,
                  introspection_ing_freq_multiplier=args.intro_ing_mult,
                  introspection_ing_prop_freq_multiplier=args.intro_ing_prop_mult,
                  introspection_epsilon_greedy=args.intro_epsilon
    )

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


    args.del_existing_exp_dir = True

    if os.path.exists(experiment_directory):
        if args.del_existing_exp_dir:
            print(f"Directory {experiment_directory} already existed, but was deleted.")
            shutil.rmtree(experiment_directory)
        else:
            raise ValueError("Experiment directory already exists!")

    os.mkdir(experiment_directory)

    # record the ingredient knowledge of the agent
    agent.write_ingredient_knowledge(experiment_directory)

    writer = SummaryWriter(log_dir=experiment_directory)

    print("Running experiment to be saved in:\n" + experiment_directory)

    print("Loading training and validation splits")



    # train_substitutions_graph:Graph = Graph()
    # train_substitutions_graph.parse("Dataset/substitutions_graph_val.ttl")

    train_dataset = TrainingDatasetActiveLearningDataset("Dataset/substitutions_graph_train.ttl")
    num_of_training_samples: int = train_dataset.get_number_of_substitution_samples_in_graph()
    print("Training data loaded, containing ingredient substitutions:", num_of_training_samples)
    # val_substitutions_graph:Graph = Graph()
    val_dataset = BasicSubstitutionsDataset("Dataset/substitutions_graph_val.ttl")
    print("Validation data loaded, containing ingredient substitutions:", val_dataset.get_number_of_substitution_samples_in_graph())

    test_substitutions_graph: Optional[Graph] = None

    test_dataset:Optional[BasicSubstitutionsDataset] = None

    if args.report_test:
        test_dataset = BasicSubstitutionsDataset("Dataset/substitutions_graph_test.ttl")
        print("Test data loaded, containing ingredient substitutions:", test_dataset.get_number_of_substitution_samples_in_graph())

    if args.run_complete_epoch:
        args.max_steps = num_of_training_samples

    # test_substitutions_graph = Graph()
    # test_substitutions_graph.parse("Dataset/substitutions_graph_test.ttl")
    # print("Test data loaded, containing ingredient substitutions:", get_number_of_substitution_samples_in_graph(test_substitutions_graph))
    # if args.run_tensorboard:
    #     os.system("tensorboard --logdir " + experiment_directory)


    train_agent(agent, train_dataset, val_dataset, test_dataset,
                eval_every=args.eval_every, max_steps=args.max_steps,
                one_epoch=args.run_complete_epoch, experiment_directory=experiment_directory, tensorboardwriter=writer,
                agent_asks_questions=agent.uses_introspection())

