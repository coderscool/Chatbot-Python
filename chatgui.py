import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import webbrowser

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(open('intents.json').read())
stores = json.loads(open('storys.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))
print(model)

def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.99
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    print(results)
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
    try:
        ints = predict_class(msg, model)
        if not ints:
            res = 'Tôi không hiểu. Bạn muốn thêm dữ liệu mới hay đặt câu hỏi?'
            messagebox.showinfo("Lựa chọn", res)
            option = simpledialog.askstring("Lựa chọn", "Nhập 'add' để thêm dữ liệu mới, 'query' để đặt câu hỏi")
            if option.lower() == 'add':
                create()
                res = 'Dữ liệu đã được thêm thành công!'
            elif option.lower() == 'query':
                search_google(msg)
                res = 'Tìm kiếm trên Google với từ khoá: "{}"'.format(msg)
                addStory(msg,res)
            else:
                res = 'Lựa chọn không hợp lệ. Vui lòng nhập "add" hoặc "query".'
            return res
        else:
            res = getResponse(ints, intents)
            addStory(msg,res)
            return res
    except Exception as e:
        return 'Đã xảy ra lỗi: {}'.format(str(e))

import tkinter
from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox

def search_google(query):
    try:
        search_url = "https://www.google.com/search?q={}".format(query)
        webbrowser.open(search_url)
    except Exception as e:
        messagebox.showerror("Lỗi", "Đã xảy ra lỗi: {}".format(str(e)))
    
def send():
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
    
        res = chatbot_response(msg)
        ChatLog.insert(END, "Bot: " + res + '\n\n')
            
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
 
def create():
    try:
        tag = simpledialog.askstring("Nhập thông tin", "Nhập tên của bạn")
        question = simpledialog.askstring("Nhập thông tin", "Nhập câu hỏi của bạn")
        result = simpledialog.askstring("Nhập thông tin", "Vui lòng cung cấp câu trả lời của bạn")
        if tag and question and result:
            addFileJson(question, result, tag)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")
    except Exception as e:
        messagebox.showerror("Lỗi", "Đã xảy ra lỗi: {}".format(str(e)))

def addStory(msg,res):
    data=[{'message': msg,
           'response': res}]
    print(data)
    store_file = stores['store']+data
    new_file = {"store": store_file}
    a_file = open("storys.json", "w")
    json.dump(new_file, a_file)
    a_file.close()
    
def addFileJson(ques, res, tag):
    try:
        fi = open("intents.json", 'r')
        data = json.load(fi)
        field = [{'tag': tag,
                  'patterns': [ques],
                  'responses': [res],
                  'context': [""]}]
        intent_file = data['intents'] + field
        new_file = {"intents": intent_file}
        a_file = open("intents.json", "w")
        json.dump(new_file, a_file)
        a_file.close()
    except Exception as e:
        messagebox.showerror("Lỗi", "Đã xảy ra lỗi: {}".format(str(e)))
        
base = Tk()
base.title("Hello")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)

ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)

ChatLog.config(state=DISABLED)

scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff',
                    command= send )

EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Arial")
scrollbar.place(x=376,y=6, height=386)
ChatLog.place(x=6,y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)

base.mainloop()