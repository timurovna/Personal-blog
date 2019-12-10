<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    <form method="post" action="/edited_post_submit">
        <i>Write post heading...</i><br>
        <textarea name="heading" rows="3" cols="40">{{heading}}</textarea><br>
        <i>Write post text...</i><br>
        <textarea name="text" rows="10" cols="40">{{text}}</textarea><br>
         <input type="hidden" name="post_id" value="{{post_id}}">
        <input type="submit" value="Update">
    </form>

</body>
</html>