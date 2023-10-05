# -*- coding: utf-8 -*-
import openai
import streamlit as st
from streamlit_chat import message

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline

import generate_pdf

# Setting page title and header
st.set_page_config(page_title="PVC Project", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>AUTOMATIC FORM FILLING WITH INTERFACES TO LANGUAGE MODELS</h1>", unsafe_allow_html=True)

# Set API key
openai.api_key = ""

# Initialise session state variables

#radio for supquestions of closed questions
if 'closed_questions_options' not in st.session_state:
    st.session_state['closed_questions_options'] = [[], [], [], [], []]#
if 'closed_questions_options_radio' not in st.session_state:
    st.session_state['closed_questions_options_radio'] = ["No"]*25
    
if 'past_en' not in st.session_state:
    st.session_state['past_en'] = []
if 'past_de' not in st.session_state:
    st.session_state['past_de'] = []
if 'generated_en' not in st.session_state:
    st.session_state['generated_en'] = []
if 'generated_de' not in st.session_state:
    st.session_state['generated_de'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'messages_en' not in st.session_state:
    st.session_state['messages_en'] = []
if 'messages_de' not in st.session_state:
    st.session_state['messages_de'] = []
if "tokenizer_en_de" not in st.session_state:
    st.session_state["tokenizer_en_de"] = AutoTokenizer.from_pretrained("D:\PVC\opus-mt-en-de")
if "tokenizer_de_en" not in st.session_state:
    st.session_state["tokenizer_de_en"] = AutoTokenizer.from_pretrained("D:\PVC\opus-mt-de-en")
if "model_en_de" not in st.session_state:
    st.session_state["model_en_de"] = AutoModelForSeq2SeqLM.from_pretrained("D:\PVC\opus-mt-en-de")
if "model_de_en" not in st.session_state:
    st.session_state["model_de_en"] = AutoModelForSeq2SeqLM.from_pretrained("D:\PVC\opus-mt-de-en")
if 'prompt' not in st.session_state:
    st.session_state['prompt'] = ""
if 'ending' not in st.session_state:
    st.session_state['ending'] = 0
    
def translation(text, task_type):
    
    if task_type == "en2de":
        
        MT_en_de = pipeline("translation_en_to_de", model = st.session_state["model_en_de"], tokenizer = st.session_state["tokenizer_en_de"])
        MT_results_en_de = MT_en_de(text)
        return MT_results_en_de[0]['translation_text']

    elif task_type == "de2en":
        # change Nein into No
        word_replace = {'nein':'No', 'Nein':'No', 'NEIN':'No'}
        for key, value in word_replace.items():
            text = text.replace(key, value)
        MT_de_en = pipeline("translation_de_to_en", model = st.session_state["model_de_en"], tokenizer = st.session_state["tokenizer_de_en"])
        MT_results_de_en = MT_de_en(text)
        return MT_results_de_en[0]['translation_text']
        
    else:
        return "type_error"

# generate a response
def generate_response(user_input):
    #add prompt
    st.session_state['messages'].append({"role": "user", "content": user_input})
    st.session_state['messages_en'].append({"role": "user", "content": user_input})
    
    #get response from ChatGPT
    completion = openai.ChatCompletion.create(model = "gpt-3.5-turbo", messages = st.session_state['messages'])
    #reply content
    response = completion.choices[0].message.content

    st.session_state['messages'].append({"role": "assistant", "content": response})
    st.session_state['messages_en'].append({"role": "assistant", "content": response})

    total_tokens = completion.usage.total_tokens
    return response, total_tokens

def calculate_cost(total_tokens):
    
    st.session_state['total_tokens'].append(total_tokens)
    cost = total_tokens * 0.002 / 1000
    st.session_state['cost'].append(cost)
    st.session_state['total_cost'] += cost    

preset_cq = ["Do you have pre-existing conditions?", 
             "Do you have allergies?", 
             "Are your currently taking medications?", 
             "Are you taking long-term medications?", 
             "Do you suffer from chronic diseases?"]

preset_cq_de = ["Haben Sie Vorerkrankungen?", 
             "Hast du Allergien?", 
             "Nehmen Sie derzeit Medikamente?", 
             "Nehmen Sie Langzeitmedikamente ein?", 
             "Leiden Sie unter chronischen Krankheiten?"]

preset_cq_prompt = ["give me 5 names of commonly pre-existing conditions without description in German", 
             "give me 5 names of common allergens without description in German", 
             "give me 5 names of commonly used medication without description in German", 
             "give me 5 names of common long-term medications without description in German", 
             "give me 5 common types of chronic diseases with only name in German"]

def get_sub_questions(i):
    
    results = []
    
    msg = []
    msg.append({"role": "user", "content": preset_cq_prompt[i]})
    #get response from ChatGPT
    completion = openai.ChatCompletion.create(model = "gpt-3.5-turbo", messages = msg)
    response = completion.choices[0].message.content
    subqustions = response.split("\n")[-6:]
    for i in range(5):
        results.append(subqustions[i][subqustions[i].find(" ")+1:])
        
    #tokens and costs
    total_tokens = completion.usage.total_tokens
    calculate_cost(total_tokens)  
    
    return results

def first_prompt(prompt):
    output, total_tokens= generate_response(prompt)
    
    st.session_state['past_en'].append(prompt)
    trans_prompt = translation(prompt, "en2de")
    st.session_state['past_de'].append(trans_prompt)
    st.session_state['messages_de'].append({"role": "user", "content": trans_prompt})
    
    st.session_state['generated_en'].append(output)
    trans_output = translation(output, "en2de")
    st.session_state['generated_de'].append(trans_output)
    st.session_state['messages_de'].append({"role": "assistant", "content": trans_output})
    
    calculate_cost(total_tokens)

# Sidebar
st.sidebar.title("Sidebar")

counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

#姓名
name = st.text_input('Bitte geben Sie hier Ihren Namen ein.', max_chars = 120, placeholder = "z.B. Thomas Müller")
#性别
gender = st.radio("Was ist Ihre Geschlecht?", ('M', 'F', 'D'), horizontal = True)
#年龄
age = st.number_input('Wie alt sind Sie?', min_value = 1, max_value = 120, format = '%d')
#居住街道
residential_street = st.text_input('Bitte geben Sie Ihre Wohnstraße ein.', max_chars = 120, placeholder = "z.B. Berliner Strasse")
#房屋号
street_number = st.number_input('Bitte geben Sie Ihre Hausnummer ein.', min_value = 1, format = '%d')
#邮编
post_code = st.text_input('Bitte geben Sie Ihre Postleitzahl ein.', max_chars = 5)
#城市
city = st.text_input('Bitte geben Sie Ihren Wohnort ein.', max_chars = 120, placeholder = "z.B. Berlin")
#手机号码
phone_number = st.text_input('Bitte geben sie ihre Telefonnummer ein.', max_chars = 20, placeholder = "z.B. 15256261791")
#radio for closed questions
radio_cq = [""]*5


#create subquestions from ChatGPT
for i in range(5):
    radio_cq[i] = st.radio("**" + preset_cq[i] + "**", ('Nein', 'Ja...'), help = "Wenn Sie auf „Ja...“ klicken, werden weitere Optionen angezeigt", horizontal = True)
    if radio_cq[i] == 'Ja...':
        if st.session_state['closed_questions_options'][i] == []:
            st.session_state['closed_questions_options'][i] = get_sub_questions(i)
            
        for j in range(5):
            st.session_state['closed_questions_options_radio'][i*5+j] = st.radio(":green[" + "    -" + st.session_state['closed_questions_options'][i][j] + "?" + "]", ('Nein', 'Ja'), horizontal = True, key = preset_cq[i]+str(j))

                
#身体状态
option = st.selectbox('Wie ist der Zustand Ihres Körpers?',
                      ('Ich habe eine Erkältung', 
                       'Ich habe Fieber',
                       'Ich huste viel',
                       'Ich habe seit Kurzem Durchfall',
                       'Ich habe Kopfschmerzen',
                       'Andere'))

if option == "Andere":
    statement = st.text_input('Bitte beschreiben Sie kurz Ihre Symptome', '')
else:
    statement = option
    
def verification():
    #name: not null and only alphabet
    if not(name.replace(' ', '').isalpha()):
        return "Bitte überprüfen Sie den Namen."
    #residential street: not null
    if residential_street == '':
        return "Bitte überprüfen Sie den Wohnstraße."
    #post code: only number
    if not(post_code.isdecimal()) or len(post_code) != 5 or int(post_code)<1067 or int(post_code)>99998:
        return "Bitte überprüfen Sie die Postleitzahl."
    #city: not null
    if city == '':
        return "Bitte überprüfen Sie den Wohnort."
    #phone number: only number
    if not(phone_number.isdecimal()):
        return "Bitte überprüfen Sie die Telefonnummer."
    else:
        return 1

def list2txt(list):

    result = ""
    
    for item in list[1:]:
        result += item['role'] + ":\n"
        result += item['content'] + "\n"
    
    return result
    

#同意
agree = st.checkbox('Ich verstehe, dass die von diesem System abgegebenen Meinungen keine medizinische Beratung darstellen.')

if agree:

    verification_result = verification();
    if verification_result == 1:
        basic_information_en = {"Name":name, "Gender":gender, "Age":age, "Residential Street":residential_street, "Street Number":street_number, 
                             "Post Code":post_code, "City":city, "Phone Number":phone_number, "Statement":statement}
        basic_information_de = {"Name":name, "Geschlecht":gender, "Alter":age, "Wohnstraße":residential_street, "Hausnummer":street_number, 
                             "Postleitzahl":post_code, "Wohnort":city, "Telefonnummer":phone_number, "Zustand":statement}
        
        # closed question
        closed_questions_answers = [{}, {}, {}, {}, {}]
        for i in range(5):
            #closed questions
            #subquestions form closed questions
            if st.session_state['closed_questions_options'][i] != []:
                for j in range(5):
                    closed_questions_answers[i][st.session_state['closed_questions_options'][i][j]] = st.session_state['closed_questions_options_radio'][i*5+j]
    
        # First prompt
        if st.session_state['messages'] == []:
            st.session_state['prompt'] = """You are doctor assistant. Ask me questions about symptoms to narrow down my disease. Questions are based on my First Description. After I answered one question then asked the next one. At one time you can only asked one question. Speak shortly and ask directly.
        First Description: %s
        When giving the final answer, please first say "##FINAL ANSWER##" then tell me the answer.""" %translation(statement, "de2en")
            first_prompt(st.session_state['prompt'])
        
        # container for chat history
        response_container = st.container()
        # container for text box
        container = st.container()
        
        with container:
            with st.form(key = 'my_form', clear_on_submit = True):
                user_input = st.text_area("Eingeben:", key = 'input', height = 100)
                submit_button = st.form_submit_button(label = 'Senden')
        
                
            if submit_button and user_input:
                # input_de
                st.session_state['past_de'].append(user_input)
                st.session_state['messages_de'].append({"role": "user", "content": user_input})
                # translate input de2en
                user_input = translation(user_input, "de2en")
                print({"role": "user", "content": user_input})
                output, total_tokens = generate_response(user_input)
                st.session_state['past_en'].append(user_input)
                st.session_state['generated_en'].append(output)
                print({"role": "assistant", "content": output})
                
                output = translation(output, "en2de")
                st.session_state['messages_de'].append({"role": "assistant", "content": output})
                
                if "##FINAL ANSWER##" in output:
                    # output an ending
                    output = "Danke für Ihre Eingaben!"
                    st.session_state['ending'] = 1

                st.session_state['generated_de'].append(output)
                calculate_cost(total_tokens)
                
        if st.session_state['generated_de']:
            with response_container:
                for i in range(len(st.session_state['generated_de'])):
        
                    if i != 0:
                        message(st.session_state["past_de"][i], is_user=True, key=str(i) + '_user')

                    message(st.session_state["generated_de"][i], key=str(i))
                    
                    st.write(f"Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
                    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
                        
        if st.session_state['ending'] == 1:
            
            order = "Extract the disease in short answer without ##FINAL ANSWER##."
            trans_order = translation(order, "en2de")
            
            output, total_tokens = generate_response(order)
            trans_output = translation(output, "en2de")

            st.session_state['messages_de'].append({"role": "user", "content": trans_order})
            st.session_state['messages_de'].append({"role": "assistant", "content": trans_output})
            
            calculate_cost(total_tokens)
            counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

            #terminate
            st.session_state['ending'] = 2
            
        if st.session_state['ending'] == 2:
            if st.button('Form PDF'):
                generate_pdf.gen_pdf(basic_information_en, closed_questions_answers, st.session_state['messages_en'], "en")
            if st.button('Formular PDF'):
                generate_pdf.gen_pdf(basic_information_de, closed_questions_answers, st.session_state['messages_de'], "de")
            
            basic_infomation_str_en = "Name: " + name + "\nGender: " + gender + "\nAge: " + str(age) + "\nResidential Street: " + residential_street + "\nStreet Number: " + str(street_number) + "\nPost Code: " + str(post_code) + "\nCity: " + city + "\nPhone Number: " + str(phone_number) + "\nStatement: " + statement + "\n"
            basic_infomation_str_de = "Name: " + name + "\nGeschlecht: " + gender + "\nAlter: " + str(age) + "\nWohnstraße: " + residential_street + "\nHausnummer: " + str(street_number) + "\nPostleitzahl: " + str(post_code) + "\nWohnort: " + city + "\nTelefonnummer: " + str(phone_number) + "\nZustand: " + statement + "\n"
            
            # recording for cq
            all_cq_de = ""
            all_cq_en = ""
            for i in range(5):
                all_cq_de = all_cq_de + preset_cq_de[i] + "\n" + str(closed_questions_answers[i]) + "\n"
                all_cq_en = all_cq_en + preset_cq[i] + "\n" + str(closed_questions_answers[i]) + "\n"
            
            st.download_button('Form generate', basic_infomation_str_en + all_cq_en + list2txt(st.session_state['messages_en']), file_name = name + "_" + str(age) + '_en' + '.csv')
            st.download_button('Formular generieren', basic_infomation_str_de + all_cq_de + list2txt(st.session_state['messages_de']), file_name = name + "_" + str(age) + '_de' + '.csv')
                
    else:
        st.write(verification_result)

