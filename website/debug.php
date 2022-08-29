<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <title>Crosswalk Detection</title>
        <link rel="stylesheet" href="./home.css">
        <link rel="stylesheet" href="./traj.css">
        <link rel="stylesheet" href="./debug.css">
        <script src="./carousel.js" ></script>
    </head> 
    <header>
        <nav class="navbar4">
            <a href="index.php" class="navbar-name4">
                <h1 style="font-weight: 800; font-family:'Open Sans', sans-serif; font-size: 42px; display:inline; color: #8AA574;">
                     Sage
                    <p style="border-top: 2px solid black; font-weight: 100; font-family:'Open Sans', sans-serif; font-size: 19px; color: black;">
                        Crosswalk Detection
                    </p>
                </h1>
            </a>
            <div class="hideable">
                <ul>
                    <li class="navlist4">
                        <a href="restructure.php" class="textdecor">Debug/Filter</a>
                    </li>
                    <li class="navlist4">
                        <a href="blog.html" class="textdecor">Blog</a>
                    </li>
                    <li class="navlist4">
                        <a href="https://ddilab.cs.niu.edu/" class="textdecor">NIU ddiLab</a>
                    </li>
                    <li class="navlist4">
                        <a href="https://github.com/ddiLab/SagePedestrian" class="textdecor">Github</a>
                    </li>
                    <li class="navlist4">
                        <a href="https://sagecontinuum.org/" class="textdecor">Sage</a>
                    </li>
                </ul>
            </div>
            <div class="navbar-menu-mobile4">
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
            <div class="burger-style4">
                <span class="bar4"></span>
                <span class="bar4"></span>
                <span class="bar4"></span>
            </div>
            <script src="burger4.js"></script>
        </nav>
    </header>
    <body style="background-color: #8AA574">
        <?php
            $command = "python3 ./get_trajectory_images.py " . $_GET['id'];
            if(!is_numeric($_GET['id'])) { echo "Failure"; return; }    //must be a number
            $output = null;
            $retval = null;
            exec($command,$output,$retval); //execute command to retrieve images from hartley server

            if($output[0] == "None") echo "Failure";

            //thanks SO
            $dir = './images/debug_images/';
            $files = scandir($dir);
            sort($files);
            echo "<div class='carousel'><div class='im'>";
            $count = 0;
            $extension = "class=\"showplease\"";
            foreach ($files as $file) {
                if ($file != '.' && $file != '..') {
                    //this is dumb but php is dumber
                    echo ( '<img ' . $extension . ' src="' . $dir . $file . '"/>' );
                    $extension = "";
                }
            }
            echo "<div class='buttons'>";
            echo "<div id='previous' class='prev'></div>";
            echo "<div id='next' class='next'></div>";
            echo "</div>";
            echo "</div></div>";
        ?>
    </body>
</html>