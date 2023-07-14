from typing import Iterable, Optional, Tuple, Union, cast, Any, List, Type, Dict, DefaultDict
from SPARQLWrapper import SPARQLWrapper, JSON

from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointInternalError


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



def get_all_recipe_ids_and_urls(foodkg_repository:str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> dict[str, Tuple[str, str]]:
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

    recipe_url_to_foodkg_uri_and_name_dict:dict[str: tuple[str, str]] = dict()

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
def get_recipe_URL_given_recipe_IRI(recipe_IRI:str, foodkg_repository:str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> str:
    recipe_IRI_and_name_given_URL_sparql_query = """
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select distinct ?recipe_url where {
        Graph ?graph {""" + "<"+recipe_IRI+">" + """ a a recipe-kb:recipe}.
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

def get_recipe_IRIs_given_recipe_URL(recipe_URL:str, foodkg_repository:str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> list[str]:
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

    recipe_iris:list[str] = []
    for result in results["results"]["bindings"]:
        recipe_IRI = result["recipe_iri"]["value"]
        # recipe_name = result["recipe_name"]["value"]
        recipe_iris.append(recipe_IRI)
        # print("EDW:", recipe_IRI, recipe_name)
    return recipe_iris

# def get_all_ingredient_info_of_recipe_url(recipe_url:str, foodkg_repository:str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> list[dict[str:str]]:
#     pass

def check_if_ingredient_name_exists_as_rdfs_label(ingredient_name, foodkg_repository:str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> bool:
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


def check_if_ingredient_name_exists_in_foodKG_as_IRI(ingredient_iri, foodkg_repository:str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> bool:

    ingredient_name_exists_in_foodKG_as_IRI_sparql_query = """
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    ask {<http://idea.rpi.edu/heals/kb/ingredientname/"""+ingredient_iri + "> rdf:type recipe-kb:ingredientname. }"


    sparql = SPARQLWrapper(foodkg_repository)
    sparql.setQuery(ingredient_name_exists_in_foodKG_as_IRI_sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    exists = results["boolean"]
    return exists

def get_IRI_of_ingredient_with_rdfs_label(ingredient_name, foodkg_repository:str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> Optional[list[str]]:

    match_ingredient_by_name_sparql_query= """
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT Distinct ?ingredient_iri Where { 
    ?ingredient_iri rdfs:label  \"""" + ingredient_name +  """\".
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
        raise ValueError("Multiple ingredient matched by rdfs label (name) with value:" + ingredient_name + "\n" + results["results"]["bindings"])

    return related_IRI

def match_ingredient_from_1Msubs_to_foodKG_by_IRI_or_name(ingredient_name) -> Optional[str]:
    cleaned_ingredient_name = clean_ingredient_name(ingredient_name)
    possible_IRIs = generate_synonyms_of_ingredient(cleaned_ingredient_name, replace_underscore_with="%20")
    # print(possible_IRIs)
    try:
        matched_IRI: str = None
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
            print("Probably run out of memory Error!")
            raise Exception(exception)
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


def get_FoodKG_ingredient_IRIs_of_given_recipe_IRI(recipe_iri: str, foodkg_repository: str = "http://nick-the-greek.home:7200/repositories/FoodKG") -> list[str]:

    get_ingredients_of_recipe_IRI_sparql_query = """
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select ?ingredientIRI where {
    <""" + recipe_iri + """> recipe-kb:uses ?ingredientRecipeIRI.
    ?ingredientRecipeIRI recipe-kb:ing_name ?ingredientIRI.
    ?ingredientIRI a recipe-kb:ingredientname.}"""

    sparql = SPARQLWrapper(foodkg_repository)
    sparql.setQuery(get_ingredients_of_recipe_IRI_sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    ingredient_IRIs: List[str] = []
    for result in results["results"]["bindings"]:
        ingredient_IRIs.append(result["ingredientIRI"]["value"])

    return ingredient_IRIs

#
# def return_IRI_of_recipe1mSubs_ingredient(ingredient_name):
# #     clean name (remove any '"')
#     # search it by IRI
#     if
#     # search it by name

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