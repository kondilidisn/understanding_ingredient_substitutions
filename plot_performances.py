from collections import defaultdict
import pickle
import matplotlib.pyplot as plt
import os

# extended_dataset_legend_2_exp_dir = {
#     "Rand-Freq": "experiments/all_ontology_pairs__TP=random__SP=frequency-based__reps=10__instances=extended__max_steps=100",
#     "Rand-Logic": "experiments/all_ontology_pairs__TP=random__SP=logic-based__reps=10__instances=extended__max_steps=100",
#     "Prop-Freq": "experiments/all_ontology_pairs__TP=property-based__SP=frequency-based__reps=10__instances=extended__max_steps=100",
#     "Prop-Logic": "experiments/all_ontology_pairs__TP=property-based__SP=logic-based__reps=10__instances=extended__max_steps=100"}
#
# simple_dataset_legend_2_exp_dir = {
#     "Rand-Freq": "experiments/all_ontology_pairs__TP=random__SP=frequency-based__reps=10__instances=simple__max_steps=100",
#     "Rand-Logic": "experiments/all_ontology_pairs__TP=random__SP=logic-based__reps=10__instances=simple__max_steps=100",
#     "Prop-Freq": "experiments/all_ontology_pairs__TP=property-based__SP=frequency-based__reps=10__instances=simple__max_steps=100",
#     "Prop-Logic": "experiments/all_ontology_pairs__TP=property-based__SP=logic-based__reps=10__instances=simple__max_steps=100"}

exp_dir = "/Users/kondy/PycharmProjects/Understanding_Recipes/experiments"

# ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100__final
# ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_100
# ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100
# remaining: ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_100__final


# upper bounds?
# random active learning policies, adn the two policies for learning.
# baseline: /Users/kondy/PycharmProjects/Understanding_Recipes/experiments/ing2ing=1__No_Ingredient_Perception_Used__introspection_random__complete_epoch
# ours: (pending) ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__complete_epoch__final


legend_2_exp_dir = {
    "LT+Freq - PL": "ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_100",
    "LT+Freq - AL": "ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100__final",

    "HC - PL": "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_100__final",
    "HC - AL": "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100"}



max_steps = 100
steps = [i for i in list(range(max_steps))]
steps.append(max_steps)




exp_results = dict()
for exp_legend in legend_2_exp_dir:
    exp_results[exp_legend] = defaultdict(list)
    with open(os.path.join( exp_dir + "/" + legend_2_exp_dir[exp_legend], "test_performance.pkl"), 'rb') as handle:
        exp_performance = pickle.load(handle)
    for step in exp_performance:
        if step > max_steps:
            break
        for metric in exp_performance[0]:
            exp_results[exp_legend][metric].append(exp_performance[step][metric])

# extended_exp_results = dict()
# for exp_legend in extended_dataset_legend_2_exp_dir:
#     extended_exp_results[exp_legend] = defaultdict(list)
#     with open(os.path.join(extended_dataset_legend_2_exp_dir[exp_legend], "av_stats_per_step_dict.pickle"),
#               'rb') as handle:
#         exp_performance = pickle.load(handle)
#     for metric in exp_performance:
#         for step in steps:
#             extended_exp_results[exp_legend][metric].append(exp_performance[metric][step])
#
#         print()

#  Metrics:
# ["Hit@1"]
# ["Hit@3"]
# ["Hit@10"]
# ["Hit@100"]
# ["Target_Rank"]
# ["Results"]
# ["|Not_Found|"]

# legends = ["ing2ing", "ing2ing+props", "ing2ing+10%props"]
legends = ["LT+Freq - PL", "LT+Freq - AL", "HC - PL", "HC - AL"]

fig, axs = plt.subplots(2, 3, sharey="row")
metric = "Hit@1"
axs[0, 0].plot(steps, exp_results[legends[0]][metric], '-')
axs[0, 0].plot(steps, exp_results[legends[1]][metric], ':')
axs[0, 0].plot(steps, exp_results[legends[2]][metric], '-.')
axs[0, 0].plot(steps, exp_results[legends[3]][metric], '--')
# axs[0, 0].plot(steps, simple_exp_results["Prop-Freq"]["1.precision"], '--')
axs[0, 0].set_title('Hit@1', fontsize=12)

