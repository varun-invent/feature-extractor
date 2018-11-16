<?php
    $currentDir = getcwd();
    $uploadDirectory = "/uploads/";

    $errors = []; // Store all foreseen and unforseen errors here

    $fileExtensions = ['nii','nii.gz']; // Get all the file extensions

    $fileName = $_FILES['brain']['name'];
    $fileSize = $_FILES['brain']['size'];
    $fileTmpName  = $_FILES['brain']['tmp_name'];
    $fileType = $_FILES['brain']['type'];
    $fileExtension = strtolower(end(explode('.',$fileName)));

    $uploadPath = $currentDir . $uploadDirectory . basename($fileName);

    if (isset($_POST['submit'])) {

        if (! in_array($fileExtension,$fileExtensions)) {
            $errors[] = "This file extension is not allowed. Please upload a .nii or .nii.gz file";
        }

        // if ($fileSize > 2000000) {
        //     $errors[] = "This file is more than 2MB. Sorry, it has to be less than or equal to 2MB";
        // }

        if (empty($errors)) {
            $didUpload = move_uploaded_file($fileTmpName, $uploadPath);

            if ($didUpload) {
                echo "The file " . basename($fileName) . " has been uploaded";
            } else {
                echo "An error occurred somewhere. Try again or contact the admin";
            }
        } else {
            foreach ($errors as $error) {
                echo $error . "These are the errors" . "\n";
            }
        }

        $threshold = $_POST['threshold'];

    }
?>
