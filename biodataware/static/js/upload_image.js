function uploadSize(name_id, msg_id) {
    if (typeof ($(name_id)[0].files) != "undefined") {
        //check upload file size
        var size = parseFloat($(name_id)[0].files[0].size / 1024 / 1024).toFixed(2); // cal the file size in MB
        if (size > 10) {
            $(msg_id).text('Maximum upload file size is 10MB!');
            return false;
        }

        //check the upload file format/exteions
        var type = $(name_id)[0].files[0].type;
        if (type == "image/png" || type == "image/jpeg" || type == "image/bmp" || type == "image/gif") {
            return true;
        }
        else {
            $(msg_id).text('Only allow for ".bmp", ".jpg", ".gif" and ".png"!');
            return false;
        }
    }
    return true;
}

function getFilePath(pathname, filename) {
    var fullPath = document.getElementById(pathname).value;
    fileName = fullPath.split(/(\\|\/)/g).pop();
    document.getElementById(filename).value = fileName;
}