####
#
# VUT FIT
# Projekt - IPP: interpret
# Zaciatok projektu: 28.3.2021
# Autor: Jan Homola
#
####


from os import execlp
import sys
import xml.etree.ElementTree as elemTree
from operator import attrgetter
import re


# Globane premenne
sourceFile = sys.stdin
inputFile = sys.stdin
instructions = []

# Funkcia na kontrolu argumentov skriptu 
def check_script_param():
    global sourceFile
    global inputFile

    if len(sys.argv) < 2 or len(sys.argv) > 3 :
        exit(10)

    for arg in sys.argv[1:] :
        if arg == '-h' or arg == '--help' :
            print('Program na interpretaciu zdrojoveho kodu v jazyku IPPcode21')
            exit(0)

        elif arg.find('--source=') != -1 :
            sourceFile = arg[9:]

        elif arg.find('--input=') != -1 :
            inputFile = arg[8:]             

        else :
            exit(10)


# Funkcia na kontrolu XML suboru
def parse_xml(fileXML) :
    global instructions
    order_list = []
    
    try:
        tree = elemTree.parse(fileXML)
    except FileNotFoundError:
        exit(11)
    except:
        exit(31)
    
    root = tree.getroot()
    
    if root.tag != 'program' :
        exit(32)

    if root.attrib.get('language') == None :
        exit(32)

    if root.attrib.get('language').upper() != 'IPPCODE21' :
        exit(32)

    for atrib in root.attrib :
        if atrib != 'language' and atrib != 'description' and atrib != 'name' :
            exit(32)


    for inst in root :
        if inst.tag != 'instruction' :                          # V <program> musi byt <istruction>
            exit(32)

        if inst.attrib.get('opcode') == None :                  # Instrukcia musi mat opcode
            exit(32)        

        if inst.attrib.get('order') == None :                   # Instrukcia musi mat order
            exit(32)
        try: 
            if int(inst.attrib.get('order')) <= 0 :             # Order musi byt kladne cislo
                exit(32)
        except Exception:
            exit(32)
        
        if inst.attrib.get('order') not in order_list :
            order_list.append(inst.attrib.get('order'))
        else :
            exit(32)

        instructions.append(inst)

    # usporiadanie instrukcii vzostupne
    instructions = sorted(instructions, key=lambda instr: int(instr.attrib['order']))
    


# Funkcia na kontrolu spravnoti zapisania instrukcie v xml  
def check_instruction(instruction) :
    instr = []
    arg1 = []
    arg2 = []
    arg3 = [] 
    instr.append(instruction.attrib['opcode'].upper())
    
    if len(instruction) > 3 :                                   # mozu byt max 3 arg                 
        exit(32)

    
    for arg in instruction :
        if arg.tag != 'arg1' and arg.tag != 'arg2' and arg.tag != 'arg3' :
            exit(32) 

        # kontrola ci instrukcia obsahuje atribut type
        if arg.attrib.get('type') == None :
            exit(32)

        # kontrola ci instrukcia obsahuje spravne typy 
        if arg.attrib.get('type') not in ['label', 'var', 'nil', 'type', 'int', 'bool', 'string', 'float'] :
            exit(32)  

        arg_type = arg.attrib.get('type')
        if arg.tag == 'arg1' :
            arg1.append(arg_type)
            arg1.append(arg.text)
        elif arg.tag == 'arg2' :
            arg2.append(arg_type)
            arg2.append(arg.text)
        elif arg.tag == 'arg3' :
            arg3.append(arg_type)
            arg3.append(arg.text)
    
    # kontrola duplikatov arg
    check_duplicate_arg(instruction, instr, arg1, arg2, arg3)
    
    # kontrola syntaxe instrukcie
    check_syntax_instr(instr)

    return instr


# Funkcia na kontrolu ci nema instrukcia duplicitni argument
def check_duplicate_arg(instruction, instr, arg1, arg2, arg3) :
    required_num_of_arg = 0
    arg1_cnt = 0
    arg2_cnt = 0
    arg3_cnt = 0

    for arg in instruction :
        if arg.tag == 'arg1' :
            arg1_cnt += 1
        elif arg.tag == 'arg2' :
            arg2_cnt += 1
        elif arg.tag == 'arg3' :
            arg3_cnt += 1 

    # Kontrola duplikatu
    if arg1_cnt > 1 or arg2_cnt > 1 or arg3_cnt > 1 :
        exit(32)
    else :
        if len(arg1) != 0 :
            instr.append(arg1)
            required_num_of_arg = 1
        if len(arg2) != 0 :
            instr.append(arg2)
            required_num_of_arg = 2
        if len(arg3) != 0 :
            instr.append(arg3)
            required_num_of_arg = 3
        
    # Kontrola ci nechyba dajaky arg 
    if required_num_of_arg != len(instruction) :
        exit(32)


