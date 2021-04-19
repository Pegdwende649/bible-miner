# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 13:11:41 2021

@author: David OUBDA
"""
from search_engine.code.utils import Documents
from search_engine.code.utils import DataReader
from search_engine.code.utils import Preprocessor
from search_engine.code.utils import index_builder
from search_engine.code.utils import mapred_index_algorithm
from search_engine.code.utils import sequential_index_algorithm
from search_engine.code.utils import Queries

def construct_index(version,granularity):
    
    version_docs = Documents("./search_engine/data/bibles/"+version+"/t_"+version+".csv")
    get_data_func_name = "get_"+granularity+"()"
    exec("version_docs."+get_data_func_name)
    version_data_reader =  DataReader(path = "search_engine/data/bibles/"+version+"/" + granularity+ "/")
    version_data = version_data_reader.read()
    version_data["Text"] = version_data["Text"].apply(Preprocessor.preprocess)
    algorithm = sequential_index_algorithm()
    version_index_builder = index_builder(version_data)
    print("building index")
    version_index = version_index_builder.run(algorithm)
    return version_index,version_data
    

dby_chapters_index,version_data = construct_index(version = "web",granularity = "books")

queries = Queries(dby_chapters_index,version_data)
r=queries.single_word_query_tf_idf_ordered("christ")  
r1=queries.single_word_query_frequency_ordered("christ")  
r2=queries.single_word_query_occurences_ordered("christ")  
r3=queries.free_text_query(["christ"])  
r4=queries.key_words_query("christ jesus")
r5=queries.exact_match_query("christ jesus")
r6=queries.sentence_query_vector_space("christ jesus")

