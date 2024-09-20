<!DOCTYPE html>
<html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Logowanie</title>
        <style>
            body{
                font-family: "Source Sans Pro", sans-serif;
                /* background-color: #B0C4DE; */
            }
            input{
                width: 25rem;
                height: 2rem;
                border-radius: 10px;
                border: none;
                /* border: #333333 solid; */
            }
            h2{
                color: #333333;
                text-align: center;
            }
            .formularz{
                text-align: center;
                position: absolute;
                top: 30%;
                left: 50%;
                transform: translate(-50%, -50%);
                border: black solid;
                border-radius: 10px;
                width: 35rem;
                height: 22.5rem;
                background-color: #B0C4DE;
            }
            form{
            }
            .button{
                font-size: 1rem;
                font-weight: bold;
                margin-top: 2rem;
                width: 25rem;
                height: 3rem;
                border-radius: 10px;
                border: #B0C4DE solid;
                background-color: white;
            }
            label{
                font-weight: bold;
                font-size: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="formularz">
            <form method="POST">
                <h2>Logowanie</h2>
                <br><label>Podaj login:</label>
                <br><input type="text" id="login" name="login"><br>
                <br><label>Podaj hasło:</label>
                <br><input type="password" id="haslo" name="haslo"><br>
                <br><input class="button" type="submit" value="Zaloguj" id="zaloguj" name="zaloguj"><br>
            </form>
        </div>
    </body>
</html>
