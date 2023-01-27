<?php
/************************
*
*   Projekt- IPPcode21
*   Začiatok projektu: 19.2.2021
*   Autor: Ján Homola
*  
*************************/


// Inicializacia exit hodnot 
const parameter_err = 10;
const input_file_err = 11;
const output_file_err = 12;
const header_err = 21;
const code_err = 22;
const lex_syn_err = 23;

$instruction_counter = 0;

// Otvorenie suboru pre citanie 
$stdin = fopen('php://stdin', 'r');
$stdout = fopen('php://stdout', 'w');


$instructions = array(
    "MOVE" => 0,
    "CREATEFRAME" => 1,
    "PUSHFRAME" => 2,
    "POPFRAME" => 3,
    "DEFVAR" => 4,
    "CALL" => 5,
    "RETURN" => 6,
    "PUSHS" => 7,
    "POPS" => 8,
    "ADD" => 9,
    "SUB" => 10,
    "MUL" => 11,
    "IDIV" => 12,
    "LT" => 13,
    "GT" => 14,
    "EQ" => 15,
    "AND" => 16,
    "OR" => 17,
    "NOT" => 18,
    "INT2CHAR" => 19,
    "STRI2INT" => 20,
    "READ" => 21,
    "WRITE" => 22,
    "CONCAT" => 23,
    "STRLEN" => 24,
    "GETCHAR" => 25,
    "SETCHAR" => 26,
    "TYPE" => 27,
    "LABEL" => 28,
    "JUMP" => 29,
    "JUMPIFEQ" => 30,
    "JUMPIFNOQ" => 31,
    "EXIT" => 32,
    "DPRINT" => 33,
    "BREAK" => 34
);

// kontrolovanie argumentov 
if ($argc == 2) 
{
    if ($argv[1] == "--help" or $argv[1] == "-h")
    {
        printf("Skript skontroluje zdrojovy kod v jazyku IPPcode21 \n");
        printf("Kontroluje sa lexikalna a syntakticka spravnost kodu \n");
        exit(0);
    }
    else
        exit(parameter_err);
}


// Vytvorenie DOM document
$DOM_doc = new DOMDocument("1.0", "UTF-8");
$DOM_doc->formatOutput = true;
$DOM_doc->preserveWhiteSpace = false;

$program_xml = $DOM_doc->createElement('program');
$program_xml->setAttribute('language', 'IPPcode21');

$DOM_doc->appendChild($program_xml);
$xml_instruction;

// Osetrenie hlavicky osobytne
$sentence = get_sentence();
check_number_of_operand($sentence, 0);
if (strtoupper($sentence[0]) != ".IPPCODE21")
    exit(header_err);

