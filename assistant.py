from unidecode import unidecode
import speech_recognition as sr
from nltk import word_tokenize, corpus
import json

CORPUS_LANGUAGE = 'portuguese'
SPEECH_LANGUAGE = 'pt-BR'
CONFIG_PATH = 'D:/Projetos/IFBA/IA/assistente-virtual-python/config.json'

recognizer = None
stop_words = None
assistant_name = None
questions = None

def init():
    global recognizer
    global stop_words
    global assistant_name
    global questions
    
    recognizer = sr.Recognizer()
    stop_words = set(corpus.stopwords.words(CORPUS_LANGUAGE))
    stop_words.remove('qual')
    stop_words.remove('mais')
    stop_words.remove('é')
    stop_words.remove('são')
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
        assistant_name = config['name']
        questions = config['questions']
        
        config_file.close()
        

def listen_question():
    global recognizer
    global stop_words
    question = None
    
    with sr.Microphone() as audio_source:
        recognizer.adjust_for_ambient_noise(audio_source)
        
        print('Faça uma pergunta...')
        speech = recognizer.listen(audio_source)
        
        try:
            question = recognizer.recognize_google(speech, language=SPEECH_LANGUAGE).lower()
            print('Pergunta reconhecida:', question)
        except sr.UnknownValueError:
            pass
        
    return question

def remove_stop_words(tokens):
    global stop_words    
    filtered_tokens = []
    
    for token in tokens:
        if token not in stop_words:
            filtered_tokens.append(token)
            
    return filtered_tokens

def tokenize_question(question):
    global assistant_name
    question_parts = None
    tokens = word_tokenize(question, CORPUS_LANGUAGE)
    
    if tokens:
        tokens = remove_stop_words(tokens)
        total_tokens = len(tokens)
        
        if total_tokens >= 3:
            if assistant_name == unidecode(tokens[0]):
                question_parts = []
                
                for i in range(1, total_tokens):
                    question_parts.append(tokens[i])
                    
    return question_parts

def recognize_prefix(question_parts):
    global questions
    valid_prefix = False
    total_valid_parts = 0
    valid_questions_numbers = []
    
    for expected_question in questions:
        for prefix in expected_question['prefix']:
            expected_prefix = word_tokenize(prefix, CORPUS_LANGUAGE)
            total_expected = len(expected_prefix)
            
            if total_expected <= len(question_parts):
                total_valid_parts_partial = 0
                
                for i in range(0, total_expected):
                    if expected_prefix[i] == question_parts[i]:
                        total_valid_parts_partial = total_valid_parts_partial + 1

                if total_valid_parts_partial == total_expected:
                    valid_prefix = True
                    total_valid_parts = total_valid_parts_partial
                    valid_questions_numbers.append(expected_question['number']) #testar retornar pergunta de fato
                
    return valid_prefix, valid_questions_numbers, total_valid_parts

def recognize_main_part(questions_numbers, question_main_parts):
    global questions
    valid = False
    answer = None
    
    for expected_question in questions:
        if expected_question['number'] in questions_numbers: #testar
            for main_part in expected_question['main_parts']:
                expected_main_part = word_tokenize(main_part, CORPUS_LANGUAGE)
                total_expected = len(expected_main_part)
                
                if total_expected <= len(question_main_parts):
                    total_valid_parts_partial = 0
                    
                    for i in range(0, total_expected):
                        if expected_main_part[i] == question_main_parts[i]:
                            total_valid_parts_partial = total_valid_parts_partial + 1
                            
                    if total_valid_parts_partial == total_expected:
                        valid = True
                        answer = expected_question['answer']
                        break
                        
    return valid, answer 
    

if __name__ == '__main__':
    init()
    keep = True
    
    while keep:
        question = listen_question()
        valid_prefix, valid_main_part = False, False
        
        if question:
            question_parts = tokenize_question(question)
            
            if question_parts:
                valid_prefix, valid_questions_numbers, total_valid_parts = recognize_prefix(question_parts)
                
                if valid_questions_numbers:
                    question_main_parts = question_parts[total_valid_parts:]
                    valid_main_part, answer = recognize_main_part(valid_questions_numbers, question_main_parts)
                    
                    if valid_main_part:
                        print('A resposta é:', answer)
                        
        if not (valid_prefix and valid_main_part):
            print('Não entendi a pergunta. Repita, por favor!')
                    
                    
                