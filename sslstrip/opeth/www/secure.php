<?php
    session_start();
    if(!isset($_SESSION["user_data"]["username"])){
        header("location:http://147.210.12.1/index.php");
        exit();
    } 
?>
<html>
  <body>
    <p> Hello, <?php echo $_SESSION["user_data"]["username"]; ?></p>
  </body>
</html>
