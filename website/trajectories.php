<html lang="en">
    <head>
        <title>Trajectories</title>
        <link rel="stylesheet" href="menu.css">
    </head>
    <body class="body2">
        <header>
            <nav class="navbar2">
                <a href="index.html" class="navbar-name">Northern Illinois University Sage Project</a>
                <ul class="navbar-menu" style="list-style: none;">
                    <span class="bar2"></span>
		            <li>
                        <a href="trajectories.php" class="navbar-menu-item">Daily Trajectories</a>
                    </li>
		            <span class="bar2"></span>
                    <li>
                        <a href="#" class="navbar-menu-item">Other Analytics Here</a>
                    </li>
                    <span class="bar2"></span>
                </ul>
                <div class="burger-style">
                    <span class="bar"></span>
                    <span class="bar"></span>
                    <span class="bar"></span>
                </div>
            </nav>
        </header>
	    <table class="mastertable">
	        <tr>
	            <td class="mastercell1" colspan="1">
	                <ul class="big-list">
                        <li>
                            <div class="topnav2">
                                <form action="trajectories.php" method="GET" id="date">
                                    <h1>Enter date to find trajectories</h1>
                                    <input class="dateform" type="date" name="date" style="margin: 0; font-size: 22px;" id="date_input">
                                    <input class="dateform" type="submit" style="font-size: 22px;" value="Submit" onclick="checkifValid()"/>
		                            <script>
                                        function checkifValid(){
                                                let variable = document.getElementById("date_input").value;
                                                if(variable.length != 10){
                                                        alert("Please choose a valid date");
                                                }
                                        }
        	                        </script>
		                            </br></br>
                                    <table class="center" >
                                        <tr>
                                            <th class="border" colspan=3>Used Crosswalk / Crossed Road</th>
                                        </tr>
                                        <tr>
                                            <td class="border" colspan=3>
                                                <div style="text-align: left; margin: 3px;">
                                                    <input type="radio" name="xwalkOpts" checked="checked" value=0/>All options</br>
                                                    <input type="radio" name="xwalkOpts"  value=1/>Neither crosswalk/road used</br>
                                                    <input type="radio" name="xwalkOpts" value=2/>Only Road</br>
                                                    <input type="radio" name="xwalkOpts" value=3/>Only Crosswalk</br>
                                                    <input type="radio" name="xwalkOpts" value=4/>Both Crosswalk and Road</br>
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td colspan="4" style="text-align: center;">
                                                <span class="bar3"></span>
                                                <h3>Time Range (Default is the entire day)</h3>
                                                <h4>Hours with valid data: 8:00am - 5:00pm</h4>
                                            </td>
                                        </tr>
                                        <tr style="text-align: center;">
                                            <td colspan="2">
                                                <label for="timestart">Time Start:</br></label>
                                                <input type="time" value="08:00" id="timestart" name="timestart" />
                                            </td>
                                            <td colspan="2">
                                                <label for="timestop">Time Stop:</br></label>
                                                <input type="time" value="17:59" id="timestop" name="timestop" />
                                            </td>
                                        </tr>
                                        <tr>
                                            <td colspan="4">
                                                <br>
                                                <span class="bar3"></span>
                                            </td>
                                        </tr>
                                        <?php
                                            echo "</table>";
                                            echo "</br>";
                                            if(isset($_GET['date']) && $_GET['date'] !== ""){
                                                $user_option = $_GET['xwalkOpts'];
                                                $user_option = $user_option + 1;
                                                $user_choice = "Generated results for: " . $_GET['date'] . " Between hours " . $_GET['timestart'] . " and " . $_GET['timestop'] . "\n" 
                                                . " with crossing option " . $user_option . "\n";
                                                echo $user_choice;
                                            }
                                        ?>
                                </form>
                            </div>
                        </li>
                    </ul>
                </td>
                <td class="mastercell2" colspan="3">
                    <?php
                        if(!isset($_GET["date"])) return;
                        
                        $user_date = $_GET["date"];
                        $xwalk_opts = $_GET["xwalkOpts"];
                        $time_start = $_GET["timestart"];
                        $time_stop = $_GET["timestop"];
        
                        $query = set_query($user_date, $xwalk_opts, $time_start, $time_stop);

                        //echo "Query: " . $query;
                        //echo "<br>";
                        $command = "python3 ./process_image.py \"" . $query . "\" " . $user_date;
                        //echo "Command: " . $command;
                        //echo "<br>";
                        $output =null;
                        $retval =null;
                        exec($command,$output,$retval);
                        //foreach ($output as $res)
                        //{
                           // echo '<script>alert("' . $output[0] . '");</script>';
                        //}
                        $no_data = false;
                        if($output[0] == "No data available"){
                            echo '<script>alert("No data in database for this day or time range");</script>';
                        }
                        if(($user_date != null) && ($output[0] != "No data available")){
                            echo "<img src='./images/user_img.jpg' alt='Temporary display' class='traj-img'>";
                        }else{
                            $no_data = true;
                            echo '<p>Image not available</p>';
                        }
                echo "</td>";
            echo "</tr>";
        echo "</table>";
        echo '<hr class="solid" style="position:relative;">';
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
                echo '<td class="graphcell">';
                    if(!$no_data) {
                        echo '<img src="./images/crosswalk_heatmap.png" alt="Pie Chart" class="graph">';
                    }
                    else{
                        echo "<p>Graph not available</p>";
                    }
                echo "</td>";
            echo "</tr>";
            echo "<tr>";
            echo '<td class="graphcell">';
                if(!$no_data) {
                    echo '<img src="./images/crosswalk_line_chart.png" alt="Line Graph" class="graph">';
                }
                else{
                    echo "<p>Graph not available</p>";
                }
            echo "</td>";
            echo "</tr>";
        echo "</table>";
    ?>
	<script src="app.js"></script>
    </body>