// Kontrola syntaxe do konca suboru 
while ($sentence[0] != "EOF")
{
    $sentence = get_sentence();

    
    // Instrukcie su "case insensitive"
    $instruction = strtoupper($sentence[0]); 
    
    $instruction_counter++;

    switch ($instruction) 
    {
        // Instrukcie s 0 operandov
        case "CREATEFRAME" :
        case "PUSHFRAME" :
        case "POPFRAME" :
        case "RETURN" :
        case "BREAK" :

            check_number_of_operand($sentence, 0);
            generate_xml_instruction($instruction_counter, $instruction);
            break;
        
        
        // Instrukcia s 1 operandom <symb>
        case "PUSHS" :
        case "WRITE" :
        case "EXIT" :
        case "DPRINT" :

            check_number_of_operand($sentence, 1);
            generate_xml_instruction($instruction_counter, $instruction);

            $arg_type = check_symb($sentence[1]);
            if ($arg_type == "var")
                generate_xml_arg("arg1", $sentence[1], $arg_type);
            else
            {
                $arg_value = explode("@",$sentence[1],2);
                generate_xml_arg("arg1",$arg_value[1],$arg_type);
            }    
            break;


        // Instrukcia s 1 operandom <label>
        case "CALL" :
        case "LABEL" :
        case "JUMP" :

            check_number_of_operand($sentence, 1);
            generate_xml_instruction($instruction_counter, $instruction);

            // Kontrola spravnosti navesti
            check_alpha_num_spec_char($sentence[1]);

            generate_xml_arg("arg1", $sentence[1], "label");
            break;
        

        // Instrukcia s 1 operandom <var>
        case "DEFVAR" :
        case "POPS" :    

            check_number_of_operand($sentence, 1);
            generate_xml_instruction($instruction_counter, $instruction);
            
            check_var($sentence[1]);
            generate_xml_arg("arg1", $sentence[1], "var");
            break;


        // Instrukcia s 2 operandami <var>  <symb>
        case "MOVE" :
        case "INT2CHAR" :
        case "STRLEN" :
        case "TYPE" :

            check_number_of_operand($sentence, 2);
            generate_xml_instruction($instruction_counter, $instruction);

            check_var($sentence[1]);
            generate_xml_arg("arg1", $sentence[1], "var");

            $arg_type = check_symb($sentence[2]);
            if ($arg_type == "var")
                generate_xml_arg("arg2", $sentence[2], $arg_type);
            else
            {
                $arg_value = explode("@",$sentence[2],2);
                generate_xml_arg("arg2",$arg_value[1],$arg_type);
            }    
            break;


        // Instrukcia s 2 operandami <var> a <type>
        case "READ" :

            check_number_of_operand($sentence, 2);
            generate_xml_instruction($instruction_counter, $instruction);

            check_var($sentence[1]);
            generate_xml_arg("arg1", $sentence[1], "var");

            check_type($sentence[2]);
            generate_xml_arg("arg2", $sentence[2], "type");
            break;


        // Instrukcia s 3 operandami <var> <symb1> <symb2>
        case "ADD" :
        case "SUB" :
        case "MUL" :
        case "IDIV" :
        case "LT" :
        case "GT" :
        case "EQ" :
        case "AND" :
        case "OR" :
        case "NOT" :
        case "STRI2INT" :
        case "CONCAT" :
        case "GETCHAR" :
        case "SETCHAR" :

            check_number_of_operand($sentence, 3);
            generate_xml_instruction($instruction_counter, $instruction);

            // kontrola <var>
            check_var($sentence[1]);           
            generate_xml_arg("arg1", $sentence[1], "var");

            // kontrola <symb1>
            $arg_type = check_symb($sentence[2]);
            if ($arg_type == "var")
                generate_xml_arg("arg2", $sentence[2], $arg_type);
            else
            {
                $arg_value = explode("@",$sentence[2],2);
                generate_xml_arg("arg2",$arg_value[1],$arg_type);
            }

            // kontrola <symb2>
            $arg_type = check_symb($sentence[3]);
            if ($arg_type == "var")
                generate_xml_arg("arg3", $sentence[3], $arg_type);
            else
            {
                $arg_value = explode("@",$sentence[3],2);
                generate_xml_arg("arg3",$arg_value[1],$arg_type);
            } 
            break;
        


        // Instrukcia s 3 operandami <label> <symb1> <symb2>
        case "JUMPIFEQ" :
        case "JUMPIFNEQ" :

            check_number_of_operand($sentence, 3);
            generate_xml_instruction($instruction_counter, $instruction);

            // kontrola <label>
            check_alpha_num_spec_char($sentence[1]);
            generate_xml_arg("arg1", $sentence[1], "label");
            
            // kontrola <symb1>
            $arg_type = check_symb($sentence[2]);
            if ($arg_type == "var")
                generate_xml_arg("arg2", $sentence[2], $arg_type);
            else
            {
                $arg_value = explode("@",$sentence[2],2);
                generate_xml_arg("arg2",$arg_value[1],$arg_type);
            }

            // kontrola <symb2>
            $arg_type = check_symb($sentence[3]);
            if ($arg_type == "var")
                generate_xml_arg("arg3", $sentence[3], $arg_type);
            else
            {
                $arg_value = explode("@",$sentence[3],2);
                generate_xml_arg("arg3",$arg_value[1],$arg_type);
            } 
            break;
          
            

        // Koniec suboru
        case "EOF" :
            break;

        default :
            exit(code_err);
    }    
}


echo $DOM_doc->saveXML();

exit(0);

// Deklaracia funkcii 

/**
 *  Funkcia odstrani komentare a znak konca riadku
 *  vriacia jeden riadok zo STDIN 
 */
function get_sentence()
{
    global $stdin;
    $sentence = array();

    while(true) 
    {
        $sentence = fgets($stdin);

        if ($sentence == false)
        {
            $sentence[0] = "EOF";
            return $sentence;
        }

        // Ak tam je komentar alebo novy riadok tak preskoci tento riadok
        if ($sentence[0] == "#" or $sentence[0] == "\n" or $sentence[1] == "\n")
            continue;
            

        $sentence = explode("#",$sentence)[0];      // vymaze komenty
        $sentence = explode(" ",$sentence);
    
        $sentence = str_replace("\r", "", $sentence);
        $sentence = str_replace("\n", "", $sentence);

        //$sentence = array_diff($sentence, array("\t", ""));
        
        // odstranenie prazdnych hodnot z pola a preindexovanie 
        $sentence = array_values(array_filter($sentence));

        return $sentence;
    }
}


/**
 *  Funkcia na kontrolu poctu operandov
 *  pokial chyba => exit  
 */ 
function check_number_of_operand($sentence, $reqired_count)
{
    $count = count($sentence) - 1;              // prva je instrukcia 
    if ($count != $reqired_count)
    {
        exit(lex_syn_err);
    }
}

/**
 *  Funkcia na kontrolu operandu <type>
 *  pokial chyba => exit
 */
function check_type($word)
{
    if ($word != "int" and $word != "string" and $word != "bool")
        exit(lex_syn_err);
}

