import json

f = open('Raspberry/json/topic_mqtt.json')
topics = json.load(f)
f.close()

list_topics = []

for subpart in topics:
	for part, listtopic in subpart.items():
		for value in listtopic:
			#print("partie {0} topics : {1} bdd : {2}".format(part,value['topic'],value['field']))
			list_topics.append(tuple([part,value['topic'],value['field']]))


subscribe_topics = []
for part,topic_name,field_name in list_topics:
	topic = topic_name
	subscribe_topics.append(topic)

print(subscribe_topics)