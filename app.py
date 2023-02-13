import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model


nltk.download('popular')
lemmatizer = WordNetLemmatizer()


model = load_model('chat_model.h5')
import json
import random
intents = json.loads(open('intents.json', encoding='utf-8').read())
words = pickle.load(open('texts.pkl','rb'))
classes = pickle.load(open('labels.pkl','rb'))

def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

student_query = []
def chat():
    print("Start chating with Level advicers assistant \nType 'quit' to stop \nPlease kindly note that this chat is being recorded for the purpose of improving the chatbot")
    while True:
        inp = input("You: ")
        student_query.append(inp)
        

        if inp.lower() == "quit":
            break

        print('bot:', chatbot_response(inp))


from flask import Flask, render_template, request, jsonify
import json
import sqlite3
from student_query import Std_querry

app = Flask(__name__)
app.config["DEBUG"] = True
app.static_folder = 'static'

# def go_home():
#     c = sqlite3.connect('student.db').cursor()
#     c.execute("CREATE TABLE IF NOT EXISTS STUDENTS("
#             "id TEXT, querry TEXT)"
#         )
#     c.connection.close()

# @app.route('/ff', methods=['GET'])
# def go_hom():
#     go_home()
#     return 'Welcome to students API!'
    
# def get_querries():
#     c = sqlite3.connect("student.db").cursor()
#     c.execute("SELECT * FROM STUDENTS")
#     data = c.fetchall()
#     return jsonify(data)

@app.route("/yet")
def home():
    return render_template("index.html")

@app.route("/")
def nothing():
    return "Hello World"

@app.route("/get") 
def get_bot_response():
    query = request.get_json('query')
    print(query)
    bot_reply = chatbot_response(query)
    payload = {
        "chat": {
            "query": query,
            "bot_reply": bot_reply,
        },
    }
    return payload



if __name__ == "__main__":
    app.run()
    # chat()