# -*- coding: utf-8 -*-
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

def drawRuler(pdf):
    pdf.setFont('Helvetica', 5)
    
    for i in range(5):
        pdf.drawString((i+1)*100, 810, 'x' + str((i+1)*100))
    
    for i in range(8):
        pdf.drawString(10, (i+1)*100, 'y' + str((i+1)*100))
    
def insert_basic_info(pdf, A, B, x, y):
    pdf.setFont('Helvetica', 10)
    pdf.drawString(x, y, A + ': ')
    pdf.setFont('Times-Italic', 10)
    textWidth = stringWidth(A + ": ", 'Helvetica', 10)
    x += textWidth + 1
    pdf.drawString(x, y, B)

def gen_pdf(basic_information, closed_questions_answers, all_message, language):

    if language == "en":
        name = 'Name'
        gender = 'Gender'
        age = 'Age'
        residential_street = 'Residential Street'
        street_number = 'Street Number'
        post_code = 'Post Code'
        city = 'City'
        phone_number = 'Phone Number'
        statement = 'Statement'
        form = 'Form'
        yes = 'yes'
        no = 'no'
        yes_list = ['yes', 'yeah', 'exactly']
        no_list = ['no']
        only_for_doctor = "Only for doctor:"
        preset_cq = ["Do you have pre-existing conditions?", 
                     "Do you have allergies?", 
                     "Are your currently taking medications?", 
                     "Are you taking long-term medications?", 
                     "Do you suffer from chronic diseases?"]
        
    elif language == "de":
        name = 'Name'
        gender = 'Geschlecht'
        age = 'Alter'
        residential_street = 'Wohnstraße'
        street_number = 'Hausnummer'
        post_code = 'Postleitzahl'
        city = 'Wohnort'
        phone_number = 'Telefonnummer'
        statement = 'Zustand'
        form = 'Formular'
        yes = 'Ja'
        no = 'Nein'
        yes_list = ['ja']
        no_list = ['nein']
        only_for_doctor = "Nur für Arzt:"
        preset_cq = ["Haben Sie Vorerkrankungen?", 
                     "Hast du Allergien?", 
                     "Nehmen Sie derzeit Medikamente?", 
                     "Nehmen Sie Langzeitmedikamente ein?", 
                     "Leiden Sie unter chronischen Krankheiten?"]
        
        
    #创建画布
    pdf = canvas.Canvas(str(basic_information[name]) + "_" + str(basic_information[age]) + "_" + language + ".pdf")
    pdf.setTitle(form)
    
    #drawRuler(pdf)
    
    pdf.setFont('Helvetica', 20)
    pdf.drawString(280, 800, form)
    #-----------basic information-----------
    bi_init = 790
    pdf.line(100, bi_init, 500, bi_init)
    
    insert_basic_info(pdf, name, basic_information[name], 120, bi_init-30)
    insert_basic_info(pdf, gender, basic_information[gender], 320, bi_init-30)
    insert_basic_info(pdf, age, str(basic_information[age]), 120, bi_init-50)
    insert_basic_info(pdf, residential_street, basic_information[residential_street], 320, bi_init-50)
    insert_basic_info(pdf, street_number, str(basic_information[street_number]), 120, bi_init-70)
    insert_basic_info(pdf, post_code, str(basic_information[post_code]), 320, bi_init-70)
    insert_basic_info(pdf, city, basic_information[city], 120, bi_init-90)
    insert_basic_info(pdf, phone_number, str(basic_information[phone_number]), 320, bi_init-90)
    insert_basic_info(pdf, statement, basic_information[statement], 120, bi_init-110)
    #-----------closed question-----------
    cq_init = 650
    pdf.line(100, cq_init+20, 500, cq_init+20)
    pdf.setFont('Helvetica', 10)
    for i in range(5):
        pdf.drawString(120, cq_init, preset_cq[i])
        if closed_questions_answers[i] == {}:
            pdf.drawString(400, cq_init, no)
        elif "Ja" in closed_questions_answers[i].values() == False:
            pdf.drawString(400, cq_init, no)
        else:
            for k in closed_questions_answers[i].keys():
                pdf.drawString(250, cq_init-15, k)
                if closed_questions_answers[i][k] == "Ja":
                    bol = True
                else:
                    bol = False
                pdf.drawString(150, cq_init-15, yes)
                pdf.acroForm.checkbox(checked = bol, buttonStyle = "cross", shape = "square",
                                      size = 15, x = 130, y = cq_init-18, tooltip = preset_cq[i] + "-----" + k, name = k + '_yes')
                pdf.drawString(190, cq_init-15, no)
                pdf.acroForm.checkbox(checked = not bol, buttonStyle = "cross", shape = "square",
                                      size = 15, x = 170, y = cq_init-18, tooltip = preset_cq[i] + "-----" + k, name = k + '_no')
                cq_init -=15
                
        cq_init -=18
    
    #-----------open question-----------
    oq_init = cq_init-12
    pdf.setFont('Helvetica', 10)
    pdf.line(100, oq_init+20, 500, oq_init+20)
    for item in all_message[1:-3]:
        pdf.setFont('Helvetica', 10)
        if item['role'] == 'assistant':
            pdf.drawString(120, oq_init, item['content'])
            string = item['content']
        elif item['role'] == 'user':
            #if "yes" in item['content'] or "Yes" in item['content'] or "yeah" in item['content']:
            if any(substring in item['content'].lower() for substring in yes_list):
                pdf.acroForm.checkbox(checked = True, buttonStyle = "cross", shape = "square",
                                      size = 15, x = 120, y = oq_init - 3, tooltip = string, name = string + '_yes')
                pdf.drawString(136, oq_init, yes)
                pdf.acroForm.checkbox(checked = False, buttonStyle = "cross", shape = "square",
                                      size = 15, x = 300, y = oq_init - 3, tooltip = string, name = string + '_no')
                pdf.drawString(316, oq_init, no)
                pdf.setFont('Times-Italic', 10)
                pdf.drawString(400, oq_init, item['content'])
            #elif "no" in item['content'] or "No" in item['content']:
            elif any(substring in item['content'].lower() for substring in no_list):
                pdf.acroForm.checkbox(checked = False, buttonStyle = "cross", shape = "square",
                                      size = 15, x = 120, y = oq_init - 3, tooltip = string, name = string + '_yes')
                pdf.drawString(136, oq_init, yes)
                pdf.acroForm.checkbox(checked = True, buttonStyle = "cross", shape = "square",
                                      size = 15, x = 300, y = oq_init - 3, tooltip = string, name = string + '_no')
                pdf.drawString(316, oq_init, no)
                pdf.setFont('Times-Italic', 10)
                pdf.drawString(400, oq_init, item['content'])
            else:
                pdf.setFont('Times-Italic', 10)
                pdf.drawString(120, oq_init, item['content'])
        oq_init -= 20
        
    #yes no
    
    pdf.line(100, oq_init, 500, oq_init)
    pdf.setFont('Helvetica', 10)
    pdf.setFillColorRGB(1, 0, 0)
    pdf.drawString(120, oq_init-20, only_for_doctor)
    pdf.setFont('Times-Italic', 10)
    pdf.drawString(120, oq_init-40, all_message[-1]['content'])
    
    pdf.save()
    
    print(str(basic_information[name]) + "_" + str(basic_information[age]) + "_" + language + ".pdf generated!")
    

