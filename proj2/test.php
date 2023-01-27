<?php
/************************* 
* 
*   VUT FIT
*   Projekt - IPP - test
*   Zaciatok projektu : 12.4.2021
*   Autor: Ján Homola 
* 
*************************/


/* Deklaracia premennych */
$directory = "./";
$recursive = false;
$parse_script = "./parse.php";
$int_script = "./interpret.py";
$parse_only = false;
$int_only = false;
$jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";       
$jexamxml = "/mnt/c/Users/homol/Desktop/jexamxml/jexamxml.jar";     // DEBUG
$jexamcfg = "/pub/courses/ipp/jexamxml/options";            
$jexamcfg = "/mnt/c/Users/homol/Desktop/jexamxml/options";          // DEBUG



/* MAIN */
check_script_param($argc, $argv);

$files_to_test ;
if ($recursive == true)
    exec("find " . $directory, $files_to_test);
else
    exec("find " . $directory . " -maxdepth 1", $files_to_test);


$pass = 0;
$fail = 0;
$number_of_tests = 0;
$tmp_html;
$html_header;
$list_of_dirs = [];

// iterovanie cez testovacie subory
foreach ($files_to_test as $file)
{   
    if (preg_match("/\.src$/", $file))
    {
        $test_name = substr($file, 0, -4);

        $tmp_dir = implode(explode('/', $test_name, -1), '/');

        if (!in_array($tmp_dir, $list_of_dirs))
        {
            array_push($list_of_dirs, $tmp_dir);
            $html_header = true;
        }
        else
            $html_header = false;

        $file_src = $test_name . ".src";
        $file_in = $test_name . ".in";
        $file_out = $test_name . ".out";
        $file_rc = $test_name . ".rc";

        $number_of_tests++;

        if (!file_exists($file_in))
        {
            $tmp_file = fopen($file_in, "w");
            fclose($tmp_file);
        }
        if (!file_exists($file_out))
        {
            $tmp_file = fopen($file_out, "w");
            fclose($tmp_file);
        }
        if (!file_exists($file_rc))
        {
            $tmp_file = fopen($file_rc, "w");
            fwrite($tmp_file, "0");
            fclose($tmp_file);
        }


        if ($parse_only == false and $int_only == false)
        {
            exec("php7.4 " . $parse_script . " <" . $file_src . " >parse_out", $output, $return_value);

            if ($return_value == 0) 
            {
                exec("python3.8 " . $int_script . " --source=parse_out --input=" . $file_in . " >int_out", $output, $return_value);
            }
            if (!check_return_value($file_rc, $return_value))
            {
                print_html($number_of_tests, $test_name, $file_rc, $return_value, false);
                $fail++;
            }
            
            elseif ($return_value != 0)
            {
                print_html($number_of_tests, $test_name, $file_rc, $return_value, true);
                $pass++;
            }
            else
            {
                if (check_int_out($test_name, $file_out))
                    print_html($number_of_tests, $test_name, $file_rc, $return_value, true);
                else
                    print_html($number_of_tests, $test_name, $file_rc, $return_value, false);
                
                unlink("int_out");
            }
            unlink("parse_out");
        }
        elseif ($parse_only == true)
        {
            exec("php7.4 " . $parse_script . " <" . $file_src . " >parse_out", $output, $return_value);
            
            if (!check_return_value($file_rc, $return_value))
            {
                print_html($number_of_tests, $test_name, $file_rc, $return_value, false);
                $fail++;
            }
            elseif ($return_value != 0)
            {
                print_html($number_of_tests, $test_name, $file_rc, $return_value, true);
                $pass++;
            }
            else
            {
                if (check_parse_out($test_name, $file_out))
                    print_html($number_of_tests, $test_name, $file_rc, $return_value, true);
                else
                    print_html($number_of_tests, $test_name, $file_rc, $return_value, true);
            }
            unlink("parse_out");

        }
        elseif ($int_only == true)
        {
            exec("python3.8 " . $int_script . " --source=" . $file_src . " --input=" . $file_in. " >int_out",$output, $return_value);
            
            if (!check_return_value($file_rc, $return_value))
            {
                print_html($number_of_tests, $test_name, $file_rc, $return_value, false);
                $fail++;
            }
            
            elseif ($return_value != 0)
            {
                print_html($number_of_tests, $test_name, $file_rc, $return_value, true);
                $pass++;
            }
            else
            {
                if (check_int_out($test_name, $file_out))
                    print_html($number_of_tests, $test_name, $file_rc, $return_value, true);
                else
                    print_html($number_of_tests, $test_name, $file_rc, $return_value, false);
            }
            unlink("int_out");
        }
    }
}

