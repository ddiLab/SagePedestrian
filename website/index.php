<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Crosswalk Detection</title>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-2.4.3.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.4.3.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-api-2.4.3.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.4.3.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.4.3.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-gl-2.4.3.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-mathjax-2.4.3.min.js"></script>
        <script type="text/javascript">
            Bokeh.set_log_level("info");
        </script>
        
        <link rel="stylesheet" href="./home.css">
        <link rel="stylesheet" href="./traj.css">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css" integrity="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ==" crossorigin="" />
        <script src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js" integrity="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ==" crossorigin=""></script>  
    </head> 
    <header>
        <nav class="navbar">
            <a href="index.php" class="navbar-name">
                <h1 style="font-weight: 800; font-family:'Open Sans', sans-serif; font-size: 42px; display:inline; color: #8AA574;">
                     Sage
                    <p style="border-top: 2px solid black; font-weight: 100; font-family:'Open Sans', sans-serif; font-size: 19px; color: black;">
                        Crosswalk Detection
                    </p>
                </h1>
            </a>
            <div class="navbar-menu-mobile">
                <br>
                <a href="restructure.php" class="textdecor">Debug/Filter</a>
                <br><br>
                <a href="blog.html" class="textdecor">Blog</a>
                <br><br>
                <a href="https://ddilab.cs.niu.edu/" class="textdecor">NIU ddiLab</a>
                <br><br>
                <a href="https://github.com/ddiLab/SagePedestrian" class="textdecor">Github</a>
                <br><br>
                <a href="https://sagecontinuum.org/" class="textdecor">Sage</a>
                <br><br>
            </div>
            <ul class="navbar-menu" style="list-style: none;">
                <li class="navlist">
                    <a href="restructure.php" class="textdecor">Debug/Filter</a>
                </li>
                <li class="navlist">
                    <a href="blog.html" class="textdecor">Blog</a>
                </li>
                <li class="navlist">
                    <a href="https://ddilab.cs.niu.edu/" class="textdecor">NIU ddiLab</a>
                </li>
                <li class="navlist">
                    <a href="https://github.com/ddiLab/SagePedestrian" class="textdecor">Github</a>
                </li>
                <li class="navlist">
                    <a href="https://sagecontinuum.org/" class="textdecor">Sage</a>
                </li>
            </ul>
            <div class="burger-style">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </div>
            <script src="burger.js"></script>
        </nav>
    </header>
    <body class="body1">
        <br><br><br><br><br><br><br><br>
        
            <?php
                $date = date('Y-m-d');  //format the date
                $date = date('Y-m-d',(strtotime ( '-1 day' , strtotime ( $date) ) ));   //subtract 1 from day
                //echo '<div class="image-caption">';
                $command = "python3 ./homepage.py";
                $output =null;
                $retval =null;
                exec($command,$output,$retval);
                echo "<p class='caption'>The following trajectories are the crosswalk detections for $output[0] between 8am - 5pm.</p>";
                echo '<br>';
                //Gets the output from the python command and places the JSON strings
                //into appropriate div tags to create bokeh graphs
                echo '<div class="image-container">';
                echo "<div id='map' style='width:90%;'></div>";
                //should convert this to a loop
                //embed items into graph and leaflet map
                if($output[0] != "{}")
                    echo "<script type='text/javascript'>var traj = " . json_encode(($output[1])) . ";</script>";
                else {
                    echo "<script type='text/javascript'>var traj = null; </script>";
                    //echo "<p class='caption'>Missing data for $date</p>";
                }
                //this REALLY should be a loop. Please
                echo "<script type='text/javascript'>
                    var item = " . json_encode(($output[2])) . ";
                    var line = " . json_encode(($output[3])) . ";
                    var sctr = " . json_encode(($output[4])) . ";
                    var drgh = " . json_encode(($output[5])) . ";
                    console.log(item, line, sctr, drgh);
                    item = JSON.parse(item);
                    line = JSON.parse(line);
                    sctr = JSON.parse(sctr);
                    drgh = JSON.parse(drgh);
                    Bokeh.embed.embed_item(item);
                    Bokeh.embed.embed_item(line);
                    Bokeh.embed.embed_item(sctr);
                    Bokeh.embed.embed_item(drgh);
                </script>";
                echo "</div>";
                echo "<script type='text/javascript' src='app.js'></script>";
            ?>
       
        <br><br>
        <hr class="solid">
        <br><br>
        <div class="image-caption">
            <p class="caption">The following graphs represent the recent trends over a larger period of time.</p>
        </div>
        <br><br>
        <div id="heatmap" class="mybokehplot bk-root"></div>
        <br/>
        <div id="doublelinegraph" class="mybokehplot bk-root"></div>
        <br/>
        <div id="scatterplot" class="mybokehplot bk-root"></div>
        <br/>
        <div id="directionplot" class="mybokehplot bk-root"></div>
        <br/>
        <hr class="solid" style="position: relative; bottom: 1px; left: 0px;">
        <p class="botleft">This material is based upon work supported by the National Science Foundation under Grant No. OAC 1935984.</p>
    </body>
</html>
