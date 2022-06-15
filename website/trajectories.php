<html lang="en">
    <head>
        <title>
            Trajectories
        </title>
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
	<td class="mastercell1">
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
                                        <input type="checkbox" name="north" checked="checked"/> North</br>
                                        <input type="checkbox" name="west" checked="checked"/> West</br>
                                        <input type="checkbox" name="east" checked="checked"/> East<br> 
                                        <input type="checkbox" name="south" checked="checked"/> South</br>
                                    </div>
                                </td>
                                <td class="border">
                                    <div class="rdirectional">
                                        <input type="radio" checked="checked" name="raw" value="true"/>Raw</br>
                                        <div class="tooltip"><input type="radio" name="raw" value="false"/>Cleaned<span class="tooltiptext">What is cleaned data?</span></br></div>
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
                    </table>
                    </br>
                    <div id="date_alert" style="color: #FFFFFF"></br></div>
                </form>
            </div>
        </li>
        <li>
            <div class="topnav3">
                <h1>Trajectory Statistics</h1>
            </div>
        </li>
	</td>
        <td class="mastercell2">

        <?php
        echo '<li style="list-style:none;">';
        //the user has submitted a search query
	    if(!isset($_GET["north"])) return;
        if(!isset($_GET["date"])) return;
        
        $user_date = $_GET["date"];

    	$xwalk_opts = $_GET["xwalkOpts"];

        $query = set_query($user_date, $xwalk_opts);

	    //echo "Query: " . $query;
	    //echo "<br>";
	    $command = "python3 process_image.py \"" . $query . "\" ";
        //echo "Command: " . $command;
        //echo "<br>";
	    $output =null;
	    $retval =null;
	    exec($command,$output,$retval);
        //echo '<p>' . $output[0] . '</p>';

        echo "</li>";
        echo "</ul>";
	    if($output[0] == "No data available"){
		    echo '<script>alert("No data in database for this day");</script>';
	    }
	    if(($user_date != null) && ($output[0] != "No data available")){
		    echo '<img src="./images/user_img.jpg" alt="Temporary display" class="traj-img">';
	    }else{
	    	    echo '<p>Image not available</p>';
            }
    	?>
	</td>
	<script src="app.js"></script>
    </body>
</html>

<?php
class PedestrianDetectionDB extends SQLite3
{
    function __construct()
    {
        $this->open('/home/justind/Website/pedestrian_detections.db');
    }
}

/*
Gets the draw on image using the results from the search query.
Calls a python script that draws on the image based on the query.
*/
function getImage(
    $date,
    $northFlag,
    $westFlag,
    $eastFlag,
    $southFlag,
    $raw,
    $useRoad,
    $useCrosswalk
)
{

}

function connectToDB() { return (new PedestrianDetectionDB()); }

function set_query($date, $xwalk_opts){
/*
    if($north && (!$south)){
	return "SELECT (a.PERMAID),(a.XCOORD),(a.YCOORD) FROM (SELECT NS FROM Person WHERE NS == 1 INTERSECT SELECT PERMAID,XCOORD,YCOORD from Coordinate WHERE DATE LIKE '" . $date . "%' as a;";
    }
    else{
*/  $opt = (int)$xwalk_opts;
    switch($opt)
    {
        case 0:
            return "SELECT PERMAID,XCOORD,YCOORD from Coordinate where DATE like '" . $date . "%';";
            break;
	    case 1:
            return "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in 
                    (select PERMAID from Person where USEROAD==0 and USECROSSWALK==0 
                        intersect select PERMAID from Contains where DATE like '" . $date . "%');";
	        break;
	    case 2:
            return "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in 
                    (select PERMAID from Person where USEROAD==1 and USECROSSWALK==0 
                        intersect select PERMAID from Contains where DATE like '" . $date . "%');";
	        break;
	    case 3:
            return "SELECT PERMAID, XCOORD, YCOORD from Coordinate where PERMAID in 
                    (select PERMAID from Person where USEROAD==1 and USECROSSWALK==1 
                        intersect select PERMAID from Contains where DATE like '" . $date . "%');";
	        break;
    }
    
    //return "SELECT PERMAID,XCOORD,YCOORD from Coordinate where DATE like '" . $date . "%';";
   /* } */
}
?>
