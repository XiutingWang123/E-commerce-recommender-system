<form action="/recommend" method="post">
Enter source items: <input name="keywords" type="text" />
<input type="submit" /><br/>
</form>

<p>You clicked these items: {{keyword}}</p>

<p>You may also like: </p>

<table border="0">
   %for item in recommend_list:
     <tr>
       <td>Item ID: {{item}}</td>
     </tr>
   %end
</table>