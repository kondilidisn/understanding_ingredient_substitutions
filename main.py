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
# random-ours-100
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test --repetitions 4 --threads 1
# Aggregated average performance on Validation set:
# val, steps:0| h@1:0.0247, h@3:0.0366, h@10:0.0396, h@100:0.0582, MRR:0.0310, av_results:1735.1, #found:0.2356
# val, steps:10| h@1:0.0222, h@3:0.0374, h@10:0.0402, h@100:0.0594, MRR:0.0301, av_results:1790.9, #found:0.2403
# val, steps:20| h@1:0.0235, h@3:0.0394, h@10:0.0424, h@100:0.0628, MRR:0.0318, av_results:1852.9, #found:0.2504
# val, steps:30| h@1:0.0282, h@3:0.0409, h@10:0.0440, h@100:0.0675, MRR:0.0351, av_results:1922.1, #found:0.2682
# val, steps:40| h@1:0.0303, h@3:0.0433, h@10:0.0469, h@100:0.0708, MRR:0.0374, av_results:2019.1, #found:0.2799
# val, steps:50| h@1:0.0322, h@3:0.0440, h@10:0.0473, h@100:0.0687, MRR:0.0387, av_results:2095.9, #found:0.2852
# val, steps:60| h@1:0.0327, h@3:0.0445, h@10:0.0486, h@100:0.0704, MRR:0.0394, av_results:2123.6, #found:0.2892
# val, steps:70| h@1:0.0333, h@3:0.0447, h@10:0.0492, h@100:0.0722, MRR:0.0399, av_results:2179.6, #found:0.2973
# val, steps:80| h@1:0.0326, h@3:0.0517, h@10:0.0560, h@100:0.0726, MRR:0.0424, av_results:2219.8, #found:0.3024
# val, steps:90| h@1:0.0321, h@3:0.0470, h@10:0.0507, h@100:0.0729, MRR:0.0399, av_results:2284.1, #found:0.3102
# val, steps:100| h@1:0.0328, h@3:0.0486, h@10:0.0524, h@100:0.0757, MRR:0.0410, av_results:2313.5, #found:0.3142
# Aggregated average performance on Test set:
# test, steps:0| h@1:0.0241, h@3:0.0343, h@10:0.0380, h@100:0.0603, MRR:0.0300, av_results:1731.0, #found:0.2421
# test, steps:10| h@1:0.0210, h@3:0.0356, h@10:0.0389, h@100:0.0617, MRR:0.0291, av_results:1786.0, #found:0.2465
# test, steps:20| h@1:0.0223, h@3:0.0371, h@10:0.0407, h@100:0.0646, MRR:0.0305, av_results:1847.0, #found:0.2567
# test, steps:30| h@1:0.0282, h@3:0.0393, h@10:0.0428, h@100:0.0704, MRR:0.0348, av_results:1916.3, #found:0.2757
# test, steps:40| h@1:0.0303, h@3:0.0415, h@10:0.0448, h@100:0.0735, MRR:0.0369, av_results:2013.8, #found:0.2877
# test, steps:50| h@1:0.0320, h@3:0.0423, h@10:0.0453, h@100:0.0715, MRR:0.0382, av_results:2091.0, #found:0.2934
# test, steps:60| h@1:0.0323, h@3:0.0430, h@10:0.0466, h@100:0.0724, MRR:0.0388, av_results:2118.1, #found:0.2971
# test, steps:70| h@1:0.0326, h@3:0.0432, h@10:0.0475, h@100:0.0745, MRR:0.0393, av_results:2173.4, #found:0.3071
# test, steps:80| h@1:0.0323, h@3:0.0496, h@10:0.0537, h@100:0.0745, MRR:0.0416, av_results:2213.7, #found:0.3121
# test, steps:90| h@1:0.0315, h@3:0.0445, h@10:0.0483, h@100:0.0752, MRR:0.0388, av_results:2278.1, #found:0.3195
# test, steps:100| h@1:0.0320, h@3:0.0457, h@10:0.0505, h@100:0.0784, MRR:0.0398, av_results:2308.0, #found:0.3228