metric = "Hit@3"
axs[0, 1].plot(steps, exp_results[legends[0]][metric], '-')
axs[0, 1].plot(steps, exp_results[legends[1]][metric], ':')
axs[0, 1].plot(steps, exp_results[legends[2]][metric], '-.')
axs[0, 1].plot(steps, exp_results[legends[3]][metric], '--')
axs[0, 1].set_title('Hit@3', fontsize=12)

metric = "Hit@10"
axs[0, 2].plot(steps, exp_results[legends[0]][metric], '-')
axs[0, 2].plot(steps, exp_results[legends[1]][metric], ':')
axs[0, 2].plot(steps, exp_results[legends[2]][metric], '-.')
axs[0, 2].plot(steps, exp_results[legends[3]][metric], '--')
axs[0, 2].set_title('Hit@10', fontsize=12)


metric = "MRR"
axs[1, 0].plot(steps, exp_results[legends[0]][metric], '-')
axs[1, 0].plot(steps, exp_results[legends[1]][metric], ':')
# axs[0, 1].plot(steps, exp_results[legends[2]][metric], '-.')
# axs[0, 0].plot(steps, simple_exp_results["Prop-Freq"]["1.precision"], '--')
axs[1, 0].set_title('Target Sub. Rank', fontsize=12)

metric = "Results"
axs[1, 1].plot(steps, exp_results[legends[0]][metric], '-')
axs[1, 1].plot(steps, exp_results[legends[1]][metric], ':')
# axs[1, 1].plot(steps, exp_results[legends[2]][metric], '-.')
axs[1, 1].set_title('# Results', fontsize=12)

metric = "Tar_Found"
axs[1, 2].plot(steps, exp_results[legends[0]][metric], '-')
axs[1, 2].plot(steps, exp_results[legends[1]][metric], ':')
# axs[2, 1].plot(steps, exp_results[legends[2]][metric], '-.')
axs[1, 2].set_title('Target Not Suggested', fontsize=12)
#
# axs[0, 1].plot(steps, extended_exp_results["Rand-Freq"]["1.precision"], '-')
# axs[0, 1].plot(steps, extended_exp_results["Rand-Logic"]["1.precision"], ':')
# axs[0, 1].plot(steps, extended_exp_results["Prop-Freq"]["1.precision"], '--')
# axs[0, 1].plot(steps, extended_exp_results["Prop-Logic"]["1.precision"], '-.')
#
# axs[0, 1].set_title('Extended Dataset', fontsize=12)
# axs[1, 0].plot(steps, simple_exp_results["Rand-Freq"]["2.recall"], '-')
# axs[1, 0].plot(steps, simple_exp_results["Rand-Logic"]["2.recall"], ':')
# axs[1, 0].plot(steps, simple_exp_results["Prop-Freq"]["2.recall"], '--')
# axs[1, 0].plot(steps, simple_exp_results["Prop-Logic"]["2.recall"], '-.')
# # axs[1, 0].set_title('Simple Dataset Recall')
# axs[1, 1].plot(steps, extended_exp_results["Rand-Freq"]["2.recall"], '-')
# axs[1, 1].plot(steps, extended_exp_results["Rand-Logic"]["2.recall"], ':')
# axs[1, 1].plot(steps, extended_exp_results["Prop-Freq"]["2.recall"], '--')
# axs[1, 1].plot(steps, extended_exp_results["Prop-Logic"]["2.recall"], '-.')

axs[0, 0].legend(legends, loc=0)

# axs[0, 1].get_xaxis().set_visible(False)
# axs[0, 0].get_xaxis().set_visible(False)

# fig.tight_layout()

axs[0, 0].set_ylabel('Hit @ (%)', fontsize=12)  # Y label

axs[1, 0].set_ylabel('# of Cases', fontsize=12)  # Y label
#
# axs[0, 0].set_ylabel('Hit @ (%)', fontsize=12)  # Y label
#
# axs[0, 0].set_ylabel('Hit @ (%)', fontsize=12)  # Y label

# axs[1, 0].set_ylabel('Recall', fontsize=12)
axs[1, 0].set_xlabel('# Examples', fontsize=12)

axs[1, 1].set_xlabel('# Examples', fontsize=12)  # X label

axs[1, 2].set_xlabel('# Examples', fontsize=12)  # X label
# plt.figure(figsize=(WIDTH_SIZE,HEIGHT_SIZE))
plt.figure(figsize=(200,100))
plt.show()
# fig.savefig('samplefigure', bbox_extra_artists=(lgd,), bbox_inches='tight')