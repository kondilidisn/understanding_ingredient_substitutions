import argparse
from experiments import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp_dir', type=str, default="experiments")
    parser.add_argument('--exp_dir_addition', type=str, default="")
    parser.add_argument("--del_existing_exp_dir", action="store_true")

    # Experiment parameters
    # parser.add_argument("--repetitions", default=10, type=int)
    parser.add_argument("--max_steps", default=100, type=int)# one epoch is currently 38142 training samples
    parser.add_argument("--eval_every", default=1, type=int)
    parser.add_argument("--run_complete_epoch", action="store_true", help="train over the complete training set")
    parser.add_argument("--report_test", action="store_true", help="also register performance on test set while training")

    parser.add_argument("--ing2ing", default=0, type=int, help="ingredient_to_ingredient_substitution_counter")
    parser.add_argument("--ingP2ingP", default=0, type=int, help="ing_prop_to_ing_prop_score_multiplier")
    parser.add_argument("--recP2ingP", default=0, type=int, help="recipe_prop_to_ing_prop_score_multiplier")
    parser.add_argument("--unsRecP", default=0, type=int, help="recipe_property_similarity_score_multiplier")
    parser.add_argument("--unsIngP", default=0, type=int, help="original_ingredient_property_similarity_score_multiplier")

    # introspection parameters
    parser.add_argument("--intro_ing_mult", default=10, type=float, help="multiplied over log frequency of source ingredient")
    parser.add_argument("--intro_ing_prop_mult", default=1, type=float, help="multiplied over log frequency of source ingredient properties")
    parser.add_argument("--intro_epsilon", default=0.1, type=float, help="epsilon Greedy selection of expected informativeness over examples")


    # Dataset Parameters
    parser.add_argument('--dataset_dir', type=str, default="Dataset")
    parser.add_argument('--ing_prop_from_ont_filename_starts_with', type=str, default="ingredient_properties_from_ontology_")
    parser.add_argument('--ing_props', '--list', nargs='+', help='["foodOn", "foodOn_one_hop", "foodOn_all_hops"]', default=["foodOn", "foodOn_one_hop"]) # [foodOn, foodOn_one_hop, foodOn_all_hops]
    # Use like:
    # python arg.py -l 1234 2345 3456 4567
    parser.add_argument("--top_prop_percent", default=10, type=int, help="use the least frequent properties (percentage wise)")
    # parser.add_argument('--ing_properties_sources_ont', '--list', nargs='+', help='<Required> Set flag', default=["obo"])
    # python main.py -ing_properties_sources obo usda flavor

    # parser.add_argument("--run_tensorboard", action="store_true")
    args = parser.parse_args()
    # args.del_existing_exp_dir = True

    train_and_eval_all_recipe_subs(args)