# random-baseline-100
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 0 --intro_ing_prop_mult 0 --ing2ing 1 --report_test --repetitions 4 --threads 1
# Aggregated average performance on Validation set:
# val, steps:0| h@1:0.0216, h@3:0.0335, h@10:0.0412, h@100:0.0462, MRR:0.0287, av_results:0.6, #found:0.0408
# val, steps:10| h@1:0.0224, h@3:0.0347, h@10:0.0426, h@100:0.0479, MRR:0.0297, av_results:0.6, #found:0.0419
# val, steps:20| h@1:0.0233, h@3:0.0365, h@10:0.0444, h@100:0.0496, MRR:0.0311, av_results:0.7, #found:0.0439
# val, steps:30| h@1:0.0234, h@3:0.0382, h@10:0.0461, h@100:0.0519, MRR:0.0320, av_results:0.7, #found:0.0456
# val, steps:40| h@1:0.0256, h@3:0.0405, h@10:0.0488, h@100:0.0547, MRR:0.0344, av_results:0.7, #found:0.0482
# val, steps:50| h@1:0.0264, h@3:0.0412, h@10:0.0496, h@100:0.0557, MRR:0.0351, av_results:0.7, #found:0.0489
# val, steps:60| h@1:0.0270, h@3:0.0418, h@10:0.0501, h@100:0.0554, MRR:0.0357, av_results:0.7, #found:0.0498
# val, steps:70| h@1:0.0273, h@3:0.0423, h@10:0.0507, h@100:0.0560, MRR:0.0361, av_results:0.7, #found:0.0501
# val, steps:80| h@1:0.0276, h@3:0.0434, h@10:0.0534, h@100:0.0592, MRR:0.0369, av_results:0.8, #found:0.0528
# val, steps:90| h@1:0.0283, h@3:0.0440, h@10:0.0543, h@100:0.0592, MRR:0.0376, av_results:0.8, #found:0.0536
# val, steps:100| h@1:0.0288, h@3:0.0446, h@10:0.0551, h@100:0.0593, MRR:0.0381, av_results:0.8, #found:0.0544
# Aggregated average performance on Test set:
# test, steps:0| h@1:0.0201, h@3:0.0327, h@10:0.0405, h@100:0.0454, MRR:0.0277, av_results:0.6, #found:0.0400
# test, steps:10| h@1:0.0207, h@3:0.0338, h@10:0.0418, h@100:0.0469, MRR:0.0286, av_results:0.6, #found:0.0412
# test, steps:20| h@1:0.0219, h@3:0.0357, h@10:0.0435, h@100:0.0491, MRR:0.0301, av_results:0.7, #found:0.0430
# test, steps:30| h@1:0.0222, h@3:0.0378, h@10:0.0456, h@100:0.0514, MRR:0.0313, av_results:0.7, #found:0.0452
# test, steps:40| h@1:0.0241, h@3:0.0399, h@10:0.0482, h@100:0.0529, MRR:0.0333, av_results:0.7, #found:0.0475
# test, steps:50| h@1:0.0247, h@3:0.0403, h@10:0.0485, h@100:0.0534, MRR:0.0339, av_results:0.7, #found:0.0482
# test, steps:60| h@1:0.0251, h@3:0.0411, h@10:0.0498, h@100:0.0546, MRR:0.0346, av_results:0.7, #found:0.0489
# test, steps:70| h@1:0.0254, h@3:0.0413, h@10:0.0498, h@100:0.0546, MRR:0.0348, av_results:0.7, #found:0.0493
# test, steps:80| h@1:0.0258, h@3:0.0424, h@10:0.0525, h@100:0.0588, MRR:0.0358, av_results:0.8, #found:0.0520
# test, steps:90| h@1:0.0261, h@3:0.0429, h@10:0.0534, h@100:0.0587, MRR:0.0362, av_results:0.8, #found:0.0527
# test, steps:100| h@1:0.0266, h@3:0.0436, h@10:0.0543, h@100:0.0596, MRR:0.0368, av_results:0.8, #found:0.0534

