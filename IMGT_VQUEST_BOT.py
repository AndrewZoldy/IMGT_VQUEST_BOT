from selenium import webdriver
from selenium.webdriver.support.ui import Select
from Bio import SeqIO
import csv
import re
import argparse
import time
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'This is simple bot')
    
    parser.add_argument('-In','--Input_file',help='File for processing, please enter the path to the directory', default = '0')
    parser.add_argument('-Out', '--Output_file', help='Save data in csv file, enter the path to the directory', action='store_true', default = '0')
    parser.add_argument('-lc', '--locus', help='choose the species (type the number)', default = 0)
    parser.add_argument('-sp', '--species', help='choose the receptor type or locus (type the number)', default = 0)
    
    ar = parser.parse_args()
        
    #ar.Input_file
    #ar.Output_file
    
# >>>> НАЧАЛО ОБЪЯВЛЕНИЯ ФУНКЦИЙ !!!!!
    
    #Функция возвращает группу:
    def g(x,y):
        return(x.group(y))
    
    # Регулярное выражение для поиска:
    ID_csv = re.compile(r""">(?P<ID>[A-Z]{1,2}[\d]{6}\.[\d]{1})
                    [\s\S]*?
                    Result\ssummary:\s;\s*
                    (?P<Functionality>(Productive)|(Unproductive)|(Unknown)|(No\sresults)|(Productive\swith\scomments)|())
                    [\s\S]*?
                     V-GENE\sand\sallele;Homsap\s
                    (?P<position>[A-Z\d\s\-]*)
                    [\s\S]*?   
                    N1-REGION[\s]*
                    (?P<N1_start>[\d]+)
                    \.\.(?P<N1_stop>[\d]+)
                    [\s\S]*?
                    /nucleotide\ssequence[\s]*
                    (?P<N1_seq>[agtcAGTC]*)
                    [\s\S]*?
                    /translation
                    """, re.VERBOSE)
    
    # Основная функция:

    def MAKE(x,whole_seq,selected_seq,data_out):
            
        select_species = Select(browser.find_element_by_name("l01p01c02"))
        sp = select_species.options
        select_species.select_by_value(sp[x].get_attribute("value"))
         #Выбор вида
         
        select_rtype = Select(browser.find_element_by_name("l01p01c04"))
        rc = select_rtype.options
        select_rtype.select_by_visible_text(rc[y].get_attribute("value"))
        #Выбор типа рецептора или локуса
        
        dt = browser.find_element_by_xpath("/html/body/form/div/div/table/tbody/tr/td/input[1]")
        dt.click() #Выбор способа загрузки данных (во встроенное текстовое окно)
        
        browser.find_element_by_link_text("Uncheck all").click() #Сброс параметров поиска
        browser.find_element_by_name("l01p01c18").click() #Выбор только 13 пункта в параметрах поиска  
        
        text_area = browser.find_element_by_name("l01p01c11")
        text_area.send_keys(os.getcwd()+"\\fastabot.fasta")#Загрузка данных из файла
        
        text_output = browser.find_element_by_xpath("/html/body/form/p[6]/table[1]/tbody/tr/td[2]/input[2]")
        text_output.click()#Выбор способа вывода результатов (в виде текста)
        
        subm = browser.find_element_by_class_name("vquestquery")
        subm.submit() #Переход на страницу с результатами
         
        #Находим текстовые поля на сайте и записываем в текстовый документ
        with open(os.getcwd()+'\\fastabot_50_temp.txt', 'w') as temp:
            text_finder = browser.find_element_by_xpath("/html/body/pre").text
            temp.writelines(text_finder)
            temp.write('\n')
            
        #Находит в текстовом документе необходимые группы и переносит их в csv файл
        with open(os.getcwd()+'\\fastabot_50_temp.txt','r') as text:
            m=text.read()
            x=ID_csv.finditer(m)
            
            with open(data_out,'a',newline='') as csvfile:
                my_riter = csv.writer(csvfile,delimiter=';')
                for i in x:
                    #print(g(i,"Functionality"),g(i,"ID"))
                    whole_seq+=1
                    if g(i,"Functionality") == 'Productive':
                        my_riter.writerow([g(i,"ID"),g(i,"position"),g(i,"N1_seq")])
                        selected_seq+=1
                    else:
                        continue
        browser.get('https://www.imgt.org/IMGT_vquest/vquest?livret=0&Option=humanIg')
        return(whole_seq,selected_seq)
    
