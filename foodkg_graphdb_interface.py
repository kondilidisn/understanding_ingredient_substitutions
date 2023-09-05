from collections import defaultdict
from typing import Iterable, Optional, Tuple, Union, cast, Any, List, Type, Dict, DefaultDict
from xml.dom.minidom import Document

from SPARQLWrapper import SPARQLWrapper, JSON

from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointInternalError
import os, time, pickle
from rdflib import Graph, URIRef, Namespace, RDF, OWL

foodkg_local_repository = "http://nick-the-greek.home:7200/repositories/FoodKG"


def clean_ingredient_name(ingredient_name):
    return ingredient_name.replace('"', "")


def generate_synonyms_of_ingredient(ingredient_name, replace_underscore_with=" ") -> set[str]:
    our_synonyms: set[str] = set()
    our_synonyms.add(ingredient_name.replace('_', replace_underscore_with))
    temp_ingredient_name = ingredient_name.replace('_', replace_underscore_with + "-" + replace_underscore_with)
    our_synonyms.add(temp_ingredient_name)
    split_words = ingredient_name.split('_')

    split_words_first_letter_capital = [str.capitalize(word[0]) + word[1:] for word in split_words]
    our_synonyms.add(replace_underscore_with.join(split_words_first_letter_capital))

    for i in range(len(split_words)):
        one_word_capital = split_words.copy()
        one_word_capital[i] = str.capitalize(one_word_capital[i])
        our_synonyms.add(replace_underscore_with.join(one_word_capital))

    return our_synonyms


