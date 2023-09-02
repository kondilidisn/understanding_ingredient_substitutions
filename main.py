import argparse
from experiments import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp_dir', type=str, default="experiments")
    parser.add_argument('--exp_dir_addition', type=str, default="")
    parser.add_argument("--del_existing_exp_dir", action="store_true")

    # Experiment parameters
    parser.add_argument("--repetitions", default=1, type=int)
    parser.add_argument("--max_steps", default=100, type=int)# one epoch is currently 38142 training samples
    parser.add_argument("--eval_every", default=1, type=int)
    parser.add_argument("--run_complete_epoch", action="store_true", help="train over the complete training set")
    parser.add_argument("--skip_val", action="store_true", help="Do not evaluate performance on validation set.")
    parser.add_argument("--report_test", action="store_true", help="also register performance on test set while training")
    parser.add_argument("--threads", default=1, type=int)

    parser.add_argument("--ing2ing", default=0, type=int, help="ingredient_to_ingredient_substitution_counter")
    parser.add_argument("--ingP2ingP", default=0, type=int, help="ing_prop_to_ing_prop_score_multiplier")
    parser.add_argument("--recP2ingP", default=0, type=int, help="recipe_prop_to_ing_prop_score_multiplier")
    parser.add_argument("--unsRecP", default=0, type=int, help="recipe_property_similarity_score_multiplier")
    parser.add_argument("--unsIngP", default=0, type=int, help="original_ingredient_property_similarity_score_multiplier")

    # introspection parameters
    parser.add_argument("--intro_ing_mult", default=0, type=float, help="multiplied over log frequency of source ingredient")
    parser.add_argument("--intro_ing_prop_mult", default=0, type=float, help="multiplied over log frequency of source ingredient properties")
    parser.add_argument("--intro_epsilon", default=0.1, type=float, help="epsilon Greedy selection of expected informativeness over examples")

    # Dataset Parameters
    parser.add_argument('--dataset_dir', type=str, default="Dataset")
    parser.add_argument('--ing_prop_from_ont_filename_starts_with', type=str, default="ingredient_properties_from_ontology_")
    parser.add_argument('--ing_props', '--list', nargs='+', help='["foodOn", "foodOn_one_hop", "foodOn_all_hops"]', default=["foodOn", "foodOn_one_hop"]) # [foodOn, foodOn_one_hop, foodOn_all_hops]

    # Use like:
    # python arg.py -l 1234 2345 3456 4567
    parser.add_argument("--top_prop_percent", default=100, type=int, help="use the least frequent properties (percentage wise)")
    # parser.add_argument('--ing_properties_sources_ont', '--list', nargs='+', help='<Required> Set flag', default=["obo"])
    # python main.py -ing_properties_sources obo usda flavor

    # parser.add_argument("--run_tensorboard", action="store_true")
    args = parser.parse_args()
    # args.del_existing_exp_dir = True


    #
    # args["max_steps"] = 2
    # args["eval_every"] = 1
    # args["ing_props"] = ["foodOn", "foodOn_one_hop"]
    # args["top_prop_percent"] = 100
    # args["intro_ing_mult"] = 0
    # args["intro_ing_prop_mult"] = 0
    # args["ing2ing"] = 1
    # args["report_test"] = True
    # args["repetitions"] = 1
    # args["exp_dir_addition"] = "test_threads"
    # args["del_existing_exp_dir"] = True
    # args["threads"] = 1


    train_recipe_subs(args)

# (with repetitions)
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test --repetitions 4 --threads 1
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 1 --report_test --repetitions 4 --threads 1
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test --repetitions 4 --threads 1
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 1 --report_test --repetitions 4 --threads 1

#
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test --repetitions 4 --threads 1
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 1 --report_test --repetitions 4 --threads 1
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test --repetitions 4 --threads 1
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 1 --report_test --repetitions 4 --threads 1




# commands that resulted to the test reported results:
# random-ours-100
# python3 main.py --run_complete_epoch --eval_every 1000 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test
# random-baseline-100
# python3 main.py --run_complete_epoch --eval_every 1000 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 1 --report_test
# random-ours-10
# python3 main.py --run_complete_epoch --eval_every 1000 --ing_props foodOn foodOn_one_hop --top_prop_percent 10 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test
# random-baseline-10
# python3 main.py --run_complete_epoch --eval_every 1000 --ing_props foodOn foodOn_one_hop --top_prop_percent 10 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 1 --report_test
#
# intro-ours-100
# python3 main.py --run_complete_epoch --eval_every 1000 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test
# intro-baseline-100
# python3 main.py --run_complete_epoch --eval_every 1000 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 1 --report_test
# intro-ours-10
# python3 main.py --run_complete_epoch --eval_every 1000 --ing_props foodOn foodOn_one_hop --top_prop_percent 10 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test
# intro-baseline-10
# python3 main.py --run_complete_epoch --eval_every 1000 --ing_props foodOn foodOn_one_hop --top_prop_percent 10 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 1 --report_test


# upper bounds:
# python3 main.py --run_complete_epoch --eval_every 40000 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test


    #             ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100
    # experiments/ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100__final
# ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_100

# ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100
        # ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_100
        # ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_100__final


# ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__complete_epoch
# ing2ing=1__No_Ingredient_Perception_Used__introspection_random__complete_epoch

# ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__complete_epoch
# ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__complete_epoch


# test repetitions
# python3 main.py --max_steps 2 --eval_every 1 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 1 --report_test --repetitions 2 --exp_dir_addition test_repetitions --del_existing_exp_dir