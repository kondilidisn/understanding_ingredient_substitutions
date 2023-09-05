from collections import defaultdict
import pickle
import matplotlib.pyplot as plt
import os
import numpy as np

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

#
# single repetition, eval every 1
# legend_2_exp_dir = {
#     "LT+Freq - PL": "ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_100",
#     "LT+Freq - AL": "ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100__final",
#
#     "HC - PL": "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_100__final",
#     "HC - AL": "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100"}

# with repetitions, eval every 10
legend_2_exp_dir = {
    "LT+Freq - PL": "ing2ing=1__No_Ingredient_Perception_Used__introspection_random__max_steps_100",
    "LT+Freq - AL": "ing2ing=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100",

    "HC - PL": "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_random__max_steps_100",
    "HC - AL": "ing2ing=100__ingP2ingP=10__recP2ingP=1__ing_perception=foodOn_foodOn_one_hop__introspection_epsilon_greedy_0.1_ing_10.0_ing_prop_1.0__max_steps_100"}
#





# max_steps = 100
max_steps = 100
# steps = [i for i in list(range(max_steps))]
# steps.append(max_steps)

steps_to_plot = set()


exp_results = dict()
for exp_legend in legend_2_exp_dir:
    exp_results[exp_legend] = defaultdict(list)
    with open(os.path.join( exp_dir + "/" + legend_2_exp_dir[exp_legend], "test_performance.pkl"), 'rb') as handle:
        exp_performance = pickle.load(handle)
    steps_to_plot.update(exp_performance.keys())
    for step in exp_performance:

        if step > max_steps:
            break
        for metric in exp_performance[0]:
            exp_results[exp_legend][metric].append(exp_performance[step][metric])
steps_to_plot = list(steps_to_plot)
steps_to_plot.sort()
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
fig, axs = plt.subplots(2, 3, figsize=(10, 5), dpi=100) #, sharey="row")
legends = ["LT+Freq - PL", "LT+Freq - AL", "HC - PL", "HC - AL"]

metrics = [["Hit@1", "Hit@3", "Hit@10"], ["MRR", "Results", "Tar_Found"]]
plot_marks = ['-', ':', '-.', '--']
plot_titles = [['Hit@1 (%)', 'Hit@3 (%)', 'Hit@10 (%)'], ['MRR (%)', "# Justified Recommendations", "Target Justified (%)"]]

value_multipliers = [[100, 100, 100], [100, 1, 100]]

axs[0,1].sharey(axs[0,0])
axs[0,2].sharey(axs[0,0])


fig.tight_layout()

# fig.figsize((100,50))

for i in range(2):
    for j in range(3):
        metric = metrics[i][j]
        plot_title = plot_titles[i][j]
        axs[i, j].set_title(plot_title, fontsize=14)
        value_multiplier = value_multipliers[i][j]
        for z in range(len(legends)):
            legend = legends[z]
            plot_mark = plot_marks[z]
            axs[i,j].plot(steps_to_plot, np.asarray(exp_results[legend][metric]) * value_multiplier, plot_mark)
        # axs[i, j].legend(legends, loc=0)
    axs[i, 0].set_ylim(bottom=0)

# plt.subplot(222, sharey=axs[0,0])

axs[0, 0].legend(legends, loc='best')
axs[1, 0].set_xlabel('# Examples', fontsize=12)
axs[1, 1].set_xlabel('# Examples', fontsize=12)
axs[1, 2].set_xlabel('# Examples', fontsize=12)

# axs[0, 0].get_xaxis().set_visible(False)
# axs[0, 1].get_xaxis().set_visible(False)
# axs[0, 2].get_xaxis().set_visible(False)

# fig.set_ylim([0,100])
# plt.figure(figsize=(WIDTH_SIZE,HEIGHT_SIZE))
# plt.figure(figsize=(200,100))
plt.show()

