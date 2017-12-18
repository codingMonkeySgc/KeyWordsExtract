import jieba.analyse
#jieba.load_userdict("file\\newdict.txt")
import json

def testjieba():
    wlist = list(jieba.cut("提出了一种基于伪随机补偿技术的流水线模数转换器（ADC）子级电路．该子级电路能够对比较器失调和"
                           "电容失配误差进行实时动态补偿．误差补偿采用伪随机序列控制比较器阵列中参考比较电压的方式实现．"
                           "比较器的高低位被随机分配，以消除各比较器固有失调对量化精度的影响，同时子ADC输出的温度计码具"
                           "有伪随机特性，可进一步消除MDAC电容失配误差对余量输出的影响．",cut_all=True))
    for word in wlist:
        print(word)

def main():
    """
    主函数
    :return: None
    """
    init()
    lines = readFile(dataPath)
    for paper in lines[0:100]:
        storeKeywords(keywordsPath, createAllKeyWords(paper))
    print("共提取%d篇论文的关键词. " % (len(lines)))


def init():
    """
    初始化全局变量和停用词表
    :return: None
    """
    global stopwordsPath, dataPath, keywordsPath, stopwords  # 声明全局变量
    stopwordsPath = "file\\stopwords_cn.txt"
    dataPath = "file\\paper_clean.dat"
    keywordsPath = "file\\paper_keywords_textrank2.dat"
    stopwords = loadStopWord(stopwordsPath)
    print("停用词加载完成: 共%d个停用词. " % (len(stopwords)))
    print("初始化完成. ")


def loadStopWord(fileName):
    """
    加载停用词
    :fileName: 停用词路径
    :return: 返回停用词的集合
    """
    stopwords = set()
    fstop = open(stopwordsPath, 'r', encoding='utf-8', errors='ignore')
    for eachWord in fstop:
        stopwords.add(eachWord.strip())
    fstop.close()
    return stopwords


def readFile(fileName):
    """
    读取数据文件
    :param fileName: 文件名
    :return: 文件中的每一行组成的列表
    """
    with open(fileName, 'r', encoding='utf-8') as f:
        return f.readlines()


def createAllKeyWords(paper):
    """
    生成关键词
    :param paper: 论文对象
    :return: 论文id和其对应的关键词列表
    """
    decodejson = json.loads(paper)
    _id = decodejson["_id"]  # paper id
    allKeywords = decodejson["keywords"]  # paper 原关键词
    title = decodejson["title"]  # paper 标题
    abstract = decodejson["abstract"]  # paper 摘要
    if ("Chinese" in abstract):
        text = "%s．%s" % (title, abstract["Chinese"])  # 中文摘要 把标题和摘要拼一块了
    else:
        text = title
    #allKeywords.extend(extractPhrases(text))
    id2Keywords = {}
    #id2Keywords["_id"] = _id
    id2Keywords["standordKeywords"] = allKeywords
    id2Keywords["abstract"] = abstract
    #id2Keywords["keywords"] = list(set(allKeywords))  # 去重
    id2Keywords["keywords"] = extractPhrases(text)
    return json.dumps(id2Keywords, ensure_ascii=False)


def cutText(text):
    """
    对文本进行分词
    :param text: 待分词的文本
    :return: 分词结果
    """
    wordList = list(jieba.cut(text))  # 用结巴分词，对每行内容进行分词
    reList = []
    for word in wordList:
        if word not in stopwords:  # 手动去停用词
            reList.append(word)
    return reList


def extractWords(text, num=20, withWeight=False):
    """
    提取关键词
    :param text: 待提取文本
    :param num: 提取关键词的数量
    :param withWeight: 是否返回权重
    :return: 关键词的列表
    """
    jieba.analyse.set_stop_words(stopwordsPath)  # 加载停用词
    # return jieba.analyse.extract_tags(text, topK = num, withWeight = withWeight)  tf-idf
    return jieba.analyse.textrank(text, topK=num, withWeight=withWeight)


def extractPhrases(text, keywordsNum=20, reKeywordsNum=5, minOccurNum=2):
    """
    获取关键[词语]和[短语]。
    获取 keywordsNum 个关键词中前 reKeywordsNum 个关键词。
    获取 keywordsNum 个关键词构造的可能出现的[短语]，要求这个短语在原文本中至少出现的次数为 minOccurNum 。
    :param text: 待提取文本
    :param keywordsNum: 待选关键[词语]数量
    :param reKeywordsNum: 返回关键[词语]数量
    :param minOccurNum: [短语]最少出现次数
    :return: 关键关键词语和短语的列表。
    """
    keywordsList = extractWords(text, num=keywordsNum)  # 提取关键词语
    # 将候选关键词中的前 reKeywordsNum 添加到返回列表中
    reKeyWords = [keywordsList[i] for i in
                  range((reKeywordsNum < len(keywordsList)) and reKeywordsNum or len(keywordsList))]
    keywordsSet = set(keywordsList)
    keyphrases = set()
    one = []
    # 获取关键短语
    for word in cutText(text):
        if word in keywordsSet:
            one.append(word)
        else:
            if len(one) > 1:
                keyphrases.add(''.join(one))
            if len(one) == 0:
                continue
            else:
                one = []
    # 最后一个
    if len(one) > 1:
        keyphrases.add(''.join(one))
    # 出现次数大于 minOccurNum 的加入关键词列表
    reKeyWords.extend([phrase for phrase in keyphrases
                       if text.count(phrase) >= minOccurNum])
    return reKeyWords


def storeKeywords(fileName, eachLine):
    """
    存储获取到的关键词，每篇paper一行，存储格式为json字符串
    :param fileName: 存储路径
    :param eachLine: json字符串
    :return: None
    """
    with open(fileName, 'a', encoding='utf-8', newline='\n') as f:
        f.write(eachLine + '\n')


if __name__ == "__main__":
    #print("test")
    # pass
    main()

