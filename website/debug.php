<!DOCTYPE html>
<html lang="en">
    <head>
    </head>
    <body>
        <?php
            $command = "python3 ./get_trajectory_images.py " . $_GET['id'];
            //echo "Command: " . $command;
            $output = null;
            $retval = null;
            exec($command,$output,$retval);
            echo $output;

            if($output == "None") exit("No information");

            $handle = opendir('/var/www/html/images/debug_images/');
            if ($handle) {
                while (($entry = readdir($handle)) !== FALSE) {
                    echo '<img src="' . $entry . '" >';
                }
            }
            closedir($handle);
        ?>
    </body>
</html>
