<?php
    session_start();
    if(isset($_POST["submit"])){
        $users = array(
                        "user" => "toto",
                        "admin"=>"password"          
                );
        $username = isset($_POST["username"]) ? $_POST["username"] : "";
        $password = isset($_POST["password"]) ? $_POST["password"] : "";
        if(isset($users[$username]) && $password == $users[$username]){
            $_SESSION["user_data"]["username"] = $users[$username];
            header("location: https://147.210.12.1/secure.php");
            exit();
        }else{
            $msg = "Invalid Login";
        }
    }
?>
<html>
  <head>
    <title> Index </title>
  </head>
  <body>
    <h1>Welcome to our page</h1>

    <form action="" method="post">
        <p><?php if (isset($msg)) echo $msg;?></p>
        <p>Username : <input type="text" name="username" id="username" autocomplete="off"/></p>
        <p>Password : <input type="password" name="password" id="password" autocomplete="off"/></p>
        <input type="submit" name="submit" value="Login" autocomplete="off">
    </form>
  </body>
</html>
