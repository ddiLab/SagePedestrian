<html>
    <head>
        <title>Testing Workspace</title>
    </head>
    <body>
        <h2 style="text-align: center;">This temporary page is used to test new ideas and see if they integrate well</h1>
        <div>
            <?php

                $command = "python3 ./SageBokeh.py";
                $output =null;
                $retval =null;
                exec($command,$output,$retval);
                if($output[0] != "None") 
                {
                    echo "<div id='map'></div>";
                    echo "<script type='text/javascript'>var traj = " . json_encode(($output[0])) . ";</script>";
                    echo "<script type='text/javascript' src='app.js'></script>";
                }

            ?>
        </div>
    </body>
</html>