</html>

<?php

function connectToDB() { return (new PedestrianDetectionDB()); }

function set_query($date, $xwalk_opts, $time_start, $time_stop) {

    $return_query = "";
    $start = "13:00";
    $stop = "22:59";
    if(isset($time_start) && $time_start !== "") {
        //add 5 to the time to match offset of camera
        $hoursub = substr($time_start, -5, 2);
        $minutesub = substr($time_start, -2);
        $intvalue = intval($hoursub);
        $intvalue = $intvalue + 5;
        $new_hr_str = strval($intvalue);
        $concat = $new_hr_str . ":" . $minutesub;
        $start = $concat;
    }

    if(isset($time_stop) && $time_stop !== "") {
        //add 5 to the time to match offset of camera
        $hoursub = substr($time_stop, -5, 2);
        $minutesub = substr($time_stop, -2);
        $intvalue = intval($hoursub);
        $intvalue = $intvalue + 5;
        $new_hr_str = strval($intvalue);
        $concat = $new_hr_str . ":" . $minutesub;
        $stop = $concat;
    }

    $start = $date . " " . $start . ":00";
    $stop = $date . " " . $stop . ":59";

    $opt = (int)$xwalk_opts;
    switch($opt) {
        case 0:
            $return_query = "SELECT PERMAID,XCOORD,YCOORD from Coordinate where DATE >= DATE('" . $start . "') and DATE <= DATE('" . $stop . "')+1;";
            break;
	    case 1:
            $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=0 and USECROSSWALK=0 intersect select PERMAID from Contains where DATE >= DATE('" . $start . "') and DATE <= DATE('" . $stop . "')+1);";
	        break;
	    case 2:
            $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 and USECROSSWALK=0 intersect select PERMAID from Contains where DATE >= DATE('" . $start . "') and DATE <= DATE('" . $stop . "')+1);";
	        break;
	    case 3:
            $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 and USECROSSWALK=1 intersect select PERMAID from Contains where DATE >= DATE('" . $start . "') and DATE <= DATE('" . $stop . "')+1);";
	        break;
        case 4:
            $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select PERMAID from Contains where DATE >= DATE('" . $start . "') and DATE <= DATE('" . $stop . "')+1);";
            break;
    }
    return $return_query;
}
?>