# intro-ours-100
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 100 --ingP2ingP 10 --recP2ingP 1 --report_test --repetitions 4 --threads 1
# Aggregated average performance on Validation set:
# val, steps:0| h@1:0.0405, h@3:0.0647, h@10:0.0755, h@100:0.1000, MRR:0.0548, av_results:2747.5, #found:0.3539
# val, steps:10| h@1:0.0487, h@3:0.0733, h@10:0.0819, h@100:0.1072, MRR:0.0626, av_results:2933.3, #found:0.3739
# val, steps:20| h@1:0.0494, h@3:0.0739, h@10:0.0817, h@100:0.1064, MRR:0.0632, av_results:3109.0, #found:0.3942
# val, steps:30| h@1:0.0518, h@3:0.0779, h@10:0.0845, h@100:0.1133, MRR:0.0665, av_results:3309.2, #found:0.4181
# val, steps:40| h@1:0.0529, h@3:0.0794, h@10:0.0871, h@100:0.1169, MRR:0.0677, av_results:3443.9, #found:0.4364
# val, steps:50| h@1:0.0564, h@3:0.0835, h@10:0.0919, h@100:0.1215, MRR:0.0717, av_results:3591.2, #found:0.4556
# val, steps:60| h@1:0.0577, h@3:0.0861, h@10:0.0937, h@100:0.1250, MRR:0.0735, av_results:3684.9, #found:0.4710
# val, steps:70| h@1:0.0593, h@3:0.0876, h@10:0.0983, h@100:0.1296, MRR:0.0758, av_results:3783.0, #found:0.4797
# val, steps:80| h@1:0.0580, h@3:0.0867, h@10:0.0980, h@100:0.1288, MRR:0.0748, av_results:3931.8, #found:0.4894
# val, steps:90| h@1:0.0579, h@3:0.0864, h@10:0.0982, h@100:0.1300, MRR:0.0748, av_results:4074.6, #found:0.5016
# val, steps:100| h@1:0.0574, h@3:0.0900, h@10:0.1036, h@100:0.1356, MRR:0.0764, av_results:4130.8, #found:0.5090
# Aggregated average performance on Test set:
# test, steps:0| h@1:0.0408, h@3:0.0639, h@10:0.0752, h@100:0.1018, MRR:0.0548, av_results:2732.5, #found:0.3518
# test, steps:10| h@1:0.0486, h@3:0.0724, h@10:0.0816, h@100:0.1092, MRR:0.0624, av_results:2918.4, #found:0.3716
# test, steps:20| h@1:0.0492, h@3:0.0731, h@10:0.0811, h@100:0.1084, MRR:0.0629, av_results:3092.4, #found:0.3922
# test, steps:30| h@1:0.0510, h@3:0.0761, h@10:0.0841, h@100:0.1150, MRR:0.0656, av_results:3291.3, #found:0.4149
# test, steps:40| h@1:0.0516, h@3:0.0773, h@10:0.0866, h@100:0.1183, MRR:0.0665, av_results:3425.1, #found:0.4328
# test, steps:50| h@1:0.0553, h@3:0.0808, h@10:0.0914, h@100:0.1242, MRR:0.0705, av_results:3572.4, #found:0.4526
# test, steps:60| h@1:0.0572, h@3:0.0845, h@10:0.0934, h@100:0.1276, MRR:0.0729, av_results:3665.0, #found:0.4689
# test, steps:70| h@1:0.0585, h@3:0.0861, h@10:0.0980, h@100:0.1321, MRR:0.0750, av_results:3762.6, #found:0.4784
# test, steps:80| h@1:0.0571, h@3:0.0850, h@10:0.0978, h@100:0.1309, MRR:0.0739, av_results:3911.0, #found:0.4875
# test, steps:90| h@1:0.0573, h@3:0.0856, h@10:0.0987, h@100:0.1321, MRR:0.0743, av_results:4053.4, #found:0.4995
# test, steps:100| h@1:0.0573, h@3:0.0894, h@10:0.1036, h@100:0.1367, MRR:0.0763, av_results:4109.0, #found:0.5067

