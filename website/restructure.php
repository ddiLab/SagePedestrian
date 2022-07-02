<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Crosswalk Detection</title>
        <link rel="stylesheet" href="//code.jquery.com/ui/1.13.1/themes/base/jquery-ui.css">
        <link rel="stylesheet" href="/resources/demos/style.css">
        <link rel="stylesheet" href="./traj.css">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css" integrity="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ==" crossorigin="" />
        <script src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js" integrity="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ==" crossorigin=""></script>    
        <script src="https://code.jquery.com/jquery-3.6.0.js"></script>
        <script src="https://code.jquery.com/ui/1.13.1/jquery-ui.js"></script>
        <script src="calendar.js"></script>
    </head> 
    <body style="background-color: #8AA574">
        <header>
            <nav class="navbar">
                <a href="index.html" class="navbar-name">
                    <h1 style="font-weight: 800; font-family:'Open Sans', sans-serif; font-size: 42px; display:inline; color: #8AA574;">
                        Sage
                        <p style="border-top: 2px solid black; font-weight: 100; font-family:'Open Sans', sans-serif; font-size: 19px; color: black;">
                            Crosswalk Detection
                        </p>
                    </h1>
                </a>
                <form action="restructure.php" method="GET" id="date">
                    <div style="text-align:center; display:inline-block;vertical-align:center;">
                        <input class="dateform" id="dateinput" type="text" name="date" style="margin: 0; font-size: 22px;" placeholder="Click to choose a date" />
                    </div>
                    <div class="separate"></div>
                    <div class="xwalk">
                        <input type="radio" name="xwalkOpts" checked="checked" value=0/>All options</br>
                        <input type="radio" name="xwalkOpts" value=4/>Both Crosswalk and Road
                    </div>
                    <div class="separate"></div>
                    <div class="xwalk">
                        <input type="radio" name="xwalkOpts" value=2/>Only Road</br>
                        <input type="radio" name="xwalkOpts" value=3/>Only Crosswalk</br>
                    </div> 
                    <div class="separate"></div> 
                    <div class="xwalk">
                        <input type="radio" name="xwalkOpts" value=1/>Neither crosswalk/road used</br>
                    </div>           
            </nav>
        </header>
        <div class="timediv" style="text-align:center;">
            <p class="textdecor" style="width:100%";>
            Choose Hour: 
                <input type="range" style="width:80%;margin:auto;" min="13" max="22" value="13" step="1" id="time" name="time" oninput="this.nextElementSibling.value = this.value" list="tickmarks">
                Hour: <output>13</output>
                <datalist id="tickmarks">
                    <option value="13"></option>
                    <option value="14"></option>
                    <option value="15"></option>
                    <option value="16"></option>
                    <option value="17"></option>
                    <option value="18"></option>
                    <option value="19"></option>
                    <option value="20"></option>
                    <option value="21"></option>
                    <option value="22"></option>
                </datalist>
                <div class="tooltip" style="display:inline;">  
                    <input type="checkbox" id="accum" name="accum" value="1">
                    <label for="accum" class="textdecor">Accumulate</label>
                    <span class="tooltiptext">Accumulates all hours up to the chosen hour <br> (ex: Hour 14 runs hours 13 and 14)</span>
                </div>               
            </p> 
        </div>
        <div class="submitdiv">
            <br><br>
                <input class="dateform" style="box-shadow:3px 3px grey" type="submit" style="font-size: 22px;" value="Submit"/>
            </div>
        </form>
            <?php
                if(!isset($_GET["date"])) return;
                
                //calendar created from jQuery has date as mm/dd/yyyy so it needs to be restructured
                $bad_date = $_GET["date"];
                $year = substr($bad_date,-4);
                $month = substr($bad_date, -10,2);
                $day = substr($bad_date, -7,2);
                $user_date = $year . "-" . $month . "-" . $day;

                $xwalk_opts = $_GET["xwalkOpts"];
                $timestop = $_GET["time"];
                $accum = $_GET["accum"];
                $timestart = ""; //only used if accumulate is checked always defaults to hour 13

                $paths = null;
                if($_GET["date"] == null){//new structure because javascript messing with alert messages
                    echo '<script>alert("Please enter a valid date.");</script>';
                }
                else{
                    $query = set_query($user_date, $xwalk_opts, $timestop, $timestart, $accum);
                    $command = "python3 ./process_image.py \"" . $query . "\" " . $user_date;
                    echo "Command: " . $command;
                    $output =null;
                    $retval =null;
                    exec($command,$output,$retval);
                    $no_data = false;
                    if($output[0] == "No data available"){
                        echo '<script>alert("No data in database for this day or time range.");</script>';
                    }
                    if(($user_date != null) && ($output[0] != "No data available")){
                        //echo "<img id='result' src='./images/user_img.jpg' alt='Temporary display' class='traj-img' />";
                        echo "<div class='map_outer'><div id='map'></div><div>";
                        echo "<script type='text/javascript'>var traj = " . json_encode(($output[0])) . ";</script>";
                        echo "<script type='text/javascript' src='app.js'></script>";
                    }else{
                        $no_data = true;
                        echo '<p>Image not available</p>';
                    }
                    echo '<div class="stats">';
                    echo '<h1>Trajectory Statistics</h1>';
                    echo '</div>';
                    echo "<table class='mastertable' style='margin:auto;'>";
                    echo "<tr>";
                    echo '<td class="graphcell">';
                        if(!$no_data) {
                            echo '<img src="./images/uses_per_hour.png" alt="Graph" class="graph">';
                        }
                        else{
                            echo "<p>Graph not available</p>";
                        }
                    echo "</td>";
                    echo '<td class="graphcell">';
                        if(!$no_data) {
                            echo '<img src="./images/xwalk_pie_per_hr.png" alt="Pie Chart" class="graph">';
                        }
                        else{
                            echo "<p>Graph not available</p>";
                        }
                    echo "</td>";
                    echo "</tr>";
                    echo "</table>";
                }
            ?>
    </body>