# Funkcia na kontrolu poctu argumentov
def check_number_of_arg(instruction, required_cnt) :
    arg_cnt = len(instruction) - 1                  # na prvej pozicii je nazov instrukcie 

    if arg_cnt != required_cnt :
        exit(32)

    

# Funckia na kontrolu syntaxe instrukcie
def check_syntax_instr(instruction):
    # Instrukcie s 0 operandami
    if instruction[0] in ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK'] :
        check_number_of_arg(instruction, 0)

    # Instrukcie s 1 operandom <var>
    elif instruction[0] in ['DEFVAR', 'POPS'] :
        check_number_of_arg(instruction, 1)
        check_var(instruction[1])

    # Instrukcie s 1 operandom <symb>
    elif instruction[0] in ['PUSHS', 'WRITE', 'EXIT', 'DPRINT'] :
        check_number_of_arg(instruction, 1)
        check_symb(instruction[1])

    # Instrukcie s 1 operandom <label>
    elif instruction[0] in ['CALL', 'LABEL', 'JUMP'] :
        check_number_of_arg(instruction, 1)
        check_label(instruction[1])

    # Instrukcie s 2 operandami <var> <symb>
    elif instruction[0] in ['MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'NOT', 'INT2FLOAT', 'FLOAT2INT'] :
        check_number_of_arg(instruction, 2)
        check_var(instruction[1])
        check_symb(instruction[2])
    
    # Instrukcia s 2 operandami <var> <type>
    elif instruction[0] == 'READ' :
        check_number_of_arg(instruction, 2)
        check_var(instruction[1])
        check_type(instruction[2])


    # Instrukcie s 3 operandami <var> <symb1> <symb2>
    elif instruction[0] in ['ADD', 'SUB', 'MUL', 'IDIV', 'DIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR'] :
        check_number_of_arg(instruction, 3)
        check_var(instruction[1])
        check_symb(instruction[2])
        check_symb(instruction[3])

    # Instrukcie s 3 operandami <label> <symb1> <symb2>
    elif instruction[0] in ['JUMPIFEQ', 'JUMPIFNEQ'] :
        check_number_of_arg(instruction, 3)
        check_label(instruction[1])
        check_symb(instruction[2])
        check_symb(instruction[3])

    # Zasobnikove instrukcie s 0 operandami (aritmeticke) 
    elif instruction[0] in ['ADDS', 'SUBS', 'MULS', 'DIVS', 'IDIVS'] :
        check_number_of_arg(instruction, 0)
    
    # Zasobnikove instrukcie s 0 operandami (logicke a relacne)
    elif instruction[0] in ['LTS', 'GTS', 'EQS', 'ANDS', 'ORS', 'NOTS'] :
        check_number_of_arg(instruction, 0)

    # Zasobnikove instukcie s 0 operandami (kovrezne)
    elif instruction[0] in ['INT2FLOATS', 'FLOAT2INTS', 'INT2CHARS', 'STRI2INTS', 'CLEARS'] :
        check_number_of_arg(instruction, 0)

    # Zasobnikove instrukcie s 1 operandom <label>
    elif instruction[0] in ['JUMPIFEQS', 'JUMPIFNEQS'] :
        check_number_of_arg(instruction, 1)

    # Ak to nie je ani jedna  povolena instrukcia 
    else :
        exit(32)    



# Funkcia na kontrolu <var>
def check_var(arg) :
    if arg[0] != 'var' :
        exit(32)

    if arg[1].find('@') != 1 :
        splitted_arg = arg[1].split('@', 1)

        if splitted_arg[0] not in ['LF', "TF", 'GF'] :
            exit(32)

        if not re.match(r'^[a-zA-Z_\-\$&%*!?][0-9a-zA-Z_\-\$&%*!?]*$', splitted_arg[1]) :
            exit(32)

    else :
        exit(32)


# Funkcia na kontrolu <symb>
def check_symb(arg) :
    # Kontrola konstant
    if arg[0] == 'int' :
        if not re.match(r'^[+\-0-9][0-9]*$', arg[1]) :
            exit(32)

    elif arg[0] == 'string' :
        if arg[1] == None :
            arg[1] = ''
        
        elif not re.match(r'^((\\[0-9]{3})|[^#\s\\])*$', arg[1]) :    # alebo re.match(r'^(?:(\\[0-9]{3})|[^#\s\\])*$', arg[1])
            exit(32)
        
    elif arg[0] == 'bool' :
        if arg[1] not in ['true', 'false'] :
            exit(32)
    
    elif arg[0] == 'nil' :
        if arg[1] != 'nil' :
            exit(32)

    elif arg[0] == 'float' :
        try :
            float_value = float.fromhex(arg[1])
        except :
            exit(32) 

    # Kontrola premennej
    elif arg[0] == 'var' :
        check_var(arg)

    # arg not [int, string, bool, nil, var, float]
    else :
        exit(32)

# Funkcia na kontrolu <label>
def check_label(arg) :
    if arg[0] != 'label' :
        exit(32)
    
    else:
        if not re.match(r'^[a-zA-Z_\-\$&%*!?][a-zA-Z0-9_\-\$&%*!?]*$', arg[1]) :
            exit(32)



# Funkcia na kontrolu <type>
def check_type(arg) :
    if arg[0] != 'type' :
        exit(32)

    if arg[1] not in ['int', 'string', 'bool', 'float'] :
        exit(32) 


# Funkcia vytvorenie premenej ktora sa vlozi do dict
def defvar(arg) :
    frame = arg[:2]
    name = arg[3:]

    if frame == 'GF' :
        if name in GF :
            exit(52)
        GF[name] = {}
        GF[name]['type'] = None
        GF[name]['value'] = None
    
    elif frame == 'LF' :
        if len(LF) == 0 :
            exit(55)
        
        if name in LF[TOP] :
            exit(52)
        LF[TOP][name] = {}
        LF[TOP][name]['type'] = None
        LF[TOP][name]['value'] = None
        
    elif frame == 'TF' :
        if TF == None :
            exit(55)
        if name in TF :
            exit(52)
        TF[name] = {}
        TF[name]['type'] = None
        TF[name]['value'] = None
    

# priradi hodnotu do premenej
def move(var, symb) :
    frame = var[:2]
    var_name = var[3:]

    type = None
    value = None

    type, value = get_value(symb)

    if frame == 'GF' :
        if var_name not in GF :
            exit(54)
        GF[var_name]['type'] = type
        GF[var_name]['value'] = value

    elif frame == 'LF' :
        if len(LF) == 0 :
            exit(55)
        if var_name not in LF[TOP] :
            exit(54)
        LF[TOP][var_name]['type'] = type
        LF[TOP][var_name]['value'] = value

    elif frame == 'TF' :
        if TF == None :
            exit(55)
        if var_name not in TF :
            exit(54)
        TF[var_name]['type'] = type
        TF[var_name]['value'] = value


# funckia ktora ziska 'type' a 'value'
def get_value(symb) :
    type = symb[0]
    value = None

    if type == 'string' :
        if symb[1] != '' :
            value = decode_escape_char(symb[1])
        else : 
            value = ''

    elif type == 'int' :
        value = int(symb[1])

    elif type == 'bool' :
        value = symb[1]
    
    elif type == 'float' :
        try :
            value = float.fromhex(symb[1])
        except :
            value = symb[1]

    elif type == 'var' :
        type, value = get_value_var(symb[1])
    

    if type == None :
        exit(56)
    
    return type, value 


# funkcia ktora ziska 'type' a 'value' z premennej
def get_value_var(var) :
    type = None
    value = None

    frame = var[:2]
    var_name = var[3:]

    if frame == 'GF' :
        if var_name not in GF :
            exit(54)
        type = GF[var_name]['type']
        value = GF[var_name]['value']
    
    elif frame == 'LF' :
        if len(LF) == 0 :
            exit(55)
        if var_name not in LF[TOP] :
            exit(54)
        type = LF[TOP][var_name]['type']
        value = LF[TOP][var_name]['value']

    elif frame == 'TF' :
        if TF == None :
            exit(55)
        if var_name not in TF :
            exit(54)
        type = TF[var_name]['type']
        value = TF[var_name]['value']


    return type, value

# Funkcia ktora dekoduje escape sekvencie v stringu
def decode_escape_char(string) :
    value = ''
    cnt = 0

    while cnt < len(string) :
        if string[cnt] == '\\' :
            tmp = string[cnt+1] + string[cnt+2] + string[cnt+3]
            tmp = chr(int(tmp))
            value = value + tmp
            cnt += 3
        else :
            value = value + string[cnt]
        cnt += 1

    return value


# Funkcia na vypis hodnoty na standartni vystup
def write(symb) :
    type, value = get_value(symb)

    if type == 'int' :
        print(value, end='')

    elif type == 'string' :
        print(value, end='')

    elif type == 'bool' :
        print(value, end='')

    elif type == 'float' :
        print(float.hex(value), end='')

    elif type == 'nil' :
        print('',end='')
 

# Funkcia presunie docasny ramec na zasobnik ramcov
def pushframe() :
    global TF

    if TF == None :
        exit(55)
    
    else :
        LF.append(TF)
        TF = None

    
# Funkcia presunie aktualny ramec do docasneho 
def popframe() :
    global TF

    if len(LF) == 0 :
        exit(55)
    
    TF = LF.pop()


# Funkcia na aritmeticke instrukcie [ADD, SUB, MUL, IDIV, DIV]
def arithmetics_instructions(instruction, var, symb1, symb2) :
    type1, value1 = get_value(symb1)
    type2, value2 = get_value(symb2)
    
    if type1 != type2 :
        exit(53)

    if type1 not in ['int' , 'float'] or type2 not in ['int', 'float'] :
        exit(53)

    if instruction == 'ADD' :
        if type1 == 'int' :
            move(var[1], [type1, int(value1 + value2)])
        else :
            move(var[1], [type1, value1 + value2])
            
    elif instruction == 'SUB' :
        if type1 == 'int' :
            move(var[1], [type1, int(value1 - value2)])
        else :
            move(var[1], [type1, value1 - value2])

    elif instruction == 'MUL' :
        if type1 == 'int' :
            move(var[1], [type1, int(value1 * value2)])
        else :
            move(var[1], [type1, value1 * value2])

    elif instruction == 'IDIV' :
        if value2 == 0 :
            exit(57)
        if type1 == 'int' :
            move(var[1], [type1, int(value1 // value2)])
        else :
            move(var[1], [type1, value1 // value2])

    elif instruction == 'DIV' :
        if type1 != 'float' :
            exit(53)
        if value2 == 0.0 :
            exit(57)
        move(var[1], [type1, value1 / value2])



# Funkcia na relacne instrukcie [LT, GT, EQ]
def relational_instructions(instruction, var, symb1, symb2) :
    type1, value1 = get_value(symb1)
    type2, value2 = get_value(symb2)

    if instruction == 'LT' :
        if type1 != type2 or type1 == 'nil' or type2 == 'nil' :
            exit(53)
        else :
            if value1 < value2 :
                move(var[1], ['bool', 'true'])
            else :
                move(var[1], ['bool', 'false'])

    elif instruction == 'GT' :
        if type1 != type2 or type1 == 'nil' or type2 == 'nil' :
            exit(53)
        else :
            if value1 > value2 :
                move(var[1], ['bool', 'true'])
            else :
                move(var[1], ['bool', 'false'])

    elif instruction == 'EQ' :
        if type1 == 'nil' or type2 == 'nil' :
            if value1 == value2 :                       
                move(var[1], ['bool', 'true'])          # nil == nil
            else :
                move(var[1], ['bool', 'false'])         # nil == nieco  || nieco == nil 

        elif type1 == type2 :
            if value1 == value2 :
                move(var[1], ['bool', 'true'])
            else :
                move(var[1], ['bool', 'false'])

        else :
            exit(53)


# Funkcia na logicke instrukcie [AND, OR, NOT]
def logical_instructions(instruction, var, symb1, symb2) :
    type1, value1 = get_value(symb1)
    
    if instruction != 'NOT' :                   # instrukcia NOT ma iba symb1
        type2, value2 = get_value(symb2)

    if instruction == 'AND' :
        if type1 != 'bool' or type2 != 'bool' :
            exit(53)
        else :
            if value1 == 'true' and value2 == 'true' :
                move(var[1], ['bool', 'true'])
            else :
                move(var[1], ['bool', 'false'])

    elif instruction == 'OR' :
        if type1 != 'bool' or type2 != 'bool' :
            exit(53)
        else :
            if value1 == 'true' or value2 == 'true' :
                move(var[1], ['bool', 'true'])
            else :
                move(var[1], ['bool', 'false'])

    elif instruction == 'NOT' :
        if type1 != 'bool' :
            exit(53)
        else:
            if value1 == 'false' :
                move(var[1], ['bool', 'true'])
            else :
                move(var[1], ['bool', 'false'])
    


# Funkcia vlozi hodnotu na vrchol data_stack
def pushs(symb, data_stack) :
    type1, value1 = get_value(symb)
    
    data_stack.append([type1, value1])


# Funkcia vyberie hodnotu z vrcholu data_stack
def pops(var, data_stack) :
    if len(data_stack) == 0 :
        exit(56)
    else :
        move(var[1], data_stack.pop())



# Funkcia na prevod celeho cisla na znak
def int2char(var, symb) :
    type1, value1 = get_value(symb)
    
    if type1 != 'int' :
        exit(53)
    
    is_var_defined(var[1])
    try :
        value1 = chr(value1)
        move(var[1], ['string', value1])
    except :
        exit(58)
    

# Funkcia na ziskanie ordinalnej hodnoty znaku
def stri2int(var, symb1, symb2) :
    type1, value1 = get_value(symb1)
    type2, value2 = get_value(symb2)

    if type1 != 'string' or type2 != 'int' :
        exit(53)
    
    else :
        if value2 < 0 :
           exit(58)

        is_var_defined(var[1])
        try :
          ord_value = ord(value1[value2])
          move(var[1], ['int', ord_value])
        except :
            exit(58)


# Funkcia na konkatenaciu dvoch retazcov
def concat(var, symb1, symb2) :
    type1, value1 = get_value(symb1)
    type2, value2 = get_value(symb2)

    if type1 != 'string' or type2 != 'string' :
        exit(53)

    else :
        move(var[1], ['string', value1 + value2])


# Funkcia na ziskanie dlzky retazca
def strlen(var, symb) :
    type1, value1 = get_value(symb)

    if type1 != 'string' :
        exit(53)
    
    else :
        move(var[1], ['int', len(value1)])


# Funkcia na vrateniu znaku v retazci
def getchar(var, symb1, symb2) :
    type1, value1 = get_value(symb1)
    type2, value2 = get_value(symb2)

    if type1 != 'string' or type2 != 'int' :
        exit(53)

    if value2 < 0 :
        exit(58)

    is_var_defined(var[1])
    try :
        char_value = value1[value2]
        move(var[1], ['string', char_value])
    except:
        exit(58)


# Funkcia na zmenenie znaku v retazci 
def setchar(var, symb1, symb2) :
    type_var, value_var = get_value(var)
    type1, value1 = get_value(symb1)
    type2, value2 = get_value(symb2)

    if type_var != 'string' or type1 != 'int' or type2 != 'string' :
        exit(53)
    
    if value1 < 0 :
        exit(58)
    
    if value2 == '' :
        exit(58)

    is_var_defined(var[1])
    try :
        finall_string = list(value_var)
        finall_string[value1] = value2[0]
        finall_string = ''.join(finall_string)
        move(var[1], ['string', finall_string])
    except:
        exit(58)


# Funkcia na zistenie typu daneho symbolu 
def type_instruc(var, symb) :
    if symb[0] in ['int', 'bool', 'string', 'nil'] :
        move(var[1], ['string', symb[0]])
    
    elif symb[0] == 'var' :
        type1, value1 = get_value_var(symb[1])
        if type1 == None :
            move(var[1], ['string', ''])
        else:
            move(var[1], ['string', type1])
    

# Funkcia na ukoncenie interpretu s navratovym kodom
def exit_instruc(symb) :
    type1, value1 = get_value(symb)

    if type1 != 'int' :
        exit(53)
    if value1 < 0 or value1 > 49 :
        exit(57)
    
    exit(value1)


# Funkcia vykona nepodmieneny skok na navestie
def jump(label, dict_labels) :
    if label[1] in dict_labels :
        order = labels[label[1]]
        return order
    
    else :
        exit(52)

# Funkcia zisti ci je label definovany
def is_label_defined(label, dict_labels) :
    if label[1] not in dict_labels :
        exit(52)


# Funkcia vykona podmieneny skok na navestie pri rovnosti
def jumpifeq(symb1, symb2) :
    type1, value1 = get_value(symb1)
    type2, value2 = get_value(symb2)

    if type1 != type2 and type1 != 'nil' and type2 != 'nil' :
        exit(53)
    
    else :
        if value1 == value2 :
            return True
        else :
            return False

# Funkia vykona podmieneny skok na navestie pri nerovnosti
def jumpifneq(symb1, symb2) :
    type1, value1 = get_value(symb1)
    type2, value2 = get_value(symb2)

    if type1 != type2 and type1 != 'nil' and type2 != 'nil' :
        exit(53)

    else :
        if value1 != value2 :
            return True
        else :
            return False


# Funkcia nacita hodnotu zo stdin
def read(var, type) :
    global inputFile
    
    if inputFile != sys.stdin :
        try :
            readed_value = inputFile.readline()
            readed_value = readed_value.split('\n')[0]
        except :
            move(var[1], ['nil', 'nil'])
            return
            
    else :
        try :
            readed_value = input()
            readed_value = readed_value.split('\n')[0]
        except :
            move(var[1], ['nil', 'nil'])
            return

    if type[1] == 'int' :
        try :
            move(var[1], ['int', int(readed_value)])
        except:
            move(var[1],['nil', 'nil'])

    elif type[1] == 'string' :
        move(var[1], ['string', readed_value])

    elif type[1] == 'bool' :
        if readed_value.lower() == 'true' :
            move(var[1], ['bool', 'true'])
        else :
            move(var[1], ['bool', 'false'])
    
    elif type[1] == 'float' :
        try :
            readed_value = float.fromhex(readed_value)
            move(var[1], ['float', readed_value])
        except:
            move(var[1], ['nil', 'nil'])



# Funkcia zisti ci je premenna definovana 
def is_var_defined(var) :
    frame = var[:2]
    var_name = var[3:]

    if frame == 'GF' :
        if var_name not in GF :
            exit(54)

    elif frame == 'LF' :
        if len(LF) == 0 :
            exit(55)
        if var_name not in LF[TOP] :
            exit(54)

    elif frame == 'TF' :
        if TF == None :
            exit(55)
        if var_name not in TF :
            exit(54)


# Funkcia na prevod celociselnej hodnoty na desatinu
def int2float(var, symb) :
    type1, value1 = get_value(symb)

    if type1 != 'int' :
        exit(53)
    
    is_var_defined(var[1])
    try :
        value1 = float(value1)
        move(var[1], ['float', value1])
    except :
        exit(57)
    


# Funkcia na prevod desatinej hodnoty na celociselnu
def float2int(var, symb) :
    type1, value1 = get_value(symb)

    if type1 != 'float' :
        exit(53)

    is_var_defined(var[1])
    try :
        value1 = int(value1)
        move(var[1], ['int', value1])
    except :
        exit(57)


# Funkcia na aritmeticke instrukcie so zasobikom [ADDS, SUBS, MULS, IDIVS, DIVS,]
def arithmetics_instrucktions_stack(instruction, stack) :
    type2, value2 = get_value_stack(stack)
    type1, value1 = get_value_stack(stack)

    if type1 != type2 :
        exit(53)

    if type1 not in ['int', 'float'] :
        exit(53)  

    if instruction == 'ADDS' :
        stack.append([type1, value1 + value2]) 

    elif instruction == 'SUBS' :
        stack.append([type1, value1 - value2])
    
    elif instruction == 'MULS' :
        stack.append([type1, value1 * value2])

    elif instruction == 'IDIVS' :
        if value2 == 0 :
            exit(57)
        else :
            stack.append([type1, value1 // value2])
    
    elif instruction == 'DIVS' :
        if type1 != 'float' :
            exit(53)
        if value2 == 0 :
            exit(57)
        else :
            stack.append([type1, value1 / value2])


# Funkcia na relacne instrukcie so zasobnikom [LTS, GTS, EQS] 
def relational_instructions_stack(instruction, stack) :
    type2, value2 = get_value_stack(stack)
    type1, value1 = get_value_stack(stack)

    if instruction == 'LTS' :
        if type1 != type2 or type1 == 'nil' or type2 == 'nil' :
            exit(53)
        if value1 < value2 :
            stack.append(['bool', 'true'])
        else :
            stack.append(['bool', 'false'])

    elif instruction == 'GTS' :
        if type1 != type2 or type1 == 'nil' or type2 == 'nil' :
            exit(53)
        if value1 > value2 :
            stack.append(['bool', 'true'])
        else :
            stack.append(['bool', 'false'])

    elif instruction == 'EQS' :
        if type1 == 'nil' or type2 == 'nil' :
            if value1 == value2 :
                stack.append(['bool', 'true'])
            else :
                stack.append(['bool', 'false'])
        elif type1 == type2 :
            if value1 == value2 :
                stack.append(['bool', 'true'])
            else :
                stack.append(['bool', 'false'])
        else :
            exit(53)


# Funkcia na logicke instrukcie so zasobnikom [ANDS, ORS, NOTS]
def logical_instructions_stack(instruction, stack) :
    type2, value2 = get_value_stack(stack)
    
    if instruction != 'NOTS' :
        type1, value1 = get_value_stack(stack)
        if type1 != 'bool' or type2 != 'bool' :
            exit(53)
    
    elif type2 != 'bool':
        exit(53)    
    
    if instruction == 'ANDS' :
        if value1 == 'true' and value2 == 'true' :
            stack.append(['bool', 'true'])
        else :
            stack.append(['bool', 'false'])
    
    elif instruction == 'ORS' :
        if value1 == 'true' or value2 == 'true' :
            stack.append(['bool', 'true'])
        else :
            stack.append(['bool', 'false'])
    
    elif instruction == 'NOTS' :
        if value2 == 'true' :
            stack.append(['bool', 'false'])
        else :
            stack.append(['bool', 'true'])


# Funkcia na prevod celeho cisla na znak (zo zasobnika)
def int2chars(stack) :
    type1, value1 = get_value_stack(stack)
    
    if type1 != 'int' :
        exit(53)
    
    try :
        value1 = chr(value1)
        stack.append(['string', value1])
    except :
        exit(58)


# Funkcia na prevod znaku na cele cislo (zo zasobnika)
def stri2ints(stack) :
    type2, value2 = get_value_stack(stack)
    type1, value1 = get_value_stack(stack)

    if type1 != 'string' or type2 != 'int' :
        exit(53)
    
    if value2 < 0 :
        exit(58)

    try :
          ord_value = ord(value1[value2])
          stack.append(['int', ord_value])
    except :
        exit(58)


# Funkcia na prevod celociselnej hodnoty na desatinu (zo zasobnika)
def int2floats(stack) :
    type1, value1 = get_value_stack(stack)

    if type1 != 'int' :
        exit(53)
    
    try :
        value1 = float(value1)
        stack.append(['float', value1])
    except :
        exit(57)


# Funkcia na prevod desatineho cisla na cele (zo zasobnikom)
def float2ints(stack) :
    type1, value1 = get_value_stack(stack)

    if type1 != 'float' :
        exit(53)

    try :
        value1 = int(value1)
    except :
        exit(57)
    

# Funkcia na podmienenz skok pri rovnosti (zo zasobnika)
def jumpifeqs(stack) :
    type2, value2 = get_value_stack(stack)
    type1, value1 = get_value_stack(stack)

    if type1 != type2 and type1 != 'nil' and type2 != 'nil' :
        exit(53)
    
    else :
        if value1 == value2 :
            return True
        else :
            return False


# Funkcia na podmieneny skok pri nerovnosti (zo zasobnika)
def jumpifneqs(stack) :
    type2, value2 = get_value_stack(stack)
    type1, value1 = get_value_stack(stack)

    if type1 != type2 and type1 != 'nil' and type2 != 'nil' :
        exit(53)

    else :
        if value1 != value2 :
            return True
        else :
            return False


# Funkcia na ziskanie hodnoty z datoveho zasobnika
def get_value_stack(stack) :
    if len(stack) == 0 :
        exit(56)

    symb = stack.pop()

    type1 = symb[0]
    value1 = symb[1]

    return type1, value1



def print_frames(GF, LF, TF) :
    print()
    print('-------- GLOBAL FRAME --------')
    if GF == None :
        print('None')
    else :
        for key in GF :
            print(key, ':', GF[key]['value'], '[', GF[key]['type'], ']')

    print('-------- LOCAL FRAME --------')
    if len(LF) == 0 :
        print('None')
    else :
        for key in LF[TOP] :
            print(key, ':', LF[TOP][key]['value'], '[', LF[TOP][key]['type'], ']')

    print('-------- TEMPORARY FRAME --------')
    if TF == None :
        print('None')
    else :
        for key in TF :
            print(key, ':', TF[key]['value'], '[', TF[key]['type'], ']')




# # #   Main   # # #
inst_cnt = 0
instruc_list = []           # list pripravenych instrukcii
order = 0                   # cislo prevadzanej instrukcie
labels = {}                 # dict pre labels 
GF = {}                     # globalny frame
LF = []                     # lokalny frame
TF = None                   # docasny frame
TOP = -1                    # vrchol zasobnika           
data_stack = []    
call_stack = []


check_script_param()

# otvorenie suboru na citanie 
if inputFile != sys.stdin :
    inputFile = open(inputFile, 'r')


parse_xml(sourceFile)


# kontrola instrukcii  
while inst_cnt < len(instructions) :
    instruc_list.append(check_instruction(instructions[inst_cnt]))

    # ulozenie orderu daneho labelu
    if instruc_list[inst_cnt][0] == 'LABEL' :
        label_name = instruc_list[inst_cnt][1][1]
        
        # kontrol ci dany label uz neexistuje
        if label_name in labels :
            exit(52)
        else :
            labels[label_name] = inst_cnt

    inst_cnt += 1


# interpretacia kodu 
while order < len(instruc_list) :
    #print(instruc_list[order])
    if instruc_list[order][0] == 'MOVE' :
        move(instruc_list[order][1][1], instruc_list[order][2])

    elif instruc_list[order][0] == 'CREATEFRAME' :
        TF = {}

    elif instruc_list[order][0] == 'PUSHFRAME' :
        pushframe()

    elif instruc_list[order][0] == 'POPFRAME' :
        popframe()

    elif instruc_list[order][0] == 'DEFVAR' :
        defvar(instruc_list[order][1][1])

    elif instruc_list[order][0] == 'CALL' :
        call_stack.append(order)
        order = jump(instruc_list[order][1], labels)

    elif instruc_list[order][0] == 'RETURN' :
        if len(call_stack) == 0 :
            exit(56)
        order = call_stack.pop()

    elif instruc_list[order][0] == 'PUSHS' :
        pushs(instruc_list[order][1], data_stack)

    elif instruc_list[order][0] == 'POPS' :
        pops(instruc_list[order][1], data_stack)

    elif instruc_list[order][0] == 'CLEARS' :
        data_stack = []

    elif instruc_list[order][0] in ['ADD', 'SUB', 'MUL', 'IDIV', 'DIV'] :
        arithmetics_instructions(instruc_list[order][0], instruc_list[order][1], instruc_list[order][2], instruc_list[order][3])

    elif instruc_list[order][0] in ['ADDS', 'SUBS', 'MULS', 'IDIVS', 'DIVS'] :
        arithmetics_instrucktions_stack(instruc_list[order][0], data_stack)

    elif instruc_list[order][0] in ['LT', 'GT', 'EQ'] :
        relational_instructions(instruc_list[order][0], instruc_list[order][1], instruc_list[order][2], instruc_list[order][3])
    
    elif instruc_list[order][0] in ['LTS', 'GTS', 'EQS'] :
        relational_instructions_stack(instruc_list[order][0], data_stack)

    elif instruc_list[order][0] in ['AND', 'OR', 'NOT'] :
        if instruc_list[order][0] == 'NOT' :
            logical_instructions(instruc_list[order][0], instruc_list[order][1], instruc_list[order][2], None)
        else :
            logical_instructions(instruc_list[order][0], instruc_list[order][1], instruc_list[order][2], instruc_list[order][3])

    elif instruc_list[order][0] in ['ANDS', 'ORS', 'NOTS'] :
        logical_instructions_stack(instruc_list[order][0], data_stack)

    elif instruc_list[order][0] == 'INT2CHAR' :
        int2char(instruc_list[order][1], instruc_list[order][2])

    elif instruc_list[order][0] == 'INT2CHARS' :
        int2chars(data_stack)

    elif instruc_list[order][0] == 'STRI2INT' :
        stri2int(instruc_list[order][1], instruc_list[order][2], instruc_list[order][3])

    elif instruc_list[order][0] == 'STRI2INTS' :
        stri2ints(data_stack)

    elif instruc_list[order][0] == 'INT2FLOAT' :
        int2float(instruc_list[order][1], instruc_list[order][2])

    elif instruc_list[order][0] == 'INT2FLOATS' :
        int2floats(data_stack)

    elif instruc_list[order][0] == 'FLOAT2INT' :
        float2int(instruc_list[order][1], instruc_list[order][2])

    elif instruc_list[order][0] == 'FLOAT2INTS' :
        float2ints(data_stack)

    elif instruc_list[order][0] == 'READ' :
        read(instruc_list[order][1], instruc_list[order][2])

    elif instruc_list[order][0] == 'WRITE' :
        write(instruc_list[order][1])

    elif instruc_list[order][0] == 'CONCAT' :
        concat(instruc_list[order][1], instruc_list[order][2], instruc_list[order][3])

    elif instruc_list[order][0] == 'STRLEN' :
        strlen(instruc_list[order][1], instruc_list[order][2])

    elif instruc_list[order][0] == 'GETCHAR' :
        getchar(instruc_list[order][1], instruc_list[order][2], instruc_list[order][3])

    elif instruc_list[order][0] == 'SETCHAR' :
        setchar(instruc_list[order][1], instruc_list[order][2], instruc_list[order][3])

    elif instruc_list[order][0] == 'TYPE' :
        type_instruc(instruc_list[order][1], instruc_list[order][2])

    elif instruc_list[order][0] == 'LABEL' :
        pass

    elif instruc_list[order][0] == 'JUMP' :
        order = jump(instruc_list[order][1], labels)

    elif instruc_list[order][0] in ['JUMPIFEQ', 'JUMPIFEQS'] :
        if instruc_list[order][0] == 'JUMPIFEQ' :
            equal = jumpifeq(instruc_list[order][2], instruc_list[order][3])
        else :
            equal = jumpifeqs(data_stack)
        is_label_defined(instruc_list[order][1], labels)
        if equal :
            order = jump(instruc_list[order][1], labels)

    elif instruc_list[order][0] in ['JUMPIFNEQ', 'JUMPIFNEQS'] :
        if instruc_list[order][0] == 'JUMPIFNEQ' :
            notequal = jumpifneq(instruc_list[order][2], instruc_list[order][3])
        else :
            notequal = jumpifneqs(data_stack)
        is_label_defined(instruc_list[order][1], labels)
        if notequal == True :
            order = jump(instruc_list[order][1], labels)

    elif instruc_list[order][0] == 'EXIT' :
        exit_instruc(instruc_list[order][1])

    elif instruc_list[order][0] == 'DPRINT' :
        pass

    elif instruc_list[order][0] == 'BREAK' :
        pass

    order += 1


#print_frames(GF, LF, TF)
#print()