#
#
# metric = "Hit@1"
# axs[0, 0].plot(steps_to_plot, np.asarray(exp_results[legends[0]][metric])*100, '-')
# axs[0, 0].plot(steps_to_plot, np.asarray(exp_results[legends[1]][metric])*100, ':')
# axs[0, 0].plot(steps_to_plot, np.asarray(exp_results[legends[2]][metric])*100, '-.')
# axs[0, 0].plot(steps_to_plot, np.asarray(exp_results[legends[3]][metric])*100, '--')
# # axs[0, 0].plot(steps, simple_exp_results["Prop-Freq"]["1.precision"], '--')
# axs[0, 0].set_title('Hit@1 (%)', fontsize=12)
#
# metric = "Hit@3"
# axs[0, 1].plot(steps_to_plot, np.asarray(exp_results[legends[0]][metric])*100, '-')
# axs[0, 1].plot(steps_to_plot, np.asarray(exp_results[legends[1]][metric])*100, ':')
# axs[0, 1].plot(steps_to_plot, np.asarray(exp_results[legends[2]][metric])*100, '-.')
# axs[0, 1].plot(steps_to_plot, np.asarray(exp_results[legends[3]][metric])*100, '--')
# axs[0, 1].set_title('Hit@3 (%)', fontsize=12)
#
# metric = "Hit@10"
# axs[0, 2].plot(steps_to_plot, np.asarray(exp_results[legends[0]][metric])*100, '-')
# axs[0, 2].plot(steps_to_plot, np.asarray(exp_results[legends[1]][metric])*100, ':')
# axs[0, 2].plot(steps_to_plot, np.asarray(exp_results[legends[2]][metric])*100, '-.')
# axs[0, 2].plot(steps_to_plot, np.asarray(exp_results[legends[3]][metric])*100, '--')
# axs[0, 2].set_title('Hit@10 (%)', fontsize=12)
#
# #
# # metric = "Hit@100"
# # axs[1, 0].plot(steps_to_plot, exp_results[legends[0]][metric], '-')
# # axs[1, 0].plot(steps_to_plot, exp_results[legends[1]][metric], ':')
# # axs[1, 0].plot(steps_to_plot, exp_results[legends[2]][metric], '-.')
# # axs[1, 0].plot(steps_to_plot, exp_results[legends[3]][metric], '--')
# # # axs[0, 1].plot(steps, exp_results[legends[2]][metric], '-.')
# # # axs[0, 0].plot(steps, simple_exp_results["Prop-Freq"]["1.precision"], '--')
# # axs[1, 0].set_title('Hit@100', fontsize=12)
#
# metric = "MRR"
# axs[1, 1].plot(steps_to_plot, np.asarray(exp_results[legends[0]][metric])*100, '-')
# axs[1, 1].plot(steps_to_plot, np.asarray(exp_results[legends[1]][metric])*100, ':')
# axs[1, 1].plot(steps_to_plot, np.asarray(exp_results[legends[2]][metric])*100, '-.')
# axs[1, 1].plot(steps_to_plot, np.asarray(exp_results[legends[3]][metric])*100, '--')
# # axs[1, 1].plot(steps, exp_results[legends[2]][metric], '-.')
# axs[1, 1].set_title('MRR  (%)', fontsize=12)
# #
# metric = "Tar_Found"
# axs[1, 2].plot(steps_to_plot, np.asarray(exp_results[legends[0]][metric])*100, '-')
# axs[1, 2].plot(steps_to_plot, np.asarray(exp_results[legends[1]][metric])*100, ':')
# axs[1, 2].plot(steps_to_plot, np.asarray(exp_results[legends[2]][metric])*100, '-.')
# axs[1, 2].plot(steps_to_plot, np.asarray(exp_results[legends[3]][metric])*100, '--')
# # axs[2, 1].plot(steps, exp_results[legends[2]][metric], '-.')
# axs[1, 2].set_title('Target was Suggested (%)', fontsize=12)
# #
# # axs[0, 1].plot(steps, extended_exp_results["Rand-Freq"]["1.precision"], '-')
# # axs[0, 1].plot(steps, extended_exp_results["Rand-Logic"]["1.precision"], ':')
# # axs[0, 1].plot(steps, extended_exp_results["Prop-Freq"]["1.precision"], '--')
# # axs[0, 1].plot(steps, extended_exp_results["Prop-Logic"]["1.precision"], '-.')
# #
# # axs[0, 1].set_title('Extended Dataset', fontsize=12)
# # axs[1, 0].plot(steps, simple_exp_results["Rand-Freq"]["2.recall"], '-')
# # axs[1, 0].plot(steps, simple_exp_results["Rand-Logic"]["2.recall"], ':')
# # axs[1, 0].plot(steps, simple_exp_results["Prop-Freq"]["2.recall"], '--')
# # axs[1, 0].plot(steps, simple_exp_results["Prop-Logic"]["2.recall"], '-.')
# # # axs[1, 0].set_title('Simple Dataset Recall')
# # axs[1, 1].plot(steps, extended_exp_results["Rand-Freq"]["2.recall"], '-')
# # axs[1, 1].plot(steps, extended_exp_results["Rand-Logic"]["2.recall"], ':')
# # axs[1, 1].plot(steps, extended_exp_results["Prop-Freq"]["2.recall"], '--')
# # axs[1, 1].plot(steps, extended_exp_results["Prop-Logic"]["2.recall"], '-.')
#
# axs[0, 0].legend(legends, loc=0)
#
# # axs[0, 1].get_xaxis().set_visible(False)
# # axs[0, 0].get_xaxis().set_visible(False)
#
# # fig.tight_layout()
#
# axs[0, 0].set_ylabel('Hit @ (%)', fontsize=12)  # Y label
#
# axs[1, 0].set_ylabel('# of Cases', fontsize=12)  # Y label
#
# #
# # axs[0, 0].set_ylabel('Hit @ (%)', fontsize=12)  # Y label
# #
# # axs[0, 0].set_ylabel('Hit @ (%)', fontsize=12)  # Y label
#
# # axs[1, 0].set_ylabel('Recall', fontsize=12)
#
# axs[1, 0].set_xlabel('# Examples', fontsize=12)
#
# axs[1, 1].set_xlabel('# Examples', fontsize=12)  # X label
#
# axs[1, 2].set_xlabel('# Examples', fontsize=12)  # X label
# # plt.figure(figsize=(WIDTH_SIZE,HEIGHT_SIZE))
# plt.figure(figsize=(200,100))
# plt.show()
# # fig.savefig('samplefigure', bbox_extra_artists=(lgd,), bbox_inches='tight')