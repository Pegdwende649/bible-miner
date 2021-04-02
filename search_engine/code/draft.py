###### PREPARING THE DATA ######


asv_docs = Documents("./search_engine/data/bibles/asv/t_asv.csv")
bbe_docs = Documents("./search_engine/data/bibles/bbe/t_bbe.csv")
dby_docs = Documents("./search_engine/data/bibles/dby/t_dby.csv")
kjv_docs = Documents("./search_engine/data/bibles/kjv/t_kjv.csv")
wbt_docs = Documents("./search_engine/data/bibles/wbt/t_wbt.csv")
web_docs = Documents("./search_engine/data/bibles/web/t_web.csv")
ylt_docs = Documents("./search_engine/data/bibles/ylt/t_ylt.csv")


asv_docs.get_books()
bbe_docs.get_books()
dby_docs.get_books()
kjv_docs.get_books()
wbt_docs.get_books()
web_docs.get_books()
ylt_docs.get_books()


asv_docs.get_chapters()
bbe_docs.get_chapters()
dby_docs.get_chapters()
kjv_docs.get_chapters()
wbt_docs.get_chapters()
web_docs.get_chapters()
ylt_docs.get_chapters()
    

asv_docs.get_verses()
bbe_docs.get_verses()
dby_docs.get_verses()
kjv_docs.get_verses()
wbt_docs.get_verses()
web_docs.get_verses()
ylt_docs.get_verses()


asv_data_books = DataReader(path = "search_engine/data/bibles/asv/books/").read()
bbe_data_books = DataReader(path = "search_engine/data/bibles/bbe/books/").read()
dby_data_books = DataReader(path = "search_engine/data/bibles/dby/books/").read()
kjv_data_books = DataReader(path = "search_engine/data/bibles/kjv/books/").read()
wbt_data_books = DataReader(path = "search_engine/data/bibles/wbt/books/").read()
web_data_books = DataReader(path = "search_engine/data/bibles/web/books/").read()
ylt_data_books = DataReader(path = "search_engine/data/bibles/ylt/books/").read()


asv_data_chapters = DataReader(path = "search_engine/data/bibles/asv/chapters/").read()
bbe_data_chapters = DataReader(path = "search_engine/data/bibles/bbe/chapters/").read()
dby_data_chapters = DataReader(path = "search_engine/data/bibles/dby/chapters/").read()
kjv_data_chapters = DataReader(path = "search_engine/data/bibles/kjv/chapters/").read()
wbt_data_chapters = DataReader(path = "search_engine/data/bibles/wbt/chapters/").read()
web_data_chapters = DataReader(path = "search_engine/data/bibles/web/chapters/").read()
ylt_data_chapters = DataReader(path = "search_engine/data/bibles/ylt/chapters/").read()


asv_data_verses = DataReader(path = "search_engine/data/bibles/asv/verses/").read()
bbe_data_verses = DataReader(path = "search_engine/data/bibles/bbe/verses/").read()
dby_data_verses = DataReader(path = "search_engine/data/bibles/dby/verses/").read()
kjv_data_verses = DataReader(path = "search_engine/data/bibles/kjv/verses/").read()
wbt_data_verses = DataReader(path = "search_engine/data/bibles/wbt/verses/").read()
web_data_verses= DataReader(path = "search_engine/data/bibles/web/verses/").read()
ylt_data_verses = DataReader(path = "search_engine/data/bibles/ylt/verses/").read()



%%time
asv_data_books["Text"] = asv_data_books["Text"].apply(Preprocessor.preprocess)


%%time
asv_data_chapters["Text"] = asv_data_chapters["Text"].apply(Preprocessor.preprocess)


%%time
asv_data_verses["Text"] = asv_data_verses["Text"].apply(Preprocessor.preprocess)



algorithm = sequential_index_algorithm()

%%time
asv_books_index_builder = index_builder(asv_data_books)
asv_books_index = asv_books_index_builder.run(algorithm)


%%time
asv_chapters_index_builder = index_builder(asv_data_chapters)
asv_chapters_index = asv_chapters_index_builder.run(algorithm)



