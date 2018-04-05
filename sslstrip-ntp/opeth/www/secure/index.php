<?php
session_start();
if(isset($_POST["submit"])){
    $users = array(
        "user" => "toto",
        "admin"=>"password"
    );
    $username = isset($_POST["username"]) ? $_POST["username"] : "";
    $password = isset($_POST["password"]) ? $_POST["password"] : "";
    if(isset($users[$username]) && $password === $users[$username]){
        $_SESSION["user_data"]["username"] = $username;
        $msg = "Hello " . $username;
    }else{
        $msg = "Invalid Login";
    }
} else {
    if(isset($_SESSION["user_data"])) {
        $msg = "Welcome back, " . $_SESSION["user_data"]["username"];
    } else {
        $msg = "Not logged in";
        header('Location: http://www.opeth.local/index.php');
    }
}
?>
<html>
  <head>
    <title>Secure page</title>
  </head>
  <body>
    <h1>Secure page</h1>
    <p><?php echo $msg; ?></p>
  </body>
</html>