# intro-baseline-100
# python3 main.py --max_steps 100 --eval_every 10 --ing_props foodOn foodOn_one_hop --top_prop_percent 100 --intro_ing_mult 10 --intro_ing_prop_mult 1 --ing2ing 1 --report_test --repetitions 4 --threads 1
# Aggregated average performance on Validation set:
# val, steps:0| h@1:0.0401, h@3:0.0722, h@10:0.0904, h@100:0.0968, MRR:0.0583, av_results:1.5, #found:0.0916
# val, steps:10| h@1:0.0444, h@3:0.0784, h@10:0.0980, h@100:0.1062, MRR:0.0640, av_results:1.6, #found:0.1008
# val, steps:20| h@1:0.0480, h@3:0.0837, h@10:0.1032, h@100:0.1113, MRR:0.0688, av_results:1.7, #found:0.1059
# val, steps:30| h@1:0.0493, h@3:0.0864, h@10:0.1073, h@100:0.1154, MRR:0.0709, av_results:1.8, #found:0.1105
# val, steps:40| h@1:0.0503, h@3:0.0886, h@10:0.1108, h@100:0.1195, MRR:0.0725, av_results:1.9, #found:0.1141
# val, steps:50| h@1:0.0520, h@3:0.0933, h@10:0.1154, h@100:0.1245, MRR:0.0755, av_results:1.9, #found:0.1199
# val, steps:60| h@1:0.0527, h@3:0.0960, h@10:0.1181, h@100:0.1274, MRR:0.0771, av_results:2.0, #found:0.1224
# val, steps:70| h@1:0.0541, h@3:0.0976, h@10:0.1200, h@100:0.1303, MRR:0.0786, av_results:2.1, #found:0.1252
# val, steps:80| h@1:0.0540, h@3:0.1008, h@10:0.1254, h@100:0.1354, MRR:0.0802, av_results:2.2, #found:0.1309
# val, steps:90| h@1:0.0567, h@3:0.1020, h@10:0.1282, h@100:0.1385, MRR:0.0823, av_results:2.3, #found:0.1329
# val, steps:100| h@1:0.0581, h@3:0.1047, h@10:0.1320, h@100:0.1410, MRR:0.0843, av_results:2.4, #found:0.1362
# Aggregated average performance on Test set:
# test, steps:0| h@1:0.0391, h@3:0.0701, h@10:0.0889, h@100:0.0944, MRR:0.0568, av_results:1.5, #found:0.0899
# test, steps:10| h@1:0.0424, h@3:0.0760, h@10:0.0962, h@100:0.1047, MRR:0.0619, av_results:1.6, #found:0.0991
# test, steps:20| h@1:0.0460, h@3:0.0809, h@10:0.1014, h@100:0.1094, MRR:0.0664, av_results:1.7, #found:0.1041
# test, steps:30| h@1:0.0469, h@3:0.0828, h@10:0.1045, h@100:0.1128, MRR:0.0680, av_results:1.8, #found:0.1082
# test, steps:40| h@1:0.0477, h@3:0.0852, h@10:0.1086, h@100:0.1175, MRR:0.0697, av_results:1.9, #found:0.1118
# test, steps:50| h@1:0.0489, h@3:0.0896, h@10:0.1129, h@100:0.1232, MRR:0.0722, av_results:1.9, #found:0.1175
# test, steps:60| h@1:0.0505, h@3:0.0925, h@10:0.1157, h@100:0.1250, MRR:0.0744, av_results:2.0, #found:0.1203
# test, steps:70| h@1:0.0520, h@3:0.0939, h@10:0.1176, h@100:0.1282, MRR:0.0759, av_results:2.2, #found:0.1234
# test, steps:80| h@1:0.0521, h@3:0.0974, h@10:0.1236, h@100:0.1345, MRR:0.0778, av_results:2.3, #found:0.1294
# test, steps:90| h@1:0.0545, h@3:0.0989, h@10:0.1267, h@100:0.1363, MRR:0.0799, av_results:2.3, #found:0.1316
# test, steps:100| h@1:0.0564, h@3:0.1020, h@10:0.1305, h@100:0.1397, MRR:0.0822, av_results:2.4, #found:0.1345






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