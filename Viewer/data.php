<?php
    header('Content-type: application/json');
    echo(file_get_contents('../Server/state.json'));
?>