import orjson

conf = open('config.json','r')
confStr = conf.read()
conf.close()

CONFIG = orjson.loads(confStr)