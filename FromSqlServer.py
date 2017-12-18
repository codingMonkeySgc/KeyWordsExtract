import  SQLServer.MSSQL as db
import KeyWordsExtract.ExtractKeyWords as ex

def main():
    ex.init()
    ms = db.MSSQL(**db.args)
    resList = ms.execQuery("select uid, title_cn, keywords_cn, abstract_text_cn from [dbo].[Paper]")
    for eachItem in resList:
        id = ""
        title = ""
        abstract = ""
        keywords = []
        if eachItem[0] != None :
            id = eachItem[0]
        if eachItem[1] != None :
            title = eachItem[1]
        if eachItem[2] != None :
            keywords = eachItem[2].split(",")
        if eachItem[3] != None :
            abstract = eachItem[3]
        text = title + "." + abstract
        keywords.extend(ex.extractPhrases(text))
        keywords = list(set(keywords))
        keywordsStr = ",".join(keywords)
        if keywordsStr == "":
            sql = "insert into [dbo].[KeyWords] values('%s', NULL)" % (id)
        else:
            sql = "insert into [dbo].[KeyWords] values('%s', '%s')" % (id, keywordsStr)
        print(sql)
        ms.execNonQuery(sql)

if  __name__ == "__main__":
    main()
