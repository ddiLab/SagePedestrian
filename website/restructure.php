<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Crosswalk Detection</title>
        <link rel="stylesheet" href="//code.jquery.com/ui/1.13.1/themes/Le-Frog/jquery-ui.css">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css" integrity="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ==" crossorigin="" />
        
        <script src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js" integrity="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ==" crossorigin=""></script>    
        <script src="https://code.jquery.com/jquery-1.9.1.js"></script>
        <script src="https://code.jquery.com/ui/1.9.2/jquery-ui.js"></script>
        <link rel="stylesheet" href="./traj.css">
        <link rel="stylesheet" href="./calendar.css">
    </head> 
    <body style="background-color: #8AA574">
    <input type="file" name="inputfile" id="inputfile" style="display:hidden;">
        <header>
            <nav class="navbar2">
                <a href="index.php" class="navbar-name2">
                    <h1 style="font-weight: 800; font-family:'Open Sans', sans-serif; font-size: 42px; display:inline; color: #8AA574;">
                        Sage
                        <p style="border-top: 2px solid black; font-weight: 100; font-family:'Open Sans', sans-serif; font-size: 19px; color: black;">
                            Crosswalk Detection
                        </p>
                    </h1>
                </a>
                <form action="restructure.php" method="GET" id="date">
                    <div style="text-align:center; display:inline-block;vertical-align:center;">
                    <?php
                            $command1 = "python3 ./get_dates.py";
                            $output1 =null;
                            $retval1 =null;
                            exec($command1,$output1,$retval1);
                            //echo $output1[0];
                            //echo "json here: " . json_encode($output1[0]);
                            if($output1[0] != "None") 
                            {   
                                echo "<script>var dates = " . json_encode($output1[0]) . ";</script>";
                                echo '<input class="dateform" id="dateinput" type="text" name="date" style="margin: 0; font-size: 22px;" placeholder="Click to choose date" />';
                                #echo "<script>var dates = " . json_encode($output1[0]) . ";</script>";
                                echo "<script src='calendar.js'></script>";
                            }
                    ?>
                    </div>
                    <div class="navbar-menu-mobile2">
                        <input type="radio" name="xwalkOpts" checked="checked" value=0 />All options</br>
                        <input type="radio" name="xwalkOpts" value=4 />Crosswalk and Road<br>
                        <input type="radio" name="xwalkOpts" value=2 />Only Road</br>
                        <input type="radio" name="xwalkOpts" value=3 />Only Crosswalk</br>
                        <input type="radio" name="xwalkOpts" value=1 />Neither crosswalk/road</br>
                    </div>
                    <div class="burger-style2">
                        </br>
                        <span class="bar2"></span>
                        <span class="bar2"></span>
                        <span class="bar2"></span>
                    </div>
                    <script src="burger2.js"></script>
                    <div class="separate"></div>
                    <div class="xwalk">
                        <input type="radio" name="xwalkOpts" checked="checked" value=0 />All options</br>
                        <input type="radio" name="xwalkOpts" value=4 />Both Crosswalk and Road
                    </div>
                    <div class="separate"></div>
                    <div class="xwalk">
                        <input type="radio" name="xwalkOpts" value=2 />Only Road</br>
                        <input type="radio" name="xwalkOpts" value=3 />Only Crosswalk</br>
                    </div> 
                    <div class="separate"></div> 
                    <div class="xwalk">
                        <input type="radio" name="xwalkOpts" value=1 />Neither crosswalk/road used</br>
                    </div>           
            </nav>
        </header>
            <div class="timediv" style="text-align:center;">
                <div>
                    <p style="width:100%;text-align:center;display:block;font-size:20px;">Choose Hour Range: </p>
                </div>
                <div style="width:100%;margin:auto;">
                    <script src='slider.js'></script>
                    <input type="text" class="sliderValue" data-index="0" value=13 id="timestart" name="timestart" style="width:15px;"/>
                    <div id="slider" class="slider"></div>
                    <input type="text" class="sliderValue" data-index="1" value=22 id="timestop" name="timestop" style="width:15px;"/> 
                </div>
        </div>
        <div class="submitdiv">
            <br><br>
                <input class="dateform" style="box-shadow:3px 3px grey" type="submit" style="font-size: 22px;" value="Submit"/>
            </div>
        </form>
        <div class="mobilespacing">
            <br><br><br><br><br><br><br><br><br>
        </div>
            <?php
                if(!isset($_GET["date"])) return;
                
                $user_date = $_GET["date"];
                $xwalk_opts = $_GET["xwalkOpts"];
                $timestop = $_GET["timestop"];
                $timestart = $_GET["timestart"];

                //these should be numbers
                if(!is_numeric($xwalk_opts)) { echo "Failure"; return; }
                if(!is_numeric($timestop)) { echo "Failure"; return; }
                if(!is_numeric($timestart)) { echo "Failure"; return; }

                $paths = null;
                if($_GET["date"] == null){//new structure because javascript messing with alert messages
                    echo '<script>alert("Please enter a valid date.");</script>';
                }
                else{
                    $query = set_query($user_date, $xwalk_opts, $timestop, $timestart);
                    $command = "python3 ./process_image.py \"" . $query . "\" " . $user_date;
                    //echo "Command: " . $command;
                    $output =null;
                    $retval =null;
                    exec($command,$output,$retval);
                    $no_data = false;
                    if($output[0] == "No data available"){
                        echo '<script>alert("No data for this time range.");</script>';
                    }
                    if(($user_date != null) && ($output[0] != "No data available")){
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

function set_query($date, $xwalk_opts, $timestop, $timestart) {
    $return_query = "";
    $time_start = $date . " " . $timestart . ":00:00";//get all data
    $time_stop = $date . " " . $timestop . ":59:59";//get all data
    $opt = (int)$xwalk_opts;
        switch($opt) {
            case 0://WORKING!
                $return_query = "SELECT PERMAID,XCOORD,YCOORD from Coordinate where DATE between '" . $time_start . "' and '" . $time_stop . "' order by PERMAID;";
                break;
            case 1://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=0 and USECROSSWALK=0 intersect select PERMAID from Contains where DATE between '" . $time_start . "' and '" . $time_stop . "') order by PERMAID;";
                break;
            case 2://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 and USECROSSWALK=0 intersect select PERMAID from Contains where DATE between '" . $time_start . "' and '" . $time_stop . "') order by PERMAID;";
                break;
            case 3://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 and USECROSSWALK=1 intersect select PERMAID from Contains where DATE between '" . $time_start . "' and '" . $time_stop . "') order by PERMAID;";
                break;
            case 4://WORKING!
                $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select PERMAID from Contains where DATE between '" . $time_start . "' and '" . $time_stop . "') order by PERMAID;";
                break;
        }
    return $return_query;
}
?>