</html>
<?php

function set_query($date, $xwalk_opts, $timestop, $timestart, $accum) {

    $return_query = "";

    if($accum == 1){ //we are accumulating and must provide both start and stop times
        $timestart = $date . " " . "13:00:00";
        $timestop = $date . " " . $timestop . ":59:59";
        $opt = (int)$xwalk_opts;
        switch($opt) {
            case 0://WORKING!
                $return_query = "SELECT PERMAID,XCOORD,YCOORD from Coordinate where DATE >= " . "'" . $timestart . "'" . " and DATE <= " . "'" . $timestop . "'" . ';';
                break;
            case 1://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=0 and USECROSSWALK=0 intersect select PERMAID from Contains where DATE >= " . "'" . $timestart . "'" . " and DATE <= " . "'" . $timestop . "');";
                break;
            case 2://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 and USECROSSWALK=0 intersect select PERMAID from Contains where DATE >= " . "'" . $timestart . "'" . " and DATE <= " . "'" . $timestop . "');";
                break;
            case 3://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 and USECROSSWALK=1 intersect select PERMAID from Contains where DATE >= " . "'" . $timestart . "'" . " and DATE <= " . "'" . $timestop . "');";
                break;
            case 4://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select PERMAID from Contains where DATE >= " . "'" . $timestart . "'" . " and DATE <= " . "'" . $timestop . "');";
                break;
        }
        return $return_query;
    }
    else{   //we are not accumulating which means we only need 1 time (which becomes the timestart and timestop)
        $opt = (int)$xwalk_opts;
        $formatted_timestart = $date . " " . $timestop . ":00:00";
        $formatted_timestop = $date . " " . $timestop . ":59:59";
        switch($opt) {
            case 0://WORKING!
                $return_query = "SELECT PERMAID,XCOORD,YCOORD from Coordinate where DATE LIKE '" . $date . " " . $timestop . "%'";
                break;
            case 1://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=0 and USECROSSWALK=0 intersect select PERMAID from Contains where DATE >= " . "'" . $formatted_timestart . "'" . " and DATE <= " . "'" . $formatted_timestop . "');";
                break;
            case 2://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 and USECROSSWALK=0 intersect select PERMAID from Contains where DATE >= " . "'" . $formatted_timestart . "'" . " and DATE <= " . "'" . $formatted_timestop . "');";
                break;
            case 3://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 and USECROSSWALK=1 intersect select PERMAID from Contains where DATE >= " . "'" . $formatted_timestart . "'" . " and DATE <= " . "'" . $formatted_timestop . "');";
                break;
            case 4://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select PERMAID from Contains where DATE >= " . "'" . $formatted_timestart . "'" . " and DATE <= " . "'" . $formatted_timestop . "');";
                break;
        }
        return $return_query;
    }
}
?>
