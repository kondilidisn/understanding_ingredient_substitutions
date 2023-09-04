import os

from experiments import *
import shutil
from utils import *
from experiment_utils import *
from Agent import Agent
from Datasets import BasicSubstitutionsDataset, TrainingDatasetActiveLearningDataset

from tensorboardX import SummaryWriter


def init_agent(args) -> Agent:

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

    return agent

def train_agent(agent: Agent, train_dataset: TrainingDatasetActiveLearningDataset,
                val_dataset: Optional[BasicSubstitutionsDataset],
                test_dataset: Optional[BasicSubstitutionsDataset], experiment_directory: str, eval_every: int,
                max_steps: int,
                one_epoch: bool = False, agent_asks_questions: bool = False,
                register_in_tensorboard:bool=True, number_of_threads:int=1) -> Tuple[
    Optional[dict[int,dict]], Optional[dict[int,dict]]]:

    tensorboardwriter:Optional[SummaryWriter] = None
    if register_in_tensorboard:
        tensorboardwriter = SummaryWriter(log_dir=experiment_directory)

    # eval_on_val: bool = val_dataset is not None
    # eval_on_test: bool = test_dataset is not None

    performance_record_on_val_set: Optional[dict[int,dict]] = defaultdict(dict) if val_dataset is not None else None
    performance_record_on_test_set: Optional[dict[int,dict]] = defaultdict(dict) if test_dataset is not None else None

    training_steps = 0
    if agent_asks_questions:
        ingredient_substitutions, all_recipe_ingredients, source_ingredients = train_dataset.return_all_subs_iris_recipe_ings_and_source_ings()
        agent.receive_available_training_data(ingredient_substitutions, all_recipe_ingredients, source_ingredients)
        agent.init_introspection()
    else:
        training_sample_generator = train_dataset.get_random_substitution_sample_generator()

    terminate: bool = False

    while not terminate:
        # if training_steps != 0:
        # calculate agent's task performance
        eval_and_report_agent_performance(agent, val_dataset, test_dataset,
                                          performance_record_on_val_set, performance_record_on_test_set,
                                          training_steps,
                                          experiment_directory, tensorboardwriter=tensorboardwriter,
                                          number_of_threads=number_of_threads)

        agent.save_agent(os.path.join(experiment_directory,"agent_state_steps_" + str(training_steps) + ".pkl"))

        for _ in tqdm(range(eval_every)):

            if agent_asks_questions:
                agents_substitution_query = agent.decide_which_substitution_to_reveal_next()
                # in case the agent has queried over the complete training data, we terminate the training
                if agents_substitution_query is None:
                    print("Training of one epoch was completed.")
                    terminate = True
                    break
                else:
                    selected_substitution_iri, recipe_ingredients, original_ingredient = agents_substitution_query
                new_ingredient = train_dataset.reveal_new_ingredient_of_substitution(selected_substitution_iri)
            else:
                try:
                    substitution_example = next(training_sample_generator)
                except:
                    if one_epoch:
                        print("Training of one epoch was completed.")
                        terminate = True
                        break
                    training_sample_generator = train_dataset.get_random_substitution_sample_generator()
                    substitution_example = next(training_sample_generator)

                recipe_ingredients, original_ingredient, new_ingredient = substitution_example

            agent.learn_from_example(recipe_ingredients=recipe_ingredients, original_ingredient=original_ingredient,
                                     new_ingredient=new_ingredient)
            training_steps += 1
            if training_steps == max_steps:
                print(f"Training reached the defined maximum number of steps ({max_steps}), and will now terminate")
                terminate = True
                break

    # calculate agent's task performance
    eval_and_report_agent_performance(agent, val_dataset, test_dataset,
                                      performance_record_on_val_set, performance_record_on_test_set,
                                      training_steps,
                                      experiment_directory, tensorboardwriter=tensorboardwriter,
                                      number_of_threads=number_of_threads)

    agent.save_agent(os.path.join(experiment_directory, "agent_state_final.pkl"))

    return performance_record_on_val_set, performance_record_on_test_set