/**
 *  Funkcia na kontrolu operandu <var>
 *  pokial chyba => exit
 */
function check_var($word)
{
    if (strpos($word, "@") !== false)
    {
        $word = explode("@", $word);

        if ($word[0] != "LF" and $word[0] != "TF" and $word[0] != "GF")
        {
            exit(lex_syn_err);
        }
        else
            check_alpha_num_spec_char($word[1]);

    }
    else
        exit(lex_syn_err);
}

/**
 *  Funkcia na kontrolu operandu <symb>
 *  pokial chyba => exit 
 */
function check_symb($word)
{
    $temp_word = $word; 
    if (strpos($word, "@") !== false)
    {
        $word = explode("@", $word,2);

        // kontrola ci sa nejedna o premennu 
        if ($word[0] != "bool" and $word[0] != "nil" and $word[0] != "int" and $word[0] != "string")
        {
            check_var($temp_word);
            return "var";
        }
        else
        {
            // kontrola konstanty bool
            if ($word[0] == "bool")
            {
                if ($word[1] != "true" and $word[1] != "false")
                {
                    exit(lex_syn_err);
                }
                else
                    return "bool";
            }

            // kontrola konstanty nil
            elseif ($word[0] == "nil")
            {
                if ($word[1] != "nil")
                    exit(lex_syn_err);
                else
                    return "nil";
            }
            // kontrola konstanty int 
            elseif ($word[0] == "int")
            {
                foreach (str_split($word[1]) as $index=>$char)
                {
                    if (($char != "+" and $char != "-") or $index != 0 or strlen($word[1]) == 1)
                    {
                        if (!($char >= "0" and $char <= "9"))
                            exit(lex_syn_err);
                        else
                            return "int";
                    }
                } 
            }
            // kontrola konstany string
            elseif ($word[0] == "string")
            {
                $num_counter = 0;
                $back_slash = false;
                $len_word = strlen($word[1]);
                if ($word[1] == "")                 // Kontrola ci sa nejedna o prazdny string
                    return "string";

                foreach (str_split($word[1]) as $index=>$char)
                {
                    if (!preg_match('/[\\\\0-9a-zA-Z_\-$&%*!?<>,;\.\)\(\+\=@ěščřžýáíéóúůďťňĎŇŤŠČŘŽÝÁÍÉÚŮα-ωΑ-ΩίϊΐόάέύϋΰήώΊΪΌΆΈΎΫΉΏ]/',$char))
                        exit(lex_syn_err);
                    if ($char == "\\")
                    {
                        $back_slash = true;
                        continue;
                    }
                    elseif ($back_slash == true and preg_match('/[0-9]/',$char))
                    {
                        $num_counter++;
                        if ($num_counter > 3)
                        {
                            $back_slash = false;
                            $num_counter = 0;
                            continue;
                            //exit(lex_syn_err);
                        }
                        if ($len_word == $index+1)
                        {
                            if ($num_counter != 3)
                                exit(lex_syn_err);
                        }
                        continue;
                    }
                    else
                    {
                        if ($back_slash == true)
                        {
                            if ($num_counter != 3)
                                exit(lex_syn_err);

                            $back_slash = false;
                            $num_counter = 0;
                        }
                    }

                }
                return "string";
            }
        }

    }
    else
        exit(lex_syn_err);
}


/**
 *  Funkcia na kontrolu alfa-numerickych znakov
 *  pokial chyba => exit 
 */
function check_alpha_num_spec_char($word)
{
    foreach (str_split($word) as $index=>$char)
    {
        if (
            !($char >= "a" and $char <= "z") and
            !($char >= "A" and $char <= "Z") and
            $char != "_" and $char != "-" and
            $char != "$" and $char != "&" and
            $char != "%" and $char != "*" and
            $char != "!" and $char != "?"     
        )
        {
            if (!($char >= "0" and $char <= "9" and $index != 0))
            {
                exit(lex_syn_err);
            }
        }    
    } 
}


/**
 *  Funkcia na generovanie konkretne instrukcie
 *  obsahuje typ instrukcie popripade jej hodnotu
 */
function generate_xml_arg($arg, $value, $arg_type)
{
    global $DOM_doc;
    global $xml_instruction;
    
    $xml_arg = $DOM_doc->createElement($arg, htmlspecialchars($value));
    $xml_arg->setAttribute("type", $arg_type);

    $xml_instruction->appendChild($xml_arg);
}

/**
 *  Funkcia generuje xml kod danej intrukcie
 *  ktora ma pociadlo o ktoru instrukciu v poradi ide 
 */
function generate_xml_instruction($counter, $name_of_instruction)
{
    global $DOM_doc;
    global $program_xml;
    global $xml_instruction;

    $xml_instruction = $DOM_doc->createElement("instruction");
    $xml_instruction->setAttribute("order", $counter);
    $xml_instruction->setAttribute("opcode",$name_of_instruction);

    $program_xml->appendChild($xml_instruction);
}

?>