def get_all_recipe_ids_and_urls(foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> dict[
    str, Tuple[str, str]]:
    """
    :param: foodkg_local_repository:str the repository url
    :return: dict[recipe_url:url --> tuple(recipe URI:str, recipe_name:str)
    """

    #
    # get_recipe_example_sparql_query = """ \
    # select * where {
    #     Graph ?graphName {  <http://idea.rpi.edu/heals/kb/recipe/fc9f994e-Pepperoni%20Potato%20Bake> ?predicate ?object.}
    # } limit 100"""

    get_all_recipes_sparql_query = """
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select ?recipe_id ?graph where {
    Graph ?graph {?recipe_id a recipe-kb:recipe}
    }"""

    get_all_recipe_URI_name_and_URL_sparql_query = """
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select ?recipe_uri ?recipe_name ?recipe_url where {
    Graph ?graph {?recipe_uri a recipe-kb:recipe.
        ?recipe_id rdfs:label ?recipe_name}.
        ?graph prov:wasDerivedFrom ?recipe_url.
        
} Limit 100 """

    recipe_url_to_foodkg_uri_and_name_dict: dict[str, tuple[str, str]] = dict()

    sparql = SPARQLWrapper(foodkg_repository)
    sparql.setQuery(get_all_recipe_URI_name_and_URL_sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        recipe_URL = result["recipe_url"]["value"]
        recipe_URI = result["recipe_uri"]["value"]
        recipe_name = result["recipe_name"]["value"]
        recipe_url_to_foodkg_uri_and_name_dict[recipe_URL] = (recipe_URI, recipe_name)
        print(recipe_URI, recipe_name, recipe_URL)
        # break

    # print('---------------------------')
    #
    # for result in results["results"]["bindings"]:
    #     print('%s: %s' % (result["label"]["xml:lang"], result["label"]["value"]))


#
# get_all_recipe_ids_and_urls()
#
def get_recipe_URL_given_recipe_IRI(recipe_IRI: str,
                                    foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> str:
    recipe_IRI_and_name_given_URL_sparql_query = """
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select distinct ?recipe_url where {
        Graph ?graph {""" + "<" + recipe_IRI + ">" + """ a a recipe-kb:recipe}.
            ?graph prov:wasDerivedFrom ?recipe_url.}"""

    sparql = SPARQLWrapper(foodkg_repository)
    sparql.setQuery(recipe_IRI_and_name_given_URL_sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    assert len(results["results"]["bindings"]) == 1

    for result in results["results"]["bindings"]:
        recipe_URL = result["recipe_url"]["value"]
        # recipe_name = result["recipe_name"]["value"]
        # print(recipe_URL, recipe_name)
        return recipe_URL,


def get_recipe_IRIs_given_recipe_URL(recipe_URL: str,
                                     foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> \
list[str]:
    recipe_URL_and_name_given_IRI_sparql_query = """
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select distinct ?recipe_iri where {
        Graph ?graph {?recipe_iri a recipe-kb:recipe}.
            ?graph prov:wasDerivedFrom """ + "<" + recipe_URL + ">.}"

    sparql = SPARQLWrapper(foodkg_repository)
    sparql.setQuery(recipe_URL_and_name_given_IRI_sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # if len(results["results"]["bindings"]) != 1:
    #     print(f"multiple ({len(results['results']['bindings'])}) recipe IRIs for the same URL:{recipe_URL}")
    # assert len(results["results"]["bindings"]) == 1

    recipe_iris: list[str] = []
    for result in results["results"]["bindings"]:
        recipe_IRI = result["recipe_iri"]["value"]
        # recipe_name = result["recipe_name"]["value"]
        recipe_iris.append(recipe_IRI)
        # print("EDW:", recipe_IRI, recipe_name)
    return recipe_iris


# def get_all_ingredient_info_of_recipe_url(recipe_url:str, foodkg_repository:str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> list[dict[str,str]]:
#     pass

def check_if_ingredient_name_exists_as_rdfs_label(ingredient_name,
                                                  foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> bool:
    ingredient_name_exists_in_foodKG_as_IRI_sparql_query = """
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    ASK  { ?ingredient rdfs:label \"""" + ingredient_name + "\"}"

    sparql = SPARQLWrapper(foodkg_repository)
    sparql.setQuery(ingredient_name_exists_in_foodKG_as_IRI_sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    exists = results["boolean"]
    return exists


def check_if_ingredient_name_exists_in_foodKG_as_IRI(ingredient_iri,
                                                     foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> bool:
    ingredient_name_exists_in_foodKG_as_IRI_sparql_query = """
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    ask {<http://idea.rpi.edu/heals/kb/ingredientname/""" + ingredient_iri + "> rdf:type recipe-kb:ingredientname. }"

    sparql = SPARQLWrapper(foodkg_repository)
    sparql.setQuery(ingredient_name_exists_in_foodKG_as_IRI_sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    exists = results["boolean"]
    return exists


def get_IRI_of_ingredient_with_rdfs_label(ingredient_name,
                                          foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> \
Optional[list[str]]:
    match_ingredient_by_name_sparql_query = """
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT Distinct ?ingredient_iri Where { 
    ?ingredient_iri rdfs:label  \"""" + ingredient_name + """\".
    ?ingredient_iri rdf:type recipe-kb:ingredientname }
    """

    sparql = SPARQLWrapper(foodkg_repository)
    sparql.setQuery(match_ingredient_by_name_sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    related_IRI: Optional[str] = None
    if len(results["results"]["bindings"]) == 1:
        for result in results["results"]["bindings"]:
            related_IRI = result["ingredient_iri"]["value"]
    elif len(results["results"]["bindings"]) > 1:
        raise ValueError("Multiple ingredient matched by rdfs label (name) with value:" + ingredient_name + "\n" +
                         results["results"]["bindings"])

    return related_IRI


def depricated_match_ingredient_from_1Msubs_to_foodKG_by_IRI_or_name(ingredient_name,
                                                                     run_out_of_memory_just_now: bool = False) -> \
Optional[str]:
    cleaned_ingredient_name = clean_ingredient_name(ingredient_name)
    possible_IRIs = generate_synonyms_of_ingredient(cleaned_ingredient_name, replace_underscore_with="%20")

    try:
        matched_IRI: Optional[str] = None
        exists_as_IRI: bool = False
        for possible_iri in possible_IRIs:
            exists_as_IRI = check_if_ingredient_name_exists_in_foodKG_as_IRI(possible_iri)
            if exists_as_IRI:
                matched_IRI = "http://idea.rpi.edu/heals/kb/ingredientname/" + possible_iri
                break
        if not exists_as_IRI:
            possible_names = generate_synonyms_of_ingredient(cleaned_ingredient_name, replace_underscore_with=" ")
            for possible_name in possible_names:
                matched_by_name = check_if_ingredient_name_exists_as_rdfs_label(possible_name)
                matched_IRI = get_IRI_of_ingredient_with_rdfs_label(possible_name)
                if matched_IRI is not None:
                    break
    except Exception as exception:
        if isinstance(exception, QueryBadFormed):
            print("Query Bad Formed Error!")
            raise Exception(exception)
        elif isinstance(exception, EndPointInternalError):
            # depending on whether this query cause a memory error before or not,
            # we either raise the error or run the query again respectively
            if run_out_of_memory_just_now:
                print("GraphDB run out of memory for the same query twice in a row!")
                raise Exception(exception)

            print("GraphDB Desktop run out of memory. Restarting now...")
            # frist kill running GraphDB
            os.system("pkill GraphDB\ Desktop")
            # wait for 10" to make sure GraphDB terminated
            time.sleep(25)
            # then re-open it
            os.system("/Applications/GraphDB\ Desktop.app/Contents/MacOS/GraphDB\ Desktop&")
            # and wait for 30" to make sure GraphDB is running and ready for queries
            time.sleep(25)
            return depricated_match_ingredient_from_1Msubs_to_foodKG_by_IRI_or_name(ingredient_name,
                                                                                    run_out_of_memory_just_now=True)
        else:
            print("Other type of error occurred while running SPARQL Query!")
            raise Exception(exception)
            # print(type(inst))  # the exception type
            # print(inst.args)  # arguments stored in .args
            # print(inst)  # __str__ allows args to be printed directly,

    return matched_IRI


# check_if_ingredient_name_exists_as_rdfs_label
# check_if_ingredient_name_exists_in_foodKG_as_IRI


# def get_FoodKG_ingredient_IRIs_of_given_recipe_url(recipe_url: str, foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> list[str]:
#
#     get_ingredients_of_recipe_url_sparql_query = """
#     PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
#     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#     PREFIX prov: <http://www.w3.org/ns/prov#>
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#     select distinct ?ingredientIRI where {
#
#     Graph ?graph {?recipe_uri a recipe-kb:recipe.
#         ?recipe_id rdfs:label ?recipe_name}.
#         ?graph prov:wasDerivedFrom <""" + recipe_url + """>.
#         ?recipe_uri recipe-kb:uses ?ingredientLocalIRI.
#         ?ingredientLocalIRI recipe-kb:ing_name ?ingredientIRI.
#         ?ingredientIRI a recipe-kb:ingredientname.}"""
#
#     sparql = SPARQLWrapper(foodkg_repository)
#     sparql.setQuery(get_ingredients_of_recipe_url_sparql_query)
#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()
#       ...


def create_ingredient_IDs_and_dictionaries_from_IRI_and_name(
        pickle_filename_theme: str = "Dataset/1Mrecipes_ingredient",
        foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> None:
    get_all_ingredients_and_their_names_sparql_query = """
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    select ?ingredientIRI ?ingredientName where { 
	?ingredientIRI rdf:type recipe-kb:ingredientname.
    ?ingredientIRI rdfs:label ?ingredientName.
}"""
    # ?ing_iri owl:equivalentClass ?equivalentClass

    ingredient_name_prefix = "http://idea.rpi.edu/heals/kb/ingredientname/"

    sparql = SPARQLWrapper(foodkg_repository)
    sparql.setQuery(get_all_ingredients_and_their_names_sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    short_ingredient_IRIs: list[str] = []

    ingredient_name_to_ID_dict: dict[str,int] = dict()
    short_ingredient_IRI_to_ID_dict: dict[str,int] = dict()

    for result in results["results"]["bindings"]:
        ingredient_IRI = result["ingredientIRI"]["value"]
        ingredient_name = result["ingredientName"]["value"]
        ingredient_ID = len(short_ingredient_IRIs)
        short_ingredient_iri = ingredient_IRI[len(ingredient_name_prefix):]
        short_ingredient_IRIs.append(short_ingredient_iri)
        short_ingredient_IRI_to_ID_dict[short_ingredient_iri] = ingredient_ID
        ingredient_name_to_ID_dict[ingredient_name] = ingredient_ID

    ingredient_short_IRIs_pickle_filename: str = pickle_filename_theme + "_short_IRIs_list.pickle"
    with open(ingredient_short_IRIs_pickle_filename, 'wb') as handle:
        pickle.dump(short_ingredient_IRIs, handle, protocol=pickle.HIGHEST_PROTOCOL)

    ingredient_name_to_ingredient_ID_pickle_filename: str = pickle_filename_theme + "_name_to_ingredient_ID_dict.pickle"
    with open(ingredient_name_to_ingredient_ID_pickle_filename, 'wb') as handle:
        pickle.dump(ingredient_name_to_ID_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    ingredient_short_IRI_to_ingredient_ID_pickle_filename: str = pickle_filename_theme + "_short_IRI_to_ingredient_ID_dict.pickle"
    with open(ingredient_short_IRI_to_ingredient_ID_pickle_filename, 'wb') as handle:
        pickle.dump(short_ingredient_IRI_to_ID_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"{len(short_ingredient_IRIs)} Ingredients were indexed in pickles and specifically in the following files:")
    print(ingredient_short_IRIs_pickle_filename)
    print(ingredient_name_to_ingredient_ID_pickle_filename)
    print(ingredient_short_IRI_to_ingredient_ID_pickle_filename)


def load_ingredient_indexes_from_pickles(pickle_filename_theme: str = "Dataset/1Mrecipes_ingredient") -> \
        tuple[list[str], dict[str,int], dict[str,int]]:
    ingredient_short_IRIs_pickle_filename: str = pickle_filename_theme + "_short_IRIs_list.pickle"
    with open(ingredient_short_IRIs_pickle_filename, 'rb') as handle:
        short_ingredient_IRIs = pickle.load(handle)

    ingredient_name_to_ingredient_ID_pickle_filename: str = pickle_filename_theme + "_name_to_ingredient_ID_dict.pickle"
    with open(ingredient_name_to_ingredient_ID_pickle_filename, 'rb') as handle:
        ingredient_name_to_ID_dict = pickle.load(handle)

    ingredient_short_IRI_to_ingredient_ID_pickle_filename: str = pickle_filename_theme + "_short_IRI_to_ingredient_ID_dict.pickle"
    with open(ingredient_short_IRI_to_ingredient_ID_pickle_filename, 'rb') as handle:
        short_ingredient_IRI_to_ID_dict = pickle.load(handle)

    return short_ingredient_IRIs, ingredient_name_to_ID_dict, short_ingredient_IRI_to_ID_dict


class FoodKGGraphDBInterface:
    def __init__(self, foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG",
                 load_ingredient_indexes_from_files: bool = False,
                 ingredient_indexes_filename_theme: str = "Dataset/1Mrecipes_ingredient",
                 substitutions_namespace=Namespace("http://lr.cs.vu.nl/ingredient_substitutions#")):
        self.foodkg_repository = foodkg_repository
        self.substitutions_namespace:Namespace = substitutions_namespace
        self.ingredient_iri_prefix:str = "http://idea.rpi.edu/heals/kb/ingredientname/"
        self.foodkg_namespace:Namespace = Namespace("http://idea.rpi.edu/heals/kb/")
        self.usda_namespace:Namespace = Namespace("http://idea.rpi.edu/heals/kb/usda#")
        self.obo_namespace:Namespace = Namespace("http://purl.obolibrary.org/obo/")
        self.run_out_of_memory_just_now: bool = False
        self.foodKG_sparql_wrapper:SPARQLWrapper = SPARQLWrapper(self.foodkg_repository)
        self.ingredient_indexes_filename_theme:str = ingredient_indexes_filename_theme

        if load_ingredient_indexes_from_files:
            short_ingredient_IRIs, ingredient_name_to_ID_dict, short_ingredient_IRI_to_ID_dict = \
                load_ingredient_indexes_from_pickles(pickle_filename_theme=self.ingredient_indexes_filename_theme)

            self.short_ingredient_IRIs = short_ingredient_IRIs
            self.ingredient_name_to_ID_dict = ingredient_name_to_ID_dict
            self.short_ingredient_IRI_to_ID_dict = short_ingredient_IRI_to_ID_dict
            self.ingredient_indexes_are_loaded = True
            print("ingredient Indexes were successfully loaded from pickle with theme:",
                  self.ingredient_indexes_filename_theme)
        else:
            self.short_ingredient_IRIs = None
            self.ingredient_name_to_ID_dict = None
            self.short_ingredient_IRI_to_ID_dict = None
            self.ingredient_indexes_are_loaded = False

    def get_foodk_ingredient_iri_prefix(self) -> str:
        return self.ingredient_iri_prefix

    def run_sparql_query(self, sparql_query_str: str) -> Union[Graph, None, bytes, str, dict, Document]:

        try:

            self.foodKG_sparql_wrapper.setQuery(sparql_query_str)
            self.foodKG_sparql_wrapper.setReturnFormat(JSON)
            results = self.foodKG_sparql_wrapper.query().convert()
        except Exception as exception:
            if isinstance(exception, QueryBadFormed):
                print("Query Bad Formed Error!")
                raise Exception(exception)
            elif isinstance(exception, EndPointInternalError):
                # depending on whether this query cause a memory error before or not,
                # we either raise the error or run the query again respectively
                if self.run_out_of_memory_just_now:
                    print("GraphDB run out of memory for the same query twice in a row!")
                    raise Exception(exception)

                print("GraphDB Desktop run out of memory. Restarting now...")
                # frist kill running GraphDB
                os.system("pkill GraphDB\ Desktop")
                # wait for 10" to make sure GraphDB terminated
                time.sleep(30)
                # then re-open it
                os.system("/Applications/GraphDB\ Desktop.app/Contents/MacOS/GraphDB\ Desktop&")
                # and wait for 30" to make sure GraphDB is running and ready for queries
                time.sleep(30)
                self.run_out_of_memory_just_now = True
                return self.run_sparql_query(sparql_query_str=sparql_query_str)
            else:
                print("Other type of error occurred while running SPARQL Query!")
                raise Exception(exception)
                # print(type(inst))  # the exception type
                # print(inst.args)  # arguments stored in .args
                # print(inst)  # __str__ allows args to be printed directly,

        self.run_out_of_memory_just_now = False
        return results

    def get_rdfs_label_of_iri(self, iri: URIRef) -> Optional[str]:

        sparql_query_for_rdfs_label = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select ?rdfs_label where { 
    <""" + str(iri) + "> rdfs:label ?rdfs_label.}"
        query_result = self.run_sparql_query(sparql_query_for_rdfs_label)

        iri_name: Optional[str] = None

        for result in query_result["results"]["bindings"]:
            iri_name = result["rdfs_label"]["value"]

        return iri_name

    def get_full_ingredient_iri_given_short_iri(self, short_iri):
        return self.ingredient_iri_prefix + short_iri

    def get_ingredient_id_given_short_iri(self, short_iri: str):
        if self.ingredient_indexes_are_loaded:
            if short_iri in self.short_ingredient_IRI_to_ID_dict:
                return self.short_ingredient_IRI_to_ID_dict[short_iri]
        else:
            raise ValueError("ingredient Indexes are not loaded from file!")

    def get_ingredient_id_given_name(self, ingredient_name: str) -> int:
        if self.ingredient_indexes_are_loaded:
            if ingredient_name in self.ingredient_name_to_ID_dict:
                return self.ingredient_name_to_ID_dict[ingredient_name]
        else:
            raise ValueError("ingredient Indexes are not loaded from file!")

    def get_ingredient_name_given_id(self, ingredient_id: int) -> str:
        raise NotImplementedError()

    def get_ingredient_short_iri_given_id(self, ingredient_id: int):
        if self.ingredient_indexes_are_loaded:
            return self.short_ingredient_IRIs[ingredient_id]
        else:
            raise ValueError("ingredient Indexes are not loaded from file!")

    def get_ingredient_iri_prefix(self):
        return self.ingredient_iri_prefix

    def get_ingredient_short_IRI_from_1Msubs_to_foodKG_by_IRI_or_name(self, ingredient_name: str) -> Optional[str]:

        if self.ingredient_indexes_are_loaded:
            cleaned_ingredient_name = clean_ingredient_name(ingredient_name)
            possible_short_IRIs = generate_synonyms_of_ingredient(cleaned_ingredient_name,
                                                                  replace_underscore_with="%20")
            ingredient_ID: Optional[int] = None
            for possible_iri in possible_short_IRIs:
                if possible_iri in self.short_ingredient_IRI_to_ID_dict:
                    ingredient_ID = self.short_ingredient_IRI_to_ID_dict[possible_iri]
                    break
            if ingredient_ID is None:
                possible_names = generate_synonyms_of_ingredient(cleaned_ingredient_name, replace_underscore_with=" ")
                for possible_name in possible_names:
                    if possible_name in self.ingredient_name_to_ID_dict:
                        ingredient_ID = self.ingredient_name_to_ID_dict[possible_name]
                        break

            if ingredient_ID is None:
                return None
            else:
                ingredient_short_iri: str = self.short_ingredient_IRIs[ingredient_ID]
                return ingredient_short_iri
        else:
            ingredient_iri = depricated_match_ingredient_from_1Msubs_to_foodKG_by_IRI_or_name(ingredient_name)
            if ingredient_iri is not None:
                ingredient_short_iri = ingredient_iri[len(self.ingredient_iri_prefix):]
                return ingredient_short_iri
            else:
                return None

    def get_FoodKG_ingredient_short_IRIs_of_given_recipe_IRI(self, recipe_iri: str) -> list[str]:

        if self.ingredient_indexes_are_loaded == False:
            raise ValueError("The ingredient indexes are not loaded!")

        get_ingredients_of_recipe_IRI_sparql_query = """
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select ?ingredientIRI where {
        <""" + recipe_iri + """> recipe-kb:uses ?ingredientRecipeIRI.
        ?ingredientRecipeIRI recipe-kb:ing_name ?ingredientIRI.
        ?ingredientIRI a recipe-kb:ingredientname.}"""

        # self.foodKG_sparql_wrapper.setQuery(get_ingredients_of_recipe_IRI_sparql_query)
        # self.foodKG_sparql_wrapper.setReturnFormat(JSON)
        # results = self.foodKG_sparql_wrapper.query().convert()

        results = self.run_sparql_query(get_ingredients_of_recipe_IRI_sparql_query)

        ingredient_short_IRIs: List[str] = []
        for result in results["results"]["bindings"]:
            ingredient_IRI = result["ingredientIRI"]["value"]
            ingredient_short_iri = ingredient_IRI[len(self.ingredient_iri_prefix):]
            ingredient_short_IRIs.append(ingredient_short_iri)

        return ingredient_short_IRIs

    # with open('filename.pickle', 'rb') as handle:
    #     b = pickle.load(handle)

    def retrieve_usda_nutritional_info_of_ingredient_and_return_properties(self, ingredient_iri) -> set[str]:
        pass

    # def load_foodKG_USDA_ingredient_alignments(self, filepath:str="Dataset/foodkg_usda_lings.csv"):
    #
    #     with open(filepath, "r") as foodkg_usda_links_csv_file:
    #         # we skip the first line with the headers
    #         foodkg_usda_links_csv_file.readline()
    #
    #         line = foodkg_usda_links_csv_file.readline()
    #         while line is not None:
    #             foodkg_iri, usda_iri = line.split(",")

            #     line = ingredient_classes_csv_file.readline()



    def write_class_memberships_of_ingredients_to_file_with_their_frequencies(self,
        important_property_prefixes_dict: Optional[dict[str, str]] = None,
        out_directory:str="Dataset", load_query_results_from_file="Dataset/Ingredient_property_query_results"):


        if important_property_prefixes_dict is None:
            important_property_prefixes_dict: dict[str:str] = {str(self.obo_namespace): "obo", "_:": "b_node"}
            # we ignore blank node for now
            # important_property_prefixes_dict = {str(self.obo_namespace): "obo"}

        property_frequencies: dict[str:int] = defaultdict(int)
        number_of_properties_per_ingredient: dict[str:int] = defaultdict(int)

        ingredient_properties_named_graphs: dict[str:Graph] = dict()


        for prefix in important_property_prefixes_dict:
            namespace_name = important_property_prefixes_dict[prefix]
            ingredient_properties_named_graphs[namespace_name] = Graph()



        # get_all_ingredients_and_their_class_membership_sparql_query = """
        # prefix : <http://example.org/>
        # prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        # PREFIX owl: <http://www.w3.org/2002/07/owl#>
        # PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        # PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        # select distinct ?ingredientIRI ?equivalentSuperClass  where {
        #     ?ingredientIRI rdf:type recipe-kb:ingredientname .
        #     ?ingredientIRI owl:equivalentClass ?equivalentClass.
        #     ?equivalentClass rdfs:subClassOf* ?equivalentSuperClass.}"""
        #
        # all_ingredients_and_their_classes_query_results = self.run_sparql_query(
        #     get_all_ingredients_and_their_class_membership_sparql_query)

        # read the results of the above query from csv file

        with open(load_query_results_from_file, "r") as ingredient_classes_csv_file:
            # we skip the first line with the headers
            ingredient_classes_csv_file.readline()

            # line_counter:int = 0

            line = ingredient_classes_csv_file.readline()
            while line is not None and line != "":
                ingredient_IRI, ingredient_class = line[:-1].split(",")
                # line_counter += 1
                line = ingredient_classes_csv_file.readline()


                # we skip the owl:Class statements
                if ingredient_class == str(OWL.Thing):
                    continue

                # we identify the namespace of the class, in case it is among the ones that we defined as important
                for namespace_name in important_property_prefixes_dict:
                    ontology_prefix = important_property_prefixes_dict[namespace_name]
                    # we index this property
                    if ingredient_class.startswith(namespace_name):
                        ingredient_properties_named_graphs[ontology_prefix].add((URIRef(ingredient_IRI), RDF.type, URIRef(ingredient_class)))
                        # and we update the frequencies of this property
                        property_frequencies[ingredient_class] += 1
                        # we update the properties counter of this ingredient
                        number_of_properties_per_ingredient[ingredient_IRI] += 1

        property_frequencies_histogram:dict[int:int] = defaultdict(int)
        for property in property_frequencies:
            property_frequencies_histogram[property_frequencies[property]] += 1

        number_of_properties_per_ingredient_histogram:dict[int:int] = defaultdict(int)
        for ingredient in number_of_properties_per_ingredient:
            number_of_properties_per_ingredient_histogram[number_of_properties_per_ingredient[ingredient]] += 1

        print("Total number of ingredients:", len(number_of_properties_per_ingredient))
        # Total number of ingredients: 16779
        print("Total number of properties:", len(property_frequencies))
        # Total number of properties: 5143
        print("Property frequency histogram:")
        print(property_frequencies_histogram)
        # Property frequency histogram:
        # defaultdict(<class 'int'>, {67: 9, 117: 9, 1176: 2, 10504: 2, 1365: 2, 132: 3, 125: 11, 135: 4, 16697: 2, 2293: 1, 148: 5, 16772: 4, 903: 1, 686: 2, 909: 1, 126: 2, 40: 10, 42: 23, 65: 7, 64: 8, 108: 1, 201: 3, 4751: 3, 209: 1, 112: 3, 11: 46, 123: 3, 554: 1, 124: 10, 660: 2, 221: 6, 760: 1, 1088: 1, 86: 1, 211: 2, 629: 3, 1386: 2, 1596: 1, 1450: 2, 845: 2, 2108: 3, 1474: 1, 5541: 2, 6238: 1, 18: 33, 20: 24, 32: 16, 6: 169, 36: 9, 469: 4, 558: 1, 1: 1373, 136: 3, 304: 2, 431: 1, 78: 8, 118: 2, 152: 6, 162: 2, 21: 36, 41: 12, 438: 4, 447: 2, 1468: 3, 53: 11, 55: 8, 268: 1, 393: 1, 464: 2, 775: 1, 2972: 2, 3439: 1, 44: 10, 217: 3, 13: 61, 14: 34, 884: 3, 2286: 2, 198: 2, 886: 2, 1434: 2, 1780: 1, 2420: 3, 23: 29, 121: 6, 122: 7, 154: 2, 279: 2, 625: 2, 15: 49, 27: 26, 48: 17, 58: 4, 200: 2, 68: 3, 445: 2, 150: 1, 493: 2, 569: 2, 284: 3, 285: 1, 536: 1, 83: 6, 138: 5, 80: 1, 158: 1, 5: 200, 2: 760, 84: 7, 320: 1, 87: 11, 99: 4, 31: 20, 33: 14, 73: 4, 61: 4, 62: 8, 63: 4, 302: 6, 328: 3, 187: 4, 615: 2, 204: 1, 746: 1, 251: 6, 376: 1, 581: 4, 641: 1, 252: 1, 147: 7, 24: 15, 271: 7, 286: 1, 348: 2, 754: 3, 276: 3, 344: 2, 353: 1, 1184: 1, 639: 2, 572: 2, 1245: 2, 2990: 3, 2209: 1, 9: 104, 10: 72, 227: 1, 137: 2, 402: 3, 507: 2, 591: 1, 405: 1, 183: 2, 39: 10, 7: 136, 49: 8, 25: 23, 38: 15, 56: 8, 690: 2, 4: 303, 60: 7, 653: 1, 349: 3, 428: 2, 192: 1, 194: 2, 452: 1, 532: 3, 59: 9, 375: 3, 417: 2, 8: 101, 28: 20, 235: 1, 12: 87, 22: 34, 114: 4, 51: 7, 34: 9, 325: 1, 330: 3, 105: 1, 35: 3, 37: 8, 69: 1, 249: 1, 467: 2, 474: 2, 3: 392, 128: 1, 133: 1, 143: 5, 19: 32, 116: 1, 267: 1, 107: 1, 120: 6, 131: 4, 130: 3, 156: 2, 212: 2, 215: 1, 1080: 3, 166: 4, 172: 3, 30: 22, 189: 4, 231: 2, 220: 2, 119: 1, 181: 2, 85: 2, 477: 3, 164: 2, 91: 7, 253: 1, 72: 4, 17: 33, 82: 2, 52: 6, 265: 1, 289: 2, 70: 6, 50: 11, 66: 2, 381: 2, 29: 9, 46: 10, 100: 1, 197: 1, 266: 5, 16: 35, 111: 5, 76: 9, 90: 1, 97: 1, 93: 2, 224: 1, 157: 1, 275: 1, 47: 10, 45: 4, 106: 3, 424: 2, 318: 1, 54: 4, 81: 2, 175: 1, 109: 2, 26: 17, 142: 2, 202: 1, 79: 3, 95: 3, 170: 2, 171: 2, 167: 1, 94: 5, 96: 5, 322: 1, 88: 3, 101: 3, 74: 3, 43: 5, 75: 1, 226: 2, 57: 5, 160: 2, 98: 6, 246: 2, 129: 1, 77: 2, 110: 2})
        with open("Dataset/property_frequencies_histogram_dict.pickle", 'wb') as handle:
            pickle.dump(property_frequencies_histogram, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open("Dataset/property_frequencies_dict.pickle", 'wb') as handle:
            pickle.dump(property_frequencies, handle, protocol=pickle.HIGHEST_PROTOCOL)

        print("Number of properties per ingredient histogram:")
        print(number_of_properties_per_ingredient_histogram)
        # Number of properties per ingredient histogram:
        # defaultdict(<class 'int'>, {38: 137, 31: 134, 21: 930, 26: 732, 17: 1256, 24: 574, 16: 716, 18: 1316, 22: 880, 30: 314, 20: 1032, 19: 1294, 25: 1398, 34: 349, 46: 219, 14: 508, 23: 639, 13: 66, 40: 137, 28: 248, 29: 623, 33: 154, 36: 236, 10: 30, 48: 16, 15: 1500, 27: 471, 53: 7, 43: 6, 8: 22, 32: 158, 9: 23, 12: 254, 35: 126, 39: 65, 37: 31, 44: 21, 45: 48, 7: 50, 11: 22, 49: 3, 1: 7, 57: 6, 41: 12, 47: 3, 42: 3, 54: 2, 50: 1})
        with open("Dataset/number_of_properties_per_ingredient_histogram.pickle", 'wb') as handle:
            pickle.dump(number_of_properties_per_ingredient_histogram, handle, protocol=pickle.HIGHEST_PROTOCOL)

        for namespace_name in important_property_prefixes_dict:
            namespace_prefix = important_property_prefixes_dict[namespace_name]
            out_filepath = os.path.join(out_directory, "ingredient_properties_from_ontology_" + namespace_prefix + ".ttl")
            ingredient_properties_named_graphs[namespace_prefix].serialize(destination=out_filepath, format='turtle')
            print(f"Ingredient properties from ontology '{namespace_prefix}', are saved in: {out_filepath}")
            print("Number of total triples saved:", len(ingredient_properties_named_graphs[namespace_prefix]))
            # Ingredient properties from ontology 'obo', are saved in: Dataset/ingredient_properties_from_ontology_obo.ttl
            # Number of total triples saved: 233093
            # Ingredient properties from ontology 'b_node', are saved in: Dataset/ingredient_properties_from_ontology_b_node.ttl
            # Number of total triples saved: 141315



# print(check_if_ingredient_name_exists_in_foodKG_as_IRI(ingredient_iri="garlic%20cloves"))
# print(check_if_ingredient_name_exists_as_rdfs_label(ingredient_name="garlic cloves"))
#
#
# get_recipe_IRI_and_name_given_recipe_URL(recipe_URL="http://www.epicurious.com/recipes/food/views/cheddar-cheese-and-potato-soup-374901")
# get_recipe_IRI_and_name_given_recipe_URL(recipe_URL="http://www.food.com/recipe/mexican-festa-delight-by-katt-knight-472249")
# try :
#     get_recipe_URL_and_name_given_recipe_IRI(recipe_IRI="http://idea.rpi.edu/heals/kb/recipe/49546c3d-Cheddar%20Cheese%20and%20Potato%20Soup")
# except Exception as inst:
#     print(type(inst))  # the exception type
#     print(inst.args)  # arguments stored in .args
#     print(inst)  # __str__ allows args to be printed directly,
# get_recipe_URL_and_name_given_recipe_IRI(recipe_IRI="http://idea.rpi.edu/heals/kb/recipe/325dc29f-Mexican%20Festa%20Delight%20by%20Katt%20Knight")

# print(get_IRI_of_ingredient_matched_by_rdfs_label(ingredient_name="pie shell"))

# get_FoodKG_ingredient_IRIs_of_recipe_given_url("http://www.food.com/recipe/sachertorte-cookies-170040")


#
# foodkg_graphdb_interface = FoodKGGraphDBInterface(load_ingredient_indexes_from_files=True)
#
# ingredient_results = foodkg_graphdb_interface.get_ingredient_short_IRI_from_1Msubs_to_foodKG_by_IRI_or_name("all_-_purpose_flour")
# print(ingredient_results)
# print("ok")