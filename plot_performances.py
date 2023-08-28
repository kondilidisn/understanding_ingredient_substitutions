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

legend_2_exp_dir = {
    "ing2ing": "ing2ing=1____debug",
    # "ing2ing+props": "ing2ing=1__ingP2ingP=1__ing_perception=foodOn_foodOn_one_hop__debug",
    "ing2ing+10%props": "ing2ing=1__ingP2ingP=1__ing_perception=foodOn_foodOn_one_hop_least_10_freq_props__debug"}

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
legends = ["ing2ing", "ing2ing+10%props"]

fig, axs = plt.subplots(2, 3, sharey="row")
metric = "Hit@1"
axs[0, 0].plot(steps, exp_results[legends[0]][metric], '-')
axs[0, 0].plot(steps, exp_results[legends[1]][metric], ':')
# axs[0, 0].plot(steps, exp_results[legends[2]][metric], '-.')
# axs[0, 0].plot(steps, simple_exp_results["Prop-Freq"]["1.precision"], '--')
axs[0, 0].set_title('Hit@1', fontsize=12)

metric = "Hit@3"
axs[0, 1].plot(steps, exp_results[legends[0]][metric], '-')
axs[0, 1].plot(steps, exp_results[legends[1]][metric], ':')
# axs[1, 0].plot(steps, exp_results[legends[2]][metric], '-.')
axs[0, 1].set_title('Hit@3', fontsize=12)

metric = "Hit@10"
axs[0, 2].plot(steps, exp_results[legends[0]][metric], '-')
axs[0, 2].plot(steps, exp_results[legends[1]][metric], ':')
# axs[2, 0].plot(steps, exp_results[legends[2]][metric], '-.')
axs[0, 2].set_title('Hit@10', fontsize=12)


metric = "Target_Rank"
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

metric = "|Not_Found|"
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