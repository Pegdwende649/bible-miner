# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 13:05:15 2021

@author: David OUBDA
"""
import pandas as pd
import numpy as np
import os
import glob
import nltk
from nltk.corpus import stopwords
from functools import reduce
from sklearn.feature_extraction.text import  CountVectorizer,TfidfVectorizer
from more_itertools import locate
from functools import reduce
import time
from multiprocessing import Pool
import itertools
from operator import itemgetter
import re


books_keys = pd.read_csv("./search_engine/data/keys/key_english.csv")
genre_keys = pd.read_csv("./search_engine/data/keys/key_genre_english.csv")

books_keys_dict = {books_keys["b"][i]:
                   {"name":books_keys["n"][i],"testament":books_keys["t"][i],"genre":genre_keys[genre_keys["g"]==books_keys["g"][i]]["n"].values[0]}
                   for i in range(len(books_keys))}


class Documents:
    
    def __init__(self,csv_path):
        self.csv_path = csv_path
        self.directory_path = csv_path[:-9]
        self.bible = pd.read_csv(self.csv_path)
        
    
    def get_books(self):
        
        bible = self.bible
        if  not os.path.exists(self.directory_path+"/books"):
            os.mkdir(self.directory_path+"/books")
        
        print("Writing books")
        for book in np.unique(bible["b"].values):
            book_text=bible[bible["b"]==book]["t"].values
            book_text = '\n'.join(book_text)
            f = open(self.directory_path+"books/"+books_keys_dict[book]["name"]+".txt", "w",encoding="utf-8") 
            f.write(book_text)
            f.close()  
            
        print("books succesfully written")

    
    def get_chapters(self):
        
        bible = self.bible
        if  not os.path.exists(self.directory_path+"/chapters"):
            os.mkdir(self.directory_path+"/chapters")
        
        print("Writing chapters")
        for book in np.unique(bible["b"].values):
            book_text=bible[bible["b"]==book]
            for chapter in book_text["c"]:
                chapter_text = book_text[book_text["c"]==chapter]["t"].values
                chapter_text = '\n'.join(chapter_text)
                f = open(self.directory_path+"chapters/"+books_keys_dict[book]["name"]+str(chapter)+".txt", "w",encoding="utf-8") 
                f.write(chapter_text)
                f.close()  
            
        print("books succesfully written")
        
    
    def get_verses(self):

        bible = self.bible
        if  not os.path.exists(self.directory_path+"/verses"):
            os.mkdir(self.directory_path+"/verses")
        
        print("Writing verses")
        for book in np.unique(bible["b"].values):
            book_text=bible[bible["b"]==book]
            for chapter in book_text["c"]:
                chapter_text = book_text[book_text["c"]==chapter]
                for verse in chapter_text["v"]:
                    verse_text = chapter_text[chapter_text["v"] == verse]["t"].values[0]
                    f = open(self.directory_path+"verses/"+books_keys_dict[book]["name"]+str(chapter)+"-"+str(verse)+".txt", "w",encoding="utf-8") 
                    f.write(verse_text)
                    f.close()  
            
        print("verses succesfully written")    
        

class DataReader:
    
    def __init__(self,path):
        self.path = path
    
    def read(self):
        
        files_names_list = glob.glob(self.path+'*.txt')
        documents_list = []
        for files in files_names_list :
        
            with open(files, 'r') as file:
                    #Read the file data
                    data = file.read()
            documents_list.append(data)
            
        Data = pd.DataFrame(documents_list, columns = ['Text'])
        Data["file_name"] = files_names_list
        
        return Data 





class Preprocessor:
    
    def __init__(self):
        nltk.download('stopwords')
        nltk.download('wordnet')


    def replace_contracted_words(text):
            import re
            # Replace contracted word
            re_repl= { 
                        r"\br\b": "are",
                        r"\bu\b": "you",
                        r"\bhaha\b": "ha",
                        r"\bhahaha\b": "ha",
                        r"\bdon't\b": "do not",
                        r"\bdoesn't\b": "does not",
                        r"\bdidn't\b": "did not",
                        r"\bhasn't\b": "has not",
                        r"\bhaven't\b": "have not",
                        r"\bhadn't\b": "had not",
                        r"\bwon't\b": "will not",
                        r"\bwouldn't\b": "would not",
                        r"\bcan't\b": "can not",
                        r"\bcannot\b": "can not",
                            }
            #Replacement
            for r,repl in re_repl.items():
                    text=re.sub(r,repl,text)
                    
            return text
            
       
            
    def remove_words_cont_nb(text):
            import re
            """ Remove words containing numbers

            Parameters
            ----------
            text : str
                Any text

            Returns
            ------
            str
                A text cleaned
            """
            return re.sub(' +', ' ' ,re.sub(r'\w*\d\w*', '', text).strip())

    def remove_stopwords(text, stopword):
            '''a function for removing the stopword'''
            # removing the stop words and lowercasing the selected words
            text = [word.lower() for word in text.split() if word.lower() not in stopword]
            # joining the list of words with space separator
            return " ".join(text)

    def remove_punctuation(text):
        '''a function for removing punctuation'''
        import string
        # replacing the punctuations with no space, 
        # which in effect deletes the punctuation marks 
        translator = str.maketrans('', '', string.punctuation)
        # return the text stripped of punctuation marks
        return text.translate(translator)

    def remove_special_characters(text):

        """ Removes all the special characters from a text

        Parameters
        ----------
        text : str
            Any text

        Returns
        ------
        str
            A text cleaned
        """
        import re
        return re.sub(' +',' ',re.sub('[^a-z\s]+', '', text).strip())

    def remove_single_letter(text):
        import re
        """ Remove single letters

        Parameters
        ----------
        text : str
            Any text

        Returns
        ------
        str
            A text cleaned
        """
        return re.sub(' +', ' ' ,re.sub(r'\b\w\b', '', text).strip())

    def lemmatization(text):

        '''a function which lemmatizes each word in the given text'''
        import nltk
        wnl = nltk.WordNetLemmatizer()
        text = [wnl.lemmatize(word) for word in text.split()]
        return " ".join(text)
    
    
    def preprocess(text):
    
        
        stpwds = stopwords.words('english')
        
        text =  Preprocessor.replace_contracted_words(text)
        text =  Preprocessor.remove_words_cont_nb(text)
        text =  Preprocessor.remove_punctuation(text)
        text =  Preprocessor.remove_stopwords(stopword = stpwds,text = text)
        text =  Preprocessor.remove_special_characters(text)
        text =  Preprocessor.remove_single_letter(text)
        text =  Preprocessor.lemmatization(text)
        
        return text
    



class sequential_index_algorithm:
    
    def run(self,Data):
        from more_itertools import locate

        Vocab = [list(set(doc.split())) for doc in Data["Text"]]
        index_list = []
        for text_num,vocab_text in enumerate(Vocab):
           index_text = [{word : text_num} for word in vocab_text]
           index_list.extend(index_text)


        index, keys = {},[]
        for dicti in index_list:
            key = list(dicti.keys())[0]
            val = list(dicti.values())[0]
            file_name = Data["file_name"][val]                        
            file_title_match = re.search("\\\\(.*).txt", file_name)
            file_title = file_title_match.groups()[0]           
            doc_split = Data["Text"][val].split()
            num_words = len(doc_split)
            positions = list(locate(doc_split, lambda x: x == key))

            occurences = len(positions)

            if key in keys:
                upd_key_dict = {file_title:{"number of words" :num_words,"positions":positions,"occurences":occurences}}
                index[key].update(upd_key_dict)
            else:
                temp_index = {key : {file_title:{"number of words" :num_words,"positions":positions,"occurences":occurences}}}
                index.update(temp_index)
                keys.append(key)

        return index
            





class mapred_index_algorithm:

    def mapred_split(self,split_length,Data):
        
        Vocab = [list(set(doc.split())) for doc in Data["Text"]]

        """
        Splits the Vocabulary into a certain number of blocks. each block is designed to be given as input to a mapper.
        """
        split_lists = [(i*split_length,(i+1)*split_length-1) for i in range(int(len(Data)/split_length))] #For eg:[(0, 249), (250, 499), (500, 749),... ]
        vocab_blocks = [{split[0]:Vocab[split[0]:split[1]+1]} for split in split_lists]
        return vocab_blocks



    def index_mapper(self,vocab_block):

        """
        Map function that returns a list of dictionnaries {"word":doc_num} from a block of vocabulary 
        """
        first_doc_num = list(vocab_block.keys())[0]
        list_words_by_doc = [[{"word":word,"doc_num" : doc_num + first_doc_num} for word in vocab] for doc_num, vocab in enumerate(vocab_block[first_doc_num])] #List of lists
        return reduce(list.__add__,list_words_by_doc) #Just to make one list


    def intermediate_grouping(self,mapped_vocab,blocks_numb):

    
        """
        intermediate function that groups the mapped blocks by words
        """
        mapped_vocab = reduce(list.__add__,mapped_vocab)

        grouped_index = []

        sorted_mapped_vocab = sorted(mapped_vocab, key=itemgetter('word'))

        for key, value in itertools.groupby(sorted_mapped_vocab, key=itemgetter('word')):
            grouped_index.append(list(value))
            
        block_size = len(grouped_index)//blocks_numb
        split_lists = [[i*block_size,(i+1)*block_size-1] for i in range(int(len(grouped_index)/block_size))] #For eg:[(0, 249), (250, 499), (500, 749),... ]
        split_lists[-1][1] = split_lists[-1][1]+len(grouped_index)%blocks_numb
        index_blocks = [grouped_index[split[0]:split[1]+1] for split in split_lists]

        
        return index_blocks

        

    def index_reducer(self,grouped_vocab_block,Data):

        """
        Reducer used to build the index
        """   
        index_block = {}
        for doc_list_by_word in grouped_vocab_block:
            word = doc_list_by_word[0]["word"]
            doc_list = [{"doc_num":dicti["doc_num"],
                         "number of words" : len(Data["Text"][dicti["doc_num"]].split()),
                         "occurences" : len(list(locate(Data["Text"][dicti["doc_num"]].split(), lambda x: x == word))),
                         "positions" : list(locate(Data["Text"][dicti["doc_num"]].split(), lambda x: x == word))} for dicti in doc_list_by_word ]

            index_data = {doc["doc_num"] : {"number of words" :doc["number of words"],"positions":doc["positions"],"occurences":doc["occurences"]} for doc in doc_list}
            temp_index = {word : index_data}
            index_block.update(temp_index)

        return index_block   


    def index_merge(self,index1,index2):
        index1.update(index2)
        return index1
    
    def run(self,data,n_proces = 10,map_block_size = 250,blocks_numb = 10):
        
        splited_blocks = self.mapred_split(map_block_size)

        with Pool(n_proces) as pool:
            list_mapped_blocks = pool.map(self.index_mapper,splited_blocks)
            #list_grouped_blocks = self.intermediate_grouping(list_mapped_blocks)
            list_splited_by_words = self.intermediate_grouping(list_mapped_blocks,blocks_numb)#self.split_by_words(list_grouped_blocks, blocks_numb)
            list_reduced_blocks = pool.map(self.index_reducer,list_splited_by_words)

        index_mapred = reduce(self.index_merge,list_reduced_blocks)
        
        return index_mapred


class index_builder:
    
    def __init__(self,data):
        self.data = data
        self.vocab = [list(set(doc.split())) for doc in self.data["Text"]]
        
        
    def run(self,algorithm):
        
        data = self.data
        return algorithm.run(data)




class Queries:
    def __init__(self, index,data):
        self.index = index
        self.Data = data
    
    def single_word_query_occurences_ordered(self,word,display = True):
        word = Preprocessor.preprocess(word)
        
        try:
            
            result = sorted(self.index[word].items(), key=lambda item: list(item[1].items())[2],reverse = True)
            if display:
                print("This word occurs in the following documents:\n") 
                for doc in result:
                
                    print("-> "+doc[0]+" - Number of occurences : "+ str(doc[1]["occurences"]))
            return result
        except KeyError:
            print(":( Sorry there is no result for this search")
            
    
            
    
    def single_word_query_frequency_ordered(self, word,display = True):
        
        word =  Preprocessor.preprocess(word)
        try:
            result = sorted(self.index[word].items(), key=lambda item: list(item[1].items())[2][1]/list(item[1].items())[0][1],reverse = True)
            if display:
                print("This word occurs in the following documents:\n") 
                for doc in result:
                    print("-> "+doc[0]+" - Frequency : "+ str(round((doc[1]["occurences"]/doc[1]["number of words"])*100,4))+"%")
            return result
        except KeyError:
            print(":( Sorry there is no result for this search")
            

    
    def single_word_query_tf_idf_ordered(self,word,display = True):
        
        from math import log
        word =  Preprocessor.preprocess(word)
        try: 
            result = sorted(self.index[word].items(), key=lambda item: (list(item[1].items())[2][1]/list(item[1].items())[0][1])*(log(len(self.Data)/(len(self.index[word])+1))),reverse = True)
            if display:
                print("This word occurs in the following documents:\n") 
                for doc in result:
                    print("-> "+doc[0]+" - TD-IDF : "+ str(round((doc[1]["occurences"]/doc[1]["number of words"])*log(len(self.Data)/(len(self.index[word])+1)),4)))
            return result
        except KeyError:
            print(":( Sorry there is no result for this search")
        
        
        
    
    def free_text_query(self,words_list,display = True):
        words_list = [ Preprocessor.preprocess(word) for word in words_list]
        try: 
            result = set([])
            for word in words_list:
                result = result.union(set(list(self.index[word].keys())))
            if display:
                print( "This is the list of documents contaning at least one of the given words")
                for doc in result:
                    print("-> "+doc) 
            return result
        except KeyError:
            print(":( Sorry There wer no file containing at least one word")

            
            
    def key_words_query(self,words_list,display = True):
        words_list = [ Preprocessor.preprocess(word) for word in words_list]
        try:
            result = set(list(self.index[words_list[0]].keys()))
            for word in words_list:
                result = result.intersection(set(list(self.index[word].keys())))
            
            if display:
                print( "This is the list of documents contaning the given words simultaneously")

                for doc in result:
                    print("-> "+doc)
            return result
        except:
            print(":( Sorry at least one word was not found in any file")

    def exact_match_query(self,sentence,display = True):
        
        
        words_list = sentence.split()
        sentence =  Preprocessor.preprocess(sentence)
        words_list = sentence.split()
        result_sets = []
        final_result = []
        for word in words_list:
            result = self.single_word_query_occurences_ordered(word,display = False)
            result_set = {i[0] for i in result}
            result_sets.append(result_set)
        intersection_docs = reduce(set.intersection,result_sets)   
        for doc in intersection_docs:
            words_positions = []
            for word_num,word in enumerate(words_list):
                word_positions = set(list(np.array(self.index[word][doc]["positions"])-word_num))
                words_positions.append(word_positions)
            intersect_positions = reduce(set.intersection,words_positions)
            if len(intersect_positions)!=0:
                final_result.append(doc)
                if display:
                    print(doc+ " --- "+str(len(intersect_positions))+" time(s) in this document")

        return final_result

                
    def sentence_query_vector_space(self,sentence,vectorizer,results_numb):
        sentence =  Preprocessor.preprocess(sentence)
        data_matrix = vectorizer.transform(self.Data["Text"])
        sentence_matrix = vectorizer.transform([sentence])
        result_distances = data_matrix.dot(sentence_matrix.transpose())
        result_distances=result_distances.toarray()
        sort_index = np.argsort((-np.array([i[0] for i in result_distances.tolist()])))
        print("the "+str(results_numb)+" best results are :")
        for doc_index in list(sort_index)[:results_numb]:
            print("-> Doc "+str(doc_index[0]))

    