# >>>> КОНЕЦ ОБЪЯВЛЕНИЯ ФУНКЦИЙ !!!!!

    # Объявление переменной содержащей имя файла
    if ar.Input_file == '0':
        print('Enter the path to file with sequences in fasta format:')
        data = str(input())
    else:
        data = ar.Input_file
    
    # Объявление переменной содержащей имя выходного файла
    if ar.Output_file == '0':
        print('Enter the path to output csv file:')
        data_out = str(input())
    else:
        data_out = ar.Output_file
    
    start_time = time.time()
    whole_seq = 0
    selected_seq = 0
    
    '''
    with open('C:/Work archive/control_IGHV3_only.fasta', "r") as fasta:
        records=list(SeqIO.parse(fasta, "fasta"))
    #открываем файл с последовательностями
    '''
    
    # Открываем файл с последовательностями
    with open(data, "r") as fasta:
        records=list(SeqIO.parse(fasta, "fasta"))
        
    # Подключение драйвера. Открываем IMGT_VQUEST. Проверка на успешное выполнение запроса
    browser = webdriver.Chrome()
    browser.get('https://www.imgt.org/IMGT_vquest/vquest?livret=0&Option=humanIg')
    assert 'IMGT/V-QUEST Search Page' in browser.title 
        
    
    # Выбор вида из представленного списка:  
    select_species = Select(browser.find_element_by_name("l01p01c02"))
    sp = select_species.options
    if ar.species == 0:
        print("Choose the species (type the number):")
        i = 1
        for option in sp[1:]:
            print(i,":", option.get_attribute("value"))
            i+=1
        x = int(input())
        select_species.select_by_value(sp[x].get_attribute("value"))
    else:
        x = ar.species 
     
        
    # Выбор рецептора из представленного списка:
    select_rtype = Select(browser.find_element_by_name("l01p01c04"))
    rc = select_rtype.options
    if ar.locus == 0:
        print("Choose the receptor type or locus (type the number):")
        i = 1
        for option in rc[1:]:
            print(i,":", option.get_attribute("value"))
            i+=1
        y = int(input())
    else:
        y = ar.locus
    
    # Объявление переменных:
        
    rng = len(records)//50
    rng2 = len(records)%50
    
    # Рабочий цикл программы
    
    for i in range(0,rng*50-49,50): #Просто счетчик
        with open(os.getcwd()+'\\fastabot.fasta', 'w') as temp: #Записывает последовательности
            for j in range(i,i+50):
                temp.write(">")
                temp.writelines(records[j].name)
                temp.write('\n')
                temp.writelines(records[j].seq)
                temp.write('\n')  
        
        whole_seq,selected_seq = MAKE(x,whole_seq,selected_seq, data_out)
    
    with open(os.getcwd()+"\\fastabot.fasta", 'w') as temp:
        for j in range(-1,-rng2-1,-1):
            temp.write(">")
            temp.writelines(records[j].name)
            temp.write('\n')
            temp.writelines(records[j].seq)
            temp.write('\n')
    whole_seq,selected_seq = MAKE(x,whole_seq,selected_seq, data_out)
    print("--- %s seconds ---" % (time.time() - start_time))
    print(whole_seq,'sequences were processed')
    print(selected_seq,'sequences are productive')
    
    os.remove(os.getcwd()+'\\fastabot_50_temp.txt')
    os.remove(os.getcwd()+"\\fastabot.fasta")
    