def train_recipe_subs(args) -> None:
    agent = init_agent(args)

    experiment_directory = create_exp_dir(args, agent)

    # record the ingredient knowledge of the agent
    # agent.write_ingredient_knowledge(experiment_directory)

    train_dataset, val_dataset, test_dataset = load_data_splits(args)

    if args.run_complete_epoch:
        args.max_steps = train_dataset.get_number_of_substitution_samples_in_graph()

    if args.repetitions == 1:

        performance_record_on_val_set, performance_record_on_test_set = \
            train_agent(agent, train_dataset, val_dataset, test_dataset,
                        eval_every=args.eval_every, max_steps=args.max_steps,
                        one_epoch=args.run_complete_epoch, experiment_directory=experiment_directory,
                        agent_asks_questions=agent.uses_introspection(), register_in_tensorboard=True,
                        number_of_threads=args.threads)

        # we store the agent's test performance on the test set over time, in a pickle file
        test_performance_pickle_filename = os.path.join(experiment_directory, "test_performance.pkl")
        with open(test_performance_pickle_filename, 'wb') as handle:
            pickle.dump(performance_record_on_test_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

    else:

        agent_performance_over_repetitions_val:list = []
        agent_performance_over_repetitions_test:list = []

        for repetition in range(args.repetitions):
            print(f"Running repetition {repetition + 1}, out of {args.repetitions}.")

            agent.reset_agents_dynamic_knowledge()

            iter_exp_dir = os.path.join(experiment_directory, str(repetition))
            os.mkdir(iter_exp_dir)

            performance_record_on_val_set, performance_record_on_test_set = \
                train_agent(agent, train_dataset, val_dataset, test_dataset,
                            eval_every=args.eval_every, max_steps=args.max_steps,
                            one_epoch=args.run_complete_epoch, experiment_directory=iter_exp_dir,
                            agent_asks_questions=agent.uses_introspection(), register_in_tensorboard=False,
                            number_of_threads=args.threads)
            agent_performance_over_repetitions_val.append(performance_record_on_val_set)
            agent_performance_over_repetitions_test.append(performance_record_on_test_set)


        if val_dataset is not None:

            tensorboardwriter = SummaryWriter(log_dir=experiment_directory)

            agent_av_performance_val, agent_std_performance_dict_val = \
                aggregate_agent_performance_over_exp_repetitions(agent_performance_over_repetitions_val)
            training_steps_sorted = agent_av_performance_val.keys()
            print("Aggregated average performance on Validation set:")
            for training_steps in training_steps_sorted:
                report_eval_performance(split='val', training_steps=training_steps,
                                        performance_record_dict=agent_av_performance_val[training_steps],
                                        experiment_directory=experiment_directory, tensorboardwriter=tensorboardwriter)

            # # we store the agent's test performance on the test set over time, in a pickle file
            # test_performance_pickle_filename = os.path.join(experiment_directory, "test_performance.pkl")
            # with open(test_performance_pickle_filename, 'wb') as handle:
            #     pickle.dump(agent_av_performance_test, handle, protocol=pickle.HIGHEST_PROTOCOL)

        if test_dataset is not None:
            agent_av_performance_test, agent_std_performance_dict_test = \
                aggregate_agent_performance_over_exp_repetitions(agent_performance_over_repetitions_test)
            training_steps_sorted = agent_av_performance_test.keys()

            print("Aggregated average performance on Test set:")

            for training_steps in training_steps_sorted:
                report_eval_performance(split='test', training_steps=training_steps,
                                        performance_record_dict=agent_av_performance_test[training_steps],
                                        experiment_directory=experiment_directory, tensorboardwriter=None)

            # we store the agent's test performance on the test set over time, in a pickle file
            test_performance_pickle_filename = os.path.join(experiment_directory, "test_performance.pkl")
            with open(test_performance_pickle_filename, 'wb') as handle:
                pickle.dump(agent_av_performance_test, handle, protocol=pickle.HIGHEST_PROTOCOL)

            # we store the agent's test performance on the test set over time, in a pickle file
            test_performance_std_pickle_filename = os.path.join(experiment_directory, "test_performance_std.pkl")
            with open(test_performance_std_pickle_filename, 'wb') as handle:
                pickle.dump(agent_std_performance_dict_test, handle, protocol=pickle.HIGHEST_PROTOCOL)

