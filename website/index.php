<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Crosswalk Detection</title>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.0.2.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.0.2.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-api-3.0.2.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.0.2.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.0.2.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-gl-3.0.2.min.js"></script>
        <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-mathjax-3.0.2.min.js"></script>
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
                $command = "python3 /data/pedestrian/niu/homepage.py";
                $output =null;
                $retval =null;
                //echo phpinfo();
                exec($command,$output,$retval);
                echo "<p class='caption'>The following trajectories are the crosswalk detections for $output[0] between 8am - 5pm.</p>";
                echo '<br>';
                //Gets the output from the python command and places the JSON strings
                //into appropriate div tags to create bokeh graphs
                echo '<div class="image-container">';
                echo "<div id='map' style='width:90%;'></div>";
                echo "<script type='text/javascript' src='app.js'></script>";
                //should convert this to a loop
                //embed items into graph and leaflet map
                if($output[0] != "{}")
                    echo "<script type='text/javascript'>var traj = " . json_encode(($output[1])) . "; var alpha = .30; setUpMap();</script>";
                else {
                    echo "<script type='text/javascript'>var traj = null; setUpMap(); </script>";
                    //echo "<p class='caption'>Missing data for $date</p>";
                }

                //open graph data
                $file = fopen("graphs.txt", "r") or die("Cannot open graphs.txt");
                $graphs = fread($file, filesize("graphs.txt"));

                //this REALLY should be a loop. Please
                echo "<script type='text/javascript'>
                    var graphs = " . json_encode($graphs) . "
                    graphs = graphs.split('***');
                    //var item = " . json_encode(($output[2])) . ";
                    //var line = " . json_encode(($output[2])) . ";
                    //var drgh = " . json_encode(($output[5])) . ";
                    //console.log(item, line, sctr, drgh);
                    var item = JSON.parse(graphs[0]);
                    var line = JSON.parse(graphs[1]);
                    var drgh = JSON.parse(graphs[2]);
                    console.log(item);
                    console.log(line);
                    console.log(drgh);
                    Bokeh.embed.embed_item(item, 'heatmap');
                    Bokeh.embed.embed_item(line, 'doublelinegraph');
                    Bokeh.embed.embed_item(drgh, 'directionplot');
                </script>";
                echo "</div>";
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