'''
basic_information_en = {"Name":"Zongjian Li", "Gender":"male", "Age":26, "Residential Street":"Sandbergstrasse", "Street Number":48, 
                     "Post Code":64285, "City":"Darmstadt", "Phone Number":15256261791, "Statement":"Ich habe Fieber"}

basic_information_de = {"Name":"Zongjian Li", "Geschlecht":"männlich", "Alter":26, "Wohnstraße":"Sandbergstrasse", "Hausnummer":48, 
                     "Postleitzahl":64285, "Wohnort":"Darmstadt", "Telefonnummer":15256261791, "Zustand":"Ich habe Fieber"}

closed_questions_answers = [{'Asthma': 'Ja', 'Diabetes': 'Nein', 'Hypertonie (Hypertension)': 'Nein', 'Arthritis': 'Nein', 'Allergien (Allergies)': 'Nein'}, 
                            {'Pollen': 'Nein', 'Hausstaubmilben': 'Ja', 'Tierhaare': 'Nein', 'Schimmelpilze': 'Nein', 'Erdnüsse': 'Nein'}, 
                            {'Ibuprofen': 'Nein', 'Paracetamol': 'Nein', 'Aspirin': 'Ja', 'Omeprazol': 'Nein', 'Pantoprazol': 'Nein'}, 
                            {}, 
                            {'Diabetes (Diabetes)': 'Nein', 'Herzkrankheit (Herzkrankheit)': 'Nein', 'Krebs (Krebs)': 'Nein', 'Chronische Lungenerkrankung (Chronische Lungenerkrankung)': 'Nein', 'Rheumatoide Arthritis (Rheumatoide Arthritis)': 'Ja'}]

all_message = [{'role': 'user', 'content': 'You are doctor assistent. Ask me questions about symptoms to narrow down my disease. Questions are based on my First Description. After I answered one question then asked the next one. At one time you can only asked one question. Speak shortly and ask directly.\n        First Description: I\'ve got a cold\n        When giving the final answer, please first say "##FINAL ANSWER##" then tell me the answer.'}, 
               {'role': 'assistant', 'content': 'Are you experiencing a runny or stuffy nose?'}, 
               {'role': 'user', 'content': 'No'}, 
               {'role': 'assistant', 'content': 'Are you experiencing a sore throat?'}, 
               {'role': 'user', 'content': 'No'}, 
               {'role': 'assistant', 'content': 'Are you experiencing a cough?'}, 
               {'role': 'user', 'content': 'Yes'}, 
               {'role': 'assistant', 'content': '##FINAL ANSWER##\nBased on your symptoms of having a cold with a cough, it is likely that you have a common cold.'},
               {'role': 'user', 'content': 'Extract the disease in short answer.'},
               {'role': 'assistant', 'content': 'Upper respiratory infection or common cold.'}]

gen_pdf(basic_information_de, closed_questions_answers, all_message, "de")
'''