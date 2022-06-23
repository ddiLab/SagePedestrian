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
                                            <th class="border">Directional Filters</th>
                                            <th class="border">Raw vs. Cleaned</th>
                                            <th class="border">Used Crosswalk / Crossed Road</th>
                                        </tr>
                                        <tr>
                                            <td class="border">
                                                <div class="ldirectional">
                                                    <input type="checkbox" name="north" checked="checked" value=10/> North</br>
                                                    <input type="checkbox" name="west" checked="checked" value=11/> West</br>
                                                    <input type="checkbox" name="east" checked="checked" value=12/> East<br> 
                                                    <input type="checkbox" name="south" checked="checked" value=13/> South</br>
                                                </div>
                                            </td>
                                            <td class="border">
                                                <div class="rdirectional">
                                                    <input type="radio" checked="checked" name="raw" value="true"/>Raw</br>
                                                    <div class="tooltip"><input type="radio" name="raw" value="false"/>Cleaned<span class="tooltiptext">Cleaned: outliers removed from data set</span></br></div>
                                                </div>
                                            </td>
                                            <td class="border">
                                                <div style="text-align: left; margin: 3px;">
                                                    <input type="radio" name="xwalkOpts" checked="checked" value=0/>All options</br>
                                                    <input type="radio" name="xwalkOpts"  value=1/>Neither crosswalk/road used</br>
                                                    <input type="radio" name="xwalkOpts" value=2/>Used Road</br>
                                                    <input type="radio" name="xwalkOpts" value=3/>Used Crosswalk</br>
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td colspan="4" style="text-align: center;">
                                                <span class="bar3"></span>
                                                <h3>Time Range (Default is the entire day)</h3>
                                                <h4>Hours with valid data: 8am - 5pm</h4>
                                            </td>
                                        </tr>
                                        <tr style="text-align: center;">
                                            <td colspan="2">
                                                <label for="timestart">Time Start:</br></label>
                                                <input type="time" value="08:00" id="timestart" name="timestart" />
                                            </td>
                                            <td colspan="2">
                                                <label for="timestop">Time Stop:</br></label>
                                                <input type="time" value="17:00" id="timetop" name="timestop" />
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

                        $north = $_GET["north"];
                        $east = $_GET["east"];
                        $south = $_GET["south"];
                        $west = $_GET["west"];

                        $raw = $_GET["raw"];
        
                        $query = set_query($user_date, $xwalk_opts, $time_start, $time_stop, $north, $east, $south, $west, $raw);

                        //echo "Query: " . $query;
                        //echo "<br>";
                        $command = "python3 process_image.py \"" . $query . "\" " . $user_date;
                        //echo "Command: " . $command;
                        //echo "<br>";
                        $output =null;
                        $retval =null;
                        exec($command,$output,$retval);
                        //echo '<p>' . $output[0] . '</p>';
                        $no_data = false;
                        if($output[0] == "No data available"){
                            echo '<script>alert("No data in database for this day");</script>';
                        }
                        if(($user_date != null) && ($output[0] != "No data available")){
                            echo '<img src="./images/user_img.jpg" alt="Temporary display" class="traj-img">';
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
                        //echo '<img src="./images/xwalk_per_hr.png" alt="Graph" class="graph">';
                    }
                    else{
                        echo "<p>Graph not available</p>";
                    }
                echo "</td>";
                echo '<td class="graphcell">';
                    if(!$no_data) {
                        echo '<img src="./images/xwalk_pie_per_hr.png" alt="Pie Chart" class="graph">';
                        //echo '<img src="./images/xwalk_per_hr.png" alt="Graph" class="graph">';
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
class PedestrianDetectionDB extends SQLite3 {
    function __construct() {
        $this->open('./db/pedestrian_detections.db');
    }
}

function connectToDB() { return (new PedestrianDetectionDB()); }

function set_query($date, $xwalk_opts, $time_start, $time_stop, $north, $east, $south, $west, $raw) {

    $return_query = "";
    $start = "08:00";
    $stop = "17:00";
    if(isset($time_start) && $time_start !== "") {
        $start = $time_start;
    }

    if(isset($time_stop) && $time_stop !== "") {
        $stop = $time_stop;
    }

    $start = $date . "T" . $start . ":00";
    $stop = $date . "T" . $stop . ":00";

    $opt = (int)$xwalk_opts;
    switch($opt) {
        case 0:
            $return_query = "SELECT PERMAID,XCOORD,YCOORD from Coordinate where DATE like '" . $date . "%'
                                and datetime(DATE) >= datetime('" . $start . "')
                                and datetime(DATE) <= datetime('" . $stop . "');";
            break;
	    case 1:
            $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in 
                    (select PERMAID from Person where USEROAD==0 and USECROSSWALK==0 
                        intersect select PERMAID from Contains where DATE like '" . $date . "%'
                        and datetime(DATE) >= datetime('" . $start . "')
                        and datetime(DATE) <= datetime('" . $stop . "'));";
	        break;
	    case 2:
            $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in 
                    (select PERMAID from Person where USEROAD==1 and USECROSSWALK==0 
                        intersect select PERMAID from Contains where DATE like '" . $date . "%'
                        and datetime(DATE) >= datetime('" . $start . "')
                        and datetime(DATE) <= datetime('" . $stop . "'));";
	        break;
	    case 3:
            $return_query = "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in 
                    (select PERMAID from Person where USEROAD==1 and USECROSSWALK==1 
                        intersect select PERMAID from Contains where DATE like '" . $date . "%'
                        and datetime(DATE) >= datetime('" . $start . "')
                        and datetime(DATE) <= datetime('" . $stop . "'));";
	        break;
    }
    return $return_query;
}
?>