$percent = $pass / $number_of_tests * 100;
$percent = intval($percent);

$html = '
<!DOCTYPE html>
<html>
<head>
<title>Test php (xhomol27)</title>
</head>
<style>
.tab1 {
    margin: 25px;
    padding: 8px;
    border: 3px solid #54565B;
    border-radius: 13px;
    background-color: #b1A296;
}  
.tab2 {
    margin: 25px;
    border: 1px solid #54565B;
    padding: 8px;
    border-collapse: collapse;
    width: 80%;
}  
.tab1 td{
    font-size: 130%;
    color: #54565B ;
}  
.mytd td {
    
    text-align: center;
}  
.ok td {
    text-align: center;
}
.ok {
    color: black;
    background-color: #479761;

}
.fail {
    color: black;
    background-color: #e27d60;

}
.fail td {
    text-align: center;
}
.header  {
    text-align-last: left;
    padding-left: 8px;
}

</style>
<body style="background-color: #F2F0D5;">


<table style="width: 25%;" class="tab1">
    <tr>
        <td>Celkový počet testov: ' . $number_of_tests . '</td>
    </tr>
    <tr>
        <td>Počet úspešných testov: ' . $pass . '</td>
    </tr>
    <tr>
        <td>Počet neúspešných testov: ' . $fail . '</td>
    </tr>
    <tr>
        <td style="font-size: 150%; color: #D95323;">Úspešnosť: ' . $percent .'  %</td>
    </tr>
</table>

<br>
<br>

' . $tmp_html .'

</body>
</html>';

echo $html;



/* Deklaracia funkcii */

// funkcia ktora skontruluje spravnost vstupnych parametrov programu 
function check_script_param($argc, $argv)
{
    global $directory;
    global $recursive;
    global $parse_script;
    global $int_script;
    global $parse_only;
    global $int_only;
    global $jexamxml;       
    global $jexamcfg;   

    if ($argc > 7)
    {
        fwrite(STDERR, "Prislis vela argumentov. \n");
        exit(10);
    }
    else 
    {
        foreach ($argv  as $key => $arg)
        {   
            if ($key == 0)                  // preskoci nazov suboru
                continue;

            if ($arg == "--help")
            {
                if ($argc == 2)
                {
                    printf("Skript ktory sluzi na testovanie subori parse a interpet \n");
                    exit(0);
                }
                else
                {
                    fwrite(STDERR, "--help sa nemoze kombinovat \n");
                    exit(10);
                }
            }
            elseif (strpos($arg, "--directory=") === 0)
            {   
                $tmp_dir = explode("--directory=", $arg)[1];
                if (file_exists($tmp_dir))
                    $directory = $tmp_dir;
                else
                {
                    fwrite(STDERR, "Dir neexistuje. \n");
                    exit(11);
                }
            }
            elseif ($arg == "--recursive")
            {
                $recursive = true;
            }
            elseif (strpos($arg, "--parse-script=") === 0)
            {
                $tmp_file = explode("--parse-script=", $arg)[1];
                if (file_exists($tmp_file))
                $parse_script = $tmp_file;
                else
                {
                    fwrite(STDERR, "File neexistuje. \n");
                    exit(11);
                } 
            }
            elseif (strpos($arg, "--int-script=") === 0)
            {
                $tmp_file = explode("--int-script=", $arg)[1];
                if (file_exists($tmp_file))
                $int_script = $tmp_file;
                else
                {
                    fwrite(STDERR, "File neexistuje. \n");
                    exit(11);
                } 
            }
            elseif ($arg == "--parse-only")
            {
                if ($int_only == false)
                    $parse_only = true;
                else
                {
                    fwrite(STDERR, "Parse-only sa nesmie kombinovat s int-only");
                    exit(10);
                }
            }
            elseif ($arg == "--int-only")
            {
                if ($parse_only == false)
                    $int_only = true;
                else
                {
                    fwrite(STDERR, "Int-only sa nesmie kombinovat s parse-only");
                    exit(10);
                }
            }
            elseif (strpos($arg, "--jaxamxml=") === 0)
            {
                $tmp_file = explode("--jaxamxml=", $arg)[1];
                if (file_exists($tmp_file))
                $jexamxml = $tmp_file;
                else
                {
                    fwrite(STDERR, "File neexistuje. \n");
                    exit(11);
                } 
            }
            elseif (strpos($arg, "--jaxamcfg=") === 0)
            {
                $tmp_file = explode("--jaxamcfg=", $arg)[1];
                if (file_exists($tmp_file))
                $jexamcfg = $tmp_file;
                else
                {
                    fwrite(STDERR, "File neexistuje. \n");
                    exit(11);
                } 
            }
            else
            {
                fwrite(STDERR, "Nespravny parameter \n");
                exit(10);
            }
        }
    }
}


