<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
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
            <ul>
                <li class="navlist">
                    <a href="restructure.php" class="textdecor">Debug/Filter</a>
                </li>
                <li class="navlist">
                    <a href="blog.html" class="textdecor">The Process</a>
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
                <li class="navlist">
                    <a href="SageBokeh.html" class="textdecor">Testing Workspace (Temporary)</a>
                    <!--<a href="bokehtests.html" class="textdecor">Testing Workspace (Temporary)</a> -->
                </li>
            </ul>
        </nav>
    </header>
    <body class="body1">
        <br><br><br><br><br><br><br><br>
        
            <?php
                $date = date('Y-m-d');
                $date = date('Y-m-d',(strtotime ( '-1 day' , strtotime ( $date) ) ));
                echo '<div class="image-caption" style="margin:auto;width:65.3%;">';
                echo "<p class='caption'>The following trajectories are the crosswalk detections for $date between 8am - 5pm.</p>";
                echo '</div>';
                echo '<br>';
                $command = "python3 ./homepage.py";
                $output =null;
                $retval =null;
                exec($command,$output,$retval);
                if($output[0] != "None") 
                {
                    echo "<div id='map'></div>";
                    echo "<script type='text/javascript'>var traj = " . json_encode(($output[0])) . ";
                                                         var item = " . json_encode(($output[1])) . ";
                                                         item = JSON.parse(item);
                                                         Bokeh.embed.embed_item(item);
                    </script>";
                    echo "<script type='text/javascript' src='app.js'></script>";
                }
            ?>
       
        <br><br>
        <hr class="solid">
        <br><br>
        <div class="image-caption" style="margin: auto; width: 60%;">
            <p class="caption">The following graphs represent the recent trends over a larger period of time.</p>
        </div>
        <br><br>
        <table style="margin: auto; border-spacing: 50px;">
            <tr>
                <td>
                    <div style="text-align: center; margin: auto;">
                        <img src="./images/crosswalk_heatmap.png" alt="Heatmap" style="margin:auto;width:auto;">
                        <p class="caption" style=" border: 5px solid #343c4d; padding: 10px; display: block; width:auto; margin:auto; background-color: #FFFFFF;">
                            Heatmap showing which hours have the highest frequency of crosswalk usages<br>(Yellow being the most frequent, purple the least)</p>   
                    </div>
                </td>
                <td>
                    <div style="text-align: center; margin: auto;">
                        <img src="./images/crosswalk_line_chart.png" alt="Line" style="margin:auto;width:auto;">
                        <p class="caption" style="border: 5px solid #343c4d; padding: 10px; display:block; width:auto;margin:auto;background-color: #FFFFFF;">
                            Line graph showing the overall trends of the amount of people using the <br> crosswalk per day</p>
                    </div>
                </td>
            </tr>
        </table>
        <div id="heatmap" class="mybokehplot bk-root"></div>
        <br>
        <hr class="solid" style="position: relative; bottom: 1px; left: 0px; width: 100%;">
        <p class="botleft">This material is based upon work supported by the National Science Foundation under Grant No. OAC 1935984.</p>
    </body>
</html>
