$("#photo_fn").change(function(){
    getFilePath('photo_fn', 'photo_name');
})

$('form').submit(function(){
    return uploadSize('#photo_fn', '#photo_msg');
})