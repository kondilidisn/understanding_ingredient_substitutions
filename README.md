# Exploring_FoodKG_1MRecipes (WIP)

This repository contains the code surrounding Understadning Ingredient Substitution Experiments, in the context of an agent interacting with a human chef in order to learn how to perform ingredient substitution.

The code supports the exploration and use of the Recipe1M dataset and Recipe1Msubs benchmark.
Additionally, it utilizes a GraphDB interface to query the FoodKG knowledge graph.
They are all put together to create a grounded version of the Recipe1MSubs, where the data (recipes and ingredients) are defined in Internationalized Resource Identifiers (IRI)s.
Moreover, the Ignredients are related with FoodOn concepts, enabling the agent to develop and human-centric understanding of provided ingredient substitution examples.
The experimental setup uses this produced grounded version of Recipe1MSubs, to test and evaluate different agent policies.