// funkcia ktora porovna ci sa referencny vystup rovna vystupu parseru 
function check_parse_out($test_name, $file_out)
{
    global $jexamxml;
    global $pass;
    global $fail;


    exec("java -jar " .$jexamxml . " parse_out " . $file_out, $output, $diff);

    if ($diff == 0)
    {
        $pass++;
        return true;
    }
    else
    {
        $fail++;
        return false;
    }

}


// funkcia ktora vrati ci sa rovna referencna hodnota testovacej
function check_return_value($file_rc, $return_value)
{
    $tmp_file = fopen($file_rc, "r");
    $rc_value = fread($tmp_file, filesize($file_rc));
    $rc_value = (int)$rc_value;
    fclose($tmp_file);

    if ($return_value == $rc_value)
        return true;
    else
        return false;
}

// funkcia ktora porovna ci sa referency vystup rovna vystupu interpretu
function check_int_out($test_name, $file_out)
{
    global $pass;
    global $fail;

    exec("diff int_out " . $file_out, $output, $diff);

    if ($diff == 0)
    {
        $pass++;
        return true;
    }
    else
    {
        $fail++;
        return false;
    }
}

// funkcia ktora sluzi na tvorbu html casti
function print_html($counter, $name, $file_rc, $return_value, $result)
{
    global $tmp_html;
    global $tmp_dir;
    global $html_header;

    if ($result)
        $result = "ok";
    else    
        $result = "fail";

    $tmp_file = fopen($file_rc, "r");
    $rc_value = fread($tmp_file, filesize($file_rc));
    $rc_value = (int)$rc_value;
    fclose($tmp_file);

    $table = '';

    if ($html_header)
    {   
        if ($counter != 1)
            $table = $table . '</table>';

        $table = ' 
        <tr class="mytd" style="border: 1px solid #54565B;">
            <th colspan="5" class="header">Test zo sady: ' . $tmp_dir . ' </th>
        </tr>
        <tr class="mytd" style="border: 1px solid #54565B;">
            <td style="width: 7%;">Číslo testu</td>
            <td style="width: 55%;">Test</td>
            <td style="width: 7%;">Očakavaná hodnota</td>
            <td style="width: 7%;">Testovacia hodnota</td>
            <td style="width: 7%;">Výsledok</td>
        </tr> ';
    }


    $table = ' '. $table . '
    <tr class="' . $result . '">
        <td style="width: 7%;">' . $counter .'</td>
        <td style="width: 55%;">' . $name . '</td>
        <td style="width: 7%;">' . $rc_value . '</td>
        <td style="width: 7%;">' . $return_value . '</td>
        <td style="width: 7%;">' . $result . '</td>
    </tr>';

    if ($html_header)
    {
        $table = '<table class="tab2" style="background-color: #b1A296">' . $table;
    }

    $tmp_html = $tmp_html . $table